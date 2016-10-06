#include "domlette.h"


/** Private Routines **************************************************/


/* The maximum number of characters of the nodeValue to use when
   creating the repr string.
*/
#define CHARACTERDATA_REPR_LIMIT 20

static int characterdata_init(PyCharacterDataObject *self, PyObject *data)
{
  if ((self == NULL || !PyCharacterData_Check(self)) ||
      (data == NULL || !DOMString_Check(data))) {
    PyErr_BadInternalCall();
    return -1;
  }

  Py_INCREF(data);
  self->nodeValue = data;

  return 0;
}


/** Public C API ******************************************************/


PyCharacterDataObject *_CharacterData_New(PyTypeObject *type,
                                          PyDocumentObject *ownerDocument,
                                          PyObject *data)
{
  PyCharacterDataObject *self;

  self = Node_New(PyCharacterDataObject, type, ownerDocument);
  if (self != NULL) {
    if (characterdata_init(self, data) < 0) {
      Node_Del(self);
      return NULL;
    }
  }

  PyObject_GC_Track(self);

  return self;
}


PyCharacterDataObject *_CharacterData_CloneNode(
  PyTypeObject *type, PyObject *node, int deep,
  PyDocumentObject *newOwnerDocument)
{
  PyObject *nodeValue;
  PyCharacterDataObject *newNode;

  nodeValue = PyObject_GetAttrString(node, "nodeValue");
  nodeValue = DOMString_FromObjectInplace(nodeValue);
  if (nodeValue == NULL) return NULL;

  newNode = _CharacterData_New(type, newOwnerDocument, nodeValue);
  Py_DECREF(nodeValue);

  return newNode;
}


PyObject *CharacterData_SubstringData(PyCharacterDataObject *self, int index,
                                      int count)
{
  PyObject *newValue;

  newValue = PyUnicode_FromUnicode(NULL, (Py_ssize_t)count);
  if (!newValue) return NULL;

  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue),
                  PyUnicode_AS_UNICODE(self->nodeValue) + index,
                  count);
  return newValue;
}


int CharacterData_AppendData(PyCharacterDataObject *self, PyObject *arg)
{
  PyObject *oldValue = self->nodeValue;
  PyObject *newValue;

  newValue = PyUnicode_FromUnicode(NULL,
                                   PyUnicode_GET_SIZE(oldValue) + \
                                   PyUnicode_GET_SIZE(arg));
  if (!newValue) return -1;

  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue),
                  PyUnicode_AS_UNICODE(oldValue),
                  PyUnicode_GET_SIZE(oldValue));
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue) + PyUnicode_GET_SIZE(oldValue),
                  PyUnicode_AS_UNICODE(arg),
                  PyUnicode_GET_SIZE(arg));

  Py_DECREF(oldValue);
  self->nodeValue = newValue;
  return 0;
}


int CharacterData_InsertData(PyCharacterDataObject *self, int offset,
                             PyObject *arg)
{
  PyObject *oldValue = self->nodeValue;
  PyObject *newValue;

  newValue = PyUnicode_FromUnicode(NULL,
                                   PyUnicode_GET_SIZE(oldValue) + \
                                   PyUnicode_GET_SIZE(arg));
  if (!newValue) return -1;

  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue),
                  PyUnicode_AS_UNICODE(oldValue),
                  offset);
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue) + offset,
                  PyUnicode_AS_UNICODE(arg),
                  PyUnicode_GET_SIZE(arg));
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue) + offset + PyUnicode_GET_SIZE(arg),
                  PyUnicode_AS_UNICODE(oldValue) + offset,
                  PyUnicode_GET_SIZE(oldValue) - offset);

  Py_DECREF(oldValue);
  self->nodeValue = newValue;
  return 0;
}


int CharacterData_DeleteData(PyCharacterDataObject *self, int offset,
                             int count)
{
  PyObject *oldValue = self->nodeValue;
  PyObject *newValue;

  newValue = PyUnicode_FromUnicode(NULL, PyUnicode_GET_SIZE(oldValue) - count);
  if (!newValue) return -1;

  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue),
                  PyUnicode_AS_UNICODE(oldValue),
                  offset);
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue) + offset,
                  PyUnicode_AS_UNICODE(oldValue) + offset + count,
                  PyUnicode_GET_SIZE(oldValue) - offset - count);

  Py_DECREF(oldValue);
  self->nodeValue = newValue;
  return 0;
}


int CharacterData_ReplaceData(PyCharacterDataObject *self, int offset,
                              int count, PyObject *arg)
{
  PyObject *oldValue = self->nodeValue;
  PyObject *newValue;

  newValue = PyUnicode_FromUnicode(NULL,
                                   PyUnicode_GET_SIZE(oldValue) - count + \
                                   PyUnicode_GET_SIZE(arg));
  if (!newValue) return -1;

  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue),
                  PyUnicode_AS_UNICODE(oldValue),
                  offset);
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue) + offset,
                  PyUnicode_AS_UNICODE(arg),
                  PyUnicode_GET_SIZE(arg));
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(newValue) + offset + PyUnicode_GET_SIZE(arg),
                  PyUnicode_AS_UNICODE(oldValue) + offset + count,
                  PyUnicode_GET_SIZE(oldValue) - offset - count);

  Py_DECREF(oldValue);
  self->nodeValue = newValue;
  return 0;
}


/** Python Methods ****************************************************/


static char substring_doc[] = "\
Extracts a range of data from the node.";

static PyObject *characterdata_substring(PyObject *self, PyObject *args)
{
  int offset, count;

  if (!PyArg_ParseTuple(args, "ii:substringData", &offset, &count))
    return NULL;

  return CharacterData_SubstringData((PyCharacterDataObject *)self, offset, count);
}


static char append_doc[] = "\
Append the string to the end of the character data of the node.";

static PyObject *characterdata_append(PyObject *self, PyObject *args)
{
  PyObject *data;

  if (!PyArg_ParseTuple(args, "O:appendData", &data))
    return NULL;

  if ((data = DOMString_ConvertArgument(data, "data", 0)) == NULL)
    return NULL;

  if (CharacterData_AppendData((PyCharacterDataObject *)self, data) == -1) {
    Py_DECREF(data);
    return NULL;
  }
  Py_DECREF(data);

  Py_INCREF(Py_None);
  return Py_None;
}


static char insert_doc[] = "\
Insert a string at the specified unicode unit offset.";

static PyObject *characterdata_insert(PyObject *self, PyObject *args)
{
  int offset;
  PyObject *data;

  if (!PyArg_ParseTuple(args, "iO:insertData", &offset, &data))
    return NULL;

  if ((data = DOMString_ConvertArgument(data, "data", 0)) == NULL)
    return NULL;

  if (CharacterData_InsertData((PyCharacterDataObject *)self, offset, data) == -1) {
    Py_DECREF(data);
    return NULL;
  }

  Py_DECREF(data);
  Py_INCREF(Py_None);
  return Py_None;
}


static char delete_doc[] = "\
Remove a range of unicode units from the node.";

static PyObject *characterdata_delete(PyObject *self, PyObject *args)
{
  int offset, count;

  if (!PyArg_ParseTuple(args, "ii:deleteData", &offset, &count))
    return NULL;

  if (CharacterData_DeleteData((PyCharacterDataObject *)self, offset, count) == -1)
    return NULL;

  Py_INCREF(Py_None);
  return Py_None;
}


static char replace_doc[] = "\
Replace the characters starting at the specified unicode unit offset with\n\
the specified string.";

static PyObject *characterdata_replace(PyObject *self, PyObject *args)
{
  int offset, count;
  PyObject *data;

  if (!PyArg_ParseTuple(args, "iiO:replaceData", &offset, &count, &data))
    return NULL;

  if ((data = DOMString_ConvertArgument(data, "data", 0)) == NULL)
    return NULL;

  if (CharacterData_DeleteData((PyCharacterDataObject *)self, offset, count) == -1) {
    Py_DECREF(data);
    return NULL;
  }

  Py_DECREF(data);
  Py_INCREF(Py_None);
  return Py_None;
}


static struct PyMethodDef characterdata_methods[] = {
  {"substringData", characterdata_substring, METH_VARARGS, substring_doc },
  {"appendData",    characterdata_append,    METH_VARARGS, append_doc },
  {"insertData",    characterdata_insert,    METH_VARARGS, insert_doc },
  {"deleteData",    characterdata_delete,    METH_VARARGS, delete_doc },
  {"replaceData",   characterdata_replace,   METH_VARARGS, replace_doc },
  { NULL }
};


/** Python Members *****************************************************/


/* No additional interface members defined */


/** Python Computed Members ********************************************/


static PyObject *get_data(PyCharacterDataObject *self, void *arg)
{
  Py_INCREF(self->nodeValue);
  return self->nodeValue;
}


static int set_data(PyCharacterDataObject *self, PyObject *v, void *arg)
{
  PyObject *nodeValue = DOMString_ConvertArgument(v, (char *)arg, 0);
  if (nodeValue == NULL) return -1;

  Py_DECREF(self->nodeValue);
  self->nodeValue = nodeValue;
  return 0;
}


static PyObject *get_length(PyCharacterDataObject *self, void *arg)
{
    return PyInt_FromLong(PyUnicode_GET_SIZE(self->nodeValue));
}


static PyGetSetDef characterdata_getset[] = {
  { "data",      (getter)get_data,   (setter)set_data, NULL, "data" },
  { "nodeValue", (getter)get_data,   (setter)set_data, NULL, "nodeValue" },
  { "length",    (getter)get_length },
  { NULL }
};


/** Type Object ********************************************************/


static void characterdata_dealloc(PyCharacterDataObject *self)
{
  PyObject_GC_UnTrack((PyObject *) self);

  Py_XDECREF(self->nodeValue);
  self->nodeValue = NULL;
  Node_Del(self);
}


static PyObject *characterdata_repr(PyCharacterDataObject *self)
{
  PyObject *obj, *repr, *name;

  if (PyUnicode_GET_SIZE(self->nodeValue) > CHARACTERDATA_REPR_LIMIT) {
    Py_UNICODE dots[] = { '.', '.', '.' };
    PyObject *slice, *ellipsis;
    slice = PyUnicode_FromUnicode(PyUnicode_AS_UNICODE(self->nodeValue),
                                  (Py_ssize_t)(CHARACTERDATA_REPR_LIMIT - sizeof(dots)));
    ellipsis = PyUnicode_FromUnicode(dots, 3);
    if (slice == NULL || ellipsis == NULL) {
      Py_XDECREF(slice);
      Py_XDECREF(ellipsis);
      return NULL;
    }
    obj = PyUnicode_Concat(slice, ellipsis);
    Py_DECREF(slice);
    Py_DECREF(ellipsis);
    if (obj == NULL) return NULL;
  } else {
    obj = self->nodeValue;
    Py_INCREF(obj);
  }

  repr = PyObject_Repr(obj);
  Py_DECREF(obj);
  if (repr == NULL) return NULL;

  name = PyObject_GetAttrString((PyObject *)self->ob_type, "__name__");
  if (name == NULL) {
    Py_DECREF(repr);
    return NULL;
  }

  obj = PyString_FromFormat("<%s at %p: %s>", PyString_AS_STRING(name), self,
                            PyString_AS_STRING(repr));
  Py_DECREF(name);
  Py_DECREF(repr);
  return obj;
}


static PyObject *characterdata_new(PyTypeObject *type, PyObject *args,
                                   PyObject *kwds)
{
  PyDocumentObject *doc;
  PyObject *data;
  static char *kwlist[] = { "ownerDocument", "data", NULL };
  PyCharacterDataObject *self;

  if (type == &DomletteCharacterData_Type) {
    PyErr_Format(PyExc_TypeError, "cannot create '%.100s' instances",
                 type->tp_name);
    return NULL;
  }

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O:CharacterData", kwlist,
                                   &DomletteDocument_Type, &doc, &data)) {
    return NULL;
  }

  if ((data = DOMString_ConvertArgument(data, "data", 0)) == NULL)
    return NULL;

  self = (PyCharacterDataObject *) type->tp_alloc(type, 0);
  if (self != NULL) {
    _Node_INIT(self, doc);
    if (characterdata_init(self, data) < 0) {
      Py_DECREF(self);
      self = NULL;
    }
  }
  Py_DECREF(data);

  return (PyObject *) self;
}


static char characterdata_doc[] = "\
CharacterData(ownerDocument, data) -> CharacterData object\n\
\n\
This interface represents a block of XML character data.";

PyTypeObject DomletteCharacterData_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "CharacterData",
  /* tp_basicsize      */ sizeof(PyCharacterDataObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) characterdata_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) characterdata_repr,
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
  /* tp_doc            */ (char *) characterdata_doc,
  /* tp_traverse       */ (traverseproc) 0,
  /* tp_clear          */ 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) characterdata_methods,
  /* tp_members        */ (PyMemberDef *) 0,
  /* tp_getset         */ (PyGetSetDef *) characterdata_getset,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) characterdata_new,
  /* tp_free           */ 0,
};


/** Module Setup & Teardown *******************************************/


int DomletteCharacterData_Init(PyObject *module)
{
  DomletteCharacterData_Type.tp_base = &DomletteNode_Type;
  if (PyType_Ready(&DomletteCharacterData_Type) < 0)
    return -1;

  Py_INCREF(&DomletteCharacterData_Type);
  return PyModule_AddObject(module, "CharacterData",
                            (PyObject*) &DomletteCharacterData_Type);
}


void DomletteCharacterData_Fini(void)
{
  PyType_CLEAR(&DomletteCharacterData_Type);
}
