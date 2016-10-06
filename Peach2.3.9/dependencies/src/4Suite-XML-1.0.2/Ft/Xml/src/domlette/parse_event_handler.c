#include "parse_event_handler.h"
#include "expat_module.h"
#include "domlette.h"

/*#define DEBUG_PARSER */
#define INITIAL_CHILDREN 4

typedef struct _context {
  struct _context *next;
  PyNodeObject *node;

  PyNodeObject **children;
  int children_allocated;
  int children_size;
} Context;

typedef struct {
  ExpatParser parser;
  PyDocumentObject *owner_document;

  Context *context;
  Context *free_context;

  PyObject *new_namespaces;
} ParserState;

static PyObject *xmlns_string;
static PyObject *process_includes_string;
static PyObject *strip_elements_string;
static PyObject *empty_args_tuple;
static PyObject *gc_enable_function;
static PyObject *gc_disable_function;
static PyObject *gc_isenabled_function;

/** Utility Functions **************************************************/

static PyObject *MakeQName(PyObject *prefix, PyObject *localName)
{
  PyObject *nodeName;

  if (PyObject_IsTrue(prefix)) {
    Py_UNICODE *ustr;

    nodeName = PyUnicode_FromUnicode(NULL,
                                     PyUnicode_GET_SIZE(prefix) + \
                                     PyUnicode_GET_SIZE(localName) + 1);
    if (nodeName == NULL) return NULL;

    ustr = PyUnicode_AS_UNICODE(nodeName);
    Py_UNICODE_COPY(ustr,
                    PyUnicode_AS_UNICODE(prefix),
                    PyUnicode_GET_SIZE(prefix));

    ustr[PyUnicode_GET_SIZE(prefix)] = (Py_UNICODE)':';

    Py_UNICODE_COPY(ustr + PyUnicode_GET_SIZE(prefix) + 1,
                    PyUnicode_AS_UNICODE(localName),
                    PyUnicode_GET_SIZE(localName));
  } else {
    Py_INCREF(localName);
    nodeName = localName;
  }
  return nodeName;
}


/** Context ************************************************************/


static Context *Context_New(PyNodeObject *node)
{
  Context *self = PyMem_New(Context, 1);
  if (self == NULL) {
    PyErr_NoMemory();
    return NULL;
  }
  memset(self, 0, sizeof(Context));

  self->node = node;

  self->children = PyMem_New(PyNodeObject *, INITIAL_CHILDREN);
  if (self->children == NULL) {
    PyErr_NoMemory();
    PyMem_Free(self);
    return NULL;
  }
  self->children_allocated = INITIAL_CHILDREN;
  return self;
}


static void Context_Del(Context *self)
{
  int i;

  /* This will only be set when an error has occurred, so it must be freed. */
  if (self->node) {
    Py_DECREF(self->node);
  }

  for (i = self->children_size; --i >= 0;) {
    Py_DECREF(self->children[i]);
  }
  PyMem_Free(self->children);

  if (self->next) {
    Context_Del(self->next);
  }

  PyMem_Free(self);
}


/** ParserState ********************************************************/


static ParserState *ParserState_New(PyDocumentObject *doc,
                                    PyNodeObject *rootNode)
{
  ParserState *self = PyMem_New(ParserState, 1);
  if (self == NULL) {
    PyErr_NoMemory();
    return NULL;
  }

  /* context */
  if ((self->context = Context_New(rootNode)) == NULL) {
    PyMem_Free(self);
    return NULL;
  }
  self->free_context = NULL;

  self->new_namespaces = NULL;

  self->owner_document = doc;

  return self;
}


static void ParserState_Del(ParserState *self)
{
  if (self->context) {
    Context_Del(self->context);
  }

  if (self->free_context) {
    Context_Del(self->free_context);
  }

  if (self->new_namespaces) {
    Py_DECREF(self->new_namespaces);
  }

  Py_DECREF(self->owner_document);

  PyMem_Free(self);
}


static Context *ParserState_AddContext(ParserState *self, PyNodeObject *node)
{
  Context *context = self->free_context;
  if (context != NULL) {
    /* reuse an existing context */
    context->node = node;
    self->free_context = context->next;
  } else {
    /* create a new context */
    context = Context_New(node);
    if (context == NULL) return NULL;
  }

  /* make it the active context */
  context->next = self->context;
  self->context = context;
  return context;
}


static void ParserState_FreeContext(ParserState *self)
{
  Context *context = self->context;
  if (context != NULL) {
    /* switch the active context to the following one */
    self->context = context->next;

    /* move this one to the free list */
    context->next = self->free_context;
    self->free_context = context;

    /* reset its values */
    context->node = NULL;
    context->children_size = 0;
  }
}


static int ParserState_AddNode(ParserState *self, PyNodeObject *node)
{
  Context *context = self->context;
  PyNodeObject **children;
  int newsize;

  if (node == NULL || context == NULL) {
#ifdef DEBUG_PARSER
    abort();
#else
    PyErr_BadInternalCall();
    return 0;
#endif
  }

  /* increase size of child array, if needed */
  children = context->children;
  newsize = context->children_size + 1;
  if (newsize >= context->children_allocated) {
    int new_allocated = newsize << 1;
    if (PyMem_Resize(children, PyNodeObject *, new_allocated) == NULL) {
      PyErr_NoMemory();
      return 0;
    }
    context->children = children;
    context->children_allocated = new_allocated;
  }

  /* add the node to the children array */
  children[context->children_size] = node;
  context->children_size = newsize;
  return 1;
}


/** handlers ***********************************************************/


static void builder_EndDocument(void *userState)
{
  ParserState *state = (ParserState *)userState;
  Context *context = state->context;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_EndDocument()\n");
#endif

  /* Set the document's children */
  if (_Node_SetChildren(context->node, context->children,
                        context->children_size)) {
    Expat_ParserStop(state->parser);
    return;
  }

  /* Mark the current context as free */
  ParserState_FreeContext(state);
}


static void builder_StartNamespaceDecl(void *userState, PyObject *prefix,
                                       PyObject *uri)
{
  ParserState *state = (ParserState *)userState;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_StartNamespaceDecl(prefix=");
  PyObject_Print(prefix, stderr, 0);
  fprintf(stderr, ", uri=");
  PyObject_Print(uri, stderr, 0);
  fprintf(stderr, ")\n");
#endif

  if (state->new_namespaces == NULL) {
    /* first namespace for this element */
    state->new_namespaces = PyDict_New();
    if (state->new_namespaces == NULL) {
      Expat_ParserStop(state->parser);
      return;
    }
  }

  if (uri == Py_None) {
    /* Use an empty string as this will be added as an attribute value.
       Fixes SF#834917
    */
    uri = PyUnicode_FromUnicode(NULL, (Py_ssize_t)0);
    if (uri == NULL) {
      Expat_ParserStop(state->parser);
      return;
    }
  } else {
    Py_INCREF(uri);
  }

  if (PyDict_SetItem(state->new_namespaces, prefix, uri)) {
    Expat_ParserStop(state->parser);
    /* fall through */
  }

  Py_DECREF(uri);
  return;
}

static void builder_StartElement(void *userState, ExpatExpandedName *name,
                                 ExpatAttribute atts[], int atts_len)
{
  ParserState *state = (ParserState *)userState;
  PyElementObject *elem = NULL;
  Py_ssize_t i;
  PyObject *key, *value;
  PyObject *localName, *qualifiedName, *prefix;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_StartElement(name=");
  PyObject_Print(name->qualifiedName, stderr, 0);
  fprintf(stderr, ", atts={");
  for (i = 0; i < atts_len; i++) {
    if (i > 0) {
      fprintf(stderr, ", ");
    }
    PyObject_Print(atts[i].qualifiedName, stderr, 0);
    fprintf(stderr, ", ");
    PyObject_Print(atts[i].value, stderr, 0);
  }
  fprintf(stderr, "})\n");
#endif

  elem = Element_New(state->owner_document, name->namespaceURI,
                     name->qualifiedName, name->localName);
  if (elem == NULL) {
    Expat_ParserStop(state->parser);
    return;
  }

  /** namespaces *******************************************************/

  /* new_namespaces is a dictionary where key is the prefix and value
   * is the uri.
   */
  if (state->new_namespaces) {
    i = 0;
    while (PyDict_Next(state->new_namespaces, &i, &key, &value)) {
      PyAttrObject *nsattr;
      if (key != Py_None) {
        prefix = xmlns_string;
        localName = key;
      } else {
        prefix = key;
        localName = xmlns_string;
      }

      qualifiedName = MakeQName(prefix, localName);
      if (qualifiedName == NULL) {
        Py_DECREF(elem);
        Expat_ParserStop(state->parser);
        return;
      }

      nsattr = Element_SetAttributeNS(elem, g_xmlnsNamespace, qualifiedName,
                                      localName, value);
      Py_DECREF(qualifiedName);
      if (nsattr == NULL) {
        Py_DECREF(elem);
        Expat_ParserStop(state->parser);
        return;
      }
      Py_DECREF(nsattr);
    }
    /* make sure children don't set these namespaces */
    Py_DECREF(state->new_namespaces);
    state->new_namespaces = NULL;
  }

  /** attributes *******************************************************/

  for (i = 0; i < atts_len; i++) {
    PyAttrObject *attr;
    attr = Element_SetAttributeNS(elem, atts[i].namespaceURI,
                                  atts[i].qualifiedName, atts[i].localName,
                                  atts[i].value);
    if (attr == NULL) {
      Py_DECREF(elem);
      Expat_ParserStop(state->parser);
      return;
    }

    /* save the attribute type as well (for getElementById) */
    attr->type = atts[i].type;

    Py_DECREF(attr);
  }

  /* save states on the context */
  if (ParserState_AddContext(state, (PyNodeObject *) elem) == NULL) {
    Py_DECREF(elem);
    Expat_ParserStop(state->parser);
    /* fall-through */
  }
  return;
}


static void builder_EndElement(void *userState, ExpatExpandedName *name)
{
  ParserState *state = (ParserState *)userState;
  Context *context = state->context;
  PyNodeObject *node;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_EndElement(name=");
  PyObject_Print(name->qualifiedName, stderr, 0);
  fprintf(stderr, ")\n");
#endif

  /* Get the newly constructed element */
  node = context->node;

  /* Set the element's children */
  if (_Node_SetChildren(node, context->children, context->children_size)) {
    Expat_ParserStop(state->parser);
    return;
  }

  /* Mark the current context as free */
  ParserState_FreeContext(state);

  /* ParserState_AddNode steals the reference to the new node */
  if (ParserState_AddNode(state, node) == 0) {
    Expat_ParserStop(state->parser);
    /* just fall through */
  }
}


static void builder_CharacterData(void *userState, PyObject *data)
{
  ParserState *state = (ParserState *)userState;
  PyNodeObject *node;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_CharacterData(data=");
  PyObject_Print(data, stderr, 0);
  fprintf(stderr, ")\n");
#endif

  node = (PyNodeObject *) Text_New(state->owner_document, data);

  /* ParserState_AddNode steals the reference to the new node */
  if (ParserState_AddNode(state, node) == 0) {
    Expat_ParserStop(state->parser);
    /* just fall through */
  }
}


static void builder_ProcessingInstruction(void *userState, PyObject *target,
                                          PyObject *data)
{
  ParserState *state = (ParserState *)userState;
  PyNodeObject *node;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_ProcessingInstruction(target=");
  PyObject_Print(target, stderr, 0);
  fprintf(stderr, ", data=");
  PyObject_Print(data, stderr, 0);
  fprintf(stderr, ")\n");
#endif

  node = (PyNodeObject *) ProcessingInstruction_New(state->owner_document,
                                                    target, data);

  /* ParserState_AddNode steals the reference to the new node */
  if (ParserState_AddNode(state, node) == 0) {
    Expat_ParserStop(state->parser);
    /* just fall through */
  }
}


static void builder_Comment(void *userState, PyObject *data)
{
  ParserState *state = (ParserState *)userState;
  PyNodeObject *node;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_Comment(data=");
  PyObject_Print(data, stderr, 0);
  fprintf(stderr, ")\n");
#endif

  node = (PyNodeObject *) Comment_New(state->owner_document, data);

  /* ParserState_AddNode steals the reference to the new node */
  if (ParserState_AddNode(state, node) == 0) {
    Expat_ParserStop(state->parser);
    /* just fall through */
  }
}


static void builder_DoctypeDecl(void *userState, PyObject *name,
                                PyObject *systemId, PyObject *publicId)
{
  ParserState *state = (ParserState *)userState;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_DoctypeDecl(name=");
  PyObject_Print(name, stderr, 0);
  fprintf(stderr, ", systemId=");
  PyObject_Print(systemId, stderr, 0);
  fprintf(stderr, ", publicId=");
  PyObject_Print(publicId, stderr, 0);
  fprintf(stderr, ")\n");
#endif

  Py_DECREF(state->owner_document->systemId);
  Py_INCREF(systemId);
  state->owner_document->systemId = systemId;

  Py_DECREF(state->owner_document->publicId);
  Py_INCREF(publicId);
  state->owner_document->publicId = publicId;
}


static void builder_UnparsedEntityDecl(void *userState, PyObject *name,
                                       PyObject *publicId, PyObject *systemId,
                                       PyObject *notationName)
{
  ParserState *state = (ParserState *)userState;

#ifdef DEBUG_PARSER
  fprintf(stderr, "--- builder_UnparsedEntityDecl(name=");
  PyObject_Print(name, stderr, 0);
  fprintf(stderr, ", publicId=");
  PyObject_Print(publicId, stderr, 0);
  fprintf(stderr, ", systemId=");
  PyObject_Print(systemId, stderr, 0);
  fprintf(stderr, ", notationName=");
  PyObject_Print(notationName, stderr, 0);
  fprintf(stderr, ")\n");
#endif

  if (PyDict_SetItem(state->owner_document->unparsedEntities, name, systemId))
    Expat_ParserStop(state->parser);
}


/** External Routines *************************************************/


static ExpatParser createParser(ParserState *state) {
  ExpatParser parser;

  parser = Expat_ParserCreate(state);
  if (parser == NULL) {
    return NULL;
  }

  Expat_SetEndDocumentHandler(parser, builder_EndDocument);
  Expat_SetStartElementHandler(parser, builder_StartElement);
  Expat_SetEndElementHandler(parser, builder_EndElement);
  Expat_SetStartNamespaceDeclHandler(parser, builder_StartNamespaceDecl);
  Expat_SetCharacterDataHandler(parser, builder_CharacterData);
  Expat_SetProcessingInstructionHandler(parser, builder_ProcessingInstruction);
  Expat_SetCommentHandler(parser, builder_Comment);
  Expat_SetStartDoctypeDeclHandler(parser, builder_DoctypeDecl);
  Expat_SetUnparsedEntityDeclHandler(parser, builder_UnparsedEntityDecl);

  return parser;
}

static PyObject *builder_parse(PyObject *inputSource, ParseType parseType,
                               int asEntity, PyObject *namespaces)
{
  ParserState *state;
  PyDocumentObject *document;
  PyNodeObject *rootNode;
  PyObject *uri, *strip_elements;
  PyObject *temp;
  ExpatStatus status;
  int process_xincludes, gc_enabled;

  uri = PyObject_GetAttrString(inputSource, "uri");
  if (uri == NULL) {
    return NULL;
  } else if (!PyUnicode_Check(uri)) {
    PyObject *temp = PyObject_Unicode(uri);
    Py_DECREF(uri);
    if (temp == NULL) return NULL;
    uri = temp;
  }

  document = Document_New(uri);
  Py_DECREF(uri);
  if (document == NULL) {
    return NULL;
  }

  if (asEntity) {
    rootNode = (PyNodeObject *) DocumentFragment_New(document);
    if (rootNode == NULL) {
      Py_DECREF(document);
      return NULL;
    }
  } else {
    Py_INCREF(document);
    rootNode = (PyNodeObject *) document;
  }

  /* Takes ownership of both nodes */
  state = ParserState_New(document, rootNode);
  if (state == NULL) {
    Py_DECREF(document);
    Py_DECREF(rootNode);
    return NULL;
  }

  state->parser = createParser(state);
  if (state->parser == NULL) {
    ParserState_Del(state);
    return NULL;
  }

  /* XSLT whitespace stripping rules */
  strip_elements = PyObject_GetAttr(inputSource, strip_elements_string);
  if (strip_elements == NULL) {
    ParserState_Del(state);
    return NULL;
  }
  status = Expat_SetWhitespaceRules(state->parser, strip_elements);
  if (status == EXPAT_STATUS_ERROR) {
    Py_DECREF(strip_elements);
    ParserState_Del(state);
    return NULL;
  }
  Py_DECREF(strip_elements);

  /* Determine whether XInclude processing is enabled */
  temp = PyObject_GetAttr(inputSource, process_includes_string);
  if (temp == NULL) {
    ParserState_Del(state);
    return NULL;
  }
  process_xincludes = PyObject_IsTrue(temp);
  Py_DECREF(temp);
  Expat_SetXIncludeProcessing(state->parser, process_xincludes);

  /* Disable GC (if enabled) while building the DOM tree */
  temp = PyObject_Call(gc_isenabled_function, empty_args_tuple, NULL);
  if (temp == NULL) {
    Expat_ParserFree(state->parser);
    ParserState_Del(state);
    return NULL;
  }
  gc_enabled = PyObject_IsTrue(temp);
  Py_DECREF(temp);
  if (gc_enabled) {
    temp = PyObject_Call(gc_disable_function, empty_args_tuple, NULL);
    if (temp == NULL) {
      Expat_ParserFree(state->parser);
      ParserState_Del(state);
      return NULL;
    }
    Py_DECREF(temp);
  }

  Expat_SetValidation(state->parser, parseType == PARSE_TYPE_VALIDATE);
  Expat_SetParamEntityParsing(state->parser, parseType);

  if (asEntity)
    status = Expat_ParseEntity(state->parser, inputSource, namespaces);
  else
    status = Expat_ParseDocument(state->parser, inputSource);

  if (gc_enabled) {
    temp = PyObject_Call(gc_enable_function, empty_args_tuple, NULL);
    if (temp == NULL) {
      Expat_ParserFree(state->parser);
      ParserState_Del(state);
      return NULL;
    }
    Py_DECREF(temp);
  }

  Expat_ParserFree(state->parser);
  ParserState_Del(state);

  if (status == EXPAT_STATUS_OK)
    return (PyObject *) rootNode;
  else
    return NULL;
}

PyObject *ParseDocument(PyObject *source, ParseType parseType)
{
  return builder_parse(source, parseType, 0, NULL);
}

PyObject *ParseFragment(PyObject *source, PyObject *namespaces)
{
  return builder_parse(source, 0, 1, namespaces);
}

/** Module Setup & Teardown *******************************************/


int DomletteBuilder_Init(PyObject *module)
{
  PyObject *import;

  xmlns_string = PyUnicode_DecodeASCII("xmlns", (Py_ssize_t)5, NULL);
  if (xmlns_string == NULL) return -1;

  process_includes_string = PyString_FromString("processIncludes");
  if (process_includes_string == NULL) return -1;

  strip_elements_string = PyString_FromString("stripElements");
  if (strip_elements_string == NULL) return -1;

  empty_args_tuple = PyTuple_New((Py_ssize_t)0);
  if (empty_args_tuple == NULL) return -1;

  import = PyImport_ImportModule("gc");
  if (import == NULL) return -1;

#define GET_GC_FUNC(NAME)                                       \
  gc_##NAME##_function = PyObject_GetAttrString(import, #NAME); \
  if (gc_##NAME##_function == NULL) {                           \
    Py_DECREF(import);                                          \
    return -1;                                                  \
  }

  GET_GC_FUNC(enable);
  GET_GC_FUNC(disable);
  GET_GC_FUNC(isenabled);

  Py_DECREF(import);

  return 0;
}


void DomletteBuilder_Fini(void)
{
  Py_DECREF(xmlns_string);
  Py_DECREF(process_includes_string);
  Py_DECREF(strip_elements_string);
  Py_DECREF(empty_args_tuple);
  Py_DECREF(gc_enable_function);
  Py_DECREF(gc_disable_function);
  Py_DECREF(gc_isenabled_function);
}
