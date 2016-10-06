#ifndef DOMLETTE_PARSE_EVENT_HANDLER_H
#define DOMLETTE_PARSE_EVENT_HANDLER_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

  typedef enum {
    PARSE_TYPE_STANDALONE = 0,
    PARSE_TYPE_NO_VALIDATE,
    PARSE_TYPE_VALIDATE,
  } ParseType;

  PyObject *ParseDocument(PyObject *inputSource, ParseType parseType);
  PyObject *ParseFragment(PyObject *inputSource, PyObject *namespaces);

  int DomletteBuilder_Init(PyObject *module);
  void DomletteBuilder_Fini(void);
  
#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_PARSE_EVENT_HANDLER_H */

