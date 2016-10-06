#ifndef DOMLETTE_XPATHNAMESPACE_H
#define DOMLETTE_XPATHNAMESPACE_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"
#include "element.h"

  typedef struct {
    PyNode_HEAD
    PyObject *nodeName;
    PyObject *nodeValue;
  } PyXPathNamespaceObject;

#define XPathNamespace_GET_NAME(op) \
  (((PyXPathNamespaceObject *)(op))->nodeName)
#define XPathNamespace_GET_VALUE(op) \
  (((PyXPathNamespaceObject *)(op))->nodeValue)

  extern PyTypeObject DomletteXPathNamespace_Type;

#define PyXPathNamespace_Check(op) \
  PyObject_TypeCheck(op, &DomletteXPathNamespace_Type)
#define PyXPathNamespace_CheckExact(op) \
  ((op)->ob_type == &DomletteXPathNamespace_Type)

  /* Module Methods */
  int DomletteXPathNamespace_Init(PyObject *module);
  void DomletteXPathNamespace_Fini(void);

  /* XPathNamespace Methods */
  PyXPathNamespaceObject *XPathNamespace_New(PyElementObject *parentNode,
                                             PyObject *prefix,
                                             PyObject *namespaceURI);

#ifdef __cplusplus
}
#endif


#endif /* DOMLETTE_XPATHNAMESPACE_H */
