#include "domlette.h"


/** Private Routines **************************************************/


/** Public C API ******************************************************/


PyDocumentFragmentObject *DocumentFragment_New(PyDocumentObject *ownerDocument)
{
  PyDocumentFragmentObject *self;

  self = Node_NewContainer(PyDocumentFragmentObject,
                           &DomletteDocumentFragment_Type,
                           ownerDocument);

  PyObject_GC_Track(self);

  return self;
}


PyDocumentFragmentObject *DocumentFragment_CloneNode(
  PyObject *node, int deep, PyDocumentObject *newOwnerDocument)
{
  PyDocumentFragmentObject *newNode;
  PyNodeObject *newChild;
  PyObject *childNodes;
  Py_ssize_t count, i;

  newNode = DocumentFragment_New(newOwnerDocument);
  if (newNode == NULL) return NULL;

  if (deep) {
    childNodes = PyObject_GetAttrString(node, "childNodes");
    if (!childNodes) {
      Py_DECREF(newNode);
      return NULL;
    }

    count = PySequence_Length(childNodes);
    for (i = 0; i < count; i++) {
      PyObject *child = PySequence_GetItem(childNodes, i);
      if (!child) {
	Py_DECREF(childNodes);
	Py_DECREF(newNode);
	return NULL;
      }

      newChild = Node_CloneNode(child, deep, newOwnerDocument);
      Py_DECREF(child);
      if (!newChild) {
	Py_DECREF(childNodes);
	Py_DECREF(newNode);
	return NULL;
      }

      if (!Node_AppendChild((PyNodeObject *)newNode, newChild)) {
	Py_DECREF(childNodes);
	Py_DECREF(newNode);
	return NULL;
      }
      Py_DECREF(newChild);
    }
    Py_DECREF(childNodes);
  }

  return newNode;
}


/** Python Methods ****************************************************/


/* No additional interface methods defined */


/** Python Members ****************************************************/


/* PyMemberDef struct here */


/** Python Computed Members *******************************************/


/* PyGetSetDef struct and routines here */


/** Type Object ********************************************************/


static void docfrag_dealloc(PyDocumentFragmentObject *self)
{
  PyObject_GC_UnTrack((PyObject *) self);

  Node_Del(self);
}


static PyObject *docfrag_repr(PyDocumentFragmentObject *docfrag)
{
  return PyString_FromFormat("<DocumentFragment at %p: %d children>", docfrag,
                             ContainerNode_GET_COUNT(docfrag));
}


static PyObject *docfrag_new(PyTypeObject *type, PyObject *args,
                             PyObject *kwds)
{
  PyDocumentObject *doc;
  static char *kwlist[] = { "ownerDocument", NULL };
  PyDocumentFragmentObject *self;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!:DocumentFragment", kwlist,
                                   &DomletteDocument_Type, &doc)) {
    return NULL;
  }

  if (type != &DomletteDocumentFragment_Type) {
    self = (PyDocumentFragmentObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
      _Node_INIT_CONTAINER(self, doc);
    }
  } else {
    self = DocumentFragment_New(doc);
  }

  return (PyObject *) self;
}


static char docfrag_doc[] = "\
DocumentFragment(ownerDocument) -> DocumentFragment object\n\
\n\
DocumentFragment is a \"lightweight\" or \"minimal\" Document object.";

PyTypeObject DomletteDocumentFragment_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "DocumentFragment",
  /* tp_basicsize      */ sizeof(PyDocumentFragmentObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) docfrag_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) docfrag_repr,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ (Py_TPFLAGS_DEFAULT |
                           Py_TPFLAGS_BASETYPE),
  /* tp_doc            */ (char *) docfrag_doc,
  /* tp_traverse       */ (traverseproc) 0,
  /* tp_clear          */ 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) 0,
  /* tp_members        */ (PyMemberDef *) 0,
  /* tp_getset         */ (PyGetSetDef *) 0,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) docfrag_new,
  /* tp_free           */ 0,
};


/** Module Setup & Teardown *******************************************/


int DomletteDocumentFragment_Init(PyObject *module)
{
  PyObject *dict, *value;

  DomletteDocumentFragment_Type.tp_base = &DomletteNode_Type;
  if (PyType_Ready(&DomletteDocumentFragment_Type) < 0)
    return -1;

  dict = DomletteDocumentFragment_Type.tp_dict;

  value = PyInt_FromLong(DOCUMENT_FRAGMENT_NODE);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeType", value))
    return -1;
  Py_DECREF(value);

  value = PyUnicode_DecodeASCII("#document-fragment", (Py_ssize_t)18, NULL);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeName", value))
    return -1;
  Py_DECREF(value);

  Py_INCREF(&DomletteDocumentFragment_Type);
  return PyModule_AddObject(module, "DocumentFragment",
           (PyObject*) &DomletteDocumentFragment_Type);
}

void DomletteDocumentFragment_Fini(void)
{
  PyType_CLEAR(&DomletteDocumentFragment_Type);
}
