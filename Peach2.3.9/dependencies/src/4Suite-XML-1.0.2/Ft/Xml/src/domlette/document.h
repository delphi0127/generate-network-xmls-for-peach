#ifndef DOMLETTE_DOCUMENT_H
#define DOMLETTE_DOCUMENT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"

  typedef struct PyDocumentObject {
    PyContainerNode_HEAD
    PyObject *documentURI;
    PyObject *publicId;
    PyObject *systemId;
    PyObject *unparsedEntities;
    PyObject *creationIndex;
  } PyDocumentObject;

#define PyDocument_BASE_URI(op) (((PyDocumentObject *)(op))->documentURI)
#define PyDocument_PUBLIC_ID(op) (((PyDocumentObject *)(op))->publicId)
#define PyDocument_SYSTEM_ID(op) (((PyDocumentObject *)(op))->systemId)
#define PyDocument_INDEX(op) (((PyDocumentObject *)(op))->creationIndex)

  extern PyTypeObject DomletteDocument_Type;

#define PyDocument_Check(op) PyObject_TypeCheck((op), &DomletteDocument_Type)
#define PyDocument_CheckExact(op) ((op)->ob_type == &DomletteDocument_Type)

  /* Module Methods */
  int DomletteDocument_Init(PyObject *module);
  void DomletteDocument_Fini(void);

  /* Document Methods */
  PyDocumentObject *Document_New(PyObject *documentURI);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_DOCUMENT_H */
