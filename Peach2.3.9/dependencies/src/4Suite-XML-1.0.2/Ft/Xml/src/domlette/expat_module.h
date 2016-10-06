#ifndef DOMLETTE_EXPAT_H
#define DOMLETTE_EXPAT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

  #include "expat_interface.h"

  ExpatParser Expat_ParserCreate(void *userState);

  void Expat_ParserFree(ExpatParser parser);

  ExpatStatus Expat_ParseDocument(ExpatParser parser, PyObject *source);

  ExpatStatus Expat_ParseEntity(ExpatParser parser, PyObject *source,
                                PyObject *namespaces);

  void _Expat_ParserStop(ExpatParser parser, char *filename, int lineno);
#define Expat_ParserStop(p) _Expat_ParserStop((p), __FILE__, __LINE__)

  ExpatStatus Expat_ParserSuspend(ExpatParser parser);

  ExpatStatus Expat_ParserResume(ExpatParser parser);

  int Expat_GetParsingStatus(ExpatParser parser);

  int Expat_GetValidation(ExpatParser parser);

  void Expat_SetValidation(ExpatParser parser, int doValidation);

  int Expat_GetParamEntityParsing(ExpatParser parser);

  void Expat_SetParamEntityParsing(ExpatParser parser,
                                   int doParamEntityParsing);

  int Expat_GetXIncludeProcessing(ExpatParser parser);

  void Expat_SetXIncludeProcessing(ExpatParser parser,
                                   int doXIncludeProcessing);

  ExpatStatus Expat_SetWhitespaceRules(ExpatParser parser, PyObject *rules);

  int Expat_IsWhitespacePreserving(ExpatParser parser, PyObject *namespaceURI,
                                   PyObject *localName);

  PyObject *Expat_GetBase(ExpatParser parser);

  int Expat_GetLineNumber(ExpatParser parser);
  
  int Expat_GetColumnNumber(ExpatParser parser);

  void Expat_SetStartDocumentHandler(ExpatParser parser,
                                     ExpatStartDocumentHandler handler);

  void Expat_SetEndDocumentHandler(ExpatParser parser,
                                   ExpatEndDocumentHandler handler);

  void Expat_SetStartElementHandler(ExpatParser parser,
                                    ExpatStartElementHandler handler);

  void Expat_SetEndElementHandler(ExpatParser parser,
                                  ExpatEndElementHandler handler);

  void Expat_SetCharacterDataHandler(
                                ExpatParser parser,
                                ExpatCharacterDataHandler handler);

  void Expat_SetProcessingInstructionHandler(
                                ExpatParser parser,
                                ExpatProcessingInstructionHandler handler);

  void Expat_SetCommentHandler(ExpatParser parser,
                               ExpatCommentHandler handler);

  void Expat_SetStartNamespaceDeclHandler(
                                ExpatParser parser,
                                ExpatStartNamespaceDeclHandler handler);

  void Expat_SetEndNamespaceDeclHandler(
                                ExpatParser parser,
                                ExpatEndNamespaceDeclHandler handler);

  void Expat_SetStartDoctypeDeclHandler(
                                ExpatParser parser,
                                ExpatStartDoctypeDeclHandler handler);

  void Expat_SetEndDoctypeDeclHandler(
                                ExpatParser parser,
                                ExpatEndDoctypeDeclHandler handler);

  void Expat_SetUnparsedEntityDeclHandler(
                                ExpatParser parser,
                                ExpatUnparsedEntityDeclHandler handler);

  void Expat_SetSkippedEntityHandler(
                                ExpatParser parser,
                                ExpatSkippedEntityHandler handler);

  void Expat_SetStartCdataSectionHandler(
                                ExpatParser parser,
                                ExpatStartCdataSectionHandler handler);

  void Expat_SetEndCdataSectionHandler(
                                ExpatParser parser,
                                ExpatEndCdataSectionHandler handler);

  void Expat_SetIgnorableWhitespaceHandler(
                                ExpatParser parser,
                                ExpatIgnorableWhitespaceHandler handler);

  void Expat_SetWarningHandler(ExpatParser parser,
                               ExpatNotificationHandler handler);

  void Expat_SetErrorHandler(ExpatParser parser,
                             ExpatNotificationHandler handler);

  void Expat_SetFatalErrorHandler(ExpatParser parser,
                                  ExpatNotificationHandler handler);

  void Expat_SetNotationDeclHandler(ExpatParser parser,
                                    ExpatNotationDeclHandler handler);

  void Expat_SetElementDeclHandler(ExpatParser parser,
                                   ExpatElementDeclHandler handler);

  void Expat_SetAttributeDeclHandler(ExpatParser parser,
                                     ExpatAttributeDeclHandler handler);

  void Expat_SetInternalEntityDeclHandler(
                                ExpatParser parser,
                                ExpatInternalEntityDeclHandler handler);

  void Expat_SetExternalEntityDeclHandler(
                                ExpatParser parser,
                                ExpatExternalEntityDeclHandler handler);

  int DomletteExpat_Init(PyObject *module);
  void DomletteExpat_Fini(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_EXPAT_H */
