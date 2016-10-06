#ifndef DOMLETTE_ELEMENT_H
#define DOMLETTE_ELEMENT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"
#include "attr.h"

  typedef struct {
    PyContainerNode_HEAD
    PyObject *namespaceURI;
    PyObject *localName;
    PyObject *nodeName;
    PyObject *attributes;
  } PyElementObject;

#define PyElement_NAMESPACE_URI(op) (((PyElementObject *)(op))->namespaceURI)
#define PyElement_LOCAL_NAME(op) (((PyElementObject *)(op))->localName)
#define PyElement_NODE_NAME(op) (((PyElementObject *)(op))->nodeName)
#define PyElement_ATTRIBUTES(op) (((PyElementObject *)(op))->attributes)

  extern PyTypeObject DomletteElement_Type;

#define PyElement_Check(op) PyObject_TypeCheck((op), &DomletteElement_Type)
#define PyElement_CheckExact(op) ((op)->ob_type == &DomletteElement_Type)

  /* Module Methods */
  int DomletteElement_Init(PyObject *module);
  void DomletteElement_Fini(void);

  /* Element Methods */
  PyElementObject *Element_New(PyDocumentObject *ownerDocument,
                               PyObject *namespaceURI,
                               PyObject *qualifiedName,
                               PyObject *localName);

  PyAttrObject *Element_SetAttributeNS(PyElementObject *self,
                                       PyObject *namespaceURI,
                                       PyObject *qualifiedName,
                                       PyObject *localName,
                                       PyObject *value);

  PyObject *Element_GetAttributeNodeNS(PyElementObject *self,
                                       PyObject *namespaceURI,
                                       PyObject *localName);

  PyElementObject *Element_CloneNode(PyObject *node, int deep,
                                     PyDocumentObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_ELEMENT_H */
