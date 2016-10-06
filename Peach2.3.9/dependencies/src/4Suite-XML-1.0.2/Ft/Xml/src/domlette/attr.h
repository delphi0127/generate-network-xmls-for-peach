#ifndef DOMLETTE_ATTR_H
#define DOMLETTE_ATTR_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"
#include "content_model.h"

  typedef struct {
    PyNode_HEAD
    PyObject *namespaceURI;
    PyObject *localName;
    PyObject *nodeName;
    PyObject *nodeValue;
    AttributeType type;
  } PyAttrObject;

#define PyAttr_NAMESPACE_URI(op) (((PyAttrObject *)(op))->namespaceURI)
#define PyAttr_LOCAL_NAME(op) (((PyAttrObject *)(op))->localName)
#define PyAttr_NODE_NAME(op) (((PyAttrObject *)(op))->nodeName)
#define PyAttr_NODE_VALUE(op) (((PyAttrObject *)(op))->nodeValue)
#define Attr_GET_TYPE(op) (((PyAttrObject *)(op))->type)

  extern PyTypeObject DomletteAttr_Type;

#define PyAttr_Check(op) PyObject_TypeCheck((op), &DomletteAttr_Type)
#define PyAttr_CheckExact(op) ((op)->ob_type == &DomletteAttr_Type)

  /* Module Methods */
  int DomletteAttr_Init(PyObject *module);
  void DomletteAttr_Fini(void);

  /* Attr Methods */
  PyAttrObject *Attr_New(PyDocumentObject *ownerDocument,
                         PyObject *namespaceURI, PyObject *qualifiedName,
                         PyObject *localName, PyObject *value);

  PyAttrObject *Attr_CloneNode(PyObject *node, int deep,
                               PyDocumentObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_ATTR_H */
