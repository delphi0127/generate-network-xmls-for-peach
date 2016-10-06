#ifndef DOMLETTE_EXPAT_INTERFACE_H
#define DOMLETTE_EXPAT_INTERFACE_H

#ifdef __cplusplus
extern "C" {
#endif

/*

  This header provides access to Domlette's Expat interface from C.

  Before calling any of the functions or macros, you must initialize
  the routines with:

    Expat_IMPORT

  This would typically be done in your init function.

*/

#include "content_model.h"

  struct ExpatParserStruct;
  typedef struct ExpatParserStruct *ExpatParser;

  typedef struct {
    PyObject *namespaceURI;
    PyObject *localName;
    PyObject *qualifiedName;
  } ExpatExpandedName;

  typedef struct {
    PyObject *namespaceURI;
    PyObject *localName;
    PyObject *qualifiedName;
    PyObject *value;
    AttributeType type;
  } ExpatAttribute;

  typedef enum {
    EXPAT_STATUS_ERROR = 0,
    EXPAT_STATUS_OK,
    EXPAT_STATUS_SUSPENDED,
  } ExpatStatus;

  typedef void (*ExpatStartDocumentHandler)(void *userData);

  typedef void (*ExpatEndDocumentHandler)(void *userData);

  /* name is a PyUnicodeObject, atts is a PyDictObject */
  typedef void (*ExpatStartElementHandler)(void *userData,
                                           ExpatExpandedName *name,
                                           ExpatAttribute atts[],
                                           int atts_len);

  /* name is a PyUnicodeObject */
  typedef void (*ExpatEndElementHandler)(void *userData,
                                         ExpatExpandedName *name);

  /* data is a PyUnicodeObject */
  typedef void (*ExpatCharacterDataHandler)(void *userData,
                                            PyObject *data);

  /* target is a PyUnicodeObject, data is a PyUnicodeObject */
  typedef void (*ExpatProcessingInstructionHandler)(void *userData,
                                                    PyObject *target,
                                                    PyObject *data);

  /* data is a PyUnicodeObject */
  typedef void (*ExpatCommentHandler)(void *userData,
                                      PyObject *data);

  /* prefix is a PyUnicodeObject or Py_None, uri is a PyUnicodeObject */
  typedef void (*ExpatStartNamespaceDeclHandler)(void *userData,
                                                 PyObject *prefix,
                                                 PyObject *uri);

  /* prefix is a PyUnicodeObject or Py_None */
  typedef void (*ExpatEndNamespaceDeclHandler)(void *userData,
                                               PyObject *prefix);

  /* name is a PyUnicodeObject
     systemId is a PyUnicodeObject or Py_None, 
     publicId is a PyUnicodeObject or Py_None
  */
  typedef void (*ExpatStartDoctypeDeclHandler)(void *userData,
                                               PyObject *name,
                                               PyObject *systemId,
                                               PyObject *publicId);

  typedef void (*ExpatEndDoctypeDeclHandler)(void *userData);

  /* name is a PyUnicodeObject
     model is a PyUnicodeObject
  */
  typedef void (*ExpatElementDeclHandler)(void *userData,
                                          PyObject *name,
                                          PyObject *model);

  /* elementName is a PyUnicodeObject
     attributeName is a PyUnicodeObject
     type is a PyUnicodeObject
     mode is a PyUnicodeObject oy Py_None
     value is a PyUnicodeObject or Py_None
  */
  typedef void (*ExpatAttributeDeclHandler)(void *userData,
                                            PyObject *elementName,
                                            PyObject *attributeName,
                                            PyObject *type,
                                            PyObject *mode,
                                            PyObject *value);

  /* name is a PyUnicodeObject
     value is a PyUnicodeObject
  */
  typedef void (*ExpatInternalEntityDeclHandler)(void *userData,
                                                 PyObject *name,
                                                 PyObject *value);

  /* name is a PyUnicodeObject
     publicId is a PyUnicodeObject or Py_None
     systemId is a PyUnicodeObject
  */
  typedef void (*ExpatExternalEntityDeclHandler)(void *userData,
                                                 PyObject *name,
                                                 PyObject *publicId,
                                                 PyObject *systemId);

  /* name is a PyUnicodeObject
     publicId is a PyUnicodeObject or Py_None
     systemId is a PyUnicodeObject
     notationName is a PyUnicodeObject
  */
  typedef void (*ExpatUnparsedEntityDeclHandler)(void *userData,
                                                 PyObject *name,
                                                 PyObject *publicId,
                                                 PyObject *systemId,
                                                 PyObject *notationName);

  /* name is a PyUnicodeObject
     publicId is a PyUnicodeObject or Py_None
     systemId is a PyUnicodeObject or Py_None
  */
  typedef void (*ExpatNotationDeclHandler)(void *userData,
                                           PyObject *name,
                                           PyObject *publicId,
                                           PyObject *systemId);

  /* name is a PyUnicodeObject */
  typedef void (*ExpatSkippedEntityHandler)(void *userData,
                                            PyObject *name);

  typedef void (*ExpatStartCdataSectionHandler)(void *userData);

  typedef void (*ExpatEndCdataSectionHandler)(void *userData);

  /* data is a PyUnicodeObject */
  typedef void (*ExpatIgnorableWhitespaceHandler)(void *userData,
                                                  PyObject *data);

  /* exception is an ReaderException instance */
  typedef ExpatStatus (*ExpatNotificationHandler)(void *userData,
                                                  PyObject *exception);

  typedef struct {
    ExpatParser (*ParserCreate)(void *userState);
    
    void (*ParserFree)(ExpatParser parser);

    ExpatStatus (*ParseDocument)(ExpatParser parser, PyObject *source);

    ExpatStatus (*ParseEntity)(ExpatParser parser, PyObject *source,
                               PyObject *namespaces);

    ExpatStatus (*ParserSuspend)(ExpatParser parser);

    ExpatStatus (*ParserResume)(ExpatParser parser);

    void (*ParserStop)(ExpatParser parser, char *filename, int lineno);

    PyObject *(*GetBase)(ExpatParser parser);

    int (*GetLineNumber)(ExpatParser parser);
    
    int (*GetColumnNumber)(ExpatParser parser);

    void (*SetStartDocumentHandler)(ExpatParser parser,
                                    ExpatStartDocumentHandler handler);

    void (*SetEndDocumentHandler)(ExpatParser parser,
                                  ExpatEndDocumentHandler handler);

    void (*SetStartElementHandler)(ExpatParser parser,
                                   ExpatStartElementHandler handler);

    void (*SetEndElementHandler)(ExpatParser parser,
                                 ExpatEndElementHandler handler);

    void (*SetCharacterDataHandler)(ExpatParser parser,
                                    ExpatCharacterDataHandler handler);

    void (*SetProcessingInstructionHandler)(
                                    ExpatParser parser,
                                    ExpatProcessingInstructionHandler handler);

    void (*SetCommentHandler)(ExpatParser parser,
                              ExpatCommentHandler handler);

    void (*SetStartNamespaceDeclHandler)(
                                    ExpatParser parser,
                                    ExpatStartNamespaceDeclHandler handler);

    void (*SetEndNamespaceDeclHandler)(
                                    ExpatParser parser,
                                    ExpatEndNamespaceDeclHandler handler);

    void (*SetStartDoctypeDeclHandler)(
                                    ExpatParser parser,
                                    ExpatStartDoctypeDeclHandler handler);

    void (*SetEndDoctypeDeclHandler)(
                                    ExpatParser parser,
                                    ExpatEndDoctypeDeclHandler handler);

    void (*SetSkippedEntityHandler)(ExpatParser parser,
                                    ExpatSkippedEntityHandler handler);

    void (*SetStartCdataSectionHandler)(
                                    ExpatParser parser,
                                    ExpatStartCdataSectionHandler handler);

    void (*SetEndCdataSectionHandler)(
                                    ExpatParser parser,
                                    ExpatEndCdataSectionHandler handler);

    void (*SetIgnorableWhitespaceHandler)(
                                    ExpatParser parser,
                                    ExpatIgnorableWhitespaceHandler handler);

    void (*SetWarningHandler)(ExpatParser parser,
                              ExpatNotificationHandler handler);

    void (*SetErrorHandler)(ExpatParser parser,
                            ExpatNotificationHandler handler);

    void (*SetFatalErrorHandler)(ExpatParser parser,
                                 ExpatNotificationHandler handler);

    void (*SetNotationDeclHandler)(ExpatParser parser,
                                   ExpatNotationDeclHandler handler);

    void (*SetUnparsedEntityDeclHandler)(
                                    ExpatParser parser,
                                    ExpatUnparsedEntityDeclHandler handler);

    void (*SetElementDeclHandler)(ExpatParser parser,
                                  ExpatElementDeclHandler handler);

    void (*SetAttributeDeclHandler)(ExpatParser parser,
                                    ExpatAttributeDeclHandler handler);

    void (*SetInternalEntityDeclHandler)(
                                    ExpatParser parser,
                                    ExpatInternalEntityDeclHandler handler);

    void (*SetExternalEntityDeclHandler)(
                                    ExpatParser parser,
                                    ExpatExternalEntityDeclHandler handler);

    void (*SetParamEntityParsing)(ExpatParser parser, int doParamEntityParsing);

    void (*SetXIncludeProcessing)(ExpatParser parser, int doXIncludeProcessing);

    ExpatStatus (*SetWhitespaceRules)(ExpatParser parser, PyObject *rules);

  } Expat_APIObject;


#ifndef Domlette_BUILDING_MODULE

/* --- C API ----------------------------------------------------*/

  static Expat_APIObject *Expat_API;

#define Expat_IMPORT Expat_API =                                \
    (Expat_APIObject *) PyCObject_Import("Ft.Xml.cDomlettec",   \
                                         "Expat_CAPI")

#define Expat_ParserCreate \
  Expat_API->ParserCreate
#define Expat_ParserFree \
  Expat_API->ParserFree
#define Expat_ParseDocument \
  Expat_API->ParseDocument
#define Expat_ParseEntity \
  Expat_API->ParseEntity
#define Expat_ParserSuspend \
  Expat_API->ParserSuspend
#define Expat_ParserResume \
  Expat_API->ParserResume
#define Expat_ParserStop(parser) \
  Expat_API->ParserStop((parser), __FILE__, __LINE__)
#define Expat_GetBase \
  Expat_API->GetBase
#define Expat_GetLineNumber \
  Expat_API->GetLineNumber
#define Expat_GetColumnNumber \
  Expat_API->GetColumnNumber
#define Expat_SetStartDocumentHandler \
  Expat_API->SetStartDocumentHandler
#define Expat_SetEndDocumentHandler \
  Expat_API->SetEndDocumentHandler
#define Expat_SetStartElementHandler \
  Expat_API->SetStartElementHandler
#define Expat_SetEndElementHandler \
  Expat_API->SetEndElementHandler
#define Expat_SetCharacterDataHandler \
  Expat_API->SetCharacterDataHandler
#define Expat_SetProcessingInstructionHandler \
  Expat_API->SetProcessingInstructionHandler
#define Expat_SetCommentHandler \
  Expat_API->SetCommentHandler
#define Expat_SetStartNamespaceDeclHandler \
  Expat_API->SetStartNamespaceDeclHandler
#define Expat_SetEndNamespaceDeclHandler \
  Expat_API->SetEndNamespaceDeclHandler
#define Expat_SetStartDoctypeDeclHandler \
  Expat_API->SetStartDoctypeDeclHandler
#define Expat_SetEndDoctypeDeclHandler \
  Expat_API->SeEndDoctypeDeclHandler
#define Expat_SetStartCdataSectionHandler \
  Expat_API->SetStartCdataSectionHandler
#define Expat_SetEndCdataSectionHandler \
  Expat_API->SetEndCdataSectionHandler
#define Expat_SetIgnorableWhitespaceHandler \
  Expat_API->SetIgnorableWhitespaceHandler

#define Expat_SetWarningHandler \
  Expat_API->SetWarningHandler
#define Expat_SetErrorHandler \
  Expat_API->SetErrorHandler
#define Expat_SetFatalErrorHandler \
  Expat_API->SetFatalErrorHandler

#define Expat_SetNotationDeclHandler \
  Expat_API->SetNotationDeclHandler
#define Expat_SetUnparsedEntityDeclHandler \
  Expat_API->SetUnparsedEntityDeclHandler

#define Expat_SetElementDeclHandler \
  Expat_API->SetElementDeclHandler
#define Expat_SetAttributeDeclHandler \
  Expat_API->SetAttributeDeclHandler
#define Expat_SetInternalEntityDeclHandler \
  Expat_API->SetInternalEntityDeclHandler
#define Expat_SetExternalEntityDeclHandler \
  Expat_API->SetExternalEntityDeclHandler

#define Expat_SetParamEntityParsing \
  Expat_API->SetParamEntityParsing
#define Expat_SetXIncludeProcessing \
  Expat_API->SetXIncludeProcessing
#define Expat_SetWhitespaceRules \
  Expat_API->SetWhitespaceRules

#endif /* !Domlette_BUILDING_MODULE */

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_EXPAT_INTERFACE_H */
