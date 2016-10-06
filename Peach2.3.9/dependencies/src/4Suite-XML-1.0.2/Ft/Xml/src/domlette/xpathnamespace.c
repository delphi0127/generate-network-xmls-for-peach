#include "domlette.h"


/** Private Routines **************************************************/


static int xns_init(PyXPathNamespaceObject *self,
                    PyElementObject *parentNode,
                    PyObject *prefix,
                    PyObject *namespaceURI)
{
  if ((self == NULL || !PyXPathNamespace_Check(self)) ||
      (parentNode == NULL || !PyElement_Check(parentNode)) ||
      (prefix == NULL || !DOMString_NullCheck(prefix)) ||
      (namespaceURI == NULL || !DOMString_Check(namespaceURI))) {
    PyErr_BadInternalCall();
    return -1;
  }

  if (prefix == Py_None) {
    prefix = PyUnicode_FromUnicode(NULL, (Py_ssize_t)0);
    if (prefix == NULL) return -1;
  } else {
    Py_INCREF(prefix);
  }
  self->nodeName = prefix;

  Py_INCREF(namespaceURI);
  self->nodeValue = namespaceURI;

  Node_SET_PARENT(self, (PyNodeObject *) parentNode);

  return 0;
}


/** C API **************************************************************/


PyXPathNamespaceObject *XPathNamespace_New(PyElementObject *parentNode,
                                           PyObject *prefix,
                                           PyObject *namespaceURI)
{
  PyXPathNamespaceObject *self;

  if (parentNode == NULL || !PyElement_Check(parentNode)) {
    PyErr_BadInternalCall();
    return NULL;
  }

  self = Node_New(PyXPathNamespaceObject, &DomletteXPathNamespace_Type,
                  Node_GET_DOCUMENT(parentNode));
  if (self != NULL) {
    if (xns_init(self, parentNode, prefix, namespaceURI) < 0) {
      Node_Del(self);
      return NULL;
    }
  }

  PyObject_GC_Track(self);

  return self;
}


/** Python Methods ****************************************************/


/* No additional interface methods defined */


/** Python Members ****************************************************/


static struct PyMemberDef xns_members[] = {
  { "nodeName",  T_OBJECT, offsetof(PyXPathNamespaceObject, nodeName),  RO },
  { "localName", T_OBJECT, offsetof(PyXPathNamespaceObject, nodeName),  RO },
  { "nodeValue", T_OBJECT, offsetof(PyXPathNamespaceObject, nodeValue), RO },
  { "value",     T_OBJECT, offsetof(PyXPathNamespaceObject, nodeValue), RO },
  { NULL }
};


/** Python Computed Members *******************************************/


/* No additional interface members defined */


/** Type Object ********************************************************/


static void xns_dealloc(PyXPathNamespaceObject *self)
{
  PyObject_GC_UnTrack((PyObject *) self);

  Py_DECREF(self->nodeValue);
  self->nodeValue = NULL;

  Py_DECREF(self->nodeName);
  self->nodeName = NULL;

  Node_Del(self);
}


static PyObject *xns_repr(PyXPathNamespaceObject *self)
{
  char buf[256];

  PyObject *name = PyObject_Repr(self->nodeName);
  PyObject *value = PyObject_Repr(self->nodeValue);

  sprintf(buf, "<cXPathNamespace at %p: name %.50s, value %.100s>", self,
          name == NULL ? "(null)" : PyString_AS_STRING(name),
          value == NULL ? "(null)" : PyString_AS_STRING(value));

  Py_XDECREF(name);
  Py_XDECREF(value);

  return PyString_FromString(buf);
}


static PyObject *xns_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyElementObject *parentNode;
  PyObject *prefix, *namespaceURI;
  static char *kwlist[] = { "parentNode", "prefix", "namespaceURI", NULL };
  PyXPathNamespaceObject *self;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!OO:Element", kwlist,
                                   &DomletteElement_Type, &parentNode,
                                   &prefix, &namespaceURI)) {
    return NULL;
  }

  prefix = DOMString_ConvertArgument(prefix, "prefix", 1);
  if (prefix == NULL) return NULL;

  namespaceURI = DOMString_ConvertArgument(namespaceURI, "namespaceURI", 0);
  if (namespaceURI == NULL) {
    Py_DECREF(prefix);
    return NULL;
  }

  if (type != &DomletteXPathNamespace_Type) {
    self = (PyXPathNamespaceObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
      _Node_INIT(self, Node_GET_DOCUMENT(parentNode));
      if (xns_init(self, parentNode, prefix, namespaceURI) < 0) {
        Py_DECREF(self);
        self = NULL;
      }
    }
  } else {
    self = XPathNamespace_New(parentNode, prefix, namespaceURI);
  }
  Py_DECREF(prefix);
  Py_DECREF(namespaceURI);

  return (PyObject *) self;
}


static char xns_doc[] = "\
XPathNamespace(parentNode, prefix, namespaceURI) -> XPathNamespace object\n\
\n\
The XPathNamespace interface represents the XPath namespace node type\n\
that DOM lacks.";

PyTypeObject DomletteXPathNamespace_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "XPathNamespace",
  /* tp_basicsize      */ sizeof(PyXPathNamespaceObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) xns_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) xns_repr,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ Py_TPFLAGS_DEFAULT,
  /* tp_doc            */ (char *) xns_doc,
  /* tp_traverse       */ (traverseproc) 0,
  /* tp_clear          */ 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) 0,
  /* tp_members        */ (PyMemberDef *) xns_members,
  /* tp_getset         */ (PyGetSetDef *) 0,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) xns_new,
  /* tp_free           */ 0,
};

int DomletteXPathNamespace_Init(PyObject *module)
{
  PyObject *dict, *value;

  DomletteXPathNamespace_Type.tp_base = &DomletteNode_Type;
  if (PyType_Ready(&DomletteXPathNamespace_Type) < 0)
    return -1;

  dict = DomletteXPathNamespace_Type.tp_dict;

  value = PyInt_FromLong(XPATH_NAMESPACE_NODE);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeType", value))
    return -1;
  Py_DECREF(value);

  Py_INCREF(&DomletteXPathNamespace_Type);
  return PyModule_AddObject(module, "XPathNamespace",
           (PyObject*) &DomletteXPathNamespace_Type);
}

void DomletteXPathNamespace_Fini(void)
{
  PyType_CLEAR(&DomletteXPathNamespace_Type);
}
