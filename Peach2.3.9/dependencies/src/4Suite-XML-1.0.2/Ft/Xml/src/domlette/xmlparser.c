#include "Python.h"
#include "structmember.h"
#include "compile.h"
#include "frameobject.h"

#if PY_VERSION_HEX < 0x02050000
#define PyExceptionInstance_Class(x) \
  ((PyInstance_Check((x)) \
    ? (PyObject*)((PyInstanceObject*)(x))->in_class \
    : (PyObject*)((x)->ob_type)))
#endif

#include "expat_module.h"
#include "xmlstring.h"
#include "domlette.h"

static PyObject *uri_resolver;
static PyObject *feature_external_ges;
static PyObject *feature_external_pes;
static PyObject *feature_namespaces;
static PyObject *feature_namespace_prefixes;
static PyObject *feature_string_interning;
static PyObject *feature_validation;
static PyObject *feature_process_xincludes;
static PyObject *feature_generator;
static PyObject *property_declaration_handler;
static PyObject *property_dom_node;
static PyObject *property_lexical_handler;
/*static PyObject *property_xml_string;*/
static PyObject *property_whitespace_rules;
static PyObject *property_yield_result;
static PyObject *sax_input_source;

enum HandlerTypes {
  /* ContentHandler */
  Handler_SetLocator,
  Handler_StartDocument,
  Handler_EndDocument,
  Handler_StartNamespace,
  Handler_EndNamespace,
  Handler_StartElement,
  Handler_EndElement,
  Handler_Characters,
  Handler_IgnorableWhitespace,
  Handler_ProcessingInstruction,
  Handler_SkippedEntity,

  /* DTDHandler */
  Handler_NotationDecl,
  Handler_UnparsedEntityDecl,

  /* EntityResolver */
  Handler_ResolveEntity,

  /* ErrorHandler */
  Handler_Warning,
  Handler_Error,
  Handler_FatalError,

  /* LexicalHandler */
  Handler_StartDTD,
  Handler_EndDTD,
  Handler_StartCDATA,
  Handler_EndCDATA,
  Handler_Comment,

  /* DeclHandler */
  Handler_ElementDecl,
  Handler_AttributeDecl,
  Handler_InternalEntityDecl,
  Handler_ExternalEntityDecl,

  TotalHandlers
};

typedef struct {
  PyObject_HEAD
  ExpatParser parser;

  PyObject *content_handler;
  PyObject *dtd_handler;
  PyObject *error_handler;
  PyObject *entity_resolver;

  /* SAX features */
  int generator;

  /* SAX properties */
  PyObject *whitespace_rules;
  PyObject *yield_result;
  PyNodeObject *dom_node;
  PyObject *decl_handler;
  PyObject *lexical_handler;

  /* Python callbacks */
  PyObject *handlers[TotalHandlers];
} XMLParserObject;

typedef struct {
  PyObject_HEAD
  PyObject *values;
  PyObject *qnames;
  int length;
} AttributesObject;

typedef struct {
  PyObject_HEAD
  XMLParserObject *parser;
} SaxGenObject;

/* Cached PyCodeObjects for frames */
static PyCodeObject *tb_codes[TotalHandlers];

/* Empty attributes reuse scheme to save calls to malloc and free */
#define MAX_FREE_ATTRS 80
static AttributesObject *free_attrs[MAX_FREE_ATTRS];
static int num_free_attrs = 0;

/** InputSource Helpers ***********************************************/

/* This is a minimal implementation of an InputSource for use by the
 * underlying parser.  It performs default resolution of the system ID,
 * by resolving against the base URI and opening a connection to that URI.
 *
 * This is required to map xml.sax.InputSources and bare system IDs to an
 * interface (Ft.Xml.InputSource) that is understood by the underlying
 * parser.
 */

typedef struct {
  PyObject_HEAD
  PyObject *uri;
  PyObject *stream;
  PyObject *encoding;
} InputSourceObject;

static PyObject *InputSource_New(PyObject *uri, PyObject *stream,
                                 PyObject *encoding);

static void InputSource_Del(InputSourceObject *self)
{
  Py_DECREF(self->uri);
  Py_DECREF(self->stream);
  Py_DECREF(self->encoding);
  PyObject_Del(self);
}

static PyObject *InputSource_ResolveUri(InputSourceObject *self, PyObject *uri)
{
  PyObject *stream;

  uri = PyObject_CallMethod(uri_resolver, "normalize", "OO", uri, self->uri);
  if (uri == NULL)
    return NULL;

  stream = PyObject_CallMethod(uri_resolver, "resolve", "O", uri);
  if (stream == NULL) {
    Py_DECREF(uri);
    return NULL;
  }

  Py_INCREF(Py_None);
  return InputSource_New(uri, stream, Py_None);
}

static PyObject *InputSource_Resolve(InputSourceObject *self, PyObject *args)
{
  PyObject *href, *base=Py_None, *hint=Py_None;

  if (!PyArg_ParseTuple(args, "O|OO:resolve", &href, &base, &hint))
    return NULL;

  return InputSource_ResolveUri(self, href);
}

static PyObject *InputSource_ResolveEntity(InputSourceObject *self,
                                           PyObject *args)
{
  PyObject *publicId, *systemId;

  if (!PyArg_ParseTuple(args, "OO:resolveEntity", &publicId, &systemId))
    return NULL;

  return InputSource_ResolveUri(self, systemId);
}

static PyMethodDef input_source_methods[] = {
  { "resolve", (PyCFunction) InputSource_Resolve, METH_VARARGS },
  { "resolveEntity", (PyCFunction) InputSource_ResolveEntity, METH_VARARGS },
  { NULL }
};

static PyMemberDef input_source_members[] = {
  { "uri",      T_OBJECT, offsetof(InputSourceObject, uri),      RO },
  { "stream",   T_OBJECT, offsetof(InputSourceObject, stream),   RO },
  { "encoding", T_OBJECT, offsetof(InputSourceObject, encoding), RO },
  { NULL }
};

static PyTypeObject InputSource_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ "InputSource",
  /* tp_basicsize      */ sizeof(InputSourceObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) InputSource_Del,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) 0,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ Py_TPFLAGS_DEFAULT,
  /* tp_doc            */ (char *) 0,
  /* tp_traverse       */ (traverseproc) 0,
  /* tp_clear          */ 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) input_source_methods,
  /* tp_members        */ (PyMemberDef *) input_source_members,
  /* tp_getset         */ (PyGetSetDef *) 0,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) 0,
  /* tp_free           */ 0,
};

static PyObject *InputSource_New(PyObject *uri, PyObject *stream,
                                 PyObject *encoding)
{
  InputSourceObject *self;

  self = PyObject_New(InputSourceObject, &InputSource_Type);
  if (self) {
    self->uri = uri;
    self->stream = stream;
    self->encoding = encoding;
  } else {
    Py_DECREF(uri);
    Py_DECREF(stream);
    Py_DECREF(encoding);
  }
  return (PyObject *) self;
}


/** SAXExceptions *****************************************************/

static PyObject *SAXParseExceptionObject;
static PyObject *SAXNotRecognizedExceptionObject;
static PyObject *SAXNotSupportedExceptionObject;

static PyObject *SAXParseException(PyObject *exception, PyObject *locator)
{
  PyObject *message;

  /* Get the string representation of the exception value */
  message = PyObject_GetAttrString(exception, "message");
  if (message == NULL) {
    return NULL;
  }

  /* Create a SAXParseException for this error */
  return PyObject_CallFunction(SAXParseExceptionObject, "NOO",
                               message, exception, locator);
}

static PyObject *SAXNotRecognizedException(char *msg)
{
  PyObject *obj;

  obj = PyObject_CallFunction(SAXNotRecognizedExceptionObject, "s", msg);
  if (obj) {
    PyErr_SetObject(SAXNotRecognizedExceptionObject, obj);
    Py_DECREF(obj);
  }
  return NULL;
}

static PyObject *SAXNotSupportedException(char *msg)
{
  PyObject *obj;

  obj = PyObject_CallFunction(SAXNotSupportedExceptionObject, "s", msg);
  if (obj) {
    PyErr_SetObject(SAXNotSupportedExceptionObject, obj);
    Py_DECREF(obj);
  }
  return NULL;
}

/** Constructors ******************************************************/

static AttributesObject *Attributes_New(void);

/** Expat Callback Handlers *******************************************/


/* The following few functions (getcode, trace_frame, trace_frame_exc and
 * call_with frame) are used for having proper tracebacks and
 * profiling information.  The are originally from the pyexpat module.
 */
#define getcode(slot) _getcode(Handler_##slot, #slot, __LINE__)
static PyCodeObject *_getcode(enum HandlerTypes slot, char *slot_name,
                             int lineno)
{
  PyObject *code, *name, *nulltuple, *filename;

  if (tb_codes[slot] == NULL) {
    code = PyString_FromString("");
    if (code == NULL) {
      return NULL;
    }

    name = PyString_FromString(slot_name);
    if (name == NULL) {
      Py_DECREF(code);
      return NULL;
    }

    nulltuple = PyTuple_New((Py_ssize_t)0);
    if (nulltuple == NULL) {
      Py_DECREF(code);
      Py_DECREF(name);
      return NULL;
    }

    filename = PyString_FromString(__FILE__);
    if (filename == NULL) {
      Py_DECREF(code);
      Py_DECREF(name);
      Py_DECREF(nulltuple);
      return NULL;
    }

    tb_codes[slot] = PyCode_New(0,		/* argcount */
                                0,		/* nlocals */
                                0,		/* stacksize */
                                0,		/* flags */
                                code,		/* code */
                                nulltuple,	/* consts */
                                nulltuple,	/* names */
                                nulltuple,	/* varnames */
#if PYTHON_API_VERSION >= 1010
                                nulltuple,	/* freevars */
                                nulltuple,	/* cellvars */
#endif
                                filename,	/* filename */
                                name,		/* name */
                                lineno,		/* firstlineno */
                                code		/* lnotab */
                                );
    Py_DECREF(code);
    Py_DECREF(name);
    Py_DECREF(nulltuple);
    Py_DECREF(filename);
  }
  return tb_codes[slot];
}

static int
trace_frame(PyThreadState *tstate, PyFrameObject *f, int code, PyObject *val)
{
    int result = 0;
    if (!tstate->use_tracing || tstate->tracing)
	return 0;
    if (tstate->c_profilefunc != NULL) {
	tstate->tracing++;
	result = tstate->c_profilefunc(tstate->c_profileobj,
				       f, code , val);
	tstate->use_tracing = ((tstate->c_tracefunc != NULL)
			       || (tstate->c_profilefunc != NULL));
	tstate->tracing--;
	if (result)
	    return result;
    }
    if (tstate->c_tracefunc != NULL) {
	tstate->tracing++;
	result = tstate->c_tracefunc(tstate->c_traceobj,
				     f, code , val);
	tstate->use_tracing = ((tstate->c_tracefunc != NULL)
			       || (tstate->c_profilefunc != NULL));
	tstate->tracing--;
    }
    return result;
}

static int
trace_frame_exc(PyThreadState *tstate, PyFrameObject *f)
{
    PyObject *type, *value, *traceback, *arg;
    int err;

    if (tstate->c_tracefunc == NULL)
	return 0;

    PyErr_Fetch(&type, &value, &traceback);
    if (value == NULL) {
	value = Py_None;
	Py_INCREF(value);
    }
#if PY_VERSION_HEX < 0x02040000
    arg = Py_BuildValue("(OOO)", type, value, traceback);
#else
    arg = PyTuple_Pack((Py_ssize_t)3, type, value, traceback);
#endif
    if (arg == NULL) {
	PyErr_Restore(type, value, traceback);
	return 0;
    }
    err = trace_frame(tstate, f, PyTrace_EXCEPTION, arg);
    Py_DECREF(arg);
    if (err == 0)
	PyErr_Restore(type, value, traceback);
    else {
	Py_XDECREF(type);
	Py_XDECREF(value);
	Py_XDECREF(traceback);
    }
    return err;
}

static PyObject *call_with_frame(PyCodeObject *code, PyObject *func,
                                 PyObject *args)
{
  PyThreadState *tstate = PyThreadState_GET();
  PyFrameObject *f;
  PyObject *res;

  if (code == NULL || args == NULL) {
    return NULL;
  }

  f = PyFrame_New(tstate, code, PyEval_GetGlobals(), NULL);
  if (f == NULL) {
    return NULL;
  }
  tstate->frame = f;
  if (trace_frame(tstate, f, PyTrace_CALL, Py_None) < 0) {
    return NULL;
  }
  res = PyObject_Call(func, args, NULL);
  if (res == NULL) {
    if (tstate->curexc_traceback == NULL) {
      PyTraceBack_Here(f);
    }
    if (trace_frame_exc(tstate, f) < 0) {
      return NULL;
    }
  }
  else {
    if (trace_frame(tstate, f, PyTrace_RETURN, res) < 0) {
      Py_XDECREF(res);
      res = NULL;
    }
  }
  tstate->frame = f->f_back;
  Py_DECREF(f);
  return res;
}

/* Receive notification of the beginning of a document. */
static void parser_StartDocument(void *userData)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler, *args, *result;

  if ((handler = self->handlers[Handler_SetLocator]) != NULL) {
    /* handler.setDocumentLocator(locator) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, (PyObject *)self);
    Py_INCREF(self); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(SetLocator), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }

  if ((handler = self->handlers[Handler_StartDocument]) != NULL) {
    /* handler.startDocument() */
    if ((args = PyTuple_New((Py_ssize_t)0)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }

    result = call_with_frame(getcode(StartDocument), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Receive notification of the end of a document. */
static void parser_EndDocument(void *userData)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_EndDocument];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.endDocument() */
    if ((args = PyTuple_New((Py_ssize_t)0)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }

    result = call_with_frame(getcode(EndDocument), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Begin the scope of a prefix-URI Namespace mapping. */
static void parser_StartNamespaceDecl(void *userData, PyObject *prefix,
                                      PyObject *uri)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_StartNamespace];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.startNamespace(prefix, uri) */
    if ((args = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, prefix);
    Py_INCREF(prefix); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, uri);
    Py_INCREF(uri); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(StartNamespace), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
  return;
}

/* End the scope of a prefix-URI mapping. */
static void parser_EndNamespaceDecl(void *userData, PyObject *prefix)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_EndNamespace];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.endNamespace(prefix) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, prefix);
    Py_INCREF(prefix); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(EndNamespace), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Create the Attributes object to be used in the startElement callback. */
static PyObject *createAttributes(XMLParserObject *parser,
                                  ExpatAttribute atts[], int atts_len)
{
  AttributesObject *self;
  int i;

  self = Attributes_New();
  if (self == NULL)
    return NULL;

  for (i = 0; i < atts_len; i++) {
    PyObject *expandedName;
    self->length++;

    /* create the expanded-name 'key' of (namespaceURI, localName) */
    if ((expandedName = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Py_DECREF(self);
      return NULL;
    }
    Py_INCREF(atts[i].namespaceURI);
    PyTuple_SET_ITEM(expandedName, 0, atts[i].namespaceURI);
    Py_INCREF(atts[i].localName);
    PyTuple_SET_ITEM(expandedName, 1, atts[i].localName);

    if (PyDict_SetItem(self->values, expandedName, atts[i].value)) {
      Py_DECREF(expandedName);
      Py_DECREF(self);
      return NULL;
    }

    if (PyDict_SetItem(self->qnames, expandedName, atts[i].qualifiedName)) {
      Py_DECREF(expandedName);
      Py_DECREF(self);
      return NULL;
    }

    Py_DECREF(expandedName);
  }

  return (PyObject *) self;
}

static void parser_StartElement(void *userData, ExpatExpandedName *name,
                                ExpatAttribute atts[], int atts_len)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_StartElement];
  PyObject *args, *result;
  PyObject *expandedName, *attributes;

  if (handler != NULL) {
    if ((expandedName = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_INCREF(name->namespaceURI);
    PyTuple_SET_ITEM(expandedName, 0, name->namespaceURI);
    Py_INCREF(name->localName);
    PyTuple_SET_ITEM(expandedName, 1, name->localName);

    attributes = createAttributes(self, atts, atts_len);
    if (attributes == NULL) {
      Py_DECREF(expandedName);
      Expat_ParserStop(self->parser);
      return;
    }

    /* handler.startElement((namespaceURI, localName), tagName, attributes) */
    if ((args = PyTuple_New((Py_ssize_t)3)) == NULL) {
      Py_DECREF(expandedName);
      Py_DECREF(attributes);
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, expandedName);
    Py_INCREF(name->qualifiedName);
    PyTuple_SET_ITEM(args, 1, name->qualifiedName);
    PyTuple_SET_ITEM(args, 2, attributes);

    result = call_with_frame(getcode(StartElement), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_EndElement(void *userData, ExpatExpandedName *name)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_EndElement];
  PyObject *args, *result;
  PyObject *expandedName;

  if (handler != NULL) {
    if ((expandedName = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_INCREF(name->namespaceURI);
    PyTuple_SET_ITEM(expandedName, 0, name->namespaceURI);
    Py_INCREF(name->localName);
    PyTuple_SET_ITEM(expandedName, 1, name->localName);

    /* handler.endElement((namespaceURI, localName), tagName) */
    if ((args = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Py_DECREF(expandedName);
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, expandedName);
    Py_INCREF(name->qualifiedName);
    PyTuple_SET_ITEM(args, 1, name->qualifiedName);

    result = call_with_frame(getcode(EndElement), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_CharacterData(void *userData, PyObject *data)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_Characters];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.characters(content) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, data);
    Py_INCREF(data); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(Characters), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Receive notification of ignorable whitespace in element content.
 * NOT IMPLEMENTED IN expat_module.c *
 */
static void parser_IgnorableWhitespace(void *userData, PyObject *data)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_IgnorableWhitespace];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.ignoreableWhitespace(content) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, data);
    Py_INCREF(data); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(IgnorableWhitespace), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Receive notification of a processing instruction. */
static void parser_ProcessingInstruction(void *userData, PyObject *target,
                                         PyObject *data)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_ProcessingInstruction];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.processingInstruction(target, data) */
    if ((args = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, target);
    Py_INCREF(target); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, data);
    Py_INCREF(data); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(ProcessingInstruction), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_SkippedEntity(void *userData, PyObject *name)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_SkippedEntity];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.skippedEntity(name) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, name);
    Py_INCREF(name); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(SkippedEntity), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Report the start of DTD declarations, if any. */
static void parser_StartDoctypeDecl(void *userData, PyObject *name,
                                    PyObject *systemId, PyObject *publicId)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_StartDTD];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.startDTD(name, publicId, systemId) */
    if ((args = PyTuple_New((Py_ssize_t)3)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, name);
    Py_INCREF(name); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, publicId);
    Py_INCREF(publicId); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 2, systemId);
    Py_INCREF(systemId); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(StartDTD), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Report the end of DTD declarations. */
static void parser_EndDoctypeDecl(void *userData)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_EndDTD];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.endDTD() */
    if ((args = PyTuple_New((Py_ssize_t)0)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }

    result = call_with_frame(getcode(EndDTD), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Report the start of a CDATA section. */
static void parser_StartCdataSection(void *userData)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_StartCDATA];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.startCDATA() */
    if ((args = PyTuple_New((Py_ssize_t)0)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }

    result = call_with_frame(getcode(StartCDATA), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/* Report the end of a CDATA section. */
static void parser_EndCdataSection(void *userData)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_EndCDATA];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.endCDATA() */
    if ((args = PyTuple_New((Py_ssize_t)0)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }

    result = call_with_frame(getcode(EndCDATA), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_Comment(void *userData, PyObject *data)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_Comment];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.comment(content) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, data);
    Py_INCREF(data); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(Comment), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_NotationDecl(void *userData, PyObject *name,
                                PyObject *publicId, PyObject *systemId)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_NotationDecl];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.comment(content) */
    if ((args = PyTuple_New((Py_ssize_t)3)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, name);
    Py_INCREF(name); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, publicId);
    Py_INCREF(publicId); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 2, systemId);
    Py_INCREF(systemId); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(NotationDecl), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_UnparsedEntityDecl(void *userData, PyObject *name,
                                      PyObject *publicId, PyObject *systemId,
                                      PyObject *notationName)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_UnparsedEntityDecl];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.comment(content) */
    if ((args = PyTuple_New((Py_ssize_t)4)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, name);
    Py_INCREF(name); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, publicId);
    Py_INCREF(publicId); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 2, systemId);
    Py_INCREF(systemId); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 3, notationName);
    Py_INCREF(notationName); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(UnparsedEntityDecl), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static ExpatStatus parser_Warning(void *userData, PyObject *exception)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_Warning];
  PyObject *args, *result;

  exception = SAXParseException(exception, (PyObject *) self);
  if (exception == NULL) {
    Expat_ParserStop(self->parser);
    return EXPAT_STATUS_ERROR;
  }
  if (handler != NULL) {
    /* handler.warning(exception) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Py_DECREF(exception);
      Expat_ParserStop(self->parser);
      return EXPAT_STATUS_ERROR;
    }
    PyTuple_SET_ITEM(args, 0, exception);

    result = call_with_frame(getcode(Warning), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return EXPAT_STATUS_ERROR;
    }
    Py_DECREF(result);
  } else {
    PyObject *stream = PySys_GetObject("stdout");
    if (stream != NULL) {
      if (PyFile_WriteObject(exception, stream, Py_PRINT_RAW) < 0) {
        Py_DECREF(exception);
        Expat_ParserStop(self->parser);
        return EXPAT_STATUS_ERROR;
      }
      if (PyFile_WriteString("\n", stream) < 0) {
        Py_DECREF(exception);
        Expat_ParserStop(self->parser);
        return EXPAT_STATUS_ERROR;
      }
    }
    Py_DECREF(exception);
  }
  return EXPAT_STATUS_OK;
}

static ExpatStatus parser_Error(void *userData, PyObject *exception)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_Error];
  PyObject *args, *result;

  exception = SAXParseException(exception, (PyObject *) self);
  if (exception == NULL) {
    Expat_ParserStop(self->parser);
    return EXPAT_STATUS_ERROR;
  }
  if (handler != NULL) {
    /* handler.warning(exception) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Py_DECREF(exception);
      Expat_ParserStop(self->parser);
      return EXPAT_STATUS_ERROR;
    }
    PyTuple_SET_ITEM(args, 0, exception);

    result = call_with_frame(getcode(Error), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return EXPAT_STATUS_ERROR;
    }
    Py_DECREF(result);
  } else {
    PyErr_SetObject(PyExceptionInstance_Class(exception), exception);
    Py_DECREF(exception);
    Expat_ParserStop(self->parser);
    return EXPAT_STATUS_ERROR;
  }
  return EXPAT_STATUS_OK;
}

static ExpatStatus parser_FatalError(void *userData, PyObject *exception)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_FatalError];
  PyObject *args, *result;

  exception = SAXParseException(exception, (PyObject *) self);
  if (exception == NULL) {
    Expat_ParserStop(self->parser);
    return EXPAT_STATUS_ERROR;
  }
  if (handler != NULL) {
    /* handler.warning(exception) */
    if ((args = PyTuple_New((Py_ssize_t)1)) == NULL) {
      Py_DECREF(exception);
      Expat_ParserStop(self->parser);
      return EXPAT_STATUS_ERROR;
    }
    PyTuple_SET_ITEM(args, 0, exception);

    result = call_with_frame(getcode(FatalError), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return EXPAT_STATUS_ERROR;
    }
    Py_DECREF(result);
  } else {
    PyErr_SetObject(PyExceptionInstance_Class(exception), exception);
    Py_DECREF(exception);
    Expat_ParserStop(self->parser);
    return EXPAT_STATUS_ERROR;
  }
  return EXPAT_STATUS_OK;
}

static void parser_ElementDecl(void *userData, PyObject *name, PyObject *model)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_ElementDecl];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.comment(content) */
    if ((args = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, name);
    Py_INCREF(name); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, model);
    Py_INCREF(model); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(ElementDecl), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_AttributeDecl(void *userData, PyObject *eName,
                                 PyObject *aName, PyObject *type,
                                 PyObject *decl, PyObject *value)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_AttributeDecl];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.comment(content) */
    if ((args = PyTuple_New((Py_ssize_t)5)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, eName);
    Py_INCREF(eName); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, aName);
    Py_INCREF(aName); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 2, type);
    Py_INCREF(type); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 3, decl);
    Py_INCREF(decl); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 4, value);
    Py_INCREF(value); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(AttributeDecl), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_InternalEntityDecl(void *userData, PyObject *name,
                                      PyObject *value)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_InternalEntityDecl];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.comment(content) */
    if ((args = PyTuple_New((Py_ssize_t)2)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, name);
    Py_INCREF(name); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, value);
    Py_INCREF(value); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(InternalEntityDecl), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

static void parser_ExternalEntityDecl(void *userData, PyObject *name,
                                      PyObject *publicId, PyObject *systemId)
{
  XMLParserObject *self = (XMLParserObject *) userData;
  PyObject *handler = self->handlers[Handler_ExternalEntityDecl];
  PyObject *args, *result;

  if (handler != NULL) {
    /* handler.comment(content) */
    if ((args = PyTuple_New((Py_ssize_t)3)) == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    PyTuple_SET_ITEM(args, 0, name);
    Py_INCREF(name); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 1, publicId);
    Py_INCREF(publicId); /* SET_ITEM steals reference */
    PyTuple_SET_ITEM(args, 2, systemId);
    Py_INCREF(systemId); /* SET_ITEM steals reference */

    result = call_with_frame(getcode(ExternalEntityDecl), handler, args);
    Py_DECREF(args);
    if (result == NULL) {
      Expat_ParserStop(self->parser);
      return;
    }
    Py_DECREF(result);
  }
}

/** DOMWalker *********************************************************/

static PyObject *get_prefix(PyObject *nodeName)
{
  Py_UNICODE *p;
  Py_ssize_t len, i;

  p = PyUnicode_AS_UNICODE(nodeName);
  len = PyUnicode_GET_SIZE(nodeName);
  for (i = 0; i < len; i++) {
    if (p[i] == ':') {
      return PyUnicode_FromUnicode(p, i);
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

static int domwalker_visit(XMLParserObject *parser,
                           PyNodeObject *node,
                           PyObject *current_namespaces,
                           int preserve_whitespace)
{
  if (PyElement_Check(node)) {
    AttributesObject *attrs;
    PyObject *new_namespaces, *prefixes, *namespaceURI, *prefix;
    PyObject *key, *value;
    PyObject *handler, *args, *result;
    Py_ssize_t i;

    attrs = Attributes_New();
    if (attrs == NULL) {
      return 0;
    }

    new_namespaces = PyDict_New();
    if (new_namespaces == NULL) {
      Py_DECREF(attrs);
      return 0;
    }

    /** Attributes ************************************************/

    /* Create expat-style attribute names and trim out namespaces */
    i = 0;
    while (PyDict_Next(PyElement_ATTRIBUTES(node), &i, &key, &value)) {
      PyObject *nodeName, *localName, *nodeValue, *expandedName;
      namespaceURI = PyAttr_NAMESPACE_URI(value);
      nodeName = PyAttr_NODE_NAME(value);
      localName = PyAttr_LOCAL_NAME(value);
      nodeValue = PyAttr_NODE_VALUE(value);

      /* get the prefix/namespaceURI pair to add */
      switch (PyObject_RichCompareBool(namespaceURI, g_xmlnsNamespace,
                                       Py_EQ)) {
      case 0: /* normal attribute */
        /* DOM doesn't need separate namespace declarations */
        if (namespaceURI != Py_None) {
          PyObject *prefix = get_prefix(nodeName);
          if (prefix == NULL) {
            Py_DECREF(new_namespaces);
            Py_DECREF(attrs);
            return 0;
          }
          if (PyDict_SetItem(new_namespaces, prefix, namespaceURI)) {
            Py_DECREF(prefix);
            Py_DECREF(new_namespaces);
            Py_DECREF(attrs);
            return 0;
          }
          Py_DECREF(prefix);
        }

        expandedName = PyTuple_New((Py_ssize_t)2);
        if (expandedName == NULL) {
          Py_DECREF(new_namespaces);
          Py_DECREF(attrs);
          return 0;
        }
        Py_INCREF(namespaceURI);
        PyTuple_SET_ITEM(expandedName, 0, namespaceURI);
        Py_INCREF(localName);
        PyTuple_SET_ITEM(expandedName, 1, localName);

        if (PyDict_SetItem(attrs->values, expandedName, nodeValue)) {
          Py_DECREF(expandedName);
          Py_DECREF(new_namespaces);
          Py_DECREF(attrs);
          return 0;
        }
        if (PyDict_SetItem(attrs->qnames, expandedName, nodeName)) {
          Py_DECREF(expandedName);
          Py_DECREF(new_namespaces);
          Py_DECREF(attrs);
          return 0;
        }
        Py_DECREF(expandedName);
        attrs->length++;

        break;
      case 1: /* namespace attribute */
        if (PyUnicode_AS_UNICODE(nodeName)[5] == ':') {
          /* xmlns:foo = 'namespaceURI' */
          prefix = localName;
        } else {
          /* xmlns = 'namespaceURI' */
          prefix = Py_None;
        }
        if (PyDict_SetItem(new_namespaces, prefix, nodeValue)) {
          Py_DECREF(new_namespaces);
          Py_DECREF(attrs);
          return 0;
        }
        break;
      default:
        return -1;
      }
    }

    /* DOM doesn't need separate namespace declarations */
    namespaceURI = PyElement_NAMESPACE_URI(node);
    prefix = get_prefix(PyElement_NODE_NAME(node));
    if (prefix == NULL) {
      Py_DECREF(new_namespaces);
      Py_DECREF(attrs);
      return 0;
    }
    if (namespaceURI != Py_None) {
      if (PyDict_SetItem(new_namespaces, prefix, namespaceURI)) {
        Py_DECREF(prefix);
        Py_DECREF(new_namespaces);
        Py_DECREF(attrs);
        return 0;
      }
    }
    Py_DECREF(prefix);

    /* notify start of namespace declaration(s) */
    current_namespaces = PyDict_Copy(current_namespaces);
    if (current_namespaces == NULL) {
      Py_DECREF(new_namespaces);
      Py_DECREF(attrs);
      return 0;
    }
    prefixes = PyList_New((Py_ssize_t)0);
    if (prefixes == NULL) {
      Py_DECREF(current_namespaces);
      Py_DECREF(new_namespaces);
      Py_DECREF(attrs);
      return 0;
    }

    i = 0;
    while (PyDict_Next(new_namespaces, &i, &key, &value)) {
      namespaceURI = PyDict_GetItem(current_namespaces, key);
      if (namespaceURI == NULL ||
          PyObject_RichCompareBool(namespaceURI, value, Py_NE)) {
        if (PyDict_SetItem(current_namespaces, key, value) ||
            PyList_Append(prefixes, key)) {
          Py_DECREF(prefixes);
          Py_DECREF(current_namespaces);
          Py_DECREF(new_namespaces);
          Py_DECREF(attrs);
          return 0;
        }

        parser_StartNamespaceDecl(parser, key, value);
        if (PyErr_Occurred()) {
          Py_DECREF(prefixes);
          Py_DECREF(current_namespaces);
          Py_DECREF(new_namespaces);
          Py_DECREF(attrs);
          return 0;
        }
      }
    }
    Py_DECREF(new_namespaces);

    /* report element start */
    handler = parser->handlers[Handler_StartElement];
    if (handler != NULL) {
      args = Py_BuildValue("(OO)OO",
                           PyElement_NAMESPACE_URI(node),
                           PyElement_LOCAL_NAME(node),
                           PyElement_NODE_NAME(node),
                           attrs);
      if (args == NULL) {
        Py_DECREF(current_namespaces);
        Py_DECREF(prefixes);
        Py_DECREF(attrs);
        return 0;
      }
      result = call_with_frame(getcode(StartElement), handler, args);
      Py_DECREF(args);
      if (result == NULL) {
        Py_DECREF(current_namespaces);
        Py_DECREF(prefixes);
        Py_DECREF(attrs);
        return 0;
      }
      Py_DECREF(result);
    }
    Py_DECREF(attrs);

    /* update preserving whitespace state for child nodes */
    preserve_whitespace =
      Expat_IsWhitespacePreserving(parser->parser,
                                   PyElement_NAMESPACE_URI(node),
                                   PyElement_LOCAL_NAME(node));

    /* process the children */
    for (i = 0; i < ContainerNode_GET_COUNT(node); i++) {
      PyNodeObject *child = ContainerNode_GET_CHILD(node, i);
      if (domwalker_visit(parser, child, current_namespaces,
                          preserve_whitespace) == 0) {
        Py_DECREF(current_namespaces);
        Py_DECREF(prefixes);
        return 0;
      }
    }

    /* report element end */
    handler = parser->handlers[Handler_EndElement];
    if (handler != NULL) {
      args = Py_BuildValue("(OO)O",
                           PyElement_NAMESPACE_URI(node),
                           PyElement_LOCAL_NAME(node),
                           PyElement_NODE_NAME(node));
      if (args == NULL) {
        Py_DECREF(current_namespaces);
        Py_DECREF(prefixes);
        return 0;
      }
      result = call_with_frame(getcode(StartElement), handler, args);
      Py_DECREF(args);
      if (result == NULL) {
        Py_DECREF(current_namespaces);
        Py_DECREF(prefixes);
        return 0;
      }
      Py_DECREF(result);
    }
    Py_DECREF(current_namespaces);

    /* report end of namespace declaration(s) */
    for (i = 0; i < PyList_GET_SIZE(prefixes); i++) {
      parser_EndNamespaceDecl(parser, PyList_GET_ITEM(prefixes, i));
      if (PyErr_Occurred()) {
        Py_DECREF(prefixes);
        return 0;
      }
    }
    Py_DECREF(prefixes);
  }
  else if (PyText_Check(node)) {
    PyObject *data = Text_GET_DATA(node);
    if (preserve_whitespace || !XmlString_IsSpace(data)) {
      parser_CharacterData(parser, data);
      if (PyErr_Occurred()) return 0;
    }
  }

  return 1;
}

static ExpatStatus ParseDOM(XMLParserObject *parser)
{
  PyObject *namespaces;
  int i;

  parser_StartDocument(parser);
  if (PyErr_Occurred()) return EXPAT_STATUS_ERROR;

  namespaces = PyDict_New();
  if (namespaces == NULL) return EXPAT_STATUS_ERROR;

  for (i = 0; i < ContainerNode_GET_COUNT(parser->dom_node); i++) {
    PyNodeObject *node = ContainerNode_GET_CHILD(parser->dom_node, i);
    if (domwalker_visit(parser, node, namespaces, 1) == 0) {
      Py_DECREF(namespaces);
      return EXPAT_STATUS_ERROR;
    }
  }
  Py_DECREF(namespaces);

  parser_EndDocument(parser);
  if (PyErr_Occurred()) return EXPAT_STATUS_ERROR;

  return EXPAT_STATUS_OK;
}

/**********************************************************************/
/** Python Objects ****************************************************/
/**********************************************************************/

#define METHOD_DOC(PREFIX, NAME) \
static char PREFIX##_##NAME##_doc[]

#define METHOD_DEF(PREFIX, NAME, OBJECT) \
static PyObject * PREFIX##_##NAME(OBJECT *self, PyObject *args)

#define Py_METHOD(PREFIX, NAME) \
  { #NAME, (PyCFunction) PREFIX##_##NAME, METH_VARARGS, PREFIX##_##NAME##_doc }

#define Py_MEMBER(NAME, TYPE, OBJECT) \
  { #NAME, TYPE, offsetof(OBJECT, NAME), 0 }

/********** XMLPARSERITER **********/

static void saxgen_dealloc(SaxGenObject *self)
{
  PyObject_GC_UnTrack(self);
  Py_XDECREF(self->parser);
  PyObject_GC_Del(self);
}

static int saxgen_traverse(SaxGenObject *self, visitproc visit, void *arg)
{
  return visit((PyObject *)self->parser, arg);
}

static PyObject *saxgen_iter(SaxGenObject *self)
{
  Py_INCREF(self);
  return (PyObject *)self;
}

static PyObject *saxgen_iternext(SaxGenObject *self)
{
  PyObject *result;

  if (Expat_GetParsingStatus(self->parser->parser)) {
    /* Still parsing (either suspended or actively) */
    if (self->parser->yield_result == NULL) {
      /* Resume parsing to get the next value.  Returns when suspended or
       * totally completed. */
      if (Expat_ParserResume(self->parser->parser) == EXPAT_STATUS_ERROR) {
        return NULL;
      }
    }
  }

  /* Consume the yieled value */
  result = self->parser->yield_result;
  self->parser->yield_result = NULL;

  return result;
}

static char saxgen_doc[] =
"SAX event generator.";

static PyTypeObject SaxGenerator_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ "Ft.Xml.cDomlette.SaxGenerator",
  /* tp_basicsize      */ sizeof(SaxGenObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) saxgen_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) 0,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
  /* tp_doc            */ (char *) saxgen_doc,
  /* tp_traverse       */ (traverseproc) saxgen_traverse,
  /* tp_clear          */ 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) saxgen_iter,
  /* tp_iternext       */ (iternextfunc) saxgen_iternext,
  /* tp_methods        */ (PyMethodDef *) 0,
  /* tp_members        */ (PyMemberDef *) 0,
  /* tp_getset         */ (PyGetSetDef *) 0,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) 0,
  /* tp_free           */ 0,
};

static PyObject *SaxGen_New(XMLParserObject *parser)
{
  SaxGenObject *self;

  self = PyObject_GC_New(SaxGenObject, &SaxGenerator_Type);
  if (self != NULL) {
    Py_INCREF(parser);
    self->parser = parser;
    PyObject_GC_Track(self);
  }

  return (PyObject *) self;
}

/********** XMLPARSER **********/

#define XMLPARSER_METHOD_DOC(NAME) METHOD_DOC(parser, NAME)
#define XMLPARSER_METHOD_DEF(NAME) METHOD_DEF(parser, NAME, XMLParserObject)
#define Py_XMLPARSER_METHOD(NAME) Py_METHOD(parser, NAME)
#define Py_XMLPARSER_MEMBER(NAME, TYPE) Py_MEMBER(NAME, TYPE, XMLParserObject)

static PyObject *prepareInputSource(PyObject *source)
{
  int rc;
  PyObject *systemId, *byteStream, *encoding;

  /* When multiple interpreters are in use, load the class each time */
  if (PyInterpreterState_Head()->next != NULL) {
    PyObject *module, *cls;
    module = PyImport_ImportModule("xml.sax.xmlreader");
    if (module == NULL) return NULL;
    cls = PyObject_GetAttrString(module, "InputSource");
    Py_DECREF(module);
    if (cls == NULL) return NULL;
    rc = PyObject_IsInstance(source, cls);
    Py_DECREF(cls);
  } else {
    rc = PyObject_IsInstance(source, sax_input_source);
  }
  if (rc == -1)
    return NULL;
  else if (rc) {
    systemId = PyObject_CallMethod(source, "getSystemId", NULL);
    byteStream = PyObject_CallMethod(source, "getByteStream", NULL);
    encoding = PyObject_CallMethod(source, "getEncoding", NULL);
    if (byteStream == NULL || systemId == NULL || encoding == NULL) {
      Py_XDECREF(byteStream);
      Py_XDECREF(systemId);
      Py_XDECREF(encoding);
      return NULL;
    }
    source = InputSource_New(systemId, byteStream, encoding);
  }
  /* check for 4Suite InputSource */
  else if (PyObject_HasAttrString(source, "resolveEntity") &&
	   PyObject_HasAttrString(source, "resolve")) {
    Py_INCREF(source);
  }
  /* check for stream */
  else if (PyObject_HasAttrString(source, "read")) {
    systemId = PyObject_GetAttrString(source, "name");
    if (systemId == NULL) {
      PyErr_Clear();
      Py_INCREF(Py_None);
      systemId = Py_None;
    }
    encoding = PyObject_GetAttrString(source, "encoding");
    if (encoding == NULL) {
      PyErr_Clear();
      Py_INCREF(Py_None);
      encoding = Py_None;
    }
    Py_INCREF(source);
    source = InputSource_New(systemId, source, encoding);
  }
  /* check for URL */
  else if (PyString_Check(source) || PyUnicode_Check(source)) {
    byteStream = PyObject_CallMethod(uri_resolver, "resolve", "O", source);
    if (byteStream == NULL) {
      return NULL;
    }
    Py_INCREF(source);
    Py_INCREF(Py_None);
    source = InputSource_New(source, byteStream, Py_None);
  }
  else {
    /* error */
    PyErr_SetString(PyExc_TypeError, "expected InputSource, stream or URL");
    source = NULL;
  }
  return source;
}

XMLPARSER_METHOD_DOC(getContentHandler) = \
"getContentHandler()\n\
\n\
Return the current ContentHandler.";

XMLPARSER_METHOD_DEF(getContentHandler)
{
  PyObject *handler;

  if (!PyArg_ParseTuple(args, ":getContentHandler"))
    return NULL;

  if (self->content_handler != NULL)
    handler = self->content_handler;
  else
    handler = Py_None;

  Py_INCREF(handler);
  return handler;
}


XMLPARSER_METHOD_DOC(setContentHandler) = \
"setContentHandler(handler)\n\
\n\
Registers a handler to receive document content events.";

XMLPARSER_METHOD_DEF(setContentHandler)
{
  PyObject *handler, *temp;

  if (!PyArg_ParseTuple(args, "O:setContentHandler", &handler))
    return NULL;

  temp = self->content_handler;
  Py_INCREF(handler);
  self->content_handler = handler;
  Py_XDECREF(temp);

#define GET_CALLBACK(TYPE, NAME)                                        \
  temp = self->handlers[Handler_##TYPE];                                \
  self->handlers[Handler_##TYPE] = PyObject_GetAttrString(handler, NAME); \
  Py_XDECREF(temp);

  GET_CALLBACK(SetLocator, "setDocumentLocator");
  GET_CALLBACK(StartDocument, "startDocument");
  GET_CALLBACK(EndDocument, "endDocument");
  GET_CALLBACK(StartNamespace, "startPrefixMapping");
  GET_CALLBACK(EndNamespace, "endPrefixMapping");
  GET_CALLBACK(StartElement, "startElementNS");
  GET_CALLBACK(EndElement, "endElementNS");
  GET_CALLBACK(Characters, "characters");
  GET_CALLBACK(IgnorableWhitespace, "ignorableWhitespace");
  GET_CALLBACK(ProcessingInstruction, "processingInstruction");
  GET_CALLBACK(SkippedEntity, "skippedEntity");
#undef GET_CALLBACK

  /* ignore any undefined event handler errors */
  PyErr_Clear();

  Py_INCREF(Py_None);
  return Py_None;
}

XMLPARSER_METHOD_DOC(getEntityResolver) = \
"getEntityResolver()\n\
\n\
Return the current EntityResolver.";

XMLPARSER_METHOD_DEF(getEntityResolver)
{
  PyObject *resolver;

  if (!PyArg_ParseTuple(args, ":getEntityResolver"))
    return NULL;

  if (self->entity_resolver != NULL)
    resolver = self->entity_resolver;
  else
    resolver = Py_None;

  Py_INCREF(resolver);
  return resolver;
}


XMLPARSER_METHOD_DOC(setEntityResolver) = \
"setEntityResolver(resolver)\n\
\n\
Registers a handler to receive resolveEntity events.\n\
NOTE: FOR NOW THIS CALL IS A NO-OP\n\
See also: http://docs.python.org/lib/entity-resolver-objects.html";

XMLPARSER_METHOD_DEF(setEntityResolver)
{
  PyObject *resolver, *temp;

  if (!PyArg_ParseTuple(args, "O:setEntityResolver", &resolver))
    return NULL;

  temp = NULL; /* Just to suppress the warning till following is uncommented */
  /*
  -- % --
     There's not yet any true support for user entity resolution.
     It would take more work than the code below.  For now this
     method is a dummy to satisfy xml.sax.saxutils.XMLFilterBase,
     which insists on calling setEntityResolver
  -- % --
  temp = self->entity_resolver;
  Py_INCREF(resolver);
  self->entity_resolver = resolver;
  Py_XDECREF(temp);

#define GET_CALLBACK(TYPE, NAME)                                        \
  temp = self->handlers[Handler_##TYPE];                                \
  self->handlers[Handler_##TYPE] = PyObject_GetAttrString(resolver, NAME); \
  Py_XDECREF(temp);

  GET_CALLBACK(SetLocator, "resolveEntity");
#undef GET_CALLBACK
  */

  /* ignore any undefined event handler errors */
  /*
  PyErr_Clear();
  */

  Py_INCREF(Py_None);
  return Py_None;
}



XMLPARSER_METHOD_DOC(getErrorHandler) = \
"getErrorHandler()\n\
\n\
Return the current ErrorHandler or None if none has been registered.";

XMLPARSER_METHOD_DEF(getErrorHandler)
{
  PyObject *handler;

  if (!PyArg_ParseTuple(args, ":getErrorHandler"))
    return NULL;

  if (self->error_handler != NULL)
    handler = self->error_handler;
  else
    handler = Py_None;

  Py_INCREF(handler);
  return handler;
}


XMLPARSER_METHOD_DOC(setErrorHandler) = \
"setErrorHandler(handler)\n\
\n\
Set the current error handler.\n\
\n\
If no ErrorHandler is set, errors will be raised as exceptions, and\n\
warnings will be silently ignored.";

XMLPARSER_METHOD_DEF(setErrorHandler)
{
  PyObject *handler, *temp;

  if (!PyArg_ParseTuple(args, "O:setErrorHandler", &handler))
    return NULL;

  temp = self->error_handler;
  Py_INCREF(handler);
  self->error_handler = handler;
  Py_XDECREF(temp);

#define GET_CALLBACK(TYPE, NAME)                                        \
  temp = self->handlers[Handler_##TYPE];                                \
  self->handlers[Handler_##TYPE] = PyObject_GetAttrString(handler, NAME); \
  Py_XDECREF(temp);

  GET_CALLBACK(Warning, "warning");
  GET_CALLBACK(Error, "error");
  GET_CALLBACK(FatalError, "fatalError");
#undef GET_CALLBACK

  /* ignore any undefined event handler errors */
  PyErr_Clear();

  Py_INCREF(Py_None);
  return Py_None;
}

XMLPARSER_METHOD_DOC(getDTDHandler) = \
"getDTDHandler()\n\
\n\
Return the current DTDHandler or None if none has been registered.";

XMLPARSER_METHOD_DEF(getDTDHandler)
{
  PyObject *handler;

  if (!PyArg_ParseTuple(args, ":getDTDHandler"))
    return NULL;

  if (self->dtd_handler != NULL)
    handler = self->dtd_handler;
  else
    handler = Py_None;

  Py_INCREF(handler);
  return handler;
}


XMLPARSER_METHOD_DOC(setDTDHandler) = \
"setDTDHandler(handler)\n\
\n\
Set the current DTDHandler.\n\
\n\
If no DTDHandler is set, DTD events will be discarded.";

XMLPARSER_METHOD_DEF(setDTDHandler)
{
  PyObject *handler, *temp;

  if (!PyArg_ParseTuple(args, "O:setDTDHandler", &handler))
    return NULL;

  temp = self->dtd_handler;
  Py_INCREF(handler);
  self->dtd_handler = handler;
  Py_XDECREF(temp);

#define GET_CALLBACK(TYPE, NAME)                                        \
  temp = self->handlers[Handler_##TYPE];                                \
  self->handlers[Handler_##TYPE] = PyObject_GetAttrString(handler, NAME); \
  Py_XDECREF(temp);

  GET_CALLBACK(NotationDecl, "notationDecl");
  GET_CALLBACK(UnparsedEntityDecl, "unparsedEntityDecl");
#undef GET_CALLBACK

  /* ignore any undefined event handler errors */
  PyErr_Clear();

  Py_INCREF(Py_None);
  return Py_None;
}

XMLPARSER_METHOD_DOC(parse) = \
"parse(source)\n\
\n\
Parse an XML document from an InputSource.";

XMLPARSER_METHOD_DEF(parse)
{
  PyObject *source;
  ExpatStatus status;

  if (!PyArg_ParseTuple(args, "O:parse", &source))
    return NULL;

  status = Expat_SetWhitespaceRules(self->parser, self->whitespace_rules);
  if (status == EXPAT_STATUS_ERROR) return NULL;

  if (self->dom_node) {
    /* walk over a DOM, ignoring the source argument */
    status = ParseDOM(self);
  } else {
    source = prepareInputSource(source);
    if (source == NULL) return NULL;

    /* parse the document indicated by the InputSource */
    status = Expat_ParseDocument(self->parser, source);
    Py_DECREF(source);
  }

  if (status == EXPAT_STATUS_ERROR) {
    return NULL;
  }

  if (self->generator) {
    return SaxGen_New(self);
  } else {
    Py_INCREF(Py_None);
    return Py_None;
  }
}

XMLPARSER_METHOD_DOC(getFeature) = \
"getFeature(featurename)\n\
\n\
Return the current setting for feature featurename. If the feature\n\
is not recognized, SAXNotRecognizedException is raised. The well-known\n\
featurenames are listed in the module xml.sax.handler.";

XMLPARSER_METHOD_DEF(getFeature)
{
  PyObject *featurename;
  PyObject *state;

  if (!PyArg_ParseTuple(args, "O:getFeature", &featurename))
    return NULL;

  /* SAX features */
  if (PyObject_RichCompareBool(featurename, feature_validation,
                                    Py_EQ)) {
    state = Expat_GetValidation(self->parser) ? Py_True : Py_False;
  }
  else if (PyObject_RichCompareBool(featurename, feature_external_ges,
                                    Py_EQ)) {
    state = Py_True;
  }
  else if (PyObject_RichCompareBool(featurename, feature_external_pes,
                                    Py_EQ)) {
    if (Expat_GetValidation(self->parser)) {
      /* always true if validating */
      state = Py_True;
    } else {
      state = Expat_GetParamEntityParsing(self->parser) ? Py_True : Py_False;
    }
  }
  else if (PyObject_RichCompareBool(featurename, feature_namespaces, Py_EQ)) {
    state = Py_True;
  }
  else if (PyObject_RichCompareBool(featurename, feature_namespace_prefixes,
                                    Py_EQ)) {
    state = Py_False;
  }
  else if (PyObject_RichCompareBool(featurename, feature_string_interning,
                                    Py_EQ)) {
    state = Py_True;
  }
  /* 4Suite-specific features */
  else if (PyObject_RichCompareBool(featurename, feature_process_xincludes,
                                    Py_EQ)) {
    state = Expat_GetXIncludeProcessing(self->parser) ? Py_True : Py_False;
  }
  else if (PyObject_RichCompareBool(featurename, feature_generator, Py_EQ)) {
    state = self->generator ? Py_True : Py_False;
  }
  else {
    PyObject *repr = PyObject_Repr(featurename);
    if (repr) {
      SAXNotRecognizedException(PyString_AsString(repr));
      Py_DECREF(repr);
    }
    return NULL;
  }

  Py_INCREF(state);
  return state;
}

XMLPARSER_METHOD_DOC(setFeature) = \
"setFeature(featurename, value)\n\
\n\
Set the featurename to value. If the feature is not recognized,\n\
SAXNotRecognizedException is raised. If the feature or its setting\n\
is not supported by the parser, SAXNotSupportedException is raised.";

XMLPARSER_METHOD_DEF(setFeature)
{
  PyObject *featurename, *value;
  int state;

  if (!PyArg_ParseTuple(args, "OO:setFeature", &featurename, &value))
    return NULL;

  if ((state = PyObject_IsTrue(value)) == -1) return NULL;

  if (Expat_GetParsingStatus(self->parser)) {
    return SAXNotSupportedException("cannot set features while parsing");
  }
  /* SAX features */
  else if (PyObject_RichCompareBool(featurename, feature_validation,
                                    Py_EQ)) {
    Expat_SetValidation(self->parser, state);
  }
  else if (PyObject_RichCompareBool(featurename, feature_external_ges,
                                    Py_EQ)) {
    if (state == 0)
      return SAXNotSupportedException(
                "external general entities always processed");
  }
  else if (PyObject_RichCompareBool(featurename, feature_external_pes,
                                    Py_EQ)) {
    Expat_SetParamEntityParsing(self->parser, state);
  }
  else if (PyObject_RichCompareBool(featurename, feature_namespaces, Py_EQ)) {
    if (state == 0)
      return SAXNotSupportedException("namespace processing always enabled");
  }
  else if (PyObject_RichCompareBool(featurename, feature_namespace_prefixes,
                                    Py_EQ)) {
    if (state == 1)
      return SAXNotSupportedException("namespace prefixes never reported");
  }
  else if (PyObject_RichCompareBool(featurename, feature_string_interning,
                                    Py_EQ)) {
    if (state == 0)
      return SAXNotSupportedException("string interning always enabled");
  }
  /* 4Suite-specific features */
  else if (PyObject_RichCompareBool(featurename, feature_process_xincludes,
                                    Py_EQ)) {
    Expat_SetXIncludeProcessing(self->parser, state);
  }
  else if (PyObject_RichCompareBool(featurename, feature_generator, Py_EQ)) {
    self->generator = state;
    if (state == 0 && self->yield_result) {
      Py_DECREF(self->yield_result);
      self->yield_result = NULL;
    }
  }
  else {
    PyObject *repr = PyObject_Repr(featurename);
    if (repr) {
      SAXNotRecognizedException(PyString_AsString(repr));
      Py_DECREF(repr);
    }
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

XMLPARSER_METHOD_DOC(getProperty) = \
"getProperty(propertyname)\n\
\n\
Return the current setting for property propertyname. If the property is\n\
not recognized, a SAXNotRecognizedException is raised. The well-known\n\
propertynames are listed in the module xml.sax.handler.";

XMLPARSER_METHOD_DEF(getProperty)
{
  PyObject *propertyname, *value;

  if (!PyArg_ParseTuple(args, "O:getProperty", &propertyname))
    return NULL;

  if (PyObject_RichCompareBool(propertyname, property_lexical_handler,
                                    Py_EQ)) {
    if (self->lexical_handler == NULL)
      value = Py_None;
    else
      value = self->lexical_handler;
    Py_INCREF(value);
  }
  else if (PyObject_RichCompareBool(propertyname, property_declaration_handler,
                                    Py_EQ)) {
    if (self->decl_handler == NULL)
      value = Py_None;
    else
      value = self->decl_handler;
    Py_INCREF(value);
  }
  else if (PyObject_RichCompareBool(propertyname, property_dom_node,
                                    Py_EQ)) {
    if (self->dom_node == NULL)
      value = Py_None;
    else
      value = (PyObject*) self->dom_node;
    Py_INCREF(value);
  }
  /* 4Suite-specific properties */
  else if (PyObject_RichCompareBool(propertyname, property_whitespace_rules,
                                    Py_EQ)) {
    /* XSLT-style whitespace stripping rules */
    if (self->whitespace_rules == NULL) {
      value = PyList_New((Py_ssize_t)0);
    } else {
      Py_INCREF(self->whitespace_rules);
      value = self->whitespace_rules;
    }
  }
  else if (PyObject_RichCompareBool(propertyname, property_yield_result,
                                    Py_EQ)) {
    /* result value used when generator feature is enabled */
    if (self->yield_result == NULL) {
      value = Py_None;
    } else {
      value = self->yield_result;
    }
    Py_INCREF(value);
  }
  else {
    PyObject *repr = PyObject_Repr(propertyname);
    if (repr) {
      SAXNotRecognizedException(PyString_AsString(repr));
      Py_DECREF(repr);
    }
    value = NULL;
  }

  return value;
}

XMLPARSER_METHOD_DOC(setProperty) = \
"setProperty(propertyname, value)\n\
\n\
Set the propertyname to value. If the property is not recognized,\n\
SAXNotRecognizedException is raised. If the property or its setting\n\
is not supported by the parser, SAXNotSupportedException is raised.";

XMLPARSER_METHOD_DEF(setProperty)
{
  PyObject *propertyname, *value, *temp;

  if (!PyArg_ParseTuple(args, "OO:setProperty", &propertyname, &value))
    return NULL;

  if (PyObject_RichCompareBool(propertyname, property_yield_result, Py_EQ)) {
    /* result value used when generator feature is enabled */
    if (self->generator) {
      temp = self->yield_result;
      Py_INCREF(value);
      self->yield_result = value;
      Py_XDECREF(temp);
      if (Expat_ParserSuspend(self->parser) == XML_STATUS_ERROR) {
        return NULL;
      }
    } else {
      return SAXNotSupportedException(
                "yield-result only allowed for generator parser");
    }
  }
  else if (Expat_GetParsingStatus(self->parser)) {
    return SAXNotSupportedException("cannot set properties while parsing");
  }
  else if (PyObject_RichCompareBool(propertyname, property_lexical_handler,
                                    Py_EQ)) {
    if (value == Py_None)
      value = NULL;
    else
      Py_INCREF(value);
    temp = self->lexical_handler;
    self->lexical_handler = value;
    Py_XDECREF(temp);

#define GET_CALLBACK(TYPE, NAME)                                        \
    temp = self->handlers[Handler_##TYPE];                              \
    self->handlers[Handler_##TYPE] = PyObject_GetAttrString(value, NAME); \
    Py_XDECREF(temp);

    GET_CALLBACK(StartDTD, "startDTD");
    GET_CALLBACK(EndDTD, "endDTD");
    GET_CALLBACK(StartCDATA, "startCDATA");
    GET_CALLBACK(EndCDATA, "endCDATA");
    GET_CALLBACK(Comment, "comment");
#undef GET_CALLBACK

    /* ignore any undefined event handler errors */
    PyErr_Clear();
  }
  else if (PyObject_RichCompareBool(propertyname, property_declaration_handler,
                                    Py_EQ)) {
    if (value == Py_None)
      value = NULL;
    else
      Py_INCREF(value);
    temp = self->decl_handler;
    self->decl_handler = value;
    Py_XDECREF(temp);

#define GET_CALLBACK(TYPE, NAME)                                        \
    temp = self->handlers[Handler_##TYPE];                              \
    self->handlers[Handler_##TYPE] = PyObject_GetAttrString(value, NAME); \
    Py_XDECREF(temp);

    GET_CALLBACK(ElementDecl, "elementDecl");
    GET_CALLBACK(AttributeDecl, "attributeDecl");
    GET_CALLBACK(InternalEntityDecl, "internalEntityDecl");
    GET_CALLBACK(ExternalEntityDecl, "externalEntityDecl");
#undef GET_CALLBACK

    /* ignore any undefined event handler errors */
    PyErr_Clear();
  }
  else if (PyObject_RichCompareBool(propertyname, property_dom_node,
                                    Py_EQ)) {
    /* create a "DOM Walker"-style parser */
    if (PyDocument_Check(value)) {
      Py_XDECREF(self->dom_node);
      Py_INCREF(value);
      self->dom_node = (PyNodeObject *) value;
    } else {
      return SAXNotSupportedException("dom-node must be a Document node");
    }
  }
  else if (PyObject_RichCompareBool(propertyname, property_whitespace_rules,
                                    Py_EQ)) {
    /* XSLT-style whitespace stripping rules */
    if (value == Py_None) {
      Py_XDECREF(self->whitespace_rules);
      self->whitespace_rules = NULL;
    }
    else if (PyList_Check(value)) {
      Py_XDECREF(self->whitespace_rules);
      if (PyList_GET_SIZE(value) == 0) {
        self->whitespace_rules = NULL;
      } else {
        Py_INCREF(value);
        self->whitespace_rules = value;
      }
    }
    else {
      return SAXNotSupportedException("whitespace-rules must be a list");
    }
  }
  else {
    PyObject *repr = PyObject_Repr(propertyname);
    if (repr) {
      SAXNotRecognizedException(PyString_AsString(repr));
      Py_DECREF(repr);
    }
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

/** Locator Interface **/

XMLPARSER_METHOD_DOC(getLineNumber) = \
"getLineNumber() -> int\n\
\n\
Return the line number where the current event ends.";

XMLPARSER_METHOD_DEF(getLineNumber)
{
  int lineNumber;

  if (!PyArg_ParseTuple(args, ":getLineNumber"))
    return NULL;

  if (self->dom_node)
    lineNumber = -1;
  else
    lineNumber = Expat_GetLineNumber(self->parser);

  return PyInt_FromLong(lineNumber);
}

XMLPARSER_METHOD_DOC(getColumnNumber) = \
"getColumnNumber() -> int\n\
\n\
Return the column number where the current event ends.";

XMLPARSER_METHOD_DEF(getColumnNumber)
{
  int columnNumber;

  if (!PyArg_ParseTuple(args, ":getColumnNumber"))
    return NULL;

  if (self->dom_node)
    columnNumber = -1;
  else
    columnNumber = Expat_GetColumnNumber(self->parser);

  return PyInt_FromLong(columnNumber);
}

XMLPARSER_METHOD_DOC(getSystemId) = \
"getSystemId() -> string\n\
\n\
Return the system identifier for the current event.";

XMLPARSER_METHOD_DEF(getSystemId)
{
  PyObject *systemId;

  if (!PyArg_ParseTuple(args, ":getSystemId"))
    return NULL;

  if (self->dom_node) {
    systemId = PyDocument_BASE_URI(self->dom_node);
    Py_INCREF(systemId);
  } else {
    systemId = Expat_GetBase(self->parser);
  }
  return systemId;
}

static PyMethodDef parser_methods[] = {
  Py_XMLPARSER_METHOD(getContentHandler),
  Py_XMLPARSER_METHOD(setContentHandler),
  Py_XMLPARSER_METHOD(getEntityResolver),
  Py_XMLPARSER_METHOD(setEntityResolver),
  Py_XMLPARSER_METHOD(getErrorHandler),
  Py_XMLPARSER_METHOD(setErrorHandler),
  Py_XMLPARSER_METHOD(getDTDHandler),
  Py_XMLPARSER_METHOD(setDTDHandler),
  Py_XMLPARSER_METHOD(parse),
  Py_XMLPARSER_METHOD(getFeature),
  Py_XMLPARSER_METHOD(setFeature),
  Py_XMLPARSER_METHOD(getProperty),
  Py_XMLPARSER_METHOD(setProperty),

  /* Locator Methods */
  Py_XMLPARSER_METHOD(getLineNumber),
  Py_XMLPARSER_METHOD(getColumnNumber),
  Py_XMLPARSER_METHOD(getSystemId),

  { NULL }
};

static struct memberlist parser_members[] = {
  { NULL }
};

static void parser_dealloc(XMLParserObject *self)
{
  int i;

  PyObject_GC_UnTrack(self);

  Py_XDECREF(self->dom_node);
  Py_XDECREF(self->whitespace_rules);
  Py_XDECREF(self->yield_result);
  Py_XDECREF(self->lexical_handler);
  Py_XDECREF(self->decl_handler);
  Py_XDECREF(self->error_handler);
  Py_XDECREF(self->dtd_handler);
  Py_XDECREF(self->content_handler);
  Py_XDECREF(self->entity_resolver);

  for (i = 0; i < TotalHandlers; i++) {
    Py_XDECREF(self->handlers[i]);
  }

  Expat_ParserFree(self->parser);
  self->parser = NULL;

  PyObject_GC_Del(self);
}

static int parser_traverse(XMLParserObject *self, visitproc visit, void *arg)
{
  int i;

  Py_VISIT(self->content_handler);
  Py_VISIT(self->dtd_handler);
  Py_VISIT(self->error_handler);
  Py_VISIT(self->entity_resolver);
  Py_VISIT(self->decl_handler);
  Py_VISIT(self->lexical_handler);
  for (i = 0; i < TotalHandlers; i++) {
    Py_VISIT(self->handlers[i]);
  }
  return 0;
}

static int parser_clear(PyObject *self)
{
  int i;
  XMLParserObject *xmlpobj = (XMLParserObject *)self;

  Py_CLEAR(xmlpobj->content_handler);
  Py_CLEAR(xmlpobj->dtd_handler);
  Py_CLEAR(xmlpobj->error_handler);
  Py_CLEAR(xmlpobj->entity_resolver);
  Py_CLEAR(xmlpobj->decl_handler);
  Py_CLEAR(xmlpobj->lexical_handler);
  for (i = 0; i < TotalHandlers; i++) {
    Py_CLEAR(xmlpobj->handlers[i]);
  }
  return 0;
}

static char parser_doc[] =
"Interface for reading an XML document using callbacks.\n\
\n\
Parser is the interface that an XML parser's SAX2 driver must\n\
implement. This interface allows an application to set and query\n\
features and properties in the parser, to register event handlers\n\
for document processing, and to initiate a document parse.\n\
\n\
All SAX interfaces are assumed to be synchronous: the parse\n\
methods must not return until parsing is complete, and readers\n\
must wait for an event-handler callback to return before reporting\n\
the next event.";

static PyTypeObject XMLParser_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ "Ft.Xml.cDomlette.Parser",
  /* tp_basicsize      */ sizeof(XMLParserObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) parser_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) 0,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
  /* tp_doc            */ (char *) parser_doc,
  /* tp_traverse       */ (traverseproc) parser_traverse,
  /* tp_clear          */ parser_clear,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) parser_methods,
  /* tp_members        */ (PyMemberDef *) parser_members,
  /* tp_getset         */ (PyGetSetDef *) 0,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) 0,
  /* tp_free           */ 0,
};

static ExpatParser createParser(XMLParserObject *self)
{
  ExpatParser parser = Expat_ParserCreate(self);
  if (parser != NULL) {

    /** ContentHandler ******************************************/

    /* startDocument() */
    Expat_SetStartDocumentHandler(parser, parser_StartDocument);

    /* endDocument() */
    Expat_SetEndDocumentHandler(parser, parser_EndDocument);

    /* startPrefixMapping(prefix, uri) */
    Expat_SetStartNamespaceDeclHandler(parser, parser_StartNamespaceDecl);

    /* endPrefixMapping(prefix) */
    Expat_SetEndNamespaceDeclHandler(parser, parser_EndNamespaceDecl);

    /* startElementNS((namespaceURI, localName), qualifiedName, attrs) */
    Expat_SetStartElementHandler(parser, parser_StartElement);

    /* endElementNS((namespaceURI, localName), qualifiedName) */
    Expat_SetEndElementHandler(parser, parser_EndElement);

    /* characters(data) */
    Expat_SetCharacterDataHandler(parser, parser_CharacterData);

    /* ignorableWhitespace(data) */
    Expat_SetIgnorableWhitespaceHandler(parser, parser_IgnorableWhitespace);

    /* processingInstruction(target, data) */
    Expat_SetProcessingInstructionHandler(parser,
                                          parser_ProcessingInstruction);

    /* skippedEntity(name) */
    Expat_SetSkippedEntityHandler(parser, parser_SkippedEntity);

    /** ErrorHandler ********************************************/

    /* warning(exception) */
    Expat_SetWarningHandler(parser, parser_Warning);

    /* error(exception) */
    Expat_SetErrorHandler(parser, parser_Error);

    /* fatalError(exception) */
    Expat_SetFatalErrorHandler(parser, parser_FatalError);

    /** DTDHandler **********************************************/

    /* notationDecl(name, publicId, systemId) */
    Expat_SetNotationDeclHandler(parser, parser_NotationDecl);

    /* unparsedEntityDecl(name, publicId, systemId, notationName) */
    Expat_SetUnparsedEntityDeclHandler(parser, parser_UnparsedEntityDecl);

    /** LexicalHandler ******************************************/

    /* startDTD() */
    Expat_SetStartDoctypeDeclHandler(parser, parser_StartDoctypeDecl);

    /* endDTD() */
    Expat_SetEndDoctypeDeclHandler(parser, parser_EndDoctypeDecl);

    /* startCDATA() */
    Expat_SetStartCdataSectionHandler(parser, parser_StartCdataSection);

    /* endCDATA() */
    Expat_SetEndCdataSectionHandler(parser, parser_EndCdataSection);

    /* comment(data) */
    Expat_SetCommentHandler(parser, parser_Comment);

    /** DeclHandler *********************************************/

    /* elementDecl(name, model) */
    Expat_SetElementDeclHandler(parser, parser_ElementDecl);

    /* attributeDecl(eName, aName, type, mode, value) */
    Expat_SetAttributeDeclHandler(parser, parser_AttributeDecl);

    /* internalEntityDecl(name, value) */
    Expat_SetInternalEntityDeclHandler(parser, parser_InternalEntityDecl);

    /* externalEntityDecl(name, publicId, systemId) */
    Expat_SetExternalEntityDeclHandler(parser, parser_ExternalEntityDecl);

  }

  return parser;
}


static PyObject *XMLParser_New(int feature_external_entities)
{
  XMLParserObject *self;
  int i;

  self = PyObject_GC_New(XMLParserObject, &XMLParser_Type);
  if (self != NULL) {
    /* create the XML parser */
    self->parser = createParser(self);
    if (self->parser == NULL) {
      PyObject_GC_Del(self);
      return NULL;
    }
    Expat_SetParamEntityParsing(self->parser, feature_external_entities);

    self->content_handler = NULL;
    self->dtd_handler = NULL;
    self->error_handler = NULL;
    self->entity_resolver = NULL;
    self->decl_handler = NULL;
    self->lexical_handler = NULL;

    for (i = 0; i < TotalHandlers; i++)
      self->handlers[i] = NULL;

    self->generator = 0;

    self->yield_result = NULL;
    self->whitespace_rules = NULL;
    self->dom_node = NULL;

    PyObject_GC_Track(self);
  }

  return (PyObject *) self;
}

/********** ATTRIBUTES **********/

#define ATTRIBUTES_METHOD_DOC(NAME) METHOD_DOC(attributes, NAME)
#define ATTRIBUTES_METHOD(NAME) METHOD_DEF(attributes, NAME, AttributesObject)
#define Py_ATTRIBUTES_METHOD(NAME) Py_METHOD(attributes, NAME)
#define Py_ATTRIBUTES_MEMBER(NAME,TYPE) Py_MEMBER(NAME, TYPE, AttributesObject)

ATTRIBUTES_METHOD_DOC(getValue) = \
"getValue(name)\n\
Returns the value of the attribute with the given expanded name.";

ATTRIBUTES_METHOD(getValue)
{
  PyObject *name;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "O:getValue", &name)) return NULL;

  result = PyDict_GetItem(self->values, name);
  if (result == NULL) {
    PyErr_SetObject(PyExc_KeyError, name);
  } else {
    Py_INCREF(result);
  }
  return result;
}

ATTRIBUTES_METHOD_DOC(getQNameByName) = \
"getQNameByName(name)\n\
Returns the qualified name of the attribute with the given expanded name.";

ATTRIBUTES_METHOD(getQNameByName)
{
  PyObject *name;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "O:getQNameByName", &name)) return NULL;

  result = PyDict_GetItem(self->qnames, name);
  if (result == NULL) {
    PyErr_SetObject(PyExc_KeyError, name);
  } else {
    Py_INCREF(result);
  }
  return result;
}

ATTRIBUTES_METHOD_DOC(has_key) = \
"has_key(name)\n\
Returns True if the attribute name is in the list, False otherwise.";

ATTRIBUTES_METHOD(has_key)
{
  PyObject *name;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "O:has_key", &name)) return NULL;

  result = PyMapping_HasKey(self->values, name) ? Py_True : Py_False;
  Py_INCREF(result);
  return result;
}

ATTRIBUTES_METHOD_DOC(get) = \
"get(name[, alternative=None])\n\
Return the value associated with attribute name; if it is not available,\n\
then return the alternative.";

ATTRIBUTES_METHOD(get)
{
  PyObject *name, *alternative = Py_None;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "O|O:get", &name, &alternative)) return NULL;

  result = PyDict_GetItem(self->values, name);
  if (result == NULL) {
    result = alternative;
  }
  Py_INCREF(result);
  return result;
}

ATTRIBUTES_METHOD_DOC(keys) = \
"keys()\n\
Returns a list of the names of all attribute in the list.";

ATTRIBUTES_METHOD(keys)
{
  if (!PyArg_ParseTuple(args, ":keys")) return NULL;

  return PyDict_Keys(self->values);
}

ATTRIBUTES_METHOD_DOC(items) = \
"items()\n\
Return a list of (attribute_name, value) pairs.";

ATTRIBUTES_METHOD(items)
{
  if (!PyArg_ParseTuple(args, ":items")) return NULL;

  return PyDict_Items(self->values);
}

ATTRIBUTES_METHOD_DOC(values) = \
"values()\n\
Return a list of all attribute values.";

ATTRIBUTES_METHOD(values)
{
  if (!PyArg_ParseTuple(args, ":values")) return NULL;

  return PyDict_Values(self->values);
}

static PyMethodDef attributes_methods[] = {
  Py_ATTRIBUTES_METHOD(getValue),
  Py_ATTRIBUTES_METHOD(getQNameByName),

  /* named mapping methods */
  Py_ATTRIBUTES_METHOD(has_key),
  Py_ATTRIBUTES_METHOD(get),
  Py_ATTRIBUTES_METHOD(keys),
  Py_ATTRIBUTES_METHOD(items),
  Py_ATTRIBUTES_METHOD(values),
  { NULL }
};

/** PySequenceMethods **********/

static Py_ssize_t attributes_length(PyObject *self)
{
  return ((AttributesObject *)self)->length;
}

static int attributes_contains(AttributesObject *self, PyObject *key)
{
  return PyDict_GetItem(self->values, key) != NULL;
}

static PySequenceMethods attributes_as_sequence = {
  /* sq_length         */ attributes_length,
  /* sq_concat         */ (binaryfunc) 0,
  /* sq_repeat         */ 0,
  /* sq_item           */ 0,
  /* sq_slice          */ 0,
  /* sq_ass_item       */ 0,
  /* sq_ass_slice      */ 0,
  /* sq_contains       */ (objobjproc) attributes_contains,
  /* sq_inplace_concat */ (binaryfunc) 0,
  /* sq_inplace_repeat */ 0,
};

/** PyMappingMethods **********/

static PyObject *attributes_subscript(AttributesObject *self, PyObject *name)
{
  PyObject *result = PyDict_GetItem(self->values, name);
  if (result == NULL) {
    PyErr_SetObject(PyExc_KeyError, name);
  } else {
    Py_INCREF(result);
  }
  return result;
}

static int attributes_ass_subscript(AttributesObject *self, PyObject *name,
                                    PyObject *value)
{
  int rc;

  if (value == NULL) {
    /* delete item */
    if ((rc = PyDict_DelItem(self->values, name)) == 0) {
      rc = PyDict_DelItem(self->qnames, name);
    }
  } else {
    PyErr_SetString(PyExc_TypeError,
                    "object does not support item assignment");
    rc = -1;
  }

  return rc;
}

static PyMappingMethods attributes_as_mapping = {
  /* mp_length        */ attributes_length,
  /* mp_subscript     */ (binaryfunc) attributes_subscript,
  /* mp_ass_subscript */ (objobjargproc) attributes_ass_subscript,
};

/** Type Methods **************/

static void attributes_dealloc(AttributesObject *self)
{
  PyObject_GC_UnTrack((PyObject *) self);

  self->length = 0;

  if (self->values != NULL) {
    Py_DECREF(self->values);
    self->values = NULL;
  }

  if (self->qnames != NULL) {
    Py_DECREF(self->qnames);
    self->qnames = NULL;
  }

  if (num_free_attrs < MAX_FREE_ATTRS) {
    free_attrs[num_free_attrs++] = self;
  } else {
    PyObject_GC_Del(self);
  }
}

static int attributes_print(AttributesObject *self, FILE *fp, int flags)
{
  return PyObject_Print(self->values, fp, flags);
}

static PyObject *attributes_repr(AttributesObject *self)
{
  return PyObject_Repr(self->values);
}

static int attributes_traverse(AttributesObject *self, visitproc visit,
                               void *arg)
{
  int err;

  if (self->values != NULL) {
    err = visit(self->values, arg);
    if (err) return err;
  }

  if (self->qnames != NULL) {
    err = visit(self->qnames, arg);
    if (err) return err;
  }

  return 0;
}

static int attributes_clear(PyObject *self)
{
  PyObject *tmp;
  AttributesObject *aobj = (AttributesObject *)self;

  if (aobj->values != NULL) {
    tmp = aobj->values;
    aobj->values = NULL;
    Py_DECREF(tmp);
  }

  if (aobj->qnames != NULL) {
    tmp = aobj->qnames;
    aobj->qnames = NULL;
    Py_DECREF(tmp);
  }

  return 0;
}

static PyObject *attributes_iter(AttributesObject *self)
{
  return PyObject_GetIter(self->values);
}

static char attributes_doc[] =
"Interface for a list of XML attributes.\n\
\n\
Contains a list of XML attributes, accessible by name.";

static PyTypeObject Attributes_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ "Ft.Xml.cDomlette.Attributes",
  /* tp_basicsize      */ sizeof(AttributesObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) attributes_dealloc,
  /* tp_print          */ (printfunc) attributes_print,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) attributes_repr,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) &attributes_as_sequence,
  /* tp_as_mapping     */ (PyMappingMethods *) &attributes_as_mapping,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
  /* tp_doc            */ (char *) attributes_doc,
  /* tp_traverse       */ (traverseproc) attributes_traverse,
  /* tp_clear          */ attributes_clear,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) attributes_iter,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) attributes_methods,
  /* tp_members        */ (PyMemberDef *) 0,
  /* tp_getset         */ (PyGetSetDef *) 0,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) 0,
  /* tp_free           */ 0,
};

static AttributesObject *Attributes_New(void)
{
  AttributesObject *self;

  if (num_free_attrs) {
    num_free_attrs--;
    self = free_attrs[num_free_attrs];
    _Py_NewReference((PyObject *) self);
  } else {
    self = PyObject_GC_New(AttributesObject, &Attributes_Type);
    if (self == NULL)
      return NULL;
  }

  self->length = 0;
  self->values = PyDict_New();
  self->qnames = PyDict_New();
  if (self->values == NULL || self->qnames == NULL) {
    Py_XDECREF(self->values);
    Py_XDECREF(self->qnames);
    Py_DECREF(self);
    return NULL;
  }

  PyObject_GC_Track(self);

  return self;
}

/**********************************************************************/
/** External interfaces ***********************************************/
/**********************************************************************/

static int read_external_dtd;

char CreateParser_doc[] =
"CreateParser([readExtDtd]) -> Parser\n\
\n\
Return a new XML parser object.";

PyObject *Domlette_CreateParser(PyObject *dummy, PyObject *args, PyObject *kw)
{
  static char *kwlist[] = { "readExtDtd", NULL };
  PyObject *readExtDtd=NULL;
  int read_ext_dtd=read_external_dtd;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "|O:CreateParser", kwlist,
                                   &readExtDtd))
    return NULL;

  if (readExtDtd) {
    read_ext_dtd = PyObject_IsTrue(readExtDtd);
    if (read_ext_dtd == -1) return NULL;
  }

  return XMLParser_New(read_ext_dtd);
}

int DomletteParser_Init(PyObject *module)
{
  PyObject *import, *constant;

  XmlString_IMPORT;

  import = PyImport_ImportModule("Ft.Lib.Uri");
  if (import == NULL) return -1;
  uri_resolver = PyObject_GetAttrString(import, "BASIC_RESOLVER");
  if (uri_resolver == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  import = PyImport_ImportModule("Ft.Xml");
  if (import == NULL) return -1;
  constant = PyObject_GetAttrString(import, "READ_EXTERNAL_DTD");
  if (constant == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  read_external_dtd = PyObject_IsTrue(constant);
  Py_DECREF(constant);
  if (read_external_dtd == -1) return -1;

  if (PyType_Ready(&InputSource_Type) < 0)
    return -1;

  if (PyType_Ready(&SaxGenerator_Type) < 0)
    return -1;

  if (PyType_Ready(&XMLParser_Type) < 0)
    return -1;

  if (PyType_Ready(&Attributes_Type) < 0)
    return -1;

  /* define 4Suite's extended feature & property constants */
#define ADD_STRING_CONST(cname, pname, string)          \
  if ((cname = PyString_FromString(string)) == NULL)    \
    return -1;                                          \
  if (PyModule_AddObject(module, pname, cname) == -1) { \
    Py_DECREF(cname);                                   \
    return -1;                                          \
  }                                                     \
  Py_INCREF(cname);

  ADD_STRING_CONST(feature_process_xincludes, "FEATURE_PROCESS_XINCLUDES",
                   "http://4suite.org/sax/features/process-xincludes");
  ADD_STRING_CONST(feature_generator, "FEATURE_GENERATOR",
                   "http://4suite.org/sax/features/generator");
  ADD_STRING_CONST(property_whitespace_rules, "PROPERTY_WHITESPACE_RULES",
                   "http://4suite.org/sax/properties/whitespace-rules");
  ADD_STRING_CONST(property_yield_result, "PROPERTY_YIELD_RESULT",
                   "http://4suite.org/sax/properties/yield-result");

#define GET_MODULE_EXC(name)                            \
  name##Object = PyObject_GetAttrString(import, #name); \
  if (name##Object == NULL) {                           \
    Py_DECREF(import);                                  \
    return -1;                                          \
  }

  /* load the SAX exceptions */
  import = PyImport_ImportModule("xml.sax");
  if (import == NULL) return -1;
  GET_MODULE_EXC(SAXNotRecognizedException);
  GET_MODULE_EXC(SAXNotSupportedException);
  GET_MODULE_EXC(SAXParseException);
  Py_DECREF(import);

#define GET_MODULE_CONST(name)                  \
  name = PyObject_GetAttrString(import, #name); \
  if (name == NULL) {                           \
    Py_DECREF(import);                          \
    return -1;                                  \
  }

  /* load the SAX standard feature & property constants */
  import = PyImport_ImportModule("xml.sax.handler");
  if (import == NULL) return -1;
  GET_MODULE_CONST(feature_external_ges);
  GET_MODULE_CONST(feature_external_pes);
  GET_MODULE_CONST(feature_namespaces);
  GET_MODULE_CONST(feature_namespace_prefixes);
  GET_MODULE_CONST(feature_string_interning);
  GET_MODULE_CONST(feature_validation);
  GET_MODULE_CONST(property_declaration_handler);
  GET_MODULE_CONST(property_dom_node);
  GET_MODULE_CONST(property_lexical_handler);
  /*GET_MODULE_CONST(property_xml_string);*/
  Py_DECREF(import);

  /* load the SAX InputSource class */
  import = PyImport_ImportModule("xml.sax.xmlreader");
  if (import == NULL) return -1;
  sax_input_source = PyObject_GetAttrString(import, "InputSource");
  if (sax_input_source == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  return 0;
}

void DomletteParser_Fini(void)
{
  AttributesObject *attr;
  int i;

  while(num_free_attrs) {
    num_free_attrs--;
    attr = free_attrs[num_free_attrs];
    free_attrs[num_free_attrs] = NULL;
    PyObject_GC_Del(attr);
  }

  for (i = 0; i < TotalHandlers; i++) {
    PyCodeObject *code = tb_codes[i];
    if (code != NULL) {
      tb_codes[i] = NULL;
      Py_DECREF(code);
    }
  }

  Py_DECREF(uri_resolver);
  Py_DECREF(feature_process_xincludes);
  Py_DECREF(feature_generator);
  Py_DECREF(property_whitespace_rules);
  Py_DECREF(property_yield_result);
  Py_DECREF(SAXNotRecognizedExceptionObject);
  Py_DECREF(SAXNotSupportedExceptionObject);
  Py_DECREF(SAXParseExceptionObject);
  Py_DECREF(feature_external_ges);
  Py_DECREF(feature_external_pes);
  Py_DECREF(feature_namespaces);
  Py_DECREF(feature_namespace_prefixes);
  Py_DECREF(feature_string_interning);
  Py_DECREF(feature_validation);
  Py_DECREF(property_declaration_handler);
  Py_DECREF(property_dom_node);
  Py_DECREF(property_lexical_handler);
  /*Py_DECREF(property_xml_string);*/
  Py_DECREF(sax_input_source);

  PyType_CLEAR(&InputSource_Type);
  PyType_CLEAR(&SaxGenerator_Type);
  PyType_CLEAR(&XMLParser_Type);
  PyType_CLEAR(&Attributes_Type);
}
