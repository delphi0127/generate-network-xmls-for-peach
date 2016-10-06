#ifndef DOMLETTE_DOCUMENTFRAGMENT_H
#define DOMLETTE_DOCUMENTFRAGMENT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"

  typedef struct {
    PyContainerNode_HEAD
  } PyDocumentFragmentObject;

  extern PyTypeObject DomletteDocumentFragment_Type;

#define PyDocumentFragment_Check(op) \
  PyObject_TypeCheck((op), &DomletteDocumentFragment_Type)
#define PyDocumentFragment_CheckExact(op) \
  ((op)->ob_type == &DomletteDocumentFragment_Type)

  /* Module Methods */
  int DomletteDocumentFragment_Init(PyObject *module);
  void DomletteDocumentFragment_Fini(void);

  /* DocumentFragment Methods */
  PyDocumentFragmentObject *DocumentFragment_New(
    PyDocumentObject *ownerDocument);

  PyDocumentFragmentObject *DocumentFragment_CloneNode(
    PyObject *node, int deep, PyDocumentObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_DOCUMENTFRAGMENT_H */
