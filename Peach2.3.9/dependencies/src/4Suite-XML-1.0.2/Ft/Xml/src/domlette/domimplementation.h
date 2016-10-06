#ifndef DOMLETTE_DOMIMPLEMENTATION_H
#define DOMLETTE_DOMIMPLEMENTATION_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

  typedef struct {
    PyObject_HEAD
  } PyDOMImplementationObject;

  extern PyTypeObject DomletteDOMImplementation_Type;

#define PyDOMImplementation_Check(op) ((op)->ob_type == &DomletteDOMImplementation_Type)

  /* Module Methods */
  int DomletteDOMImplementation_Init(PyObject *module);
  void DomletteDOMImplementation_Fini(void);

  extern PyObject *g_implementation;

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_DOMIMPLEMENTATION_H */
