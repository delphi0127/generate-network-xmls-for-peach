#ifndef DOMLETTE_NSS_H
#define DOMLETTE_NSS_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

  PyObject *Domlette_GetNamespaces(PyNodeObject *node);

  extern char GetAllNs_doc[];
  PyObject *Domlette_GetAllNs(PyObject *self, PyObject *args);

  extern char SeekNss_doc[];
  PyObject *Domlette_SeekNss(PyObject *self, PyObject *args);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_NSS_H */
