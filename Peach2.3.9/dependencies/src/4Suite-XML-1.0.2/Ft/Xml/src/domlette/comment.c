#include "domlette.h"


/** Private Routines **************************************************/


/** Public C API *******************************************************/


/** Python Methods ****************************************************/


/* No additional interface methods defined */


/** Python Members *****************************************************/


/* No additional interface members defined */


/** Python Computed Members ********************************************/


/* No additional interface members defined */


/** Type Object ********************************************************/


static char comment_doc[] = "\
Comment(ownerDocument, data) -> Comment object\n\
\n\
This interface represents the content of a comment, i.e., all the characters\n\
between the starting '<!--' and ending '-->'.";

PyTypeObject DomletteComment_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "Comment",
  /* tp_basicsize      */ sizeof(PyCommentObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) 0,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) 0,
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
  /* tp_doc            */ (char *) comment_doc,
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
  /* tp_new            */ (newfunc) 0,
  /* tp_free           */ 0,
};


/** Module Setup & Teardown *******************************************/


int DomletteComment_Init(PyObject *module)
{
  PyObject *dict, *value;

  DomletteComment_Type.tp_base = &DomletteCharacterData_Type;
  if (PyType_Ready(&DomletteComment_Type) < 0)
    return -1;

  dict = DomletteComment_Type.tp_dict;

  value = PyInt_FromLong(COMMENT_NODE);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeType", value))
    return -1;
  Py_DECREF(value);

  value = PyUnicode_DecodeASCII("#comment", (Py_ssize_t)8, NULL);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeName", value))
    return -1;
  Py_DECREF(value);

  Py_INCREF(&DomletteComment_Type);
  return PyModule_AddObject(module, "Comment",
                            (PyObject*) &DomletteComment_Type);
}


void DomletteComment_Fini(void)
{
  PyType_CLEAR(&DomletteComment_Type);
}
