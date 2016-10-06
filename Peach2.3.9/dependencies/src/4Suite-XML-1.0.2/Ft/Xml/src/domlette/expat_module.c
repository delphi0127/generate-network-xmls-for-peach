#include "expat_module.h"
#include "state_machine.h"
#include "util.h"
#include "xmlchar.h"
#include "content_model.h"
#include "exceptions.h"
#include "cStringIO.h"
#include "xmlstring.h"
#include "debug.h"

/*#define DEBUG_PARSER */
/*#define DEBUG_CALLBACKS */
/*#define DEBUG_XINCLUDE */

#ifdef DEBUG_PARSER
#ifdef __STDC__ /* C99 conformance macro */
#define Debug_Print(...) fprintf(stderr, __VA_ARGS__)
#else
static void Debug_Print(const char *format, ...) {
  va_list va;
  va_start(va, format);
  vfprintf(stderr, format, va);
  va_end(va);
}
#endif

#define Debug_FunctionCall(name, ptr)           \
  Debug_Print("### %s(%p)\n", #name, ptr)

#define Debug_Return(name, fmt, arg)                    \
  Debug_Print("### %s() => " fmt "\n", #name, arg)

#define Debug_ParserFunctionCall(name, parser)  \
  Debug_FunctionCall(name, parser->context)

#define Debug_ReturnStatus(name, status)                                \
  Debug_Return(name, "%s",                                              \
               (status == EXPAT_STATUS_ERROR ? "ERROR" :                \
                status == EXPAT_STATUS_OK ? "OK" :                      \
                status == EXPAT_STATUS_SUSPENDED ? "SUSPENDED" :        \
                "UNKNOWN"))
#else
#ifdef __STDC__ /* C99 conformance macro */
#define Debug_Print(...)
#else
static void Debug_Print(const char *format, ...) { }
#endif
#define Debug_FunctionCall(name, ptr)
#define Debug_Return(name, fmt, arg)
#define Debug_ParserFunctionCall(name, parser)
#define Debug_ReturnStatus(name, status)
#endif

/* Should not be a valid  XML character to ensure that splitting is correct.
   Using a form-feed (ASCII character 12).
*/
#define EXPAT_NSSEP '\f'

#if defined(XML_UNICODE_WIDE)   /* XML_Char 4 bytes wide (UTF-32) */
# define EXPAT_NAME_LEN(s) (sizeof(s) >> 2)
#elif defined(XML_UNICODE)      /* XML_Char 2 bytes wide (UTF-16) */
# define EXPAT_NAME_LEN(s) (sizeof(s) >> 1)
#else                           /* XML_Char 1 byte wide (UTF-8) */
# define EXPAT_NAME_LEN(s) sizeof(s)
#endif

#define EXPAT_NAME_COMPARE(s1, s2)                      \
  (XMLChar_NCmp((s1), (s2), EXPAT_NAME_LEN(s2)) == 0 && \
   ((s1)[EXPAT_NAME_LEN(s2)] == EXPAT_NSSEP ||          \
    (s1)[EXPAT_NAME_LEN(s2)] == '\0'))

/* using a 64K buffer helps read performance for large documents */
#define EXPAT_BUFSIZ 65536

static PyObject *encoding_string;
static PyObject *uri_string;
static PyObject *stream_string;
static PyObject *empty_string;
static PyObject *asterisk_string;
static PyObject *space_string;
static PyObject *preserve_string;
static PyObject *default_string;
static PyObject *id_string;
static PyObject *xml_namespace_string;
static PyObject *xml_space_string;
static PyObject *xml_base_string;
static PyObject *xml_lang_string;
static PyObject *base_string;
static PyObject *lang_string;
static PyObject *unicode_space_char;

static PyObject *empty_event;
static PyObject *content_model_empty;
static PyObject *content_model_any;
static PyObject *content_model_pcdata;
static PyObject *attribute_decl_implied;
static PyObject *attribute_decl_required;
static PyObject *attribute_decl_fixed;

static PyObject *xinclude_hint_string;
static PyObject *external_entity_hint_string;
static PyObject *absolutize_function;
static PyObject *expat_library_error;

static PyObject *UriException;
static PyObject *UriException_RESOURCE_ERROR;

typedef struct {
  PyObject *validator;          /* ValidatorObject */
  PyObject *root_element;       /* PyUnicodeObject */
  PyObject *ids;                /* PyDictObject */
  PyObject *entities;           /* PyDictObject */
  PyObject *notations;          /* PyDictObject */
  PyObject *used_ids;           /* PyListObject */
  PyObject *used_elements;      /* PyDictObject */
  PyObject *used_notations;     /* PyDictObject */
} DTD;

typedef struct {
  int depth;

  /* exception info (for fallback) */
  PyObject *exception;
  PyObject *value;
  PyObject *traceback;
} XIncludeContext;

enum XPointerCriteriaType {
  ELEMENT_ID,           /* Shorthand and element() scheme */
  ELEMENT_COUNT,        /* element() and xpointer() scheme */
  ELEMENT_MATCH,        /* xpointer() scheme */
  ATTRIBUTE_MATCH,      /* xpointer() scheme */
};

typedef struct XPointerCriteria {
  struct XPointerCriteria *next;
  int matched;
  enum XPointerCriteriaType code;
  union {
    struct {
      XML_Char *identifier;
    } element_id;
    struct {
      int value;
      int counter;
    } element_count;
    struct {
      XML_Char *name;
    } element_match;
    struct {
      XML_Char *name;
      XML_Char *value;
    } attribute_match;
  } criterion;
} XPointerCriteria;

typedef struct {
  StateTable *state_table;
  StateId accepting;
  int depth;
} XPointerContext;

typedef struct Context {
  struct Context *next;
  XML_Parser parser;            /* the Expat parser */
  enum XML_Status status;       /* Expat parser sstatus */
  PyObject *source;             /* the Python InputSource object */
  PyObject *uri;                /* the URI of the current document */
  PyObject *stream;             /* the stream for the current document */
  PyObject *encoding;           /* the encoding of the stream */
  ExpatStatus (*parsing)(ExpatParser);
  unsigned long flags;          /* feature flags */
  PyObject *xml_base;
  PyObject *xml_lang;
  DTD *dtd;
  XIncludeContext *xinclude;    /* extra stuff for XInclude support */
  XPointerContext *xpointer;    /* extra stuff for XPointer support */
} Context;

/* This flag indicates that a particular context is used in an XInclude. */
#define EXPAT_FLAG_XINCLUDE             (1L<<0)

/* This flag indicates that XInclude fallback should be performed. */
#define EXPAT_FLAG_XI_FALLBACK_NEEDED   (1L<<1)

/* This flag indicates that processing is within an xi:fallback element. */
#define EXPAT_FLAG_XI_FALLBACK_BODY     (1L<<2)

/* */
#define EXPAT_FLAG_XI_FALLBACK_CONTENT  ( \
                                         EXPAT_FLAG_XI_FALLBACK_NEEDED | \
                                         EXPAT_FLAG_XI_FALLBACK_BODY | \
                                         0)

/* This flag marks that an xi:fallback element has been processed.
 * (Used for validating XInclude elements) */
#define EXPAT_FLAG_XI_FALLBACK_DONE     (1L<<3)

/* This flag indicates that an XPointer expression has been matched. */
#define EXPAT_FLAG_XPOINTER             (1L<<4)

/* This flag indicates that an XPointer expression has been matched. */
#define EXPAT_FLAG_XPOINTER_FOUND       (1L<<5)

/* This flag marks that certain infoset properties need to be adjusted for
 * a particular included entity. */
#define EXPAT_FLAG_INFOSET_FIXUP        (1L<<6)

/* This flag indicates that DTD validation should be performed. */
#define EXPAT_FLAG_VALIDATE             (1L<<7)

#define Expat_HasFlag(p,f) (((p)->context->flags & (f)) == (f))
#define Expat_SetFlag(p,f) ((p)->context->flags |= (f))
#define Expat_ClearFlag(p,f) ((p)->context->flags &= ~(f))
#define Expat_DumpFlags(p) do {                               \
  if (Expat_HasFlag((p), EXPAT_FLAG_XINCLUDE))                \
    fprintf(stderr, "      EXPAT_FLAG_XINCLUDE\n");           \
  if (Expat_HasFlag((p), EXPAT_FLAG_XI_FALLBACK_NEEDED))      \
    fprintf(stderr, "      EXPAT_FLAG_XI_FALLBACK_NEEDED\n"); \
  if (Expat_HasFlag((p), EXPAT_FLAG_XI_FALLBACK_BODY))        \
    fprintf(stderr, "      EXPAT_FLAG_XI_FALLBACK_BODY\n");   \
  if (Expat_HasFlag((p), EXPAT_FLAG_XI_FALLBACK_DONE))        \
    fprintf(stderr, "      EXPAT_FLAG_XI_FALLBACK_DONE\n");   \
  if (Expat_HasFlag((p), EXPAT_FLAG_XPOINTER))                \
    fprintf(stderr, "      EXPAT_FLAG_XPOINTER\n");           \
  if (Expat_HasFlag((p), EXPAT_FLAG_XPOINTER_FOUND))          \
    fprintf(stderr, "      EXPAT_FLAG_XPOINTER_FOUND\n");     \
  if (Expat_HasFlag((p), EXPAT_FLAG_INFOSET_FIXUP))           \
    fprintf(stderr, "      EXPAT_FLAG_INFOSET_FIXUP\n");      \
  if (Expat_HasFlag((p), EXPAT_FLAG_VALIDATE))                \
    fprintf(stderr, "      EXPAT_FLAG_VALIDATE\n");           \
} while (0)

enum NameTestType {
  ELEMENT_TEST,
  NAMESPACE_TEST,
  EXPANDED_NAME_TEST,
};

typedef struct {
  enum NameTestType test_type;
  PyObject *test_namespace;
  PyObject *test_name;
  PyObject *preserve_flag;
} WhitespaceRule;

typedef struct {
  int size;
  WhitespaceRule items[1];
} WhitespaceRules;

struct ExpatParserStruct {
  /* the value passed as the userState argument to callbacks */
  void *userState;

  /* our handlers */
  ExpatStartDocumentHandler start_document_handler;
  ExpatEndDocumentHandler end_document_handler;
  ExpatStartElementHandler start_element_handler;
  ExpatEndElementHandler end_element_handler;
  ExpatCharacterDataHandler character_data_handler;
  ExpatCharacterDataHandler ignorable_whitespace_handler;
  ExpatProcessingInstructionHandler processing_instruction_handler;
  ExpatCommentHandler comment_handler;
  ExpatStartNamespaceDeclHandler start_namespace_decl_handler;
  ExpatEndNamespaceDeclHandler end_namespace_decl_handler;
  ExpatStartDoctypeDeclHandler start_doctype_decl_handler;
  ExpatEndDoctypeDeclHandler end_doctype_decl_handler;
  ExpatElementDeclHandler element_decl_handler;
  ExpatAttributeDeclHandler attribute_decl_handler;
  ExpatInternalEntityDeclHandler internal_entity_decl_handler;
  ExpatExternalEntityDeclHandler external_entity_decl_handler;
  ExpatUnparsedEntityDeclHandler unparsed_entity_decl_handler;
  ExpatNotationDeclHandler notation_decl_handler;
  ExpatSkippedEntityHandler skipped_entity_handler;
  ExpatStartCdataSectionHandler start_cdata_section_handler;
  ExpatEndCdataSectionHandler end_cdata_section_handler;

  ExpatNotificationHandler warning_handler;
  ExpatNotificationHandler error_handler;
  ExpatNotificationHandler fatal_error_handler;

  /* caching members */
  HashTable *name_cache;        /* element name parts */
  HashTable *unicode_cache;     /* XMLChar to unicode mapping */
  ExpatAttribute *attrs;        /* reusable attributes list */
  int attrs_size;               /* allocated size of attributes list */

  /* character data buffering */
  XML_Char *buffer;             /* buffer used for accumulating characters */
  int buffer_size;              /* size of buffer (in XML_Char units) */
  int buffer_used;              /* buffer units in use */

  /* parsing options */
  int dtd_validation;           /* flag for DTD validation */
  int parameter_entity_parsing; /* flag for parameter entity parsing */
  int process_xincludes;        /* flag for XInclude processing */

  /* parsing data */
  Context *context;                  /* stack of parser contexts */
  WhitespaceRules *whitespace_rules; /* array of whitespace stripping rules */
  Stack *xml_base_stack;             /* current base URI w/xml:base support */
  Stack *xml_lang_stack;             /* XInclude language fixup (xml:lang) */
  Stack *xml_space_stack;            /* indicates xml:space='preserve' */
  Stack *preserve_whitespace_stack;  /* XSLT WS-stripping allowed */
};

/* Round up n to be a multiple of sz, where sz is a power of 2. */
#define ROUND_UP(n, sz) (((n) + ((sz) - 1)) & ~((sz) - 1))

/* 8 attributes per element should be plenty for most documents */
#define ATTR_BUFSIZ 8

/* 8K buffer should be plenty for most documents (it does resize if needed) */
#define XMLCHAR_BUFSIZ 8192

/** EXPAT callbacks *****************************************************/

static XML_Char expat_xml_namespace[] = {
  'h', 't', 't', 'p', ':', '/', '/', 'w', 'w', 'w', '.', 'w', '3', '.',
  'o', 'r', 'g', '/', 'X', 'M', 'L', '/', '1', '9', '9', '8', '/', 'n',
  'a', 'm', 'e', 's', 'p', 'a', 'c', 'e', EXPAT_NSSEP
};
static XML_Char expat_base_string[] = { 'b', 'a', 's', 'e' };
static XML_Char expat_lang_string[] = { 'l', 'a', 'n', 'g' };
static XML_Char expat_space_string[] = { 's', 'p', 'a', 'c', 'e' };
static XML_Char expat_id_string[] = { 'i', 'd' };
static XML_Char expat_preserve_string[] = {
  'p', 'r', 'e', 's', 'e', 'r', 'v', 'e', '\0' };
static XML_Char expat_default_string[] = {
  'd', 'e', 'f', 'a', 'u', 'l', 't', '\0' };

static void expat_StartElement(ExpatParser parser,
                               const XML_Char *name,
                               const XML_Char **atts);
static void expat_EndElement(ExpatParser parser,
                             const XML_Char *name);

static void expat_CharacterData(ExpatParser parser,
                                const XML_Char *s,
                                int len);

static void expat_ProcessingInstruction(ExpatParser parser,
                                        const XML_Char *target,
                                        const XML_Char *data);

static void expat_Comment(ExpatParser parser, const XML_Char *data);

static void expat_StartNamespaceDecl(ExpatParser parser,
                                     const XML_Char *prefix,
                                     const XML_Char *uri);

static void expat_EndNamespaceDecl(ExpatParser parser,
                                   const XML_Char *prefix);

static void expat_SkippedEntity(ExpatParser parser,
                                const XML_Char *entityName,
                                int is_parameter_entity);

static void expat_StartDoctypeDecl(ExpatParser parser,
                                   const XML_Char *name,
                                   const XML_Char *sysid,
                                   const XML_Char *pubid,
                                   int has_internal_subset);

static void expat_EndDoctypeDecl(ExpatParser parser);

static void expat_StartCdataSection(ExpatParser parser);

static void expat_EndCdataSection(ExpatParser parser);

static void expat_ElementDecl(ExpatParser parser,
                              const XML_Char *name,
                              XML_Content *content);

static void expat_AttlistDecl(ExpatParser parser,
                              const XML_Char *elname,
                              const XML_Char *attname,
                              const XML_Char *att_type,
                              const XML_Char *dflt,
                              int isrequired);

static void expat_EntityDecl(ExpatParser parser,
                             const XML_Char *entity_name,
                             int is_parameter_entity,
                             const XML_Char *value,
                             int value_length,
                             const XML_Char *base,
                             const XML_Char *systemId,
                             const XML_Char *publicId,
                             const XML_Char *notationName);

static void expat_NotationDecl(ExpatParser parser,
                               const XML_Char *notationName,
                               const XML_Char *base,
                               const XML_Char *systemId,
                               const XML_Char *publicId);

static int expat_ExternalEntityRef(XML_Parser parser,
                                   const XML_Char *context,
                                   const XML_Char *base,
                                   const XML_Char *systemId,
                                   const XML_Char *publicId);

static int expat_UnknownEncodingHandler(void *encodingHandlerData,
                                        const XML_Char *name,
                                        XML_Encoding *info);

static void clearExpatHandlers(ExpatParser parser);


/** Error Handling ****************************************************/


static void stopExpatParser(ExpatParser parser)
{
  parser->context->status = XML_StopParser(parser->context->parser, 0);

  /* Clear the handlers so as to prevent inadvertant processing for some
   * callbacks, which include:
   *   - the end element handler for empty elements when stopped in the
   *     start element handler,
   *   - end namespace declaration handler when stopped in the end element
   *     handler,
   * and possibly others.
   */
  clearExpatHandlers(parser);
}

#define Expat_FatalError(p) _Expat_FatalError((p), __FILE__, __LINE__)
static ExpatStatus _Expat_FatalError(ExpatParser parser, char *filename,
                                     int lineno)
{
  if (!PyErr_Occurred()) {
    PyErr_Format(PyExc_SystemError, "%s:%d: Error signaled without exception",
                 filename, lineno);
  }

  Debug_Print("FatalError signaled at %s:%d\n", filename, lineno);

  stopExpatParser(parser);

  return EXPAT_STATUS_ERROR;
}


static ExpatStatus Expat_ReportWarning(ExpatParser parser,
                                       const char *errorCode,
                                       char *argspec, ...)
{
  PyObject *kwords;
  PyObject *exception;
  ExpatStatus status;

  if (argspec != NULL) {
    va_list va;
    va_start(va, argspec);
    kwords = Py_VaBuildValue(argspec, va);
    va_end(va);
  } else {
    kwords = NULL;
  }

  exception = ReaderException_FromString(errorCode, parser->context->uri,
                                         Expat_GetLineNumber(parser),
                                         Expat_GetColumnNumber(parser),
                                         kwords);
  if (exception == NULL) {
    return Expat_FatalError(parser);
  }

  if (parser->warning_handler) {
    status = parser->warning_handler(parser->userState, exception);
  } else {
    status = EXPAT_STATUS_OK;
  }
  Py_DECREF(exception);

  return status;
}


static ExpatStatus Expat_ReportError(ExpatParser parser,
                                     const char *errorCode,
                                     char *argspec, ...)
{
  PyObject *kwords;
  PyObject *exception;
  ExpatStatus status;

  if (argspec != NULL) {
    va_list va;
    va_start(va, argspec);
    kwords = Py_VaBuildValue(argspec, va);
    va_end(va);
  } else {
    kwords = NULL;
  }

  exception = ReaderException_FromString(errorCode, parser->context->uri,
                                         Expat_GetLineNumber(parser),
                                         Expat_GetColumnNumber(parser),
                                         kwords);
  if (exception == NULL) {
    return Expat_FatalError(parser);
  }

  if (parser->error_handler) {
    status = parser->error_handler(parser->userState, exception);
  } else {
    PyErr_SetObject(ReaderException_Class, exception);
    status = Expat_FatalError(parser);
  }
  Py_DECREF(exception);

  return status;
}


static ExpatStatus Expat_ReportFatalError(ExpatParser parser,
                                          const char *errorCode,
                                          char *argspec, ...)
{
  PyObject *kwords;
  PyObject *exception;
  ExpatStatus status;

  if (argspec != NULL) {
    va_list va;
    va_start(va, argspec);
    kwords = Py_VaBuildValue(argspec, va);
    va_end(va);
  } else {
    kwords = NULL;
  }

  exception = ReaderException_FromString(errorCode, parser->context->uri,
                                         Expat_GetLineNumber(parser),
                                         Expat_GetColumnNumber(parser),
                                         kwords);
  if (exception == NULL) {
    return Expat_FatalError(parser);
  }

  if (parser->fatal_error_handler) {
    status = parser->fatal_error_handler(parser->userState, exception);
    /* terminate parsing regardless of what the handler did */
    stopExpatParser(parser);
  } else {
    PyErr_SetObject(ReaderException_Class, exception);
    status = Expat_FatalError(parser);
  }
  Py_DECREF(exception);

  return status;
}

/** DTD ***************************************************************/


static DTD *DTD_New(void)
{
  DTD *dtd;

  dtd = (DTD *) PyObject_MALLOC(sizeof(DTD));
  if (dtd == NULL) {
    PyErr_NoMemory();
  } else {
    dtd->validator = Validator_New();
    if (dtd->validator == NULL) {
      PyObject_FREE(dtd);
      return NULL;
    }
    dtd->ids = PyDict_New();
    if (dtd->ids == NULL) {
      Py_DECREF(dtd->validator);
      PyObject_FREE(dtd);
      return NULL;
    }
    dtd->entities = PyDict_New();
    if (dtd->entities == NULL) {
      Py_DECREF(dtd->ids);
      Py_DECREF(dtd->validator);
      PyObject_FREE(dtd);
      return NULL;
    }
    dtd->notations = PyDict_New();
    if (dtd->notations == NULL) {
      Py_DECREF(dtd->entities);
      Py_DECREF(dtd->ids);
      Py_DECREF(dtd->validator);
      PyObject_FREE(dtd);
      return NULL;
    }
    dtd->used_ids = PyList_New((Py_ssize_t)0);
    if (dtd->used_ids == NULL) {
      Py_DECREF(dtd->notations);
      Py_DECREF(dtd->entities);
      Py_DECREF(dtd->ids);
      Py_DECREF(dtd->validator);
      PyObject_FREE(dtd);
      return NULL;
    }
    dtd->used_elements = PyDict_New();
    if (dtd->used_elements == NULL) {
      Py_DECREF(dtd->used_ids);
      Py_DECREF(dtd->notations);
      Py_DECREF(dtd->entities);
      Py_DECREF(dtd->ids);
      Py_DECREF(dtd->validator);
      PyObject_FREE(dtd);
      return NULL;
    }
    dtd->used_notations = PyDict_New();
    if (dtd->used_notations == NULL) {
      Py_DECREF(dtd->used_elements);
      Py_DECREF(dtd->used_ids);
      Py_DECREF(dtd->notations);
      Py_DECREF(dtd->entities);
      Py_DECREF(dtd->ids);
      Py_DECREF(dtd->validator);
      PyObject_FREE(dtd);
      return NULL;
    }
    dtd->root_element = Py_None;
  }
  return dtd;
}


static void DTD_Del(DTD *dtd)
{
  Py_DECREF(dtd->used_notations);
  Py_DECREF(dtd->used_elements);
  Py_DECREF(dtd->used_ids);
  Py_DECREF(dtd->notations);
  Py_DECREF(dtd->entities);
  Py_DECREF(dtd->ids);
  Py_DECREF(dtd->validator);
  PyObject_FREE(dtd);
}


/** XIncludeContext ***************************************************/


static XIncludeContext *XIncludeContext_New(void)
{
  XIncludeContext *context;

  context = (XIncludeContext *) PyObject_MALLOC(sizeof(XIncludeContext));
  if (context == NULL) {
    PyErr_NoMemory();
  } else {
    memset(context, 0, sizeof(XIncludeContext));
  }

  Debug_Return(XIncludeContext_New, "%p", context);
  return context;
}


static void XIncludeContext_Del(XIncludeContext *context)
{
  Debug_FunctionCall(XIncludeContext_Del, context);
  Py_XDECREF(context->exception);
  Py_XDECREF(context->value);
  Py_XDECREF(context->traceback);
  PyObject_FREE(context);
}


/** XPointerCriteria **************************************************/


static XPointerCriteria *XPointerCriteria_New(void)
{
  XPointerCriteria *criteria;

  criteria = (XPointerCriteria *) PyObject_MALLOC(sizeof(XPointerCriteria));
  if (criteria == NULL) {
    PyErr_NoMemory();
  } else {
    memset(criteria, 0, sizeof(XPointerCriteria));
  }
  return criteria;
}


static void XPointerCriteria_Del(XPointerCriteria *criteria)
{
  if (criteria->next) {
    XPointerCriteria_Del(criteria->next);
    criteria->next = NULL;
  }
  switch (criteria->code) {
  case ELEMENT_ID:
    if (criteria->criterion.element_id.identifier) {
      free(criteria->criterion.element_id.identifier);
      criteria->criterion.element_id.identifier = NULL;
    }
    break;
  case ELEMENT_COUNT:
    break;
  case ELEMENT_MATCH:
    if (criteria->criterion.element_match.name) {
      free(criteria->criterion.element_match.name);
      criteria->criterion.element_match.name = NULL;
    }
    break;
  case ATTRIBUTE_MATCH:
    if (criteria->criterion.attribute_match.name) {
      free(criteria->criterion.attribute_match.name);
      criteria->criterion.attribute_match.name = NULL;
    }
    if (criteria->criterion.attribute_match.value) {
      free(criteria->criterion.attribute_match.value);
      criteria->criterion.attribute_match.value = NULL;
    }
    break;
  };
  PyObject_FREE(criteria);
}


/** XPointerContext ***************************************************/


static XPointerContext *XPointerContext_New(int size)
{
  XPointerContext *context;

  context = (XPointerContext *) PyObject_MALLOC(sizeof(XPointerContext));
  if (context == NULL) {
    PyErr_NoMemory();
  } else {
    memset(context, 0, sizeof(XPointerContext));
  }

  context->state_table = StateTable_New(size+1);
  if (context->state_table == NULL) {
    PyObject_FREE(context);
    return NULL;
  }

  Debug_Return(XPointerContext_New, "%p", context);
  return context;
}


static void XPointerContext_Del(XPointerContext *context)
{
  Debug_FunctionCall(XPointerContext_Del, context);
  if (context->state_table)
    StateTable_Del(context->state_table);

  PyObject_FREE(context);
}


/** Context ***********************************************************/

/* Context objects are used to store all the things that make up the current
 * parsing state.  They are needed to enable the suspend/resume functionality
 * of the Expat XML_Parser since finalization will not happen in a linear
 * fashion.
 */

static ExpatStatus continueParsing(ExpatParser parser);

static Context *Context_New(XML_Parser parser, PyObject *source)
{
  PyObject *uri, *stream, *encoding;
  Context *context;

  if (source == Py_None) {
    Py_INCREF(source);
    uri = Py_None;
    Py_INCREF(uri);
    stream = Py_None;
    Py_INCREF(stream);
    encoding = Py_None;
    Py_INCREF(encoding);
  } else {
    uri = PyObject_GetAttr(source, uri_string);
    if (uri == NULL) {
      return NULL;
    } else if (!PyUnicode_CheckExact(uri)) {
      /* Convert the URI to a unicode object */
      PyObject *temp = PyObject_Unicode(uri);
      Py_DECREF(uri);
      if (temp == NULL) {
        return NULL;
      }
      uri = temp;
    }

    stream = PyObject_GetAttr(source, stream_string);
    if (stream == NULL) {
      Py_DECREF(uri);
      return NULL;
    }

    encoding = PyObject_GetAttr(source, encoding_string);
    if (encoding == NULL) {
      Py_DECREF(uri);
      Py_DECREF(stream);
      return NULL;
    }
  }

  context = (Context *) PyObject_MALLOC(sizeof(Context));
  if (context == NULL) {
    Py_DECREF(uri);
    Py_DECREF(stream);
    Py_DECREF(encoding);
    PyErr_NoMemory();
    return NULL;
  }
  memset(context, 0, sizeof(Context));

  context->parser = parser;
  context->status = XML_STATUS_OK;
  context->source = source;
  context->uri = uri;
  context->stream = stream;
  context->encoding = encoding;

  context->parsing = continueParsing;

  return context;
}


/* Deallocate the Context object and its contents */
static void Context_Del(Context *context)
{
  if (context->parser)
    XML_ParserFree(context->parser);

  Py_DECREF(context->source);
  Py_DECREF(context->uri);
  Py_DECREF(context->stream);
  Py_DECREF(context->encoding);

  if (context->dtd) {
    DTD_Del(context->dtd);
  }

  if (context->xinclude) {
    XIncludeContext_Del(context->xinclude);
  }

  if (context->xpointer) {
    XPointerContext_Del(context->xpointer);
  }

  PyObject_FREE(context);
}


/* Create a new Context object and set it as the current parsing context */
static Context *beginContext(ExpatParser parser, XML_Parser xmlParser,
                             PyObject *source)
{
  Context *context;

  context = Context_New(xmlParser, source);

  Debug_Return(beginContext, "%p", context);

  if (context == NULL) return NULL;

  /* Make it the active context */
  context->next = parser->context;
  parser->context = context;

  /* propagate DTD parsing flag to the context */
  if (parser->dtd_validation) {
    Expat_SetFlag(parser, EXPAT_FLAG_VALIDATE);
  }

  /* Only perform infoset fixup for included entities */
  /* context->next == NULL when starting with a document */
  /* context->next->uri == Py_None when starting with a entity */
  if (context->next != NULL && context->next->uri != Py_None) {
    Expat_SetFlag(parser, EXPAT_FLAG_INFOSET_FIXUP);
    context->xml_base = Stack_PEEK(parser->xml_base_stack);
    context->xml_lang = Stack_PEEK(parser->xml_lang_stack);
  }

  /* Set initial values for the xml:* attributes */
  /* xml:base="<document-URI>" */
  if (Stack_Push(parser->xml_base_stack, context->uri) == -1) {
    Context_Del(context);
    return NULL;
  }
  /* xml:lang="" */
  if (Stack_Push(parser->xml_lang_stack, Py_None) == -1) {
    Context_Del(context);
    return NULL;
  }
  /* xml:space="default" */
  if (Stack_Push(parser->xml_space_stack, Py_False) == -1) {
    Context_Del(context);
    return NULL;
  }

  return context;
}


/* Switch to previous parsing context and deallocate the current one */
static void endContext(ExpatParser parser)
{
  Context *context;
  PyObject *temp;

  Debug_ParserFunctionCall(endContext, parser);

  context = parser->context;
  if (context) {
    temp = Stack_Pop(parser->xml_space_stack);
    Py_DECREF(temp);

    temp = Stack_Pop(parser->xml_lang_stack);
    Py_DECREF(temp);

    temp = Stack_Pop(parser->xml_base_stack);
    Py_DECREF(temp);

    parser->context = context->next;
    Context_Del(context);
  }
}


/* Deallocate ALL Contexts that exist */
static void destroyContexts(ExpatParser parser)
{
  Debug_ParserFunctionCall(destroyContexts, parser);

  while (parser->context) {
    endContext(parser);
  }
}


/** Whitespace Stripping **********************************************/


static void freeWhitespaceRules(WhitespaceRules *rules)
{
  int i;

  i = rules->size;
  while (--i >= 0) {
    WhitespaceRule rule = rules->items[i];
    switch (rule.test_type) {
    case EXPANDED_NAME_TEST:
      Py_DECREF(rule.test_name);
      /* fall through */
    case NAMESPACE_TEST:
      Py_DECREF(rule.test_namespace);
      /* fall through */
    case ELEMENT_TEST:
      break;
    }
  }
  PyObject_FREE(rules);
}


static WhitespaceRules *createWhitespaceRules(PyObject *stripElements)
{
  int i, length, nbytes;
  WhitespaceRules *rules;

  if (stripElements == NULL) {
    PyErr_BadInternalCall();
    return NULL;
  }

  stripElements = PySequence_Tuple(stripElements);
  if (stripElements == NULL) {
    return NULL;
  }

  length = PyTuple_GET_SIZE(stripElements);
  nbytes = SIZEOF_INT + (sizeof(WhitespaceRule) * length);
  if ((rules = (WhitespaceRules *) PyObject_MALLOC(nbytes)) == NULL) {
    PyErr_NoMemory();
    Py_DECREF(stripElements);
    return NULL;
  }
  rules->size = length;

  for (i = 0; i < length; i++) {
    PyObject *rule, *namespace_uri, *local_name;

    rule = PyTuple_GET_ITEM(stripElements, i);
    if (!PyTuple_Check(rule) || PyTuple_GET_SIZE(rule) != 3) {
      PyErr_SetString(PyExc_TypeError,
                      "stripElements must be a list of 3-item tuples");
      rules->size = i; /* prevent processing of items not yet initialized */
      freeWhitespaceRules(rules);
      Py_DECREF(stripElements);
      return NULL;
    }

    /* Each strip element specifies a NS and a local name,
       The localname can be a name or *
       If the localname is * then the NS could be None.
       ns:local is a complete match
       ns:* matches any element in the given namespace
       * matches any element.

       NOTE:  There are precedence rules to stripping as (according to XSLT)
       the matches should be treated as node tests.  The precedence is based
       on level of specificity.  This code assumes the list of white space
       rules has already been sorted by precedence.
    */
    namespace_uri = PyTuple_GET_ITEM(rule, 0);
    local_name = PyTuple_GET_ITEM(rule, 1);
    if (PyObject_RichCompareBool(local_name, asterisk_string, Py_EQ)) {
      if (namespace_uri == Py_None) {
        /* rule matches every element */
        rules->items[i].test_type = ELEMENT_TEST;
      } else {
        /* rule matches any element in the target namespace */
        rules->items[i].test_type = NAMESPACE_TEST;
        rules->items[i].test_namespace = namespace_uri;
        Py_INCREF(namespace_uri);
      }
    } else {
      rules->items[i].test_type = EXPANDED_NAME_TEST;
      rules->items[i].test_namespace = namespace_uri;
      rules->items[i].test_name = local_name;
      Py_INCREF(namespace_uri);
      Py_INCREF(local_name);
    }

    if (PyObject_IsTrue(PyTuple_GET_ITEM(rule, 2))) {
      rules->items[i].preserve_flag = Py_False;
    } else {
      rules->items[i].preserve_flag = Py_True;
    }
  }
  Py_DECREF(stripElements);

  return rules;
}


static PyObject *isWhitespacePreserving(ExpatParser parser,
                                        PyObject *namespaceURI,
                                        PyObject *localName)
{
  WhitespaceRules *rules = parser->whitespace_rules;
  int i;

  if (rules != NULL) {
    for (i = 0; i < rules->size; i++) {
      WhitespaceRule rule = rules->items[i];
      switch (rule.test_type) {
      case EXPANDED_NAME_TEST:
        if (PyObject_RichCompareBool(rule.test_name, localName, Py_NE))
          break;
        /* else, fall through for namespace-uri test */
      case NAMESPACE_TEST:
        if (PyObject_RichCompareBool(rule.test_namespace, namespaceURI, Py_NE))
          break;
        /* else, fall through to handle match */
      case ELEMENT_TEST:
        return rule.preserve_flag;
      }
    }
  }

  /* by default, all elements are whitespace-preserving */
  return Py_True;
}

/** Unicode Interning *************************************************/

/* Routines to minimize the number of PyUnicodeObjects that need to be
 * created for each XML_Char string returned from Expat.
 * This is a memory AND speed improvement.
 */

#define LOOKUP_UNICODE(tbl,s,n) HashTable_Lookup((tbl), (s), (n), NULL, NULL)

#define makeUnicodeSize(p,s,n) LOOKUP_UNICODE((p)->unicode_cache, (s), (n))

#define makeUnicode(p, xc) makeUnicodeSize((p), (xc), XMLChar_Len(xc))

/* If the name from the document had a prefix, then expat name is:
 *   namespace-uri + sep + localName + sep + prefix,
 * otherwise if there is a default namespace:
 *   namespace-uri + sep + localName
 * lastly, it could just be:
 *   localName
 */
static PyObject *splitExpatName(const XML_Char *name, Py_ssize_t len, void *table)
{
  PyObject *parts, *namespaceURI, *localName, *qualifiedName;
  int i, j;

  parts = PyTuple_New((Py_ssize_t)3);
  if (parts == NULL) return NULL;

  /* scan for beginning of localName */
  for (i = 0; i < len && name[i] != EXPAT_NSSEP; i++);

  if (i == len) {
    /* just a localName, set namespace and prefix to None. */
    localName = LOOKUP_UNICODE(table, name, len);
    if (localName == NULL) {
      Py_DECREF(parts);
      return NULL;
    }
    Py_INCREF(Py_None);
    PyTuple_SET_ITEM(parts, 0, Py_None);        /* namespaceURI */
    Py_INCREF(localName);
    PyTuple_SET_ITEM(parts, 1, localName);      /* localName */
    Py_INCREF(localName);
    PyTuple_SET_ITEM(parts, 2, localName);      /* qualifiedName */
    return parts;
  }

  /* found a namespace uri */
  if ((namespaceURI = LOOKUP_UNICODE(table, name, i)) == NULL) {
    Py_DECREF(parts);
    return NULL;
  }
  i++;

  for (j = i; j < len && name[j] != EXPAT_NSSEP; j++);

  if ((localName = LOOKUP_UNICODE(table, name + i, j - i)) == NULL) {
    Py_DECREF(parts);
    return NULL;
  }
  j++;

  if (j < len) {
    /* a prefix is given as well, build the qualifiedName */
    if ((qualifiedName = PyUnicode_FromUnicode(NULL, len - i)) == NULL) {
      Py_DECREF(parts);
      return NULL;
    }


    /* copy the prefix to the qualifiedName string */
    len -= j;
    Py_UNICODE_COPY(PyUnicode_AS_UNICODE(qualifiedName), name + j, len);

    /* add the ':' separator */
    PyUnicode_AS_UNICODE(qualifiedName)[len++] = (Py_UNICODE) ':';

    /* add the localName after the ':' to finish the qualifiedName */
    Py_UNICODE_COPY(PyUnicode_AS_UNICODE(qualifiedName) + len,
                    PyUnicode_AS_UNICODE(localName),
                    PyUnicode_GET_SIZE(localName));

  } else {
    /* default namespace, re-use the localName */
    Py_INCREF(localName);
    qualifiedName = localName;
  }

  /* Only qualifiedName is a new reference, the rest are borrowed */
  Py_INCREF(namespaceURI);
  PyTuple_SET_ITEM(parts, 0, namespaceURI);
  Py_INCREF(localName);
  PyTuple_SET_ITEM(parts, 1, localName);
  PyTuple_SET_ITEM(parts, 2, qualifiedName);

  return parts;
}

static ExpatExpandedName *makeExpandedName(ExpatParser parser,
                                           const XML_Char *name)
{
  PyObject *parts;
  parts = HashTable_Lookup(parser->name_cache, name, XMLChar_Len(name),
                           splitExpatName, parser->unicode_cache);
  if (parts == NULL) return NULL;
  return (ExpatExpandedName *)&PyTuple_GET_ITEM(parts, 0);
}

/** Character Data Buffering ******************************************/

/* These routines are used to ensure that all character data is reported
 * as a single logic chunk to the application regardless of how many chunks
 * Expat returns.
 */

static ExpatStatus resizeCharacterBuffer(ExpatParser parser, int new_size)
{
  XML_Char *buffer = parser->buffer;
  new_size = ROUND_UP(new_size, XMLCHAR_BUFSIZ);
  if (PyMem_Resize(buffer, XML_Char, new_size) == NULL) {
    PyErr_NoMemory();
    return EXPAT_STATUS_ERROR;
  }
  parser->buffer = buffer;
  parser->buffer_size = new_size;
  return EXPAT_STATUS_OK;
}


static ExpatStatus writeCharacterBuffer(ExpatParser parser,
                                        const XML_Char *data, int len)
{
  XML_Char *buffer;
  register int new_len = parser->buffer_used + len;
  register int size = parser->buffer_size;

  if (len == 0) return EXPAT_STATUS_OK;

  if (new_len > size) {
    if (resizeCharacterBuffer(parser, new_len) == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
  }
  buffer = parser->buffer;

  /* store the new data */
  if (len == 1)
    buffer[parser->buffer_used] = data[0];
  else
    memcpy(buffer + parser->buffer_used, data, len * sizeof(XML_Char));
  parser->buffer_used = new_len;
  return EXPAT_STATUS_OK;
}

#define writeCharacterBufferString(p,s) \
  writeCharacterBuffer((p), (s), XMLChar_Len(s))

static ExpatStatus writeCharacterBufferChar(ExpatParser parser, XML_Char c)
{
  if (parser->buffer_used >= parser->buffer_size) {
    int new_size = parser->buffer_size + 1;
    if (resizeCharacterBuffer(parser, new_size) == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
  }
  parser->buffer[parser->buffer_used++] = c;
  return EXPAT_STATUS_OK;
}


static ExpatStatus flushCharacterBuffer(ExpatParser parser)
{
  const XML_Char *p = parser->buffer;
  register int len = parser->buffer_used;
  register int i;
  PyObject *data, *element;

  Debug_ParserFunctionCall(flushCharacterBuffer, parser);

  if (len == 0) return EXPAT_STATUS_OK;

  /* Mark buffer as empty */
  parser->buffer_used = 0;

  /* intern strings that are only whitespace */
  for (i = 0; i < len; i++) {
    XML_Char ch = p[i];
    if (!((ch == 0x09) || (ch == 0x0A) || (ch == 0x0D) || (ch == 0x20))) {
      break;
    }
  }
  if (i == len) {
    /* Only bother creating a PyUnicodeObject from the data if we are
     * going to be preserving it.
     */
    if (Stack_PEEK(parser->preserve_whitespace_stack) == Py_True) {
      /* Intern the all-whitespace data as it will be helpful
       * for those "pretty printed" XML documents.
       */
      data = makeUnicodeSize(parser, parser->buffer, len);
      if (data == NULL) return Expat_FatalError(parser);

      if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
        DTD *dtd = parser->context->dtd;

        switch (Validator_ValidateEvent(dtd->validator,
                                        content_model_pcdata)) {
        case 1:
          parser->character_data_handler(parser->userState, data);
          break;
        case 0:
          switch (Validator_CheckEvent(dtd->validator, empty_event)) {
          case 0:
            break;
          case 1:
            element = Validator_GetCurrentElementType(dtd->validator);
            element = ElementType_GET_NAME(element);
            if (Expat_ReportError(parser, "INVALID_TEXT", "{sO}",
                                  "element", element) == EXPAT_STATUS_OK) {
              break;
            }
            /* fall through */
          default:
            return Expat_FatalError(parser);
          }
          if (parser->ignorable_whitespace_handler) {
            parser->ignorable_whitespace_handler(parser->userState, data);
          } else {
            parser->character_data_handler(parser->userState, data);
          }
          break;
        default:
          return Expat_FatalError(parser);
        }
      } else {
        parser->character_data_handler(parser->userState, data);
      }
    } else if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
      DTD *dtd = parser->context->dtd;
      switch (Validator_CheckEvent(dtd->validator, empty_event)) {
      case 0:
        break;
      case 1:
        element = Validator_GetCurrentElementType(dtd->validator);
        element = ElementType_GET_NAME(element);
        if (Expat_ReportError(parser, "INVALID_TEXT", "{sO}",
                              "element", element) == EXPAT_STATUS_OK) {
          break;
        }
        /* fall through */
      default:
        return Expat_FatalError(parser);
      }
    }
  } else {
    /* Normal character data usually doesn't repeat so don't bother with
     * interning it.
     */

    data = Unicode_FromXMLCharAndSize(parser->buffer, len);
    if (data == NULL) return Expat_FatalError(parser);

    if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
      DTD *dtd = parser->context->dtd;

      switch (Validator_ValidateEvent(dtd->validator,
                                      content_model_pcdata)) {
      case 1:
        parser->character_data_handler(parser->userState, data);
        break;
      case 0:
        element = Validator_GetCurrentElementType(dtd->validator);
        element = ElementType_GET_NAME(element);
        if (Expat_ReportError(parser, "INVALID_TEXT", "{sO}",
                              "element", element) == EXPAT_STATUS_OK) {
          break;
        }
        /* fall through */
      default:
        Py_DECREF(data);
        return Expat_FatalError(parser);
      }
    } else {
      parser->character_data_handler(parser->userState, data);
    }
    Py_DECREF(data);
  }

  return parser->context->status;
}

#define FLUSH_CHARACTER_BUFFER(parser)                                 \
  if ((parser)->buffer_used) {                                         \
    if (flushCharacterBuffer(parser) == EXPAT_STATUS_ERROR) return;    \
  }

/** Parsing routines **************************************************/


static void copyExpatHandlers(ExpatParser parser, XML_Parser new_parser)
{
  if (parser->start_element_handler)
    XML_SetStartElementHandler(new_parser,
        (XML_StartElementHandler) expat_StartElement);

  if (parser->end_element_handler)
    XML_SetEndElementHandler(new_parser,
        (XML_EndElementHandler) expat_EndElement);

  if (parser->character_data_handler
      || parser->ignorable_whitespace_handler)
    XML_SetCharacterDataHandler(new_parser,
        (XML_CharacterDataHandler) expat_CharacterData);

  if (parser->processing_instruction_handler)
    XML_SetProcessingInstructionHandler(new_parser,
        (XML_ProcessingInstructionHandler) expat_ProcessingInstruction);

  if (parser->comment_handler)
    XML_SetCommentHandler(new_parser,
        (XML_CommentHandler) expat_Comment);

  if (parser->start_namespace_decl_handler)
    XML_SetStartNamespaceDeclHandler(new_parser,
        (XML_StartNamespaceDeclHandler) expat_StartNamespaceDecl);

  if (parser->end_namespace_decl_handler)
    XML_SetEndNamespaceDeclHandler(new_parser,
        (XML_EndNamespaceDeclHandler) expat_EndNamespaceDecl);

  if (parser->dtd_validation
      || parser->skipped_entity_handler)
    XML_SetSkippedEntityHandler(new_parser,
        (XML_SkippedEntityHandler) expat_SkippedEntity);

  XML_SetDoctypeDeclHandler(new_parser,
        (XML_StartDoctypeDeclHandler) expat_StartDoctypeDecl,
        (XML_EndDoctypeDeclHandler) expat_EndDoctypeDecl);

  if (parser->start_cdata_section_handler)
    XML_SetStartCdataSectionHandler(new_parser,
        (XML_StartCdataSectionHandler) expat_StartCdataSection);

  if (parser->end_cdata_section_handler)
    XML_SetEndCdataSectionHandler(new_parser,
        (XML_EndCdataSectionHandler) expat_EndCdataSection);

  if (parser->dtd_validation
      || parser->element_decl_handler)
    XML_SetElementDeclHandler(new_parser,
        (XML_ElementDeclHandler) expat_ElementDecl);

  if (parser->dtd_validation
      || parser->attribute_decl_handler)
    XML_SetAttlistDeclHandler(new_parser,
        (XML_AttlistDeclHandler) expat_AttlistDecl);

  if (parser->dtd_validation
      || parser->internal_entity_decl_handler
      || parser->external_entity_decl_handler
      || parser->unparsed_entity_decl_handler)
    XML_SetEntityDeclHandler(new_parser,
        (XML_EntityDeclHandler) expat_EntityDecl);

  if (parser->dtd_validation
      || parser->notation_decl_handler)
    XML_SetNotationDeclHandler(new_parser,
        (XML_NotationDeclHandler) expat_NotationDecl);

  XML_SetExternalEntityRefHandler(new_parser, expat_ExternalEntityRef);
}

#define setExpatHandlers(parser) \
  copyExpatHandlers(parser, parser->context->parser)


static void setExpatSubsetHandlers(ExpatParser parser)
{
  XML_SetProcessingInstructionHandler(parser->context->parser, NULL);
  XML_SetCommentHandler(parser->context->parser, NULL);
}


static void clearExpatHandlers(ExpatParser parser)
{
  XML_SetElementHandler(parser->context->parser, NULL, NULL);
  XML_SetCharacterDataHandler(parser->context->parser, NULL);
  XML_SetProcessingInstructionHandler(parser->context->parser, NULL);
  XML_SetCommentHandler(parser->context->parser, NULL);
  XML_SetNamespaceDeclHandler(parser->context->parser, NULL, NULL);
  XML_SetSkippedEntityHandler(parser->context->parser, NULL);
  XML_SetDoctypeDeclHandler(parser->context->parser, NULL, NULL);
  XML_SetElementDeclHandler(parser->context->parser, NULL);
  XML_SetAttlistDeclHandler(parser->context->parser, NULL);
  XML_SetEntityDeclHandler(parser->context->parser, NULL);
  XML_SetNotationDeclHandler(parser->context->parser, NULL);
  XML_SetExternalEntityRefHandler(parser->context->parser, NULL);
}


static XML_Memory_Handling_Suite expat_memsuite = {
  malloc, realloc, free
};

static XML_Parser createExpatParser(ExpatParser parser)
{
  static const XML_Char sep[] = { EXPAT_NSSEP, '\0' };

  XML_Parser new_parser = XML_ParserCreate_MM(NULL, &expat_memsuite, sep);
  if (new_parser == NULL) {
    PyErr_NoMemory();
    return NULL;
  }

  /* enable parsing of parameter entities if requested */
  if (parser->dtd_validation) {
    XML_SetParamEntityParsing(new_parser, XML_PARAM_ENTITY_PARSING_ALWAYS);
  } else if (parser->parameter_entity_parsing) {
    XML_SetParamEntityParsing(new_parser,
                              XML_PARAM_ENTITY_PARSING_UNLESS_STANDALONE);
  }

  /* enable prefix information in names (URI + sep + local + sep + prefix) */
  XML_SetReturnNSTriplet(new_parser, 1);

  /* enable use of all encodings available with Python */
  XML_SetUnknownEncodingHandler(new_parser, expat_UnknownEncodingHandler,
                                NULL);

  XML_SetUserData(new_parser, (void *)parser);

  return new_parser;
}


/* optimized routine for reading from real file objects */
static int read_file(PyObject *file, char *buffer, int length)
{
  FILE *fp = (FILE *) file;
  size_t bytes_read;

  Py_BEGIN_ALLOW_THREADS;
  errno = 0;
  bytes_read = fread(buffer, sizeof(char), length, fp);
  Py_END_ALLOW_THREADS;

  if (bytes_read == 0 && ferror(fp)) {
    PyErr_SetFromErrno(PyExc_IOError);
    clearerr(fp);
    return -1;
  }

  return bytes_read;
}


/* optimized routine for reading from cStringIO objects */
static int read_stringio(PyObject *stream, char *buffer, int length)
{
  char *data;
  int bytes_read;

  bytes_read = PycStringIO->cread(stream, &data, length);

  if (bytes_read > 0)
    memcpy(buffer, data, bytes_read);

  return bytes_read;
}


/* generic routine for reading from any Python object */
static int read_object(PyObject *stream, char *buffer, int length)
{
  PyObject *str;
  char *data;
  Py_ssize_t bytes_read = -1;

  str = PyObject_CallMethod(stream, "read", "i", length);
  if (str == NULL)
    return -1;

  /* bytes_read will be unmodified on error, so OK to ignore result */
  PyString_AsStringAndSize(str, &data, &bytes_read);

  if (bytes_read > 0)
    memcpy(buffer, data, bytes_read);

  Py_DECREF(str);
  return bytes_read;
}


/* Common handling of Expat error condition. */
static void processExpatError(ExpatParser parser)
{
  int error_code = XML_GetErrorCode(parser->context->parser);
  PyObject *exception;
  int line_number, column_number;

  switch (error_code) {
  case XML_ERROR_NONE:
    /* error handler called during non-error condition */
    PyErr_BadInternalCall();
    parser->context->status = XML_StopParser(parser->context->parser, 0);
    break;
  case XML_ERROR_NO_MEMORY:
    PyErr_NoMemory();
    break;
  case XML_ERROR_UNEXPECTED_STATE:
  case XML_ERROR_FEATURE_REQUIRES_XML_DTD:
  case XML_ERROR_CANT_CHANGE_FEATURE_ONCE_PARSING:
  case XML_ERROR_SUSPENDED:
  case XML_ERROR_FINISHED:
  case XML_ERROR_SUSPEND_PE:
    /* programming logic is not correct (developer error) */
    PyErr_SetString(PyExc_SystemError, XML_ErrorString(error_code));
    break;
  case XML_ERROR_NOT_SUSPENDED:
    /* user error */
    PyErr_SetString(PyExc_RuntimeError, XML_ErrorString(error_code));
    break;
  case XML_ERROR_ABORTED:
    /* XML_StopParser called (an exception should already be set) */
    if (!PyErr_Occurred()) {
      PyErr_SetString(PyExc_SystemError,
                      "parsing terminated without exception");
    }
    break;
  default:
    line_number = XML_GetErrorLineNumber(parser->context->parser);
    column_number = XML_GetErrorColumnNumber(parser->context->parser);

    Debug_Print("-- Parsing error ------------ \n"          \
                "Expat error: %s\n"                         \
                "Expat error code: %d\n",
                XML_ErrorString(error_code), error_code);

    exception = ReaderException_FromInt(error_code, parser->context->uri,
                                        line_number, column_number, NULL);
    if (parser->fatal_error_handler) {
      parser->fatal_error_handler(parser->userState, exception);
      /* terminate parsing regardless of what the handler did */
      stopExpatParser(parser);
    } else {
      PyErr_SetObject(ReaderException_Class, exception);
      Expat_FatalError(parser);
    }
    Py_DECREF(exception);
  }
}


/* The core of the parsing routines.  Process the input source until parsing
 * is finished (OK or ERROR) or suspended (SUSPENDED).
 */
static ExpatStatus continueParsing(ExpatParser parser)
{
  int (*read_func)(PyObject *, char *, int);
  PyObject *read_arg;
  enum XML_Status status;
  int bytes_read;

  Debug_ParserFunctionCall(continueParsing, parser);

  read_arg = parser->context->stream;
  if (PyFile_Check(read_arg)) {
    read_func = read_file;
    read_arg = (PyObject *) PyFile_AsFile(read_arg);
  }
  else if (PycStringIO_InputCheck(read_arg)) {
    read_func = read_stringio;
  } else {
    read_func = read_object;
  }

  do {
    XML_ParsingStatus parsing_status;
    void *buffer = XML_GetBuffer(parser->context->parser, EXPAT_BUFSIZ);
    if (buffer == NULL) {
      processExpatError(parser);
      Debug_ReturnStatus(continueParsing, EXPAT_STATUS_ERROR);
      return EXPAT_STATUS_ERROR;
    }

    bytes_read = read_func(read_arg, (char *)buffer, EXPAT_BUFSIZ);
    if (bytes_read < 0) {
      Debug_ReturnStatus(continueParsing, EXPAT_STATUS_ERROR);
      return EXPAT_STATUS_ERROR;
    }

    Debug_ParserFunctionCall(XML_ParseBuffer, parser);

    status = XML_ParseBuffer(parser->context->parser, bytes_read,
                             bytes_read == 0);

    Debug_ReturnStatus(XML_ParseBuffer, status);

    switch (status) {
    case XML_STATUS_OK:
      /* determine if parsing was stopped prematurely */
      XML_GetParsingStatus(parser->context->parser, &parsing_status);
      if (parsing_status.parsing == XML_FINISHED && bytes_read > 0) {
        Debug_ReturnStatus(continueParsing, EXPAT_STATUS_ERROR);
        return EXPAT_STATUS_ERROR;
      }
      break;
    case XML_STATUS_ERROR:
      processExpatError(parser);
      Debug_ReturnStatus(continueParsing, EXPAT_STATUS_ERROR);
      return EXPAT_STATUS_ERROR;
    case XML_STATUS_SUSPENDED:
      Debug_ReturnStatus(continueParsing, EXPAT_STATUS_SUSPENDED);
      return EXPAT_STATUS_SUSPENDED;
    }
  } while (bytes_read > 0);

  Debug_ReturnStatus(continueParsing, EXPAT_STATUS_OK);
  return EXPAT_STATUS_OK;
}


/* The entry point for parsing any entity, document or otherwise. */
static ExpatStatus doParse(ExpatParser parser)
{
  XML_Char *encoding, *base;
  enum XML_Status xml_status;
  ExpatStatus status;

  Debug_ParserFunctionCall(doParse, parser);

  /* sanity check */
  if (parser->context == NULL) {
    PyErr_BadInternalCall();
    return EXPAT_STATUS_ERROR;
  }

  /* Set externally defined encoding, if defined */
  if (parser->context->encoding != Py_None) {
    encoding = XMLChar_FromObject(parser->context->encoding);
    if (encoding == NULL) {
      return EXPAT_STATUS_ERROR;
    }
    xml_status = XML_SetEncoding(parser->context->parser, encoding);
    free(encoding);
    if (xml_status != XML_STATUS_OK) {
      PyErr_NoMemory();
      return EXPAT_STATUS_ERROR;
    }
  }

  /* Set the base URI for the stream */
  base = XMLChar_FromObject(parser->context->uri);
  if (base == NULL) {
    return EXPAT_STATUS_ERROR;
  }
  xml_status = XML_SetBase(parser->context->parser, base);
  free(base);
  if (xml_status != XML_STATUS_OK) {
    PyErr_NoMemory();
    return EXPAT_STATUS_ERROR;
  }

  status = continueParsing(parser);

  Debug_ReturnStatus(doParse, status);
  return status;
}


/* The entry point for parsing if parsing has been previously suspended. */
static ExpatStatus resumeParsing(ExpatParser parser)
{
  enum XML_Status status;
  XML_ParsingStatus parsing_status;

  Debug_ParserFunctionCall(resumeParsing, parser);

  status = XML_ResumeParser(parser->context->parser);

  switch (status) {
  case XML_STATUS_OK:
    /* determine if parsing was suspended in the final buffer */
    XML_GetParsingStatus(parser->context->parser, &parsing_status);
    if (parsing_status.finalBuffer) {
      /* restore previous context */
      endContext(parser);
      /* if last context, exit now */
      if (parser->context == NULL) {
        return EXPAT_STATUS_OK;
      }
    }
    break;
  case XML_STATUS_ERROR:
    processExpatError(parser);
    return EXPAT_STATUS_ERROR;
  case XML_STATUS_SUSPENDED:
    return EXPAT_STATUS_SUSPENDED;
  }

  return parser->context->parsing(parser);
}


/* Defined here to allow for compiler inlining */
static ExpatStatus processXmlAttributes(ExpatParser parser,
                                        const XML_Char **atts,
                                        const XML_Char **xml_id)
{
  PyObject *xml_base, *xml_lang, *xml_space_preserve, *value;
  const XML_Char **ppattr;

  /* get current xml:* settings */
  xml_base = Stack_PEEK(parser->xml_base_stack);
  xml_lang = Stack_PEEK(parser->xml_lang_stack);
  xml_space_preserve = Stack_PEEK(parser->xml_space_stack);

  for (ppattr = atts; *ppattr; ppattr += 2) {
    /* check for xml:* attributes */
    if (XMLChar_NCmp(ppattr[0], expat_xml_namespace,
                     EXPAT_NAME_LEN(expat_xml_namespace)) == 0) {
      const XML_Char *xml_attr_name =
        ppattr[0] + EXPAT_NAME_LEN(expat_xml_namespace);

      /* borrowed reference */
      if ((value = makeUnicode(parser, ppattr[1])) == NULL)
        return Expat_FatalError(parser);

      /* check for xml:base */
      if (EXPAT_NAME_COMPARE(xml_attr_name, expat_base_string)) {
        xml_base = value;
      }
      /* check for xml:lang */
      else if (EXPAT_NAME_COMPARE(xml_attr_name, expat_lang_string)) {
        xml_lang = value;
      }
      /* check for xml:space */
      else if (EXPAT_NAME_COMPARE(xml_attr_name, expat_space_string)) {
        if (XMLChar_Cmp(ppattr[1], expat_preserve_string) == 0)
          xml_space_preserve = Py_True;
        else if (XMLChar_Cmp(ppattr[1], expat_default_string) == 0)
          xml_space_preserve = Py_False;
      }
      /* check for xml:id */
      else if (EXPAT_NAME_COMPARE(xml_attr_name, expat_id_string)) {
        /* normalize the value as if an ID type */
        const XML_Char *src = ppattr[1];
        XML_Char *dst = (XML_Char *)src;

        dst = (XML_Char *)(src = *xml_id = ppattr[1]);

        /* skip leading spaces and collapse multiple spaces into one */
        while (src[0]) {
          XML_Char ch = *src++;
          if (ch == 0x20 && (dst == *xml_id || dst[-1] == 0x20)) continue;
          *dst++ = ch;
        }
        /* remove trailing space, if any */
        if (dst > *xml_id && dst[-1] == 0x20) dst--;
        *dst = '\0';
      }
    }
  }

  /* save updated xml:* settings */
  Stack_Push(parser->xml_base_stack, xml_base);
  Stack_Push(parser->xml_lang_stack, xml_lang);
  Stack_Push(parser->xml_space_stack, xml_space_preserve);

  return EXPAT_STATUS_OK;
}

static void popElementState(ExpatParser parser)
{
  PyObject *temp;

  temp = Stack_Pop(parser->xml_base_stack);
  Py_DECREF(temp);

  temp = Stack_Pop(parser->xml_lang_stack);
  Py_DECREF(temp);

  temp = Stack_Pop(parser->xml_space_stack);
  Py_DECREF(temp);

  temp = Stack_Pop(parser->preserve_whitespace_stack);
  Py_DECREF(temp);
}

static ExpatStatus validateEndElement(ExpatParser parser,
                                      const XML_Char *name)
{
  ExpatExpandedName *expanded_name;

  switch (Validator_EndElement(parser->context->dtd->validator)) {
  case 0:
    expanded_name = makeExpandedName(parser, name);
    if (expanded_name == NULL) {
      return Expat_FatalError(parser);
    }
    return Expat_ReportError(parser, "INCOMPLETE_ELEMENT", "{sO}",
                             "element", expanded_name->qualifiedName);
  case 1:
    return EXPAT_STATUS_OK;
  default:
    return Expat_FatalError(parser);
  }
}

/** XInclude Processing ***********************************************/


/* Expat callback handlers */
static void xinclude_StartElement(ExpatParser parser,
                                  const XML_Char *name,
                                  const XML_Char **atts);

static void xinclude_EndElement(ExpatParser parser,
                                const XML_Char *name);

static void xpointer_StartElement(ExpatParser parser,
                                  const XML_Char *name,
                                  const XML_Char **atts);

static void xpointer_EndElement(ExpatParser parser,
                                const XML_Char *name);


static int expat_name_compare(const XML_Char *universal_name,
                              const XML_Char *expat_name)
{
  size_t len = XMLChar_Len(universal_name);
  if (len == 0) return 1; /* work around bug in wcsncmp */
  if (XMLChar_NCmp(universal_name, expat_name, len)) return 0;
  return (expat_name[len] == '\0' || expat_name[len] == EXPAT_NSSEP);
}

/* Expat handler for XPointer processing */
static void xpointer_StartElement(ExpatParser parser, const XML_Char *name,
                                  const XML_Char **atts)
{
  XPointerContext *xpointer = parser->context->xpointer;
  const XML_Char **ppattr;

#if defined(DEBUG_CALLBACKS) || defined(DEBUG_XINCLUDE)
  fprintf(stderr, "::: xpointer_StartElement(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ", atts={");
  for (ppattr = atts; *ppattr;) {
    if (ppattr != atts) {
      fprintf(stderr, ", ");
    }
    XMLChar_Print(stderr, *ppattr++);
  }
  fprintf(stderr, "})\n");
#endif
#if defined(DEBUG_XINCLUDE)
  Expat_DumpFlags(parser);
#endif

  if (Expat_HasFlag(parser, EXPAT_FLAG_XPOINTER_FOUND)) {
    expat_StartElement(parser, name, atts);
    /* Only update the depth counter if a non-XInclude element is handled as
       a corresponding end element callback will *not* be performed. */
    if (!Expat_HasFlag(parser, EXPAT_FLAG_XINCLUDE)) {
      xpointer->depth++;
    }
  } else {
    XPointerCriteria *criteria_list, *criteria;
    const XML_Char *xml_id = NULL;
    int matched = 0;

    if (processXmlAttributes(parser, atts, &xml_id) == EXPAT_STATUS_ERROR)
      return;

    /* Get the criteria list for the current state */
    criteria_list = criteria = (XPointerCriteria *)
      StateTable_GetStateData(xpointer->state_table,
                              StateTable_GetState(xpointer->state_table));

    do {
      switch (criteria->code) {
      case ELEMENT_ID: {
        /* If there is an xml:id, then use it, otherwise try to use the
         * information from the DTD. */
        const XML_Char *id = xml_id;
        if (id == NULL) {
          int index = XML_GetIdAttributeIndex(parser->context->parser);
          if (index >= 0) {
            id = atts[index + 1];
          }
        }
        if (id != NULL) {
          matched = !XMLChar_Cmp(criteria->criterion.element_id.identifier,
                                 id);
        }
        break;
      }
      case ELEMENT_COUNT:
        matched = (criteria->criterion.element_count.value ==
                   criteria->criterion.element_count.counter);
        criteria->criterion.element_count.counter++;
        break;
      case ELEMENT_MATCH:
        matched = expat_name_compare(criteria->criterion.element_match.name,
                                     name);
        break;
      case ATTRIBUTE_MATCH:
        matched = 0;
        for (ppattr = atts; *ppattr; ppattr += 2) {
          if (expat_name_compare(criteria->criterion.attribute_match.name,
                                 ppattr[0])) {
            matched = !XMLChar_Cmp(criteria->criterion.attribute_match.value,
                                   ppattr[1]);

            break;
          }
        }
        break;
      };
    } while (matched && ((criteria = criteria->next) != NULL));

    criteria_list->matched = matched;

    if (matched) {
      /* If the end of the criteria are reached, start processing */
      StateId state = StateTable_Transit(xpointer->state_table,
                                         XPTR_MATCH_EVENT);
      if (state == xpointer->accepting) {
        /* set XPointer progressing flag */
#ifdef DEBUG_XINCLUDE
        fprintf(stderr, "      Setting EXPAT_FLAG_XPOINTER_FOUND\n");
#endif
        Expat_SetFlag(parser, EXPAT_FLAG_XPOINTER_FOUND);
        Expat_SetFlag(parser, EXPAT_FLAG_INFOSET_FIXUP);

        /* Handle this element */
        expat_StartElement(parser, name, atts);
        xpointer->depth = 1;

        /* setup remaining "normal" content handlers */
        setExpatHandlers(parser);
        XML_SetElementHandler(parser->context->parser,
                              (XML_StartElementHandler) xpointer_StartElement,
                              (XML_EndElementHandler) xpointer_EndElement);
      }
    }
  }
}


static void xpointer_EndElement(ExpatParser parser, const XML_Char *name)
{
  XPointerContext *xpointer = parser->context->xpointer;
  PyObject *temp;

#if defined(DEBUG_CALLBACKS) || defined(DEBUG_XINCLUDE)
  fprintf(stderr, "::: xpointer_EndElement(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ")\n");
#endif
#if defined(DEBUG_XINCLUDE)
  Expat_DumpFlags(parser);
#endif

  if (Expat_HasFlag(parser, EXPAT_FLAG_XPOINTER_FOUND)) {
    if (--xpointer->depth == 0) {
      /* If what was matched was an XInclude element, use the XInclude
       * EndElement handler instead of the regular handler. */
      if (Expat_HasFlag(parser, EXPAT_FLAG_XINCLUDE)) {
        xinclude_EndElement(parser, name);
      } else {
        expat_EndElement(parser, name);
      }
      /* clear XPointer processing flag */
#ifdef DEBUG_XINCLUDE
      fprintf(stderr, "      Clearing EXPAT_FLAG_XPOINTER_FOUND\n");
#endif
      Expat_ClearFlag(parser, EXPAT_FLAG_XPOINTER_FOUND);

      /* Remove other "normal" content handlers */
      clearExpatHandlers(parser);
      XML_SetElementHandler(parser->context->parser,
                            (XML_StartElementHandler) xpointer_StartElement,
                            (XML_EndElementHandler) xpointer_EndElement);

      /* Move to previous XPointer criteria for next time */
      (void) StateTable_Transit(xpointer->state_table, XPTR_CLOSE_EVENT);

      temp = Stack_Pop(parser->xml_base_stack);
      Py_DECREF(temp);

      temp = Stack_Pop(parser->xml_lang_stack);
      Py_DECREF(temp);

      temp = Stack_Pop(parser->xml_space_stack);
      Py_DECREF(temp);
    } else {
      expat_EndElement(parser, name);
    }
  } else {
    XPointerCriteria *criteria_list = (XPointerCriteria *)
      StateTable_GetStateData(xpointer->state_table,
                              StateTable_GetState(xpointer->state_table));
    if (criteria_list->matched) {
      /* Move to previous XPointer criteria for next time */
      criteria_list->matched = 0;
      (void) StateTable_Transit(xpointer->state_table, XPTR_CLOSE_EVENT);
    }

    temp = Stack_Pop(parser->xml_base_stack);
    Py_DECREF(temp);

    temp = Stack_Pop(parser->xml_lang_stack);
    Py_DECREF(temp);

    temp = Stack_Pop(parser->xml_space_stack);
    Py_DECREF(temp);
  }
}


static XML_Char *build_expat_name(PyObject *uri, PyObject *local)
{
  XML_Char *expat_name;

  if (uri == Py_None) {
    if (local == Py_None) {
      /* zero-length string (matches everything) */
      expat_name = (XML_Char *) calloc(1, sizeof(XML_Char));
    } else {
      expat_name = XMLChar_FromObject(local);
    }
  } else if (local == Py_None) {
    expat_name = XMLChar_FromObject(uri);
  } else {
    PyObject *name = PyUnicode_FromUnicode(NULL,
                                           PyUnicode_GET_SIZE(uri) + \
                                           PyUnicode_GET_SIZE(local) + 1);
    if (name == NULL) return NULL;

    Py_UNICODE_COPY(PyUnicode_AS_UNICODE(name),
                    PyUnicode_AS_UNICODE(uri),
                    PyUnicode_GET_SIZE(uri));

    PyUnicode_AS_UNICODE(name)[PyUnicode_GET_SIZE(uri)] = EXPAT_NSSEP;

    Py_UNICODE_COPY(PyUnicode_AS_UNICODE(name) + PyUnicode_GET_SIZE(uri) + 1,
                    PyUnicode_AS_UNICODE(local),
                    PyUnicode_GET_SIZE(local));
    expat_name = XMLChar_FromObject(name);
    Py_DECREF(name);
  }

  return expat_name;
}

static XPointerCriteria *buildXPointerCriteria(PyObject *params)
{
  XPointerCriteria *criteria, *current;
  Py_ssize_t length, i;

  if ((length = PyList_Size(params)) < 0) {
    return NULL;
  }

  criteria = XPointerCriteria_New();
  if (criteria == NULL) {
    return NULL;
  }
  current = NULL;

  /* params is a list of tuples */
  for (i = 0; i < length; i++) {
    PyObject *criterion;
    PyObject *uri, *local, *value;

    if (current == NULL) {
      current = criteria;
    } else {
      if ((current->next = XPointerCriteria_New()) == NULL) {
        XPointerCriteria_Del(criteria);
        return NULL;
      }
      current = current->next;
    }

    criterion = PyList_GET_ITEM(params, i);
    if (!PyTuple_CheckExact(criterion)) {
      PyErr_SetString(PyExc_TypeError,
                      "xpointer_build_criteria: params not list of tuples");
      XPointerCriteria_Del(criteria);
      return NULL;
    }

    current->code = PyInt_AsLong(PyTuple_GET_ITEM(criterion, 0));
    if (PyErr_Occurred()) {
      XPointerCriteria_Del(criteria);
      return NULL;
    }
    switch (current->code) {
    case ELEMENT_ID:
      value = PyTuple_GET_ITEM(criterion, 1);
      current->criterion.element_id.identifier = XMLChar_FromObject(value);
      if (current->criterion.element_id.identifier == NULL) {
        XPointerCriteria_Del(criteria);
        return NULL;
      }
      break;
    case ELEMENT_COUNT:
      value = PyTuple_GET_ITEM(criterion, 1);
      current->criterion.element_count.value = PyInt_AsLong(value);
      if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError,
                        "xpointer_build_criteria: ELEMENT_COUNT target");
        XPointerCriteria_Del(criteria);
        return NULL;
      }
      current->criterion.element_count.counter = 1;
      break;
    case ELEMENT_MATCH:
      uri = PyTuple_GET_ITEM(criterion, 1);
      local = PyTuple_GET_ITEM(criterion, 2);
      current->criterion.element_match.name = build_expat_name(uri, local);
      if (current->criterion.element_match.name == NULL) {
        XPointerCriteria_Del(criteria);
        return NULL;
      }
      break;
    case ATTRIBUTE_MATCH:
      uri = PyTuple_GET_ITEM(criterion, 1);
      local = PyTuple_GET_ITEM(criterion, 2);
      value = PyTuple_GET_ITEM(criterion, 3);
      current->criterion.attribute_match.name = build_expat_name(uri, local);
      if (current->criterion.attribute_match.name == NULL) {
        XPointerCriteria_Del(criteria);
        return NULL;
      }
      current->criterion.attribute_match.value = XMLChar_FromObject(value);
      if (current->criterion.attribute_match.value == NULL) {
        XPointerCriteria_Del(criteria);
        return NULL;
      }
      break;
    default:
      PyErr_Format(PyExc_ValueError, "Bad typecode: %d", current->code);
      XPointerCriteria_Del(criteria);
      return NULL;
    };
  }

  return criteria;
}


static XPointerContext *parseXPointer(ExpatParser parser, PyObject *xpointer)
{
  PyObject *module, *states;
  int size, i;
  XPointerContext *context;

  /* Load the XPointer parsing module */
  module = PyDict_GetItemString(PyImport_GetModuleDict(),
                                "Ft.Xml.cDomlette"); /* borrowed */
  if (module == NULL) {
    module = PyImport_ImportModule("Ft.Xml.cDomlette");
    if (module == NULL) {
      return NULL;
    }
    /* Make it a borrowed reference, a copy exists in sys.modules */
    Py_DECREF(module);
  }

  /* Determine is there is an XPointer fragment to process */
  states = PyObject_CallMethod(module, "ProcessFragment", "O", xpointer);
  if (states == NULL) {
    return NULL;
  } else if (states == Py_None) {
    XIncludeException_UnsupportedXPointer(xpointer);
    return NULL;
  } else if (!PyList_CheckExact(states)) {
    PyErr_SetString(PyExc_TypeError,
                    "ProcessFragment must return a list");
    Py_DECREF(states);
    return NULL;
  }
  size = PyList_GET_SIZE(states);

  context = XPointerContext_New(size);
  if (context == NULL) {
    Py_DECREF(states);
    return NULL;
  }

  /* create the states */
  for (i = 0; i < size; i++) {
    PyObject *transitions;
    XPointerCriteria *criteria;

    transitions = PyList_GET_ITEM(states, i);
    if (!PyList_CheckExact(transitions)) {
      PyErr_SetString(PyExc_TypeError,
                      "ProcessFragment must return a list of lists");
    error:
      Py_DECREF(states);
      XPointerContext_Del(context);
      return NULL;
    }

    if ((criteria = buildXPointerCriteria(transitions)) == NULL)
      goto error;

    if (StateTable_AddState(context->state_table, criteria,
                            (StateDataFree) XPointerCriteria_Del) < 0) {
      XPointerCriteria_Del(criteria);
      goto error;
    }
  }

  /* add final (accepting) state */
  context->accepting = StateTable_AddState(context->state_table, NULL, NULL);
  if (context->accepting < 0)
    goto error;

  /* set the transitions */
  for (i = 0; i < size; i++) {
    StateId state;
    /* transition to next state on match */
    state = i + 1;
    StateTable_SetTransition(context->state_table, i, XPTR_MATCH_EVENT, state);

    /* if the first state, just loop back to self */
    state = i ? i - 1 : i;
    StateTable_SetTransition(context->state_table, i, XPTR_CLOSE_EVENT, state);
  }

  /* add transition back from accepting state */
  StateTable_SetTransition(context->state_table, size, XPTR_CLOSE_EVENT,
                           size ? size - 1 : size);

  Py_DECREF(states);
  return context;
}


/* This function is used when parsing is resumed after being suspended
 * while handling the target document of an XInclude.
 */
static ExpatStatus xincludeParsing(ExpatParser parser)
{
  ExpatStatus status;

  Debug_ParserFunctionCall(xincludeParsing, parser);

  status = continueParsing(parser);

  if (status == EXPAT_STATUS_OK) {
    /* We are done parsing the XInclude'ed document, remove its context */
    endContext(parser);

    /* Switch Expat to the XInclude element content handlers. The existing
     * handlers will be restored when the current start-tag is closed.
     */
#ifdef DEBUG_XINCLUDE
    fprintf(stderr, "      Setting EXPAT_FLAG_XINCLUDE\n");
#endif
    Expat_SetFlag(parser, EXPAT_FLAG_XINCLUDE);
    clearExpatHandlers(parser);
    XML_SetElementHandler(parser->context->parser,
                          (XML_StartElementHandler) xinclude_StartElement,
                          (XML_EndElementHandler) xinclude_EndElement);
  }

  Debug_ReturnStatus(xincludeParsing, status);
  return status;
}


static ExpatStatus xincludeAsXml(ExpatParser parser, PyObject *source,
                                 PyObject *xpointer)
{
  PyObject *href;
  XML_Parser expat_parser;
  Context *context;
  ExpatStatus status;

  Debug_ParserFunctionCall(xincludeAsXml, parser);

  /* Create an Expat parser to handle the new document */
  expat_parser = createExpatParser(parser);
  if (expat_parser == NULL) {
    return Expat_FatalError(parser);
  }
  copyExpatHandlers(parser, expat_parser);

  /* Create a new parsing context using the parser and input source */
  if (beginContext(parser, expat_parser, source) == NULL) {
    XML_ParserFree(expat_parser);
    return Expat_FatalError(parser);
  }
  Py_INCREF(source);

  /* Check for recursive processing.  This is done now to avoid an addtional
   * lookup for the absolute URI of the input source since it is done in the
   * context creatation.
   */
  href = parser->context->uri;
  for (context = parser->context->next; context; context = context->next) {
    if (PyObject_RichCompareBool(href, context->uri, Py_EQ)) {
      Py_INCREF(href);
      endContext(parser);
      status = Expat_ReportFatalError(parser, "RECURSIVE_PARSE_ERROR", "{sN}",
                                      "uri", href);
      Debug_ReturnStatus(xincludeAsXml, status);
      return status;
    }
  }

  if (xpointer) {
    parser->context->xpointer = parseXPointer(parser, xpointer);
    if (parser->context->xpointer == NULL) {
      endContext(parser);
      Debug_ReturnStatus(xincludeAsXml, EXPAT_STATUS_ERROR);
      return Expat_FatalError(parser);
    }
#ifdef DEBUG_XINCLUDE
    fprintf(stderr, "      Setting EXPAT_FLAG_XPOINTER\n");
#endif
    Expat_SetFlag(parser, EXPAT_FLAG_XPOINTER);
    clearExpatHandlers(parser);
    XML_SetElementHandler(parser->context->parser,
                          (XML_StartElementHandler) xpointer_StartElement,
                          (XML_EndElementHandler) xpointer_EndElement);
  }

  /* Parse the document */
  status = doParse(parser);

  switch (status) {
  case EXPAT_STATUS_OK:
    /* We are done parsing the XInclude'ed document, remove its context */
    endContext(parser);
    break;
  case EXPAT_STATUS_ERROR:
    /* We are done parsing the XInclude'ed document, remove its context */
    endContext(parser);
    /* Notify now current parser of the error condition */
    Expat_FatalError(parser);
    break;
  case EXPAT_STATUS_SUSPENDED:
    /* Set the XInclude resume function */
    parser->context->parsing = xincludeParsing;
    break;
  }

  Debug_ReturnStatus(xincludeAsXml, status);
  return status;
}


static ExpatStatus xincludeAsText(ExpatParser parser, PyObject *source,
                                  PyObject *encoding)
{
  PyObject *stream, *decoder, *content;
  XML_Char *data;
  ExpatStatus status;
  int discard_bom;

  Debug_ParserFunctionCall(xincludeAsText, parser);

  stream = PyObject_GetAttr(source, stream_string);
  if (stream == NULL) {
    Debug_ReturnStatus(xincludeAsText, EXPAT_STATUS_ERROR);
    return Expat_FatalError(parser);
  }

  /* Convert raw stream data to Unicode */
  if (encoding) {
    char *enc = PyString_AsString(encoding);
    if (enc) {
      decoder = PyCodec_StreamReader(enc, stream, "strict");
      discard_bom = ((enc[0] == 'u' || enc[0] == 'U') &&
                     (enc[1] == 't' || enc[1] == 'T') &&
                     (enc[2] == 'f' || enc[2] == 'F') && enc[3] == '-' &&
                     ((enc[4] == '8' && enc[5] == '\0') ||
                      (enc[4] == '1' && enc[5] == '6' && enc[6] == '\0') ||
                      (enc[4] == '3' && enc[5] == '2' && enc[6] == '\0')));
    } else {
      decoder = NULL;
      discard_bom = 0;
    }
  }
  else {
    /* default encoding is UTF-8 */
    decoder = PyCodec_StreamReader("utf-8", stream, "strict");
    discard_bom = 1;
  }
  Py_DECREF(stream);
  if (decoder == NULL) {
    Debug_ReturnStatus(xincludeAsText, EXPAT_STATUS_ERROR);
    return Expat_FatalError(parser);
  }

  /* Convert Unicode from decoder to XML_Char for Expat handler */
  content = PyObject_CallMethod(decoder, "read", NULL);
  Py_DECREF(decoder);
  if (content == NULL) {
    Debug_ReturnStatus(xincludeAsText, EXPAT_STATUS_ERROR);
    return Expat_FatalError(parser);
  } else if (!PyUnicode_Check(content)) {
    PyErr_Format(PyExc_TypeError,
                 "%s decoder did not return a unicode object (type=%s)",
                 encoding ? PyString_AS_STRING(encoding) : "UTF-8",
                 content->ob_type->tp_name);
    Py_DECREF(content);
    Debug_ReturnStatus(xincludeAsText, EXPAT_STATUS_ERROR);
    return Expat_FatalError(parser);
  }

  if (discard_bom) {
    const Py_UNICODE *u = PyUnicode_AS_UNICODE(content);
    size_t size = PyUnicode_GET_SIZE(content);
    if (*u == (Py_UNICODE)0xFEFF) u++, size--;
    data = XMLChar_FromUnicode(u, size);
  } else {
    data = XMLChar_FromObject(content);
  }
  Py_DECREF(content);
  if (data == NULL) {
    Debug_ReturnStatus(xincludeAsText, EXPAT_STATUS_ERROR);
    return Expat_FatalError(parser);
  }

  status = writeCharacterBuffer(parser, data, XMLChar_Len(data));
  free(data);

  Debug_ReturnStatus(xincludeAsText, status);
  return status;
}


static ExpatStatus processXInclude(ExpatParser parser, const XML_Char **atts)
{
  static const XML_Char href_const[] = { 'h', 'r', 'e', 'f', '\0' };
  static const XML_Char xpointer_const[] = {
    'x', 'p', 'o', 'i', 'n', 't', 'e', 'r', '\0' };
  static const XML_Char parse_const[] = { 'p', 'a', 'r', 's', 'e', '\0' };
  static const XML_Char text_const[] = { 't', 'e', 'x', 't', '\0' };
  static const XML_Char xml_const[] = { 'x', 'm', 'l', '\0' };
  static const XML_Char encoding_const[] =
    { 'e', 'n', 'c', 'o', 'd', 'i', 'n', 'g', '\0' };

  PyObject *href, *encoding, *xpointer, *source;
  int i, parse_xml = 1;

  ExpatStatus status;

  Debug_ParserFunctionCall(processXInclude, parser);

  href = NULL;
  encoding = NULL;
  xpointer = NULL;

  for (i = 0; atts[i];) {
    const XML_Char *name = atts[i++];
    const XML_Char *value = atts[i++];
    const XML_Char *p;

    if (XMLChar_Cmp(name, href_const) == 0) {
      /* treat empty href as non-existent (for exception) */
      if (*value) {
        href = Unicode_FromXMLChar(value);

        /* Fragment identifiers must not be used; their appearance is a
         * fatal error.
         */
        for (p = value; *p; p++) {
          if (*p == '#') {
            XIncludeException_FragmentIdentifier(href);
            Py_DECREF(href);
            Py_XDECREF(xpointer);
            Py_XDECREF(encoding);
            return Expat_FatalError(parser);
          }
        }
      }
    }
    else if (XMLChar_Cmp(name, xpointer_const) == 0) {
      xpointer = Unicode_FromXMLChar(value);
    }
    else if (XMLChar_Cmp(name, encoding_const) == 0) {
      encoding = Unicode_FromXMLChar(value);
    }
    else if (XMLChar_Cmp(name, parse_const) == 0) {
      if (XMLChar_Cmp(value, text_const) == 0) {
        parse_xml = 0;
      }
      else if (XMLChar_Cmp(value, xml_const) != 0) {
        PyObject *attr = Unicode_FromXMLChar(value);
        XIncludeException_InvalidParseAttr(attr);
        Py_XDECREF(attr);
        Py_XDECREF(href);
        Py_XDECREF(xpointer);
        Py_XDECREF(encoding);
        return Expat_FatalError(parser);
      }
    }
  }

  if (href == NULL) {
    /* In reality, this should be a reference to the current document, but
     * that would require a "seekable" stream and not all are. */
    /* FIXME: test for seekable stream */
    XIncludeException_MissingHref();
    Py_XDECREF(xpointer);
    Py_XDECREF(encoding);
    return Expat_FatalError(parser);
  } else if (!parse_xml && xpointer) {
    XIncludeException_TextXPointer();
    Py_DECREF(href);
    Py_DECREF(xpointer);
    Py_XDECREF(encoding);
    return Expat_FatalError(parser);
  }

  /* Attempt to retrieve the resource identified by "href" */
  source = PyObject_CallMethod(parser->context->source, "resolve", "NOO",
                               href, Py_None, xinclude_hint_string);
  if (source == NULL) {
    /* Determine if the error is a resource error (that is, not found) */
    if (PyErr_ExceptionMatches(UriException)) {
      PyObject *exception, *value, *traceback, *errorCode;

      /* Get the current exception and ensure that 'value' is an instance
       * of 'exception'.  This also clears the exception.
       */
      PyErr_Fetch(&exception, &value, &traceback);
      PyErr_NormalizeException(&exception, &value, &traceback);

      errorCode = PyObject_GetAttrString(value, "errorCode");
      if (errorCode && PyObject_RichCompareBool(UriException_RESOURCE_ERROR,
                                                errorCode, Py_EQ)) {
        /* Indicate the fallback should be performed. */
#ifdef DEBUG_XINCLUDE
        fprintf(stderr, "      Setting EXPAT_FLAG_XI_FALLBACK_NEEDED\n");
#endif
        Expat_SetFlag(parser, EXPAT_FLAG_XI_FALLBACK_NEEDED);
        parser->context->xinclude->exception = exception;
        parser->context->xinclude->value = value;
        parser->context->xinclude->traceback = traceback;
        status = EXPAT_STATUS_OK;
        goto done;
      }
      PyErr_Restore(exception, value, traceback);
    }
    status = Expat_FatalError(parser);
    Debug_ReturnStatus(processXInclude, status);
    return status;
  }

  if (parse_xml) {
    status = xincludeAsXml(parser, source, xpointer);
  } else {
    status = xincludeAsText(parser, source, encoding);
  }
  Py_DECREF(source);

 done:
  Py_XDECREF(xpointer);
  Py_XDECREF(encoding);

  if (status == EXPAT_STATUS_OK) {
    /* Switch Expat to the XInclude element content handlers. The existing
     * handlers will be restored when the current start-tag is closed.
     */
#ifdef DEBUG_XINCLUDE
    fprintf(stderr, "      Setting EXPAT_FLAG_XINCLUDE\n");
#endif
    Expat_SetFlag(parser, EXPAT_FLAG_XINCLUDE);
    clearExpatHandlers(parser);
    XML_SetElementHandler(parser->context->parser,
                          (XML_StartElementHandler) xinclude_StartElement,
                          (XML_EndElementHandler) xinclude_EndElement);
  }

  Debug_ReturnStatus(processXInclude, status);
  return status;
}

static XML_Char expat_xinclude_namespace[] = {
  'h', 't', 't', 'p', ':', '/', '/', 'w', 'w', 'w', '.', 'w', '3', '.',
  'o', 'r', 'g', '/', '2', '0', '0', '1', '/', 'X', 'I', 'n', 'c', 'l',
  'u', 'd', 'e', EXPAT_NSSEP,
};

static XML_Char expat_include_name[] = {
  'i', 'n', 'c', 'l', 'u', 'd', 'e'
};

static XML_Char expat_fallback_name[] = {
  'f', 'a', 'l', 'l', 'b', 'a', 'c', 'k'
};


/* StartElementHandler for content of the xi:include element
 * Flag conditions:
 *  EXPAT_FLAG_XI_FALLBACK_NEEDED -
 *    Set when handling xi:include events and fallback needs to be done
 *  EXPAT_FLAG_XI_FALLBACK_BODY -
 *    Set when hanlding xi:fallback events
 *  EXPAT_FLAG_XI_FALLBACK_DONE -
 *    Set when handling xi:xinclude events and xi:fallback already seen
 */
static void xinclude_StartElement(ExpatParser parser, const XML_Char *name,
                                  const XML_Char **atts)
{
#if defined(DEBUG_CALLBACKS) || defined(DEBUG_XINCLUDE)
  const XML_Char **ppattr = atts;
  fprintf(stderr, "=== xinclude_StartElement(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ", atts={");
  while (*ppattr) {
    if (ppattr != atts) {
      fprintf(stderr, ", ");
    }
    XMLChar_Print(stderr, *ppattr++);
  }
  fprintf(stderr, "})\n");
#endif
#ifdef DEBUG_XINCLUDE
  Expat_DumpFlags(parser);
#endif

  /* check for xi:xxx elements, ignore all others */
  if (XMLChar_NCmp(name, expat_xinclude_namespace,
                   EXPAT_NAME_LEN(expat_xinclude_namespace)) == 0) {
    const XML_Char *expat_name =
      name + EXPAT_NAME_LEN(expat_xinclude_namespace);

    /* check for xi:include */
    if (EXPAT_NAME_COMPARE(expat_name, expat_include_name)) {
      if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_BODY)) {
        /* xi:include as child of xi:fallback */
#ifdef DEBUG_XINCLUDE
        fprintf(stderr, "      Clearing EXPAT_FLAG_XI_FALLBACK_BODY\n");
#endif
        Expat_ClearFlag(parser, EXPAT_FLAG_XI_FALLBACK_BODY);
        /* increase xi:include element counter (handler stop indicator) */
        parser->context->xinclude->depth++;
        if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_NEEDED)) {
          /* process the xi:include element */
          processXInclude(parser, atts);
        }
      } else {
        /* fatal error; xi:include as child of xi:include */
        XIncludeException_IncludeInInclude();
        Expat_FatalError(parser);
      }
    }
    /* check for xi:fallback */
    else if (EXPAT_NAME_COMPARE(expat_name, expat_fallback_name)) {
      if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_BODY)) {
        /* fatal error; xi:fallback as child of xi:fallback */
        XIncludeException_FallbackNotInInclude();
        Expat_FatalError(parser);
      }
      else if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_DONE)) {
        /* fatal error; multiple xi:fallback elements */
        XIncludeException_MultipleFallbacks();
        Expat_FatalError(parser);
      } else if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_NEEDED)) {
        /* perform fallback */
        setExpatHandlers(parser);
        XML_SetElementHandler(parser->context->parser,
                              (XML_StartElementHandler) xinclude_StartElement,
                              (XML_EndElementHandler) xinclude_EndElement);
      }
      /* indicate inside of xi:fallback element */
#ifdef DEBUG_XINCLUDE
      fprintf(stderr, "      Setting EXPAT_FLAG_XI_FALLBACK_BODY\n");
#endif
      Expat_SetFlag(parser, EXPAT_FLAG_XI_FALLBACK_BODY);
    }
  } else if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_CONTENT)) {
    expat_StartElement(parser, name, atts);
  }
}


/* EndElementHandler for content of the xi:include element */
static void xinclude_EndElement(ExpatParser parser, const XML_Char *name)
{
#if defined(DEBUG_CALLBACKS) || defined(DEBUG_XINCLUDE)
  fprintf(stderr, "=== xinclude_EndElement(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ")\n");
#endif
#ifdef DEBUG_XINCLUDE
  Expat_DumpFlags(parser);
#endif

  /* check for xi:xxx elements */
  if (XMLChar_NCmp(name, expat_xinclude_namespace,
                   EXPAT_NAME_LEN(expat_xinclude_namespace)) == 0) {
    const XML_Char *expat_name =
      name + EXPAT_NAME_LEN(expat_xinclude_namespace);

    /* check for xi:include */
    if (EXPAT_NAME_COMPARE(expat_name, expat_include_name)) {
      if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_NEEDED)) {
        /* Fallback required, but none found */
        PyErr_Restore(parser->context->xinclude->exception,
                      parser->context->xinclude->value,
                      parser->context->xinclude->traceback);
        parser->context->xinclude->exception = NULL;
        parser->context->xinclude->value = NULL;
        parser->context->xinclude->traceback = NULL;
        Expat_FatalError(parser);
      }
      else if (--parser->context->xinclude->depth == 0) {
        /* Outer-most xi:include element closed, restore "normal" handlers. */
#ifdef DEBUG_XINCLUDE
        fprintf(stderr, "      Clearing EXPAT_FLAG_XINCLUDE\n");
#endif
        Expat_ClearFlag(parser, EXPAT_FLAG_XINCLUDE);
        setExpatHandlers(parser);
        if (Expat_HasFlag(parser, EXPAT_FLAG_XPOINTER)) {
          XML_SetElementHandler(
            parser->context->parser,
            (XML_StartElementHandler) xpointer_StartElement,
            (XML_EndElementHandler) xpointer_EndElement);
        }
        if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
          if (validateEndElement(parser, name) == EXPAT_STATUS_ERROR) return;
        }
        popElementState(parser);
      }
#ifdef DEBUG_XINCLUDE
      if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_DONE)) {
        fprintf(stderr, "      Clearing EXPAT_FLAG_XI_FALLBACK_DONE\n");
      }
#endif
      Expat_ClearFlag(parser, EXPAT_FLAG_XI_FALLBACK_DONE);
    }
    /* check for xi:fallback */
    else if (EXPAT_NAME_COMPARE(expat_name, expat_fallback_name)) {
#ifdef DEBUG_XINCLUDE
      fprintf(stderr, "      Clearing EXPAT_FLAG_XI_FALLBACK_CONTENT\n");
      fprintf(stderr, "      Setting EXPAT_FLAG_XI_FALLBACK_DONE\n");
#endif
      Expat_ClearFlag(parser, EXPAT_FLAG_XI_FALLBACK_CONTENT);
      Expat_SetFlag(parser, EXPAT_FLAG_XI_FALLBACK_DONE);
      clearExpatHandlers(parser);
      XML_SetElementHandler(parser->context->parser,
                            (XML_StartElementHandler) xinclude_StartElement,
                            (XML_EndElementHandler) xinclude_EndElement);
    }
  }
  /* If fallback is being performed, pass through to "normal" handler,
   * otherwise just ignore the event .
   */
  else if (Expat_HasFlag(parser, EXPAT_FLAG_XI_FALLBACK_CONTENT)) {
    expat_EndElement(parser, name);
  }
}


static ExpatStatus beginXInclude(ExpatParser parser, const XML_Char **atts)
{
  ExpatStatus status;

  Debug_ParserFunctionCall(beginXInclude, parser);

  if (parser->context->xinclude) {
    /* previous XInclude handled, reuse that context */
    memset(parser->context->xinclude, 0, sizeof(XIncludeContext));
  } else {
    parser->context->xinclude = XIncludeContext_New();
    if (parser->context->xinclude == NULL) {
      Debug_ReturnStatus(beginXInclude, EXPAT_STATUS_ERROR);
      return Expat_FatalError(parser);
    }
  }

  /* set xi:include element counter (handler stop indicator) */
  parser->context->xinclude->depth = 1;
  status = processXInclude(parser, atts);

  Debug_ReturnStatus(beginXInclude, status);
  return status;
}


/** EXPAT callbacks ***************************************************/


static ExpatStatus validate_entity_ref(ExpatParser parser, PyObject *name)
{
  DTD *dtd = parser->context->dtd;
  PyObject *notation;

  notation = PyDict_GetItem(dtd->entities, name);
  if (notation == NULL) {
    return Expat_ReportError(parser, "UNDECLARED_ENTITY",
                             "{sO}", "entity", name);
  }
  if (notation == Py_None) {
    return Expat_ReportError(parser, "INVALID_ENTITY",
                             "{sO}", "entity", name);
  }
  if (PyDict_GetItem(dtd->notations, notation) == NULL) {
    return Expat_ReportError(parser, "UNDECLARED_NOTATION",
                             "{sO}", "notation", notation);
  }

  return EXPAT_STATUS_OK;
}

static ExpatStatus validate_attribute(ExpatParser parser,
                                      PyObject *attribute_type,
                                      PyObject *name, PyObject *value)
{
  DTD *dtd = parser->context->dtd;
  PyObject *values;
  Py_ssize_t size;

  /* validate the value for correctness */
  switch (AttributeType_GET_TYPE(attribute_type)) {
  case ATTRIBUTE_TYPE_CDATA:
    /* all content valid */
    break;
  case ATTRIBUTE_TYPE_ID:
  case ATTRIBUTE_TYPE_IDREF:
  case ATTRIBUTE_TYPE_ENTITY:
    switch (XmlString_IsName(value)) {
    case 0:
      if (Expat_ReportError(parser, "INVALID_NAME_VALUE", "{sO}",
                            "attr", name) == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    case 1:
      break;
    default:
      return Expat_FatalError(parser);
    }
    break;
  case ATTRIBUTE_TYPE_IDREFS:
  case ATTRIBUTE_TYPE_ENTITIES:
    switch (XmlString_IsNames(value)) {
    case 0:
      if (Expat_ReportError(parser, "INVALID_NAME_SEQ_VALUE", "{sO}",
                            "attr", name) == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    case 1:
      break;
    default:
      return Expat_FatalError(parser);
    }
    break;
  case ATTRIBUTE_TYPE_NMTOKEN:
    switch (XmlString_IsNmtoken(value)) {
    case 0:
      if (Expat_ReportError(parser, "INVALID_NMTOKEN_VALUE", "{sO}",
                            "attr", name) == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    case 1:
      break;
    default:
      return Expat_FatalError(parser);
    }
    break;
  case ATTRIBUTE_TYPE_NMTOKENS:
    switch (XmlString_IsNmtokens(value)) {
    case 0:
      if (Expat_ReportError(parser, "INVALID_NMTOKEN_SEQ_VALUE", "{sO}",
                            "attr", name) == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    case 1:
      break;
    default:
      return Expat_FatalError(parser);
    }
    break;
  case ATTRIBUTE_TYPE_NOTATION:
  case ATTRIBUTE_TYPE_ENUMERATION:
    values = AttributeType_GET_ALLOWED_VALUES(attribute_type);
    switch (PySequence_Contains(values, value)) {
    case 0:
      if (Expat_ReportError(parser, "INVALID_ENUM_VALUE", "{sOsO}",
                            "attr", name, "value", value)
          == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    case 1:
      break;
    default:
      return Expat_FatalError(parser);
    }
    break;
  }

  /* perform additional validation for some types */
  switch (AttributeType_GET_TYPE(attribute_type)) {
  case ATTRIBUTE_TYPE_ID:
    if (PyDict_GetItem(dtd->ids, value) != NULL) {
      if (Expat_ReportError(parser, "DUPLICATE_ID", "{sO}",
                            "id", value) == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    }
    if (PyDict_SetItem(dtd->ids, value, Py_True) < 0) {
      return Expat_FatalError(parser);
    }
    break;
  case ATTRIBUTE_TYPE_IDREF:
    if (PyList_Append(dtd->used_ids, value) < 0) {
      return Expat_FatalError(parser);
    }
    break;
  case ATTRIBUTE_TYPE_IDREFS:
    values = PyUnicode_Split(value, unicode_space_char, (Py_ssize_t)-1);
    if (values == NULL) {
      return Expat_FatalError(parser);
    }
    /* this construct is basically list.extend() */
    size = PyList_GET_SIZE(dtd->used_ids);
    if (PyList_SetSlice(dtd->used_ids, size, size, values) < 0) {
      Py_DECREF(values);
      return Expat_FatalError(parser);
    }
    Py_DECREF(values);
    break;
  case ATTRIBUTE_TYPE_ENTITY:
    if (validate_entity_ref(parser, value) == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
    break;
  case ATTRIBUTE_TYPE_ENTITIES:
    values = PyUnicode_Split(value, unicode_space_char, (Py_ssize_t)-1);
    if (values == NULL) {
      return Expat_FatalError(parser);
    }
    for (size = 0; size < PyList_GET_SIZE(values); size++) {
      if (validate_entity_ref(parser, PyList_GET_ITEM(values, size))
          == EXPAT_STATUS_ERROR) {
        Py_DECREF(values);
        return EXPAT_STATUS_ERROR;
      }
    }
    Py_DECREF(values);
    break;
  default:
    break;
  }

  return EXPAT_STATUS_OK;
}

static ExpatStatus validate_attributes(ExpatParser parser,
                                       PyObject *element_type,
                                       ExpatAttribute *attributes,
                                       int nattributes)
{
  PyObject *attribute_type, *attribute_name;
  ExpatAttribute *attribute;
  Py_ssize_t i, size;

  for (i = nattributes, attribute = attributes; i > 0; i--, attribute++) {
    attribute_type = \
      ElementType_GET_ATTRIBUTE(element_type, attribute->qualifiedName);
    if (attribute_type == NULL) {
      if (Expat_ReportError(parser, "UNDECLARED_ATTRIBUTE", "{sO}",
                            "attr", attribute->qualifiedName)
          == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
      continue;
    }

    if (validate_attribute(parser, attribute_type, attribute->qualifiedName,
                           attribute->value) == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
  }

  /* check for missing required attributes */
  while (PyDict_Next(ElementType_GET_ATTRIBUTES(element_type), &i,
                     &attribute_name, &attribute_type)) {
    if (AttributeType_GET_DECL(attribute_type) == ATTRIBUTE_DECL_REQUIRED) {
      for (size = nattributes, attribute = attributes; size > 0;
           size--, attribute++) {
        switch (PyObject_RichCompareBool(attribute->qualifiedName,
                                         attribute_name, Py_EQ)) {
        case 1:
          goto found;
        case 0:
          break;
        default:
          return Expat_FatalError(parser);
        }
      }
      if (Expat_ReportError(parser, "MISSING_ATTRIBUTE", "{sO}",
                            "attr", attribute_name) == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    found:
      continue;
    }
  }

  return EXPAT_STATUS_OK;
}

static ExpatStatus validate_element(ExpatParser parser,
                                    ExpatExpandedName *element,
                                    ExpatAttribute *attributes,
                                    int nattributes)
{
  DTD *dtd = parser->context->dtd;
  PyObject *element_type;
  ExpatStatus status;

  if (dtd == NULL) {
    /* document didn't declare a document type */
    if (Expat_HasFlag(parser, EXPAT_FLAG_INFOSET_FIXUP)) {
      /* handling an XInclude; disable DTD validation for this document */
      Expat_ClearFlag(parser, EXPAT_FLAG_VALIDATE);
      return EXPAT_STATUS_OK;
    }
    /* validity constraint */
    status = Expat_ReportError(parser, "MISSING_DOCTYPE", NULL);
    if (status == EXPAT_STATUS_ERROR) {
      return status;
    }
    /* create an empty DTD so we have something to validate against */
    parser->context->dtd = dtd = DTD_New();
    if (dtd == NULL) {
      return Expat_FatalError(parser);
    }
  }

  /* root_element will be Py_None once it has been verified */
  if (dtd->root_element == Py_None) {
    switch (Validator_ValidateEvent(dtd->validator,
                                    element->qualifiedName)) {
    case 0:
      status = Expat_ReportError(parser, "INVALID_ELEMENT", "{sO}",
                                 "element", element->qualifiedName);
      if (status == EXPAT_STATUS_ERROR) {
        return status;
      }
      /* fall through */
    case 1:
      /* everything is hunky-dory */
      break;
    default:
      return Expat_FatalError(parser);
    }
  } else {
    /* verify the declared root element */
    switch (PyObject_RichCompareBool(dtd->root_element,
                                     element->qualifiedName, Py_EQ)) {
    case 0:
      status = Expat_ReportError(parser, "ROOT_ELEMENT_MISMATCH", "{sO}",
                                 "element", element->qualifiedName);
      if (status == EXPAT_STATUS_ERROR) {
        return status;
      }
      /* fall through */
    case 1:
      /* Reference to the root element is no longer needed */
      dtd->root_element = Py_None;
      break;
    default:
      return Expat_FatalError(parser);
    }
  }

  switch (Validator_StartElement(dtd->validator,
                                 element->qualifiedName)) {
  case 0:
    status = Expat_ReportError(parser, "UNDECLARED_ELEMENT", "{sO}",
                               "element", element->qualifiedName);
    if (status == EXPAT_STATUS_ERROR) {
      return status;
    }
    /* fall through */
  case 1:
    /* everything is hunky-dory */
    break;
  default:
    return Expat_FatalError(parser);
  }

  /* validate the attributes against the element type */
  element_type = Validator_GetElementType(dtd->validator,
                                          element->qualifiedName);
  if (element_type != NULL) {
    /* only validate attributes for declared elements */
    status = validate_attributes(parser, element_type, attributes,
                                 nattributes);
    if (status == EXPAT_STATUS_ERROR) {
      return status;
    }
  }

  return EXPAT_STATUS_OK;
}

static ExpatStatus resize_attribute_list(ExpatParser parser, int size)
{
  ExpatAttribute *attrs = parser->attrs;
  int new_size = ROUND_UP(size, ATTR_BUFSIZ);
  if (PyMem_Resize(attrs, ExpatAttribute, new_size) == NULL) {
    PyErr_NoMemory();
    return Expat_FatalError(parser);
  }
  parser->attrs = attrs;
  parser->attrs_size = new_size;
  return EXPAT_STATUS_OK;
}

void expat_StartElement(ExpatParser parser, const XML_Char *name,
                        const XML_Char **atts)
{
  const XML_Char **ppattr;
  ExpatExpandedName *expanded_name;
  ExpatAttribute *expanded_attrs, *expanded_attr;
  PyObject *xml_base, *xml_lang, *xml_space, *xml_id, *preserve_whitespace;
  int i, id_index, attrs_size;

  Debug_ParserFunctionCall(expat_StartElement, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** StartElement(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ", atts={");
  for (ppattr = atts; *ppattr;) {
    if (ppattr != atts) {
      fprintf(stderr, ", ");
    }
    XMLChar_Print(stderr, *ppattr++);
  }
  fprintf(stderr, "})\n");
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  /** XML_Char -> PyObject **************************************/

  /* Convert XML_Char inputs to our format */
  expanded_name = makeExpandedName(parser, name);
  if (expanded_name == NULL) {
    Expat_FatalError(parser);
    return;
  }

  /* Determine how much memory is needed for the attributes array */
  for (ppattr = atts, attrs_size = 0; *ppattr; ppattr += 2, attrs_size++);

  /* get the array for storing the expanded attributes */
  if (attrs_size > parser->attrs_size) {
    if (resize_attribute_list(parser, attrs_size) == EXPAT_STATUS_ERROR) {
      return;
    }
  }
  expanded_attrs = parser->attrs;

  id_index = XML_GetIdAttributeIndex(parser->context->parser);
  for (ppattr = atts, expanded_attr = expanded_attrs; *ppattr;
       ppattr += 2, id_index -= 2) {
    ExpatExpandedName *attr_name = makeExpandedName(parser, ppattr[0]);
    PyObject *attr_value = makeUnicode(parser, ppattr[1]);
    if (attr_name == NULL || attr_value == NULL) {
      Expat_FatalError(parser);
      return;
    }

    /* store attribute name/value pair */
    memcpy(expanded_attr, attr_name, sizeof(ExpatExpandedName));
    expanded_attr->value = attr_value;
    expanded_attr->type = (id_index == 0
                           ? ATTRIBUTE_TYPE_ID
                           : ATTRIBUTE_TYPE_CDATA);
    expanded_attr++;
  }

  /** Validation ************************************************/

  if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
    if (validate_element(parser, expanded_name, expanded_attrs, attrs_size)
        == EXPAT_STATUS_ERROR) {
      return;
    }
  }

  /** Attributes ************************************************/

  /* Get current xml:* settings */
  xml_base = Stack_PEEK(parser->xml_base_stack);
  xml_lang = Stack_PEEK(parser->xml_lang_stack);
  xml_space = Stack_PEEK(parser->xml_space_stack);
  id_index = -1;

  /* Now check for xml:* attributes */
  for (i = 0, expanded_attr = expanded_attrs; i < attrs_size;
       i++, expanded_attr++) {
    switch (PyObject_RichCompareBool(expanded_attr->namespaceURI,
                                     xml_namespace_string, Py_EQ)) {
    case 1:
      /* check for xml:base */
      switch (PyObject_RichCompareBool(expanded_attr->localName, base_string,
                                       Py_EQ)) {
      case 1:
        xml_base = expanded_attr->value;
      case 0:
        break;
      default:
        Expat_FatalError(parser);
        return;
      }
      /* check for xml:lang */
      switch (PyObject_RichCompareBool(expanded_attr->localName, lang_string,
                                       Py_EQ)) {
      case 1:
        xml_lang = expanded_attr->value;
      case 0:
        break;
      default:
        Expat_FatalError(parser);
        return;
      }
      /* check for xml:space */
      switch (PyObject_RichCompareBool(expanded_attr->localName, space_string,
                                       Py_EQ)) {
      case 1:
        switch (PyObject_RichCompareBool(expanded_attr->value, preserve_string,
                                         Py_EQ)) {
        case 1:
          xml_space = Py_True;
        case 0:
          break;
        default:
          Expat_FatalError(parser);
          return;
        }
        switch (PyObject_RichCompareBool(expanded_attr->value, default_string,
                                         Py_EQ)) {
        case 1:
          xml_space = Py_False;
        case 0:
          break;
        default:
          Expat_FatalError(parser);
          return;
        }
      case 0:
        break;
      default:
        Expat_FatalError(parser);
        return;
      }
      /* check for xml:id */
      switch (PyObject_RichCompareBool(expanded_attr->localName, id_string,
                                       Py_EQ)) {
      case 1:
        id_index = i;
        /* fall through */
      case 0:
        break;
      default:
        Expat_FatalError(parser);
        return;
      }
    }
  }

  if (Expat_HasFlag(parser, EXPAT_FLAG_INFOSET_FIXUP)) {
    /* Ensure that there is enough room in the array to add the attributes */
    int new_size = attrs_size + 2;
    Expat_ClearFlag(parser, EXPAT_FLAG_INFOSET_FIXUP);
    if (new_size > parser->attrs_size) {
      if (resize_attribute_list(parser, new_size) == EXPAT_STATUS_ERROR) {
        return;
      }
      expanded_attrs = parser->attrs;
    }
    expanded_attr = expanded_attrs + attrs_size;

    /* XInclude 4.5.5 - Base URI Fixup */
    if (xml_base == Stack_PEEK(parser->xml_base_stack)) {
      /* attribute not present on element, check for fixup */
      switch (PyObject_RichCompareBool(parser->context->xml_base, xml_base,
                                       Py_EQ)) {
      case 0: /* different, add an attribute */
        expanded_attr->namespaceURI = xml_namespace_string;
        expanded_attr->localName = base_string;
        expanded_attr->qualifiedName = xml_base_string;
        if (xml_base == Py_None) {
          expanded_attr->value = empty_string;
        } else {
          expanded_attr->value = xml_base;
        }
        attrs_size++;
        expanded_attr++;
      case 1: /* identical, no fixup required */
        break;
      default: /* error */
        Expat_FatalError(parser);
        return;
      }
    }

    /* XInclude 4.5.6 - Language Fixup */
    if (xml_lang == Stack_PEEK(parser->xml_lang_stack)) {
      switch (PyObject_RichCompareBool(parser->context->xml_lang, xml_lang,
                                       Py_EQ)) {
      case 0: /* different, add an attribute */
        expanded_attr->namespaceURI = xml_namespace_string;
        expanded_attr->localName = lang_string;
        expanded_attr->qualifiedName = xml_lang_string;
        if (xml_lang == Py_None) {
          expanded_attr->value = empty_string;
        } else {
          expanded_attr->value = xml_lang;
        }
        attrs_size++;
        expanded_attr++;
      case 1: /* identical, no fixup required */
        break;
      default: /* error */
        Expat_FatalError(parser);
        return;
      }
    }
  }

  /* Save updated xml:* settings */
  Stack_Push(parser->xml_base_stack, xml_base);
  Stack_Push(parser->xml_lang_stack, xml_lang);
  Stack_Push(parser->xml_space_stack, xml_space);
  if (id_index >= 0) {
    xml_id = XmlString_NormalizeSpace(expanded_attrs[id_index].value);
    if (xml_id == NULL) {
      Expat_FatalError(parser);
      return;
    }
    expanded_attrs[id_index].value = xml_id;
    expanded_attrs[id_index].type = ATTRIBUTE_TYPE_ID;
  } else {
    xml_id = NULL;
  }

  /** XSLT Whitespace Stripping *********************************/

  /* By being declared static prior to this function body, this should
   * get inlined by any compiler worth its salt.
   */
  preserve_whitespace = isWhitespacePreserving(parser,
                                               expanded_name->namespaceURI,
                                               expanded_name->localName);
  if (xml_space == Py_True) {
    preserve_whitespace = Py_True;
  }
  Stack_Push(parser->preserve_whitespace_stack, preserve_whitespace);

  /** XInclude **************************************************/

  if (parser->process_xincludes) {
    /* check for xi:xxx elements */
    if (XMLChar_NCmp(name, expat_xinclude_namespace,
                     EXPAT_NAME_LEN(expat_xinclude_namespace)) == 0) {
      const XML_Char *xinclude_name =
        name + EXPAT_NAME_LEN(expat_xinclude_namespace);

      /* check for xi:include */
      if (EXPAT_NAME_COMPARE(xinclude_name, expat_include_name)) {
        /* fall through regardless of return status */
        (void) beginXInclude(parser, atts);
      }
      /* check for xi:fallback */
      else if (EXPAT_NAME_COMPARE(xinclude_name, expat_fallback_name)) {
        /* fatal error, xi:fallback not in xi:include */
        XIncludeException_FallbackNotInInclude();
        Expat_FatalError(parser);
        /* fall through */
      }
      /* ignore other xi:* elements */
      goto finally;
    }
  }

  /** Callback **************************************************/

  parser->start_element_handler(parser->userState, expanded_name,
                                expanded_attrs, attrs_size);

finally:
  Py_XDECREF(xml_id);
}


void expat_EndElement(ExpatParser parser, const XML_Char *name)
{
  ExpatExpandedName *expanded_name;

  Debug_ParserFunctionCall(expat_EndElement, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** EndElement(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ")\n");
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  expanded_name = makeExpandedName(parser, name);
  if (expanded_name == NULL) {
    Expat_FatalError(parser);
    return;
  }

  if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
    if (validateEndElement(parser, name) == EXPAT_STATUS_ERROR) return;
  }

  parser->end_element_handler(parser->userState, expanded_name);

  popElementState(parser);
}


void expat_CharacterData(ExpatParser parser, const XML_Char *data, int len)
{
  Debug_ParserFunctionCall(expat_CharacterData, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** CharacterData(data=");
  XMLChar_NPrint(stderr, data, len);
  fprintf(stderr, ")\n");
#endif

  if (writeCharacterBuffer(parser, data, len) == EXPAT_STATUS_ERROR)
    Expat_FatalError(parser);
}


void expat_ProcessingInstruction(ExpatParser parser, const XML_Char *target,
                                 const XML_Char *data)
{
  PyObject *python_target, *python_data;

  Debug_ParserFunctionCall(expat_ProcessingInstruction, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** ProcessingInstruction(target=");
  XMLChar_Print(stderr, target);
  fprintf(stderr, ", data=");
  XMLChar_Print(stderr, data);
  fprintf(stderr, ")\n");
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  python_target = makeUnicode(parser, target);
  if (python_target == NULL) {
    Expat_FatalError(parser);
    return;
  }

  python_data = makeUnicode(parser, data);
  if (python_data == NULL) {
    Expat_FatalError(parser);
    return;
  }

  parser->processing_instruction_handler(parser->userState, python_target,
                                         python_data);
}


void expat_Comment(ExpatParser parser, const XML_Char *data)
{
  PyObject *python_data;

  Debug_ParserFunctionCall(expat_Comment, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** Comment(data=");
  XMLChar_Print(stderr, data);
  fprintf(stderr, ")\n");
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  python_data = Unicode_FromXMLChar(data);
  if (python_data == NULL) {
    Expat_FatalError(parser);
    return;
  }

  parser->comment_handler(parser->userState, python_data);

  Py_DECREF(python_data);
}


void expat_StartNamespaceDecl(ExpatParser parser, const XML_Char *prefix,
                              const XML_Char *uri)
{
  PyObject *python_prefix, *python_uri;

  Debug_ParserFunctionCall(expat_StartNamespaceDecl, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** StartNamespaceDecl(prefix=");
  XMLChar_Print(stderr, prefix);
  fprintf(stderr, ", uri=");
  XMLChar_Print(stderr, uri);
  fprintf(stderr, ")\n");
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  if (prefix) {
    python_prefix = makeUnicode(parser, prefix);
    if (python_prefix == NULL) {
      Expat_FatalError(parser);
      return;
    }
  } else {
    python_prefix = Py_None;
  }

  if (uri) {
    python_uri = makeUnicode(parser, uri);
    if (python_uri == NULL) {
      Expat_FatalError(parser);
      return;
    }
  } else {
    python_uri = Py_None;
  }

  parser->start_namespace_decl_handler(parser->userState, python_prefix,
                                       python_uri);
}


void expat_EndNamespaceDecl(ExpatParser parser, const XML_Char *prefix)
{
  PyObject *python_prefix;

  Debug_ParserFunctionCall(expat_EndNamespaceDecl, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** EndNamespaceDecl(prefix=");
  XMLChar_Print(stderr, prefix);
  fprintf(stderr, ")\n");
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  if (prefix) {
    python_prefix = makeUnicode(parser, prefix);
    if (python_prefix == NULL) {
      Expat_FatalError(parser);
      return;
    }
  } else {
    python_prefix = Py_None;
  }

  parser->end_namespace_decl_handler(parser->userState, python_prefix);
}


void expat_StartDoctypeDecl(ExpatParser parser, const XML_Char *name,
                            const XML_Char *sysid, const XML_Char *pubid,
                            int has_internal_subset)
{
  PyObject *python_name;

  Debug_ParserFunctionCall(expat_StartDoctypeDecl, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** StartDoctypeDecl(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ", sysid=");
  XMLChar_Print(stderr, sysid);
  fprintf(stderr, ", pubid=");
  XMLChar_Print(stderr, pubid);
  fprintf(stderr, ", has_internal_subset=%d)\n", has_internal_subset);
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  /* add the DTD to the parsing context */
  if (parser->context->dtd) {
    PyErr_SetString(PyExc_SystemError, "DTD already started");
    Expat_FatalError(parser);
    return;
  } else {
    parser->context->dtd = DTD_New();
    if (parser->context->dtd == NULL) {
      Expat_FatalError(parser);
      return;
    }
  }

  if ((python_name = makeUnicode(parser, name)) == NULL) {
    Expat_FatalError(parser);
    return;
  }
  parser->context->dtd->root_element = python_name;

  if (parser->start_doctype_decl_handler) {
    PyObject *python_sysid, *python_pubid;

    if (sysid) {
      if ((python_sysid = Unicode_FromXMLChar(sysid)) == NULL) {
        Expat_FatalError(parser);
        return;
      }
    } else {
      Py_INCREF(Py_None);
      python_sysid = Py_None;
    }

    if (pubid) {
      if ((python_pubid = Unicode_FromXMLChar(pubid)) == NULL) {
        Py_DECREF(python_sysid);
        Expat_FatalError(parser);
        return;
      }
    } else {
      Py_INCREF(Py_None);
      python_pubid = Py_None;
    }

    parser->start_doctype_decl_handler(parser->userState, python_name,
                                       python_sysid, python_pubid);
    Py_DECREF(python_sysid);
    Py_DECREF(python_pubid);
  }

  setExpatSubsetHandlers(parser);
}


void expat_EndDoctypeDecl(ExpatParser parser)
{
  DTD *dtd = parser->context->dtd;
  PyObject *name, *temp;
  Py_ssize_t pos;

  Debug_ParserFunctionCall(expat_EndDoctypeDecl, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** EndDoctypeDecl()\n");
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  pos = 0;
  while (PyDict_Next(dtd->used_elements, &pos, &name, &temp)) {
    if (Expat_ReportWarning(parser, "ATTRIBUTES_WITHOUT_ELEMENT", "{sO}",
                            "element", name) == EXPAT_STATUS_ERROR) {
      return;
    }
  }
  PyDict_Clear(dtd->used_elements);

  if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
    pos = 0;
    while (PyDict_Next(dtd->used_notations, &pos, &name, &temp)) {
      /* Undeclared notations in attributes are errors */
      if (Expat_ReportError(parser, "ATTRIBUTE_UNDECLARED_NOTATION", "{sOsO}",
                            "attr", temp, "notation", name)
          == EXPAT_STATUS_ERROR) {
        return;
      }
    }
  }
  PyDict_Clear(dtd->used_notations);

  switch (Validator_StartElement(dtd->validator, dtd->root_element)) {
  }

  if (parser->end_doctype_decl_handler) {
    parser->end_doctype_decl_handler(parser->userState);
  }

  setExpatHandlers(parser);
}


void expat_StartCdataSection(ExpatParser parser)
{
  parser->start_cdata_section_handler(parser->userState);
}


void expat_EndCdataSection(ExpatParser parser)
{
  parser->end_cdata_section_handler(parser->userState);
}


void expat_SkippedEntity(ExpatParser parser, const XML_Char *entityName,
                         int is_parameter_entity)
{
  PyObject *python_entityName;

  Debug_ParserFunctionCall(expat_SkippedEntity, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** SkippedEntity(entityName=");
  XMLChar_Print(stderr, entityName);
  fprintf(stderr, ", is_parameter_entity=%d)\n", is_parameter_entity);
#endif

  FLUSH_CHARACTER_BUFFER(parser);

  if (is_parameter_entity) {
    /* The SAX spec requires to report skipped PEs with a '%' */
    int len = XMLChar_Len(entityName);
    XML_Char *temp = (XML_Char *) PyObject_MALLOC(sizeof(XML_Char) * (len+1));
    if (temp == NULL) {
      Expat_FatalError(parser);
      return;
    }
    temp[0] = '%';
    memcpy(temp + 1, entityName, len);
    python_entityName = Unicode_FromXMLCharAndSize(temp, len + 1);
    PyObject_FREE(temp);
  } else {
    python_entityName = Unicode_FromXMLChar(entityName);
  }
  if (python_entityName == NULL) {
    Expat_FatalError(parser);
    return;
  }

  if (parser->skipped_entity_handler) {
    parser->skipped_entity_handler(parser->userState, python_entityName);
  }

  Py_DECREF(python_entityName);
}


static ExpatStatus parseContent(ExpatParser parser, PyObject *model,
                                XML_Content *content, int initial_state,
                                int final_state);

static ExpatStatus parseName(ExpatParser parser, PyObject *model,
                             XML_Content *content, int initial_state,
                             int final_state)
{
  PyObject *token;
  int rv;

  token = makeUnicode(parser, content->name);
  if (token == NULL) {
    return Expat_FatalError(parser);
  }

  rv = ContentModel_AddTransition(model, token, initial_state, final_state);
  if (rv < 0) {
    return Expat_FatalError(parser);
  }

  return EXPAT_STATUS_OK;
}

static ExpatStatus parseSeq(ExpatParser parser, PyObject *model,
                            XML_Content *content, int initial_state,
                            int final_state)
{
  unsigned int last, i;
  int next_state;

  last = content->numchildren - 1;
  for (i = 0; i < last; i++) {
    next_state = ContentModel_NewState(model);
    if (next_state < 0) {
      return Expat_FatalError(parser);
    }
    if (parseContent(parser, model, &content->children[i], initial_state,
                     next_state) == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
    initial_state = next_state;
  }

  if (parseContent(parser, model, &content->children[last], initial_state,
                   final_state) == EXPAT_STATUS_ERROR) {
    return EXPAT_STATUS_ERROR;
  }

  return EXPAT_STATUS_OK;
}

static ExpatStatus parseChoice(ExpatParser parser, PyObject *model,
                               XML_Content *content, int initial_state,
                               int final_state)
{
  unsigned int i;

  for (i = 0; i < content->numchildren; i++) {
    if (parseContent(parser, model, &content->children[i], initial_state,
                     final_state) == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
  }

  return EXPAT_STATUS_OK;
}

static ExpatStatus parseContent(ExpatParser parser, PyObject *model,
                                XML_Content *content, int initial_state,
                                int final_state)
{
  int s1, s2;
  ExpatStatus status;

  switch (content->quant) {
  case XML_CQUANT_OPT:
    if (ContentModel_AddEpsilonMove(model, initial_state, final_state) < 0) {
      return Expat_FatalError(parser);
    }
    /* fall through */
  case XML_CQUANT_NONE:
    switch (content->type) {
    case XML_CTYPE_SEQ:
      return parseSeq(parser, model, content, initial_state, final_state);
    case XML_CTYPE_CHOICE:
      return parseChoice(parser, model, content, initial_state, final_state);
    case XML_CTYPE_NAME:
      return parseName(parser, model, content, initial_state, final_state);
    default:
      PyErr_Format(PyExc_SystemError, "invalid type %d", content->type);
      return Expat_FatalError(parser);
    }
    break;
  case XML_CQUANT_REP:
    if (ContentModel_AddEpsilonMove(model, initial_state, final_state) < 0) {
      return Expat_FatalError(parser);
    }
    /* fall through */
  case XML_CQUANT_PLUS:
    s1 = ContentModel_NewState(model);
    s2 = ContentModel_NewState(model);
    if (s1 < 0 || s2 < 0) {
      return Expat_FatalError(parser);
    }
    if (ContentModel_AddEpsilonMove(model, initial_state, s1) < 0) {
      return Expat_FatalError(parser);
    }

    switch (content->type) {
    case XML_CTYPE_SEQ:
      status = parseSeq(parser, model, content, s1, s2);
      break;
    case XML_CTYPE_MIXED:
      if (ContentModel_AddTransition(model, content_model_pcdata,
                                     s1, s2) < 0) {
        return Expat_FatalError(parser);
      }
      /* fall through */
    case XML_CTYPE_CHOICE:
      status = parseChoice(parser, model, content, s1, s2);
      break;
    case XML_CTYPE_NAME:
      status = parseName(parser, model, content, s1, s2);
      break;
    default:
      PyErr_Format(PyExc_SystemError, "invalid type %d", content->type);
      status = Expat_FatalError(parser);
    }
    if (status == EXPAT_STATUS_ERROR) return status;

    if (ContentModel_AddEpsilonMove(model, s2, s1) < 0) {
      return Expat_FatalError(parser);
    }
    if (ContentModel_AddEpsilonMove(model, s2, final_state) < 0) {
      return Expat_FatalError(parser);
    }
    break;
  }
  return EXPAT_STATUS_OK;
}

static ExpatStatus stringifyContent(ExpatParser parser, XML_Content *cp)
{
  static const XML_Char quant_chars[] = { '\0', '?', '*', '+' };
  XML_Char sep;
  unsigned int i;

  switch (cp->type) {
  case XML_CTYPE_NAME:
    if (writeCharacterBufferString(parser, cp->name) == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
    break;
  case XML_CTYPE_SEQ:
  case XML_CTYPE_CHOICE:
    if (writeCharacterBufferChar(parser, '(') == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }

    /* Now loop over the children */
    sep = (cp->type == XML_CTYPE_SEQ ? ',' : '|');
    for (i = 0; i < cp->numchildren; i++) {
      XML_Content *child = &cp->children[i];
      if (i > 0) {
        if (writeCharacterBufferChar(parser, sep) == EXPAT_STATUS_ERROR) {
          return EXPAT_STATUS_ERROR;
        }
      }
      if (stringifyContent(parser, child) == EXPAT_STATUS_ERROR) {
        return EXPAT_STATUS_ERROR;
      }
    }

    if (writeCharacterBufferChar(parser, ')') == EXPAT_STATUS_ERROR) {
      return EXPAT_STATUS_ERROR;
    }
    break;
  default:
    PyErr_SetString(PyExc_SystemError, "invalid content type");
    return Expat_FatalError(parser);
  }

  return writeCharacterBufferChar(parser, quant_chars[cp->quant]);
}

static PyObject *stringifyModel(ExpatParser parser, XML_Content *model)
{
  static const XML_Char start[] = { '(', '#', 'P', 'C', 'D', 'A', 'T', 'A' };
  static const XML_Char close[] = { ')', '*' };
  PyObject *result;
  unsigned int i;

  switch (model->type) {
  case XML_CTYPE_EMPTY:
    Py_INCREF(content_model_empty);
    return content_model_empty;
  case XML_CTYPE_ANY:
    Py_INCREF(content_model_any);
    return content_model_any;
  case XML_CTYPE_MIXED:
    if (model->numchildren == 0) {
      Py_INCREF(content_model_pcdata);
      return content_model_pcdata;
    }
    if (writeCharacterBuffer(parser, start, 8) == EXPAT_STATUS_ERROR) {
      return NULL;
    }
    /* Now loop over the Names */
    for (i = 0; i < model->numchildren; i++) {
      XML_Content *cp = &model->children[i];
      if (writeCharacterBufferChar(parser, '|') == EXPAT_STATUS_ERROR) {
        return NULL;
      }
      if (writeCharacterBufferString(parser, cp->name) == EXPAT_STATUS_ERROR) {
        return NULL;
      }
    }
    if (writeCharacterBuffer(parser, close, 2) == EXPAT_STATUS_ERROR) {
      return NULL;
    }
    break;
  default:
    if (stringifyContent(parser, model) == EXPAT_STATUS_ERROR) {
      return NULL;
    }
  }

  result = Unicode_FromXMLCharAndSize(parser->buffer, parser->buffer_used);
  parser->buffer_used = 0;
  return result;
}

void expat_ElementDecl(ExpatParser parser, const XML_Char *name,
                       XML_Content *content)
{
  PyObject *element_name, *element_type, *model_string;
  PyObject *model = NULL;

  Debug_ParserFunctionCall(expat_ElementDecl, parser);

#if defined(DEBUG_CALLBACKS)
  fprintf(stderr, "*** ElementDecl(name=");
  XMLChar_Print(stderr, name);
  fprintf(stderr, ", content=");
  model_string = stringifyModel(parser, content);
  PyObject_Print(model_string, stderr, Py_PRINT_RAW);
  Py_DECREF(model_string);
  fprintf(stderr, ")\n");
#endif

  element_name = makeUnicode(parser, name);
  if (element_name == NULL) {
    goto error;
  }

  switch (content->type) {
  case XML_CTYPE_EMPTY:
    model = ContentModel_New();
    if (model == NULL) {
      goto error;
    }
    if (ContentModel_AddEpsilonMove(model, 0, 1) < 0) {
      goto error;
    }
    if (ContentModel_AddTransition(model, empty_event, 0, 1) < 0) {
      goto error;
    }
    break;
  case XML_CTYPE_ANY:
    model = NULL;
    break;
  case XML_CTYPE_MIXED:
    content->quant = XML_CQUANT_REP;
  case XML_CTYPE_CHOICE:
  case XML_CTYPE_SEQ:
    model = ContentModel_New();
    if (model == NULL) {
      goto error;
    }
    if (parseContent(parser, model, content, 0, 1) == EXPAT_STATUS_ERROR) {
      goto finally;
    }
    break;
  default:
    PyErr_Format(PyExc_SystemError, "invalid content type %d", content->type);
    goto error;
  }

  /* see if an ElementType has already been created by an ATTLIST decl */
  element_type = PyDict_GetItem(parser->context->dtd->used_elements,
                                element_name);
  if (element_type == NULL) {
    element_type = ElementType_New(element_name, model);
    if (element_type == NULL) {
      goto error;
    }
  } else {
    /* Set the content model */
    if (ElementType_SetContentModel(element_type, model) < 0) {
      goto error;
    }

    /* removed it from the set of pre-declared elements */
    Py_INCREF(element_type);
    if (PyDict_DelItem(parser->context->dtd->used_elements,
                       element_name) < 0) {
      Py_DECREF(element_type);
      goto error;
    }
  }

  switch (Validator_AddElementType(parser->context->dtd->validator,
                                   element_type)) {
  case 0:
    Py_DECREF(element_type);
    if (Expat_ReportError(parser, "DUPLICATE_ELEMENT_DECL", "{sO}",
                          "element", element_name) == EXPAT_STATUS_ERROR) {
      goto error;
    }
    break;
  case 1:
    Py_DECREF(element_type);
    break;
  default:
    Py_DECREF(element_type);
    goto error;
  }

  if (parser->element_decl_handler) {
    model_string = stringifyModel(parser, content);
    if (model_string == NULL) goto error;
    parser->element_decl_handler(parser->userState, element_name,
                                 model_string);
    Py_DECREF(model_string);
  }

 finally:
  Py_XDECREF(model);
  XML_FreeContentModel(parser->context->parser, content);
  return;

 error:
  Expat_FatalError(parser);
  goto finally;
}

static PyObject *parseEnumeration(ExpatParser parser,
                                  const XML_Char *enumeration)
{
  const XML_Char *p;
  PyObject *items, *item;
  Py_ssize_t nitems;

  Debug_ParserFunctionCall(parseEnumeration, parser);

  /* find the number of individual items */
  for (nitems = 1, p = enumeration; *p; p++) {
    if (*p == '|') nitems++;
  }

  items = PyTuple_New(nitems);
  if (items == NULL) {
    return items;
  }

  for (nitems = 0, p = enumeration; *p++ != ')'; nitems++) {
    const XML_Char *start = p;
    /* find the end of an item */
    while (*p != '|' && *p != ')') {
      p++;
    }
    item = makeUnicodeSize(parser, start, p - start);
    if (item == NULL) {
      Py_DECREF(items);
      return NULL;
    }
    Py_INCREF(item);
    PyTuple_SET_ITEM(items, nitems, item);
  };

  return items;
}

void expat_AttlistDecl(ExpatParser parser, const XML_Char *elname,
                       const XML_Char *attname, const XML_Char *att_type,
                       const XML_Char *dflt, int isrequired)
{
  DTD *dtd = parser->context->dtd;
  AttributeDecl decl;
  AttributeType type;
  PyObject *element_type, *element_name, *attribute_name, *default_value;
  PyObject *allowed_values;
  Py_ssize_t i;

  Debug_ParserFunctionCall(expat_AttlistDecl, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** AttlistDecl(elname=");
  XMLChar_Print(stderr, elname);
  fprintf(stderr, ", attname=");
  XMLChar_Print(stderr, attname);
  fprintf(stderr, ", att_type=");
  XMLChar_Print(stderr, att_type);
  fprintf(stderr, ", dflt=");
  XMLChar_Print(stderr, dflt);
  fprintf(stderr, ", isrequired=%d)\n", isrequired);
#endif

  element_name = makeUnicode(parser, elname);
  if (element_name == NULL) {
    Expat_FatalError(parser);
    return;
  }

  attribute_name = makeUnicode(parser, attname);
  if (attribute_name == NULL) {
    Expat_FatalError(parser);
    return;
  }

  if (dflt == NULL) {
    decl = isrequired ? ATTRIBUTE_DECL_REQUIRED : ATTRIBUTE_DECL_IMPLIED;
    default_value = Py_None;
  } else {
    decl = isrequired ? ATTRIBUTE_DECL_FIXED : ATTRIBUTE_DECL_DEFAULT;
    default_value = makeUnicode(parser, dflt);
    if (default_value == NULL) {
      Expat_FatalError(parser);
      return;
    }
  }

  /* This is simplified by the fact that Expat already checks validity */
  allowed_values = NULL;
  switch (*att_type) {
  case 'C': /* CDATA */
    type = ATTRIBUTE_TYPE_CDATA;
    break;
  case 'I': /* ID, IDREF, IDREFS */
    if (att_type[2] == 0) {
      type = ATTRIBUTE_TYPE_ID;
      /* VC: ID Attribute Default */
      if (dflt) {
        if (Expat_ReportError(parser, "ID_ATTRIBUTE_DEFAULT", NULL)
            == EXPAT_STATUS_ERROR) {
          return;
        }
      }
    } else if (att_type[5] == 0) {
      type = ATTRIBUTE_TYPE_IDREF;
    } else {
      type = ATTRIBUTE_TYPE_IDREFS;
    }
    break;
  case 'E': /* ENTITY, ENTITIES */
    if (att_type[6] == 0) {
      type = ATTRIBUTE_TYPE_ENTITY;
    } else {
      type = ATTRIBUTE_TYPE_ENTITIES;
    }
    break;
  case 'N': /* NMTOKEN, NMTOKENS, NOTATION */
    if (att_type[1] == 'M') {
      if (att_type[7] == 0) {
        type = ATTRIBUTE_TYPE_NMTOKEN;
      } else {
        type = ATTRIBUTE_TYPE_NMTOKENS;
      }
    } else {
      type = ATTRIBUTE_TYPE_NOTATION;
      allowed_values = parseEnumeration(parser, att_type+8);
      if (allowed_values == NULL) {
        Expat_FatalError(parser);
        return;
      }
      for (i = PyTuple_GET_SIZE(allowed_values); i-- > 0;) {
        PyObject *notation = PyTuple_GET_ITEM(allowed_values, i);
        if (PyDict_GetItem(dtd->notations, notation) == NULL) {
          if (PyDict_SetItem(dtd->used_notations, notation,
                             attribute_name) < 0) {
            Py_DECREF(allowed_values);
            Expat_FatalError(parser);
            return;
          }
        }
      }
    }
    break;
  default: /* Enumeration */
    type = ATTRIBUTE_TYPE_ENUMERATION;
    allowed_values = parseEnumeration(parser, att_type);
    if (allowed_values == NULL) {
      Expat_FatalError(parser);
      return;
    }
    break;
  }

  /* xml:space, when declared, MUST be given as an enumerated type whose
   * values are one or both of "default" and "preserve". */
  switch (PyObject_RichCompareBool(attribute_name, xml_space_string, Py_EQ)) {
  case 1:
    if (type != ATTRIBUTE_TYPE_ENUMERATION) {
      if (Expat_ReportError(parser, "XML_SPACE_DECL", NULL)
          == EXPAT_STATUS_ERROR) {
        return;
      }
    } else {
      int cmp = 1;
      for (i = 0; cmp == 1 && i < PyTuple_GET_SIZE(allowed_values); i++) {
        PyObject *value = PyTuple_GET_ITEM(allowed_values, i);
        cmp = PyObject_RichCompareBool(value, default_string, Py_EQ);
        if (cmp == 0) {
          cmp = PyObject_RichCompareBool(value, preserve_string, Py_EQ);
        }
      }
      switch (cmp) {
      case 0: /* value other than "default" or "preserve" in enumeration */
        if (Expat_ReportError(parser, "XML_SPACE_VALUES", NULL)
            == EXPAT_STATUS_ERROR) {
          return;
        }
        /* fall through */
      case 1:
        break;
      default:
        Expat_FatalError(parser);
        return;
      }
    }
    /* fall through */
  case 0:
    break;
  default:
    Expat_FatalError(parser);
    return;
  }

  element_type = Validator_GetElementType(dtd->validator, element_name);
  if (element_type == NULL) {
    /* ATTLIST prior to ELEMENT declaration */
    element_type = PyDict_GetItem(dtd->used_elements, element_name);
    if (element_type == NULL) {
      /* first attribute declaration; create a new ElementType to hold the
       * information.
       */
      element_type = ElementType_New(element_name, NULL);
      if (element_type == NULL) {
        Expat_FatalError(parser);
        return;
      }
      if (PyDict_SetItem(dtd->used_elements, element_name, element_type) < 0) {
        Py_DECREF(element_type);
        Expat_FatalError(parser);
        return;
      }
      Py_DECREF(element_type);
    }
  }

  if (type == ATTRIBUTE_TYPE_ID) {
    /* VC: One ID per Element Type */
    PyObject *attributes, *key, *value;
    attributes = ElementType_GET_ATTRIBUTES(element_type);
    i = 0;
    while (PyDict_Next(attributes, &i, &key, &value)) {
      if (AttributeType_GET_TYPE(value) == ATTRIBUTE_TYPE_ID) {
        if (Expat_ReportError(parser, "DUPLICATE_ID_DECL", NULL)
            == EXPAT_STATUS_ERROR) {
          return;
        }
        /* Only report once */
        break;
      }
    }
  }

  /* add the attribute decl to the ElementType */
  switch (ElementType_AddAttribute(element_type, attribute_name, type, decl,
                                   allowed_values, default_value)) {
  case 0:
    /* already declared, issue warning */
    if (Expat_ReportWarning(parser, "ATTRIBUTE_DECLARED", "{sO}",
                            "attr", attribute_name) == EXPAT_STATUS_ERROR) {
      return;
    }
    break;
  case 1:
    if (parser->attribute_decl_handler) {
      PyObject *type_str, *decl_str;

      type_str = makeUnicode(parser, att_type);
      if (type_str == NULL) {
        Expat_FatalError(parser);
        return;
      }

      switch (decl) {
      case ATTRIBUTE_DECL_IMPLIED:
        decl_str = attribute_decl_implied;
        break;
      case ATTRIBUTE_DECL_REQUIRED:
        decl_str = attribute_decl_required;
        break;
      case ATTRIBUTE_DECL_FIXED:
        decl_str = attribute_decl_fixed;
        break;
      default:
        decl_str = Py_None;
      }

      parser->attribute_decl_handler(parser->userState, element_name,
                                     attribute_name, type_str, decl_str,
                                     default_value);
    }
    break;
  default:
    Expat_FatalError(parser);
    break;
  }
  Py_XDECREF(allowed_values);
}

void expat_EntityDecl(ExpatParser parser, const XML_Char *entityName,
                      int is_parameter_entity, const XML_Char *value,
                      int value_length, const XML_Char *base,
                      const XML_Char *systemId, const XML_Char *publicId,
                      const XML_Char *notationName)
{
  DTD *dtd = parser->context->dtd;
  PyObject *python_entityName;
  int len;

  Debug_ParserFunctionCall(expat_EntityDecl, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** EntityDecl(entityName=");
  XMLChar_Print(stderr, entityName);
  fprintf(stderr, ", is_parameter_entity=%d, value=", is_parameter_entity);
  XMLChar_NPrint(stderr, value, value_length);
  fprintf(stderr, ", base=");
  XMLChar_Print(stderr, base);
  fprintf(stderr, ", systemId=");
  XMLChar_Print(stderr, systemId);
  fprintf(stderr, ", publicId=");
  XMLChar_Print(stderr, publicId);
  fprintf(stderr, ", notationName=");
  XMLChar_Print(stderr, notationName);
  fprintf(stderr, ")\n");
#endif

  len = XMLChar_Len(entityName);
  if (is_parameter_entity) {
    /* parameter entity names begin with '%' */
    XML_Char *temp = (XML_Char *) PyObject_MALLOC((len+1) * sizeof(XML_Char));
    if (temp == NULL) {
      Expat_FatalError(parser);
      return;
    }
    temp[0] = (XML_Char) '%';
    memcpy(temp+1, entityName, len * sizeof(XML_Char));
    python_entityName = makeUnicodeSize(parser, temp, len+1);
    PyObject_FREE(temp);
  } else {
    python_entityName = makeUnicodeSize(parser, entityName, len);
  }
  if (python_entityName == NULL) {
    Expat_FatalError(parser);
    return;
  }

  if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
    if (PyDict_GetItem(dtd->entities, python_entityName)) {
      /* If the same entity is declared more than once, the first declaration
       * encountered is binding. */
      /* NOTE: no need to test return status of this as the handler is going
       * to exit regardless. */
      Expat_ReportWarning(parser, "ENTITY_DECLARED", "{sO}",
                          "entity", python_entityName);
      return;
    }
  }

  if (value == NULL) {
    /* external entity decl */
    PyObject *python_notationName;
    PyObject *python_base;
    PyObject *python_systemId;
    PyObject *python_publicId;

    python_base = Unicode_FromXMLChar(base);
    python_systemId = Unicode_FromXMLChar(systemId);
    if (publicId) {
      python_publicId = Unicode_FromXMLChar(publicId);
    } else {
      Py_INCREF(Py_None);
      python_publicId = Py_None;
    }
    if (python_base == NULL
        || python_systemId == NULL
        || python_publicId == NULL) {
      Py_XDECREF(python_publicId);
      Py_XDECREF(python_systemId);
      Py_XDECREF(python_base);
      Expat_FatalError(parser);
      return;
    }
    python_systemId = PyObject_CallFunction(absolutize_function, "NN",
                                            python_systemId, python_base);
    if (python_systemId == NULL) {
      Expat_FatalError(parser);
      return;
    }

    if (notationName == NULL) {
      python_notationName = Py_None;
      if (parser->external_entity_decl_handler) {
        parser->external_entity_decl_handler(parser->userState,
                                             python_entityName,
                                             python_publicId,
                                             python_systemId);
      }
    } else {
      python_notationName = makeUnicode(parser, notationName);
      if (python_notationName == NULL) {
        Py_DECREF(python_publicId);
        Py_DECREF(python_systemId);
        Expat_FatalError(parser);
        return;
      }
      if (parser->unparsed_entity_decl_handler) {
        parser->unparsed_entity_decl_handler(parser->userState,
                                             python_entityName,
                                             python_publicId,
                                             python_systemId,
                                             python_notationName);
      }
    }
    Py_DECREF(python_publicId);
    Py_DECREF(python_systemId);

    if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
      if (notationName != NULL) {
        /* unparsed entity */
        if (PyDict_GetItem(dtd->notations, python_notationName) == NULL) {
          if (PyDict_SetItem(dtd->used_notations, python_notationName,
                             python_entityName) < 0) {
            Expat_FatalError(parser);
            return;
          }
        }
      }
      if (PyDict_SetItem(dtd->entities, python_entityName,
                         python_notationName) < 0) {
        Expat_FatalError(parser);
        return;
      }
    }
  } else {
    /* internal entity decl */
    PyObject *python_value = Unicode_FromXMLCharAndSize(value, value_length);
    if (python_value == NULL) {
      Expat_FatalError(parser);
      return;
    }
    if (parser->internal_entity_decl_handler) {
      parser->internal_entity_decl_handler(parser->userState,
                                           python_entityName,
                                           python_value);
    }
    Py_DECREF(python_value);
  }
}

void expat_NotationDecl(ExpatParser parser, const XML_Char *notationName,
                        const XML_Char *base, const XML_Char *systemId,
                        const XML_Char *publicId)
{
  DTD *dtd = parser->context->dtd;
  PyObject *python_notationName;

  Debug_ParserFunctionCall(expat_NotationDecl, parser);

#ifdef DEBUG_CALLBACKS
  fprintf(stderr, "*** NotationDecl(notationName=");
  XMLChar_Print(stderr, notationName);
  fprintf(stderr, ", base=");
  XMLChar_Print(stderr, base);
  fprintf(stderr, ", systemId=");
  XMLChar_Print(stderr, systemId);
  fprintf(stderr, ", publicId=");
  XMLChar_Print(stderr, publicId);
  fprintf(stderr, ")\n");
#endif

  python_notationName = Unicode_FromXMLChar(notationName);
  if (python_notationName == NULL) {
    Expat_FatalError(parser);
    return;
  }

  if (Expat_HasFlag(parser, EXPAT_FLAG_VALIDATE)) {
    if (PyDict_SetItem(dtd->notations, python_notationName, Py_True) < 0) {
      Py_DECREF(python_notationName);
      Expat_FatalError(parser);
      return;
    }
    if (PyDict_GetItem(dtd->used_notations, python_notationName) != NULL) {
      if (PyDict_DelItem(dtd->used_notations, python_notationName) < 0) {
        Py_DECREF(python_notationName);
        Expat_FatalError(parser);
        return;
      }
    }
  }

  if (parser->notation_decl_handler) {
    PyObject *python_publicId, *python_systemId;
    if (systemId) {
      python_systemId = Unicode_FromXMLChar(systemId);
    } else {
      Py_INCREF(Py_None);
      python_systemId = Py_None;
    }
    if (publicId) {
      python_publicId = Unicode_FromXMLChar(publicId);
    } else {
      Py_INCREF(Py_None);
      python_publicId = Py_None;
    }
    if (python_publicId == NULL || python_systemId == NULL) {
      Py_XDECREF(python_publicId);
      Py_XDECREF(python_systemId);
      Py_DECREF(python_notationName);
      Expat_FatalError(parser);
      return;
    }

    parser->notation_decl_handler(parser->userState, python_notationName,
                                  python_publicId, python_systemId);

    Py_DECREF(python_publicId);
    Py_DECREF(python_systemId);
  }

  Py_DECREF(python_notationName);
}

/* internal handler */
int expat_ExternalEntityRef(XML_Parser p, const XML_Char *context,
                            const XML_Char *base, const XML_Char *systemId,
                            const XML_Char *publicId)
{
  ExpatParser parser = (ExpatParser) XML_GetUserData(p);
  PyObject *python_base, *python_systemId, *python_publicId, *source;
  XML_Parser new_parser;
  ExpatStatus status;
  enum XML_Status result = XML_STATUS_OK;

  Debug_ParserFunctionCall(expat_ExternalEntityRef, parser);

#if defined(DEBUG_CALLBACKS)
  fprintf(stderr, "*** ExternalEntityRef(context=");
  XMLChar_Print(stderr, context);
  fprintf(stderr, ", base=");
  XMLChar_Print(stderr, base);
  fprintf(stderr, ", systemId=");
  XMLChar_Print(stderr, systemId);
  fprintf(stderr, ", publicId=");
  XMLChar_Print(stderr, publicId);
  fprintf(stderr, ")\n");
#endif

  python_base = Unicode_FromXMLChar(base);
  python_systemId = Unicode_FromXMLChar(systemId);
  if (publicId) {
    python_publicId = Unicode_FromXMLChar(publicId);
  } else {
    Py_INCREF(Py_None);
    python_publicId = Py_None;
  }
  if (python_base == NULL
      || python_systemId == NULL
      || python_publicId == NULL) {
    Py_XDECREF(python_publicId);
    Py_XDECREF(python_systemId);
    Py_XDECREF(python_base);
    Expat_FatalError(parser);
    return result;
  }
  python_systemId = PyObject_CallFunction(absolutize_function, "NN",
                                          python_systemId, python_base);
  if (python_systemId == NULL) {
    Expat_FatalError(parser);
    return result;
  }

  new_parser = XML_ExternalEntityParserCreate(p, context, NULL);
  if (new_parser == NULL) {
    Py_DECREF(python_publicId);
    Py_DECREF(python_systemId);
    PyErr_NoMemory();
    Expat_FatalError(parser);
    return result;
  }

  source = PyObject_CallMethod(parser->context->source, "resolveEntity", "NN",
                               python_publicId, python_systemId);
  if (source == NULL) {
    XML_ParserFree(new_parser);
    Expat_FatalError(parser);
    return result;
  }

  if (beginContext(parser, new_parser, source) == NULL) {
    Py_DECREF(source);
    XML_ParserFree(new_parser);
    Expat_FatalError(parser);
    return result;
  }

  /* copy DTD from parent parsing context */
  parser->context->dtd = parser->context->next->dtd;

  status = doParse(parser);

  Debug_ReturnStatus(expat_ExternalEntityRef, status);

  switch (status) {
  case EXPAT_STATUS_OK:
    /* remove DTD pointer to prevent "double free" */
    parser->context->dtd = NULL;
    endContext(parser);
    break;
  case EXPAT_STATUS_ERROR:
    /* remove DTD pointer to prevent "double free" */
    parser->context->dtd = NULL;
    endContext(parser);
    /* stop the parent parser */
    result = XML_StopParser(p, 0);
    break;
  case EXPAT_STATUS_SUSPENDED:
    /* suspend the parent parser */
    result = XML_StopParser(p, 1);
  }

  return result;
}

/* unknown encoding support */

typedef struct {
  PyObject *decoder;
  int length[256];
} UnknownEncoding;

static int encoding_convert(void *userData, const char *bytes)
{
  UnknownEncoding *encoding = (UnknownEncoding *) userData;
  PyObject *result;
  int ch;

  result = PyObject_CallFunction(encoding->decoder, "s#s", bytes,
                                 encoding->length[(unsigned char)(*bytes)],
                                 "strict");
  if (result == NULL)
    return -1;

  if (PyTuple_Check(result) && PyTuple_GET_SIZE(result) == 2 &&
      PyUnicode_Check(PyTuple_GET_ITEM(result, 0))) {
    ch = (int)*PyUnicode_AS_UNICODE(PyTuple_GET_ITEM(result, 0));
  }
  else {
    PyErr_SetString(PyExc_TypeError,
                    "decoder must return a tuple (unicode, integer)");
    ch = -1;
  }
  Py_DECREF(result);

  return ch;
}

static void encoding_release(void *userData)
{
  UnknownEncoding *encoding = (UnknownEncoding *) userData;

  Py_DECREF(encoding->decoder);
  PyObject_FREE(encoding);
}

static const unsigned char template[] = {
  0x00,  0x01,  0x02,  0x03,  0x04,  0x05,  0x06,  0x07,
  0x08,  0x09,  0x0A,  0x0B,  0x0C,  0x0D,  0x0E,  0x0F,
  0x10,  0x11,  0x12,  0x13,  0x14,  0x15,  0x16,  0x17,
  0x18,  0x19,  0x1A,  0x1B,  0x1C,  0x1D,  0x1E,  0x1F,
  0x20,  0x21,  0x22,  0x23,  0x24,  0x25,  0x26,  0x27,
  0x28,  0x29,  0x2A,  0x2B,  0x2C,  0x2D,  0x2E,  0x2F,
  0x30,  0x31,  0x32,  0x33,  0x34,  0x35,  0x36,  0x37,
  0x38,  0x39,  0x3A,  0x3B,  0x3C,  0x3D,  0x3E,  0x3F,
  0x40,  0x41,  0x42,  0x43,  0x44,  0x45,  0x46,  0x47,
  0x48,  0x49,  0x4A,  0x4B,  0x4C,  0x4D,  0x4E,  0x4F,
  0x50,  0x51,  0x52,  0x53,  0x54,  0x55,  0x56,  0x57,
  0x58,  0x59,  0x5A,  0x5B,  0x5C,  0x5D,  0x5E,  0x5F,
  0x60,  0x61,  0x62,  0x63,  0x64,  0x65,  0x66,  0x67,
  0x68,  0x69,  0x6A,  0x6B,  0x6C,  0x6D,  0x6E,  0x6F,
  0x70,  0x71,  0x72,  0x73,  0x74,  0x75,  0x76,  0x77,
  0x78,  0x79,  0x7A,  0x7B,  0x7C,  0x7D,  0x7E,  0x7F,
  0x80,  0x81,  0x82,  0x83,  0x84,  0x85,  0x86,  0x87,
  0x88,  0x89,  0x8A,  0x8B,  0x8C,  0x8D,  0x8E,  0x8F,
  0x90,  0x91,  0x92,  0x93,  0x94,  0x95,  0x96,  0x97,
  0x98,  0x99,  0x9A,  0x9B,  0x9C,  0x9D,  0x9E,  0x9F,
  0xA0,  0xA1,  0xA2,  0xA3,  0xA4,  0xA5,  0xA6,  0xA7,
  0xA8,  0xA9,  0xAA,  0xAB,  0xAC,  0xAD,  0xAE,  0xAF,
  0xB0,  0xB1,  0xB2,  0xB3,  0xB4,  0xB5,  0xB6,  0xB7,
  0xB8,  0xB9,  0xBA,  0xBB,  0xBC,  0xBD,  0xBE,  0xBF,
  0xC0,  0xC1,  0xC2,  0xC3,  0xC4,  0xC5,  0xC6,  0xC7,
  0xC8,  0xC9,  0xCA,  0xCB,  0xCC,  0xCD,  0xCE,  0xCF,
  0xD0,  0xD1,  0xD2,  0xD3,  0xD4,  0xD5,  0xD6,  0xD7,
  0xD8,  0xD9,  0xDA,  0xDB,  0xDC,  0xDD,  0xDE,  0xDF,
  0xE0,  0xE1,  0xE2,  0xE3,  0xE4,  0xE5,  0xE6,  0xE7,
  0xE8,  0xE9,  0xEA,  0xEB,  0xEC,  0xED,  0xEE,  0xEF,
  0xF0,  0xF1,  0xF2,  0xF3,  0xF4,  0xF5,  0xF6,  0xF7,
  0xF8,  0xF9,  0xFA,  0xFB,  0xFC,  0xFD,  0xFE,  0xFF,
  /* terminator */
  0x00
};

static int expat_UnknownEncodingHandler(void *encodingHandlerData,
                                        const XML_Char *name,
                                        XML_Encoding *info)
{
  PyObject *_u_name, *_s_name;
  PyObject *encoder, *decoder;
  PyObject *result;
  Py_UNICODE unichr;
  int i;
  UnknownEncoding *encoding;

  _u_name = Unicode_FromXMLChar(name);
  if (_u_name == NULL)
    return XML_STATUS_ERROR;

  /* Encodings must be ASCII per the XML spec */
  _s_name = PyUnicode_EncodeASCII(PyUnicode_AS_UNICODE(_u_name),
                                  PyUnicode_GET_SIZE(_u_name),
                                  NULL);
  Py_DECREF(_u_name);
  if (_s_name == NULL)
    return XML_STATUS_ERROR;

  encoder = PyCodec_Encoder(PyString_AS_STRING(_s_name));
  decoder = PyCodec_Decoder(PyString_AS_STRING(_s_name));
  Py_DECREF(_s_name);
  if (encoder == NULL || decoder == NULL) {
    Py_XDECREF(encoder);
    Py_XDECREF(decoder);
    return XML_STATUS_ERROR;
  }

  /* Check if we can use the direct replacement method (8-bit encodings) */
  result = PyObject_CallFunction(decoder, "s#s", template, 256, "replace");
  if (result == NULL) {
    PyErr_Clear();
  } else if (PyTuple_Check(result) && PyTuple_GET_SIZE(result) == 2 &&
             PyUnicode_Check(PyTuple_GET_ITEM(result, 0)) &&
             PyUnicode_GET_SIZE(PyTuple_GET_ITEM(result, 0)) == 256) {
    /* we have a valid 8-bit encoding */
    Py_UNICODE *unistr = PyUnicode_AS_UNICODE(PyTuple_GET_ITEM(result, 0));
    for (i = 0; i < 256; i++) {
      unichr = unistr[i];
      if (unichr == Py_UNICODE_REPLACEMENT_CHARACTER)
        info->map[i] = -1;
      else
        info->map[i] = unichr;
    }
    Py_DECREF(result);
    Py_DECREF(encoder);
    Py_DECREF(decoder);
    return XML_STATUS_OK;
  } else {
    Py_DECREF(result);
  }

  /* Use the convert function method (multibyte encodings) */
  encoding = (UnknownEncoding *) PyObject_MALLOC(sizeof(UnknownEncoding));
  if (encoding == NULL) {
    Py_DECREF(encoder);
    Py_DECREF(decoder);
    return XML_STATUS_ERROR;
  }

  for (unichr = 0; unichr <= 0xFFFD; unichr++) {
    result = PyObject_CallFunction(encoder, "u#s", &unichr, 1, "ignore");
    if (result == NULL || !PyTuple_Check(result) ||
        PyTuple_GET_SIZE(result) != 2) {
      Py_XDECREF(result);
      Py_DECREF(encoder);
      Py_DECREF(decoder);
      PyObject_FREE(encoding);
      return XML_STATUS_ERROR;
    }

    /* treat non-string results as invalid value */
    if (PyString_Check(PyTuple_GET_ITEM(result, 0))) {
      int c = (unsigned char) *PyString_AS_STRING(PyTuple_GET_ITEM(result, 0));
      int n = PyString_GET_SIZE(PyTuple_GET_ITEM(result, 0));
      if (n == 1) {
        /* one-to-one replacement */
        info->map[c] = unichr;
      }
      else if (n > 1) {
        /* multibyte replacement */
        info->map[c] = -n;
      }
      encoding->length[c] = n;
    }
    Py_DECREF(result);
  }

  /* consume the reference */
  encoding->decoder = decoder;
  info->data = (void *) encoding;
  info->convert = encoding_convert;
  info->release = encoding_release;

  Py_DECREF(encoder);
  return XML_STATUS_OK;
}


/** External Routines *************************************************/


ExpatParser Expat_ParserCreate(void *userState)
{
  ExpatParser parser;

  if (expat_library_error != NULL) {
    PyErr_SetObject(PyExc_RuntimeError, expat_library_error);
    return NULL;
  }

  parser = (ExpatParser) PyObject_MALLOC(sizeof(struct ExpatParserStruct));
  if (parser == NULL) {
    PyErr_NoMemory();
    return NULL;
  }
  memset(parser, 0, sizeof(struct ExpatParserStruct));

  /* caching of split-names */
  if ((parser->name_cache = HashTable_New()) == NULL) {
    Expat_ParserFree(parser);
    return NULL;
  }

  /* interning table for XML_Char -> PyUnicodeObjects */
  if ((parser->unicode_cache = HashTable_New()) == NULL) {
    Expat_ParserFree(parser);
    return NULL;
  }

  /* character data buffering */
  if ((parser->buffer = PyMem_New(XML_Char, XMLCHAR_BUFSIZ)) == NULL) {
    PyErr_NoMemory();
    Expat_ParserFree(parser);
    return NULL;
  }
  parser->buffer_size = XMLCHAR_BUFSIZ;
  parser->buffer_used = 0;

  /* attribute buffering */
  /* parser->attrs == NULL and parser->attrs_size == 0 already, so no
   * addition work is needed as the setup happens in expat_StartElement
   * as soon as the buffer is used.
   */

  /* base URI stack */
  if ((parser->xml_base_stack = Stack_New()) == NULL) {
    Expat_ParserFree(parser);
    return NULL;
  }
  Stack_Push(parser->xml_base_stack, Py_None);

  /* language stack */
  if ((parser->xml_lang_stack = Stack_New()) == NULL) {
    Expat_ParserFree(parser);
    return NULL;
  }
  Stack_Push(parser->xml_lang_stack, Py_None);

  /* xml:space='preserve' state stack */
  if ((parser->xml_space_stack = Stack_New()) == NULL) {
    Expat_ParserFree(parser);
    return NULL;
  }
  Stack_Push(parser->xml_space_stack, Py_False); /* xml:space='default' */

  /* whitespace preserving state stack */
  if ((parser->preserve_whitespace_stack = Stack_New()) == NULL) {
    Expat_ParserFree(parser);
    return NULL;
  }
  Stack_Push(parser->preserve_whitespace_stack, Py_True);

  parser->userState = userState;

  parser->parameter_entity_parsing = 0;
  parser->process_xincludes = 1;

  return parser;
}


void Expat_ParserFree(ExpatParser parser)
{

  if (parser->context) {
    destroyContexts(parser);
  }
  /* set after creation */
  if (parser->whitespace_rules) {
    freeWhitespaceRules(parser->whitespace_rules);
    parser->whitespace_rules = NULL;
  }

  if (parser->preserve_whitespace_stack) {
    Stack_Del(parser->preserve_whitespace_stack);
    parser->preserve_whitespace_stack = NULL;
  }

  if (parser->xml_space_stack) {
    Stack_Del(parser->xml_space_stack);
    parser->xml_space_stack = NULL;
  }

  if (parser->xml_lang_stack) {
    Stack_Del(parser->xml_lang_stack);
    parser->xml_lang_stack = NULL;
  }

  if (parser->xml_base_stack) {
    Stack_Del(parser->xml_base_stack);
    parser->xml_base_stack = NULL;
  }

  if (parser->attrs) {
    PyMem_Del(parser->attrs);
    parser->attrs = NULL;
  }

  if (parser->buffer) {
    PyMem_Del(parser->buffer);
    parser->buffer = NULL;
  }

  if (parser->unicode_cache) {
    HashTable_Del(parser->unicode_cache);
    parser->unicode_cache = NULL;
  }

  if (parser->name_cache) {
    HashTable_Del(parser->name_cache);
    parser->name_cache = NULL;
  }

  PyObject_FREE(parser);
}


ExpatStatus Expat_ParserSuspend(ExpatParser parser)
{
  Context *context = parser->context;
  if (context) {
    if (XML_StopParser(context->parser, 1) == XML_STATUS_ERROR) {
      processExpatError(parser);
      return Expat_FatalError(parser);
    }
  }
  return EXPAT_STATUS_OK;
}


void _Expat_ParserStop(ExpatParser parser, char *filename, int lineno)
{
  if (parser->context) {
    _Expat_FatalError(parser, filename, lineno);
  }
}


PyObject *Expat_GetBase(ExpatParser parser)
{
  PyObject *base;

  base = Stack_PEEK(parser->xml_base_stack);
  Py_INCREF(base);
  return base;
}


int Expat_GetLineNumber(ExpatParser parser)
{
  int line;

  if (parser->context)
    line = XML_GetCurrentLineNumber(parser->context->parser);
  else
    line = -1;

  return line;
}


int Expat_GetColumnNumber(ExpatParser parser)
{
  int column;

  if (parser->context)
    column = XML_GetCurrentColumnNumber(parser->context->parser);
  else
    column = -1;

  return column;
}


/* returns 1 if parsing (suspended or not), 0 otherwise */
int Expat_GetParsingStatus(ExpatParser parser)
{
  static XML_ParsingStatus status;
  if (parser->context) {
    XML_GetParsingStatus(parser->context->parser, &status);
    return (status.parsing == XML_PARSING || status.parsing == XML_SUSPENDED);
  }
  return 0;
}


void Expat_SetStartDocumentHandler(ExpatParser parser,
                                   ExpatStartDocumentHandler handler)
{
  parser->start_document_handler = handler;
}


void Expat_SetEndDocumentHandler(ExpatParser parser,
                                 ExpatEndDocumentHandler handler)
{
  parser->end_document_handler = handler;
}


void Expat_SetStartElementHandler(ExpatParser parser,
                                  ExpatStartElementHandler handler)
{
  parser->start_element_handler = handler;
}


void Expat_SetEndElementHandler(ExpatParser parser,
                                ExpatEndElementHandler handler)
{
  parser->end_element_handler = handler;
}


void Expat_SetStartNamespaceDeclHandler(ExpatParser parser,
                                        ExpatStartNamespaceDeclHandler handler)
{
  parser->start_namespace_decl_handler = handler;
}


void Expat_SetEndNamespaceDeclHandler(ExpatParser parser,
                                      ExpatEndNamespaceDeclHandler handler)
{
  parser->end_namespace_decl_handler = handler;
}


void Expat_SetCharacterDataHandler(ExpatParser parser,
                                   ExpatCharacterDataHandler handler)
{
  parser->character_data_handler = handler;
}


void Expat_SetProcessingInstructionHandler(ExpatParser parser,
                                           ExpatProcessingInstructionHandler handler)
{
  parser->processing_instruction_handler = handler;
}


void Expat_SetCommentHandler(ExpatParser parser,
                             ExpatCommentHandler handler)
{
  parser->comment_handler = handler;
}


void Expat_SetStartDoctypeDeclHandler(ExpatParser parser,
                                      ExpatStartDoctypeDeclHandler handler)
{
  parser->start_doctype_decl_handler = handler;
}


void Expat_SetEndDoctypeDeclHandler(ExpatParser parser,
                                    ExpatEndDoctypeDeclHandler handler)
{
  parser->end_doctype_decl_handler = handler;
}


void Expat_SetUnparsedEntityDeclHandler(ExpatParser parser,
                                        ExpatUnparsedEntityDeclHandler handler)
{
  parser->unparsed_entity_decl_handler = handler;
}


void Expat_SetSkippedEntityHandler(ExpatParser parser,
                                   ExpatSkippedEntityHandler handler)
{
  parser->skipped_entity_handler = handler;
}


void Expat_SetStartCdataSectionHandler(ExpatParser parser,
                                       ExpatStartCdataSectionHandler handler)
{
  parser->start_cdata_section_handler = handler;
}


void Expat_SetEndCdataSectionHandler(ExpatParser parser,
                                     ExpatEndCdataSectionHandler handler)
{
  parser->end_cdata_section_handler = handler;
}


void Expat_SetIgnorableWhitespaceHandler(ExpatParser parser,
                                         ExpatIgnorableWhitespaceHandler handler)
{
  parser->ignorable_whitespace_handler = handler;
}


void Expat_SetWarningHandler(ExpatParser parser,
                             ExpatNotificationHandler handler)
{
  parser->warning_handler = handler;
}


void Expat_SetErrorHandler(ExpatParser parser,
                           ExpatNotificationHandler handler)
{
  parser->error_handler = handler;
}


void Expat_SetFatalErrorHandler(ExpatParser parser,
                                ExpatNotificationHandler handler)
{
  parser->fatal_error_handler = handler;
}


void Expat_SetNotationDeclHandler(ExpatParser parser,
                                  ExpatNotationDeclHandler handler)
{
  parser->notation_decl_handler = handler;
}


void Expat_SetElementDeclHandler(ExpatParser parser,
                                 ExpatElementDeclHandler handler)
{
  parser->element_decl_handler = handler;
}


void Expat_SetAttributeDeclHandler(ExpatParser parser,
                                   ExpatAttributeDeclHandler handler)
{
  parser->attribute_decl_handler = handler;
}


void Expat_SetInternalEntityDeclHandler(ExpatParser parser,
                                        ExpatInternalEntityDeclHandler handler)
{
  parser->internal_entity_decl_handler = handler;
}


void Expat_SetExternalEntityDeclHandler(ExpatParser parser,
                                        ExpatExternalEntityDeclHandler handler)
{
  parser->external_entity_decl_handler = handler;
}


void Expat_SetValidation(ExpatParser parser, int doValidation)
{
  /* do not allowing changing after parsing has begun */
  if (parser->context == NULL) {
    /* normalize value to 1 or 0 */
    parser->dtd_validation = doValidation ? 1 : 0;
  }
}


int Expat_GetValidation(ExpatParser parser)
{
  return parser->dtd_validation;
}


void Expat_SetParamEntityParsing(ExpatParser parser, int doParamEntityParsing)
{
  /* do not allowing changing after parsing has begun */
  if (parser->context == NULL) {
    /* normalize value to 1 or 0 */
    parser->parameter_entity_parsing = doParamEntityParsing ? 1 : 0;
  }
}


int Expat_GetParamEntityParsing(ExpatParser parser)
{
  return parser->parameter_entity_parsing;
}


void Expat_SetXIncludeProcessing(ExpatParser parser, int doXIncludeProcessing)
{
  /* do not allowing changing after parsing has begun */
  if (parser->context == NULL) {
    /* normalize value to 1 or 0 */
    parser->process_xincludes = doXIncludeProcessing ? 1 : 0;
  }
}


int Expat_GetXIncludeProcessing(ExpatParser parser)
{
  return parser->process_xincludes;
}


ExpatStatus Expat_SetWhitespaceRules(ExpatParser parser,
                                     PyObject *stripElements)
{
  /* do not allowing changing after parsing has begun */
  if (parser->context == NULL) {
    WhitespaceRules *rules;
    if (stripElements == NULL) {
      rules = NULL;
    } else {
      rules = createWhitespaceRules(stripElements);
      if (rules == NULL) {
        return EXPAT_STATUS_ERROR;
      }
    }
    if (parser->whitespace_rules != NULL) {
      freeWhitespaceRules(parser->whitespace_rules);
    }
    parser->whitespace_rules = rules;
  }
  return EXPAT_STATUS_OK;
}


int Expat_IsWhitespacePreserving(ExpatParser parser, PyObject *namespaceURI,
                                 PyObject *localName)
{
  return (isWhitespacePreserving(parser, namespaceURI, localName) == Py_True);
}


static ExpatStatus Expat_ContinueParsing(ExpatParser parser,
                                         ExpatStatus (*parse)(ExpatParser))
{
  ExpatStatus status;

  Debug_ParserFunctionCall(Expat_ContinueParsing, parser);

  status = parse(parser);
  if (status == EXPAT_STATUS_SUSPENDED) {
    Debug_ReturnStatus(Expat_ContinueParsing, status);
    return status;
  }
  else if (status == EXPAT_STATUS_OK) {
    if (parser->buffer_used) {
      if (flushCharacterBuffer(parser) == EXPAT_STATUS_ERROR) {
        Debug_ReturnStatus(Expat_ContinueParsing, EXPAT_STATUS_ERROR);
        return Expat_FatalError(parser);
      }
    }
    if (parser->end_document_handler) {
      parser->end_document_handler(parser->userState);
    }
  }

  /* parsing finished, cleanup parsing state */
  destroyContexts(parser);

  Debug_ReturnStatus(Expat_ContinueParsing, status);
  return status;
}


ExpatStatus Expat_ParserResume(ExpatParser parser)
{
  return Expat_ContinueParsing(parser, resumeParsing);
}


static ExpatStatus Expat_StartParsing(ExpatParser parser, XML_Parser xmlParser,
                                      PyObject *source)
{
  Py_INCREF(source);
  if (beginContext(parser, xmlParser, source) == NULL) {
    Py_DECREF(source);
    destroyContexts(parser);
    return EXPAT_STATUS_ERROR;
  }
  setExpatHandlers(parser);

  if (parser->start_document_handler) {
    parser->start_document_handler(parser->userState);
  }

  return Expat_ContinueParsing(parser, doParse);
}


ExpatStatus Expat_ParseDocument(ExpatParser parser, PyObject *source)
{
  XML_Parser expat_parser;
  ExpatStatus status;

  Debug_FunctionCall(Expat_ParseDocument, parser);

  expat_parser = createExpatParser(parser);
  if (expat_parser == NULL) {
    return EXPAT_STATUS_ERROR;
  }

  status = Expat_StartParsing(parser, expat_parser, source);

  Debug_ReturnStatus(Expat_ParseDocument, status);

  return status;
}

/* copied from xmlparse.c
   needed for entity parsing to recognize XML namespace
*/
static const XML_Char implicitContext[] = {
  'x', 'm', 'l', '=', 'h', 't', 't', 'p', ':', '/', '/',
  'w', 'w', 'w', '.', 'w', '3', '.', 'o', 'r', 'g', '/',
  'X', 'M', 'L', '/', '1', '9', '9', '8', '/',
  'n', 'a', 'm', 'e', 's', 'p', 'a', 'c', 'e', '\0'
};

static XML_Char *createExpatContext(PyObject *namespaces)
{
  PyObject *prefix, *uri;
  XML_Char *context, *ptr;
  Py_ssize_t i, used, size, new_len;

  /* convert 'namespaces' to a true dictionary */
  if (PyDict_Check(namespaces)) {
    Py_INCREF(namespaces);
  } else {
    PyObject *dict = PyDict_New();
    if (dict == NULL) return NULL;
    if (PyDict_Merge(dict, namespaces, 1) < 0) {
      Py_DECREF(dict);
      return NULL;
    }
    namespaces = dict;
  }

#define XMLCHAR_CONCAT_AND_DEL(dst, ob) do { \
  assert(sizeof(XML_Char) == sizeof(Py_UNICODE)); \
  Py_UNICODE_COPY(dst, PyUnicode_AS_UNICODE(ob), PyUnicode_GET_SIZE(ob)); \
  dst += PyUnicode_GET_SIZE(ob); \
  Py_DECREF(ob); \
} while (0)

  /* the default namespace (`None` prefix) must be the first entry.
   * Adjust the initial allocation to ensure that the URI will fit. */
  size = 1024;
  if ((uri = PyDict_GetItem(namespaces, Py_None)) != NULL) {
    uri = PyObject_Unicode(uri);
    if (uri == NULL) {
      Py_DECREF(namespaces);
      return NULL;
    }
    /* +2 for NAMESPACE_SEP ('=') and CONTEXT_SEP ('\f') */
    used = PyUnicode_GET_SIZE(uri) + 2;
    if (used >= size) {
      size = ROUND_UP(used, 1024);
    }
  } else {
    used = 0;
  }
  ptr = context = PyMem_New(XML_Char, size);
  if (context == NULL) {
    Py_DECREF(namespaces);
    PyErr_NoMemory();
    return NULL;
  }
  /* copy the uri to the context */
  if (uri) {
    *ptr++ = '=';
    XMLCHAR_CONCAT_AND_DEL(ptr, uri);
    *ptr++ = '\f';
  }

  i = 0;
  while (PyDict_Next(namespaces, &i, &prefix, &uri)) {
    if (prefix == Py_None) continue;
    prefix = PyObject_Unicode(prefix);
    uri = PyObject_Unicode(uri);
    if (prefix == NULL || uri == NULL) {
      Py_DECREF(namespaces);
      PyMem_Del(context);
      return NULL;
    }

    /* +2 for NAMESPACE_SEP ('=') and CONTEXT_SEP ('\f') */
    new_len = used + PyUnicode_GET_SIZE(prefix) + PyUnicode_GET_SIZE(uri) + 2;
    if (new_len > size) {
      size = ROUND_UP(new_len, 1024);
      ptr = context;
      if (PyMem_Resize(ptr, XML_Char, size) == NULL) {
        Py_DECREF(prefix);
        Py_DECREF(uri);
        Py_DECREF(namespaces);
        PyMem_Del(context);
        PyErr_NoMemory();
        return NULL;
      }
      context = ptr;
      ptr += used;
    }
    used = new_len;

    /* copy the prefix to the context */
    XMLCHAR_CONCAT_AND_DEL(ptr, prefix);
    *ptr++ = '=';

    /* copy the uri to the context */
    XMLCHAR_CONCAT_AND_DEL(ptr, uri);
    *ptr++ = '\f';
  }
  Py_DECREF(namespaces);

  /* add the default context */
  memcpy(ptr, implicitContext, sizeof(implicitContext));

  return context;
}

ExpatStatus Expat_ParseEntity(ExpatParser parser, PyObject *source,
                              PyObject *namespaces)
{
  XML_Char *namespace_context;
  XML_Parser expat_parser;
  ExpatStatus status;

  Debug_FunctionCall(Expat_ParseEntity, parser);

  if (namespaces) {
    namespace_context = createExpatContext(namespaces);
    if (namespace_context == NULL) {
      return EXPAT_STATUS_ERROR;
    }
  } else {
    namespace_context = (XML_Char *) implicitContext;
  }
  expat_parser = createExpatParser(parser);
  if (expat_parser == NULL) {
    PyMem_Del(namespace_context);
    return EXPAT_STATUS_ERROR;
  }
  /* create a nested context to allow a resumed parser to do the cleanup */
  parser->context = Context_New(expat_parser, Py_None);
  if (parser->context == NULL) {
    XML_ParserFree(expat_parser);
    PyMem_Del(namespace_context);
    return EXPAT_STATUS_ERROR;
  }
  expat_parser = XML_ExternalEntityParserCreate(expat_parser,
                                                namespace_context,
                                                NULL);
  if (namespaces) {
    PyMem_Del(namespace_context);
  }
  if (expat_parser == NULL) {
    endContext(parser);
    PyErr_NoMemory();
    return EXPAT_STATUS_ERROR;
  }

  status = Expat_StartParsing(parser, expat_parser, source);

  Debug_ReturnStatus(Expat_ParseEntity, status);

  return status;
}


static Expat_APIObject Expat_API = {
  Expat_ParserCreate,
  Expat_ParserFree,
  Expat_ParseDocument,
  Expat_ParseEntity,
  Expat_ParserSuspend,
  Expat_ParserResume,
  _Expat_ParserStop,
  Expat_GetBase,
  Expat_GetLineNumber,
  Expat_GetColumnNumber,
  Expat_SetStartDocumentHandler,
  Expat_SetEndDocumentHandler,
  Expat_SetStartElementHandler,
  Expat_SetEndElementHandler,
  Expat_SetCharacterDataHandler,
  Expat_SetProcessingInstructionHandler,
  Expat_SetCommentHandler,
  Expat_SetStartNamespaceDeclHandler,
  Expat_SetEndNamespaceDeclHandler,
  Expat_SetStartDoctypeDeclHandler,
  Expat_SetEndDoctypeDeclHandler,
  Expat_SetSkippedEntityHandler,
  Expat_SetStartCdataSectionHandler,
  Expat_SetEndCdataSectionHandler,
  Expat_SetIgnorableWhitespaceHandler,

  Expat_SetWarningHandler,
  Expat_SetErrorHandler,
  Expat_SetFatalErrorHandler,

  Expat_SetNotationDeclHandler,
  Expat_SetUnparsedEntityDeclHandler,

  Expat_SetElementDeclHandler,
  Expat_SetAttributeDeclHandler,
  Expat_SetInternalEntityDeclHandler,
  Expat_SetExternalEntityDeclHandler,

  Expat_SetParamEntityParsing,
  Expat_SetXIncludeProcessing,
  Expat_SetWhitespaceRules,
};


int DomletteExpat_Init(PyObject *module)
{
  PyObject *import;
  XML_Expat_Version version = XML_ExpatVersionInfo();
  const XML_Feature *features = XML_GetFeatureList();
  const XML_Feature *f;
  PyObject *capi;

  if ((PycString_IMPORT) == NULL)
    return -1;

  if ((XmlString_IMPORT) == NULL)
    return -1;

#define DEFINE_OBJECT(name, ob) \
  (name) = (ob);                \
  if ((name) == NULL) return -1
#define DEFINE_STRING(name, s) \
  DEFINE_OBJECT(name, PyString_FromString(s))
#define DEFINE_UNICODE(name, s) \
  DEFINE_OBJECT(name, PyUnicode_DecodeASCII((s), sizeof(s) - 1, NULL))

  DEFINE_STRING(encoding_string, "encoding");
  DEFINE_STRING(uri_string, "uri");
  DEFINE_STRING(stream_string, "stream");

  empty_string = PyUnicode_FromUnicode(NULL, 0);
  if (empty_string == NULL) return -1;

  DEFINE_UNICODE(asterisk_string, "*");
  DEFINE_UNICODE(space_string, "space");
  DEFINE_UNICODE(preserve_string, "preserve");
  DEFINE_UNICODE(default_string, "default");
  DEFINE_UNICODE(id_string, "id");
  DEFINE_UNICODE(xml_space_string, "xml:space");
  DEFINE_UNICODE(xml_base_string, "xml:base");
  DEFINE_UNICODE(xml_lang_string, "xml:lang");
  DEFINE_UNICODE(base_string, "base");
  DEFINE_UNICODE(lang_string, "lang");
  DEFINE_UNICODE(unicode_space_char, " ");
  DEFINE_UNICODE(empty_event, "(#EMPTY)");
  DEFINE_UNICODE(content_model_empty, "EMPTY");
  DEFINE_UNICODE(content_model_any, "ANY");
  DEFINE_UNICODE(content_model_pcdata, "(#PCDATA)");
  DEFINE_UNICODE(attribute_decl_implied, "#IMPLIED");
  DEFINE_UNICODE(attribute_decl_required, "#REQUIRED");
  DEFINE_UNICODE(attribute_decl_fixed, "#FIXED");

  DEFINE_STRING(xinclude_hint_string, "XINCLUDE");
  DEFINE_STRING(external_entity_hint_string, "EXTERNAL ENTITY");

  import = PyImport_ImportModule("Ft.Lib");
  if (import == NULL) return -1;
  UriException = PyObject_GetAttrString(import, "UriException");
  if (UriException == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  UriException_RESOURCE_ERROR = PyObject_GetAttrString(UriException,
                                                       "RESOURCE_ERROR");
  if (UriException_RESOURCE_ERROR == NULL) return -1;

  import = PyImport_ImportModule("Ft.Lib.Uri");
  if (import == NULL) return -1;
  absolutize_function = PyObject_GetAttrString(import, "Absolutize");
  if (absolutize_function == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  import = PyImport_ImportModule("Ft.Xml");
  if (import == NULL) return -1;
  xml_namespace_string = PyObject_GetAttrString(import, "XML_NAMESPACE");
  if (xml_namespace_string == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);
  if (!PyUnicode_CheckExact(xml_namespace_string)) {
    PyObject *temp = PyUnicode_FromObject(xml_namespace_string);
    if (temp == NULL) return -1;
    Py_DECREF(xml_namespace_string);
    xml_namespace_string = temp;
  }

  /* Update Expat's memory allocator to use the Python object allocator
   * if it is enabled. */
#ifdef WITH_PYMALLOC
  expat_memsuite.malloc_fcn = PyObject_MALLOC;
  expat_memsuite.realloc_fcn = PyObject_REALLOC;
  expat_memsuite.free_fcn = PyObject_FREE;
#endif

  /* verify Expat linkage due to late binding on Linux */
  expat_library_error = NULL;

  /* ensure that we're going to be using the proper Expat functions */
  if (version.major != XML_MAJOR_VERSION ||
      version.minor != XML_MINOR_VERSION ||
      version.micro != XML_MICRO_VERSION) {
    expat_library_error =
      PyString_FromFormat("Incompatible Expat library found; "          \
                          "version mismatch (expected %d.%d.%d, "       \
                          "found %d.%d.%d)", XML_MAJOR_VERSION,
                          XML_MINOR_VERSION, XML_MICRO_VERSION,
                          version.major, version.minor, version.micro);
    if (expat_library_error == NULL) return -1;
    return PyErr_Warn(PyExc_RuntimeWarning,
                      PyString_AS_STRING(expat_library_error));
  }

  /* check Expat features that we require depending on how we were
     compiled.  Unfortunately, we cannot test for namespace support.
  */
  for (f = features; f->feature != XML_FEATURE_END; f++) {
    if (f->feature == XML_FEATURE_SIZEOF_XML_CHAR &&
        f->value != sizeof(Py_UNICODE)) {
      expat_library_error =
        PyString_FromString("Incompatible Expat library found; "        \
                            "sizeof(XML_Char) != sizeof(Py_UNICODE)");
      if (expat_library_error == NULL) return -1;
      return PyErr_Warn(PyExc_RuntimeWarning,
                        PyString_AS_STRING(expat_library_error));
    }
  }

#define CHECK_FEATURE(NAME)                                             \
  for (f = features; f->feature != XML_FEATURE_ ## NAME; f++) {         \
    if (f->feature == XML_FEATURE_END) {                                \
      expat_library_error =                                             \
        PyString_FromString("Incompatible Expat library found; "        \
                            "missing feature XML_" #NAME);              \
      if (expat_library_error == NULL) return -1;                       \
      return PyErr_Warn(PyExc_RuntimeWarning,                           \
                        PyString_AS_STRING(expat_library_error));       \
    }                                                                   \
  }
#ifdef XML_UNICODE
  CHECK_FEATURE(UNICODE);
#endif
#ifdef XML_DTD
  CHECK_FEATURE(DTD);
#endif
#ifdef XML_NS
  CHECK_FEATURE(NS);
#endif
#undef CHECK_FEATURE

  PyModule_AddIntConstant(module, "XPTR_ELEMENT_ID", ELEMENT_ID);
  PyModule_AddIntConstant(module, "XPTR_ELEMENT_COUNT", ELEMENT_COUNT);
  PyModule_AddIntConstant(module, "XPTR_ELEMENT_MATCH", ELEMENT_MATCH);
  PyModule_AddIntConstant(module, "XPTR_ATTRIBUTE_MATCH", ATTRIBUTE_MATCH);

  /* Export C API - done last to serve as a cleanup function as well */
  capi = PyCObject_FromVoidPtr((void *)&Expat_API, NULL);
  if (capi == NULL) return -1;
  return PyModule_AddObject(module, "Expat_CAPI", capi);
}


void DomletteExpat_Fini(void)
{
  Py_DECREF(encoding_string);
  Py_DECREF(uri_string);
  Py_DECREF(stream_string);

  Py_DECREF(empty_string);
  Py_DECREF(asterisk_string);
  Py_DECREF(space_string);
  Py_DECREF(preserve_string);
  Py_DECREF(default_string);
  Py_DECREF(id_string);
  Py_DECREF(xml_namespace_string);
  Py_DECREF(xml_space_string);
  Py_DECREF(xml_base_string);
  Py_DECREF(xml_lang_string);
  Py_DECREF(base_string);
  Py_DECREF(lang_string);

  Py_DECREF(unicode_space_char);

  Py_DECREF(empty_event);
  Py_DECREF(content_model_empty);
  Py_DECREF(content_model_any);
  Py_DECREF(content_model_pcdata);
  Py_DECREF(attribute_decl_implied);
  Py_DECREF(attribute_decl_required);
  Py_DECREF(attribute_decl_fixed);

  Py_DECREF(xinclude_hint_string);
  Py_DECREF(external_entity_hint_string);
  Py_DECREF(absolutize_function);
  Py_XDECREF(expat_library_error);
}
