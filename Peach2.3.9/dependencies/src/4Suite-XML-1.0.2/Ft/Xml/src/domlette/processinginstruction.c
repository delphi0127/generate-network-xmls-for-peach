#include "domlette.h"


/** Private Routines **************************************************/


static int pi_init(PyProcessingInstructionObject *self,
                   PyObject *target, PyObject *data)
{
  if ((self == NULL || !PyProcessingInstruction_Check(self)) ||
      (target == NULL || !DOMString_Check(target)) ||
      (data == NULL || !DOMString_Check(data))) {
    PyErr_BadInternalCall();
    return -1;
  }

  Py_INCREF(target);
  self->nodeName = target;

  Py_INCREF(data);
  self->nodeValue = data;

  return 0;
}


/** Public C API ******************************************************/


PyProcessingInstructionObject *ProcessingInstruction_New(
  PyDocumentObject *ownerDocument, PyObject *target, PyObject *data)
{
  PyProcessingInstructionObject *self;

  self = Node_New(PyProcessingInstructionObject,
                  &DomletteProcessingInstruction_Type, ownerDocument);
  if (self != NULL) {
    if (pi_init(self, target, data) < 0) {
      Node_Del(self);
      return NULL;
    }
  }

  PyObject_GC_Track(self);

  return self;
}


PyProcessingInstructionObject *ProcessingInstruction_CloneNode(
  PyObject *node, int deep, PyDocumentObject *newOwnerDocument)
{
  PyObject *nodeValue, *target;
  PyProcessingInstructionObject *newNode;

  nodeValue = PyObject_GetAttrString(node, "nodeValue");
  nodeValue = DOMString_FromObjectInplace(nodeValue);
  target = PyObject_GetAttrString(node, "target");
  target = DOMString_FromObjectInplace(target);
  if (nodeValue == NULL || target == NULL) {
    Py_XDECREF(nodeValue);
    Py_XDECREF(target);
    return NULL;
  }

  newNode = ProcessingInstruction_New(newOwnerDocument, target, nodeValue);
  Py_DECREF(target);
  Py_DECREF(nodeValue);

  return newNode;
}


/** Python Methods ****************************************************/


/* No additional interface methods defined */


/** Python Members ****************************************************/


static struct PyMemberDef pi_members[] = {
  { "target",   T_OBJECT, offsetof(PyProcessingInstructionObject, nodeName), RO },
  { "nodeName", T_OBJECT, offsetof(PyProcessingInstructionObject, nodeName), RO },
  { NULL }
};


/** Python Computed Members *******************************************/


static PyObject *get_data(PyProcessingInstructionObject *self, void *arg)
{
  Py_INCREF(self->nodeValue);
  return self->nodeValue;
}


static int set_data(PyProcessingInstructionObject *self, PyObject *v,
                    void *arg)
{
  PyObject *nodeValue = DOMString_ConvertArgument(v, (char *)arg, 0);
  if (nodeValue == NULL) return -1;

  Py_DECREF(self->nodeValue);
  self->nodeValue = nodeValue;
  return 0;
}


static struct PyGetSetDef pi_getset[] = {
  { "data",      (getter)get_data, (setter)set_data, NULL, "data" },
  { "nodeValue", (getter)get_data, (setter)set_data, NULL, "nodeValue" },
  { NULL }
};


/** Type Object *******************************************************/


static void pi_dealloc(PyProcessingInstructionObject *self)
{
  PyObject_GC_UnTrack((PyObject *)self);

  Py_XDECREF(self->nodeName);
  self->nodeName = NULL;

  Py_XDECREF(self->nodeValue);
  self->nodeValue = NULL;

  Node_Del(self);
}


static PyObject *pi_repr(PyProcessingInstructionObject *pi)
{
  PyObject *repr;
  PyObject *target = PyObject_Repr(pi->nodeName);
  PyObject *data = PyObject_Repr(pi->nodeValue);
  if (target == NULL || data == NULL) {
    Py_XDECREF(target);
    Py_XDECREF(data);
    return NULL;
  }
  repr = PyString_FromFormat("<ProcessingInstruction at %p: target %s, data %s>",
                             pi,
                             PyString_AS_STRING(target),
                             PyString_AS_STRING(data));
  Py_DECREF(target);
  Py_DECREF(data);
  return repr;
}


static PyObject *pi_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PyDocumentObject *doc;
  PyObject *target, *data;
  static char *kwlist[] = { "ownerDocument", "target", "data", NULL };
  PyProcessingInstructionObject *self;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!OO:ProcessingInstruction",
                                   kwlist, &DomletteDocument_Type, &doc,
                                   &target, &data)) {
    return NULL;
  }

  target = DOMString_ConvertArgument(target, "target", 0);
  if (target == NULL) return NULL;

  data = DOMString_ConvertArgument(data, "data", 0);
  if (data == NULL) {
    Py_DECREF(target);
    return NULL;
  }

  if (type != &DomletteProcessingInstruction_Type) {
    self = (PyProcessingInstructionObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
      _Node_INIT(self, doc);
      if (pi_init(self, target, data) < 0) {
        Py_DECREF(self);
        self = NULL;
      }
    }
  } else {
    self = ProcessingInstruction_New(doc, target, data);
  }
  Py_DECREF(data);
  Py_DECREF(target);

  return (PyObject *) self;
}


static char pi_doc[] = "\
ProcessingInstruction(ownerDocument, target, data) -> ProcessingInstruction\n\
\n\
The ProcessingInstruction interface represents a \"processing instruction\",\n\
used in XML as a way to keep processor-specific information in the text of\n\
the document.";


PyTypeObject DomletteProcessingInstruction_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "ProcessingInstruction",
  /* tp_basicsize      */ sizeof(PyProcessingInstructionObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) pi_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) pi_repr,
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
  /* tp_doc            */ (char *) pi_doc,
  /* tp_traverse       */ (traverseproc) 0,
  /* tp_clear          */ 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) 0,
  /* tp_members        */ (PyMemberDef *) pi_members,
  /* tp_getset         */ (PyGetSetDef *) pi_getset,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) pi_new,
  /* tp_free           */ 0,
};


/** Module Setup & Teardown *******************************************/


int DomletteProcessingInstruction_Init(PyObject *module)
{
  PyObject *value;

  DomletteProcessingInstruction_Type.tp_base = &DomletteNode_Type;
  if (PyType_Ready(&DomletteProcessingInstruction_Type) < 0)
    return -1;

  value = PyInt_FromLong(PROCESSING_INSTRUCTION_NODE);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(DomletteProcessingInstruction_Type.tp_dict,
                           "nodeType", value))
    return -1;
  Py_DECREF(value);

  Py_INCREF(&DomletteProcessingInstruction_Type);
  return PyModule_AddObject(module, "ProcessingInstruction",
           (PyObject*) &DomletteProcessingInstruction_Type);
}


void DomletteProcessingInstruction_Fini(void)
{
  PyType_CLEAR(&DomletteProcessingInstruction_Type);
}
