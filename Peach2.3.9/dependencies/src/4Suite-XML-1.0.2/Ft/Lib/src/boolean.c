/*
 Boolean extension, by Uche Ogbuji
 Copyright (c) 2001 Fourthought, Inc. USA.   All Rights Reserved.
 See  http://4suite.org/COPYRIGHT  for license and copyright information
*/

#include "Python.h"
#include "number.h"


static PyTypeObject PyBoolean_Type;

#define PyBoolean_Check(op)  ((op)->ob_type == &PyBoolean_Type)
#define PyBoolean_AsLong(op)  PyInt_AS_LONG(op)

typedef PyIntObject PyBooleanObject;
static PyBooleanObject _PyBoolean_FalseStruct;
static PyBooleanObject _PyBoolean_TrueStruct;

#define PyBoolean_False ((PyObject *) &_PyBoolean_FalseStruct)
#define PyBoolean_True ((PyObject *) &_PyBoolean_TrueStruct)


static PyObject *PyBoolean_FromLong(long ok)
{
  PyObject *result;
  if (ok)
    result = PyBoolean_True;
  else
    result = PyBoolean_False;
  Py_INCREF(result);
  return result;
}

static PyObject *PyBoolean_FromObject(PyObject *obj)
{
  PyObject *result;
  if (PyNumber_IsNaN(obj)) 
    result = PyBoolean_False;
  else {
    switch (PyObject_IsTrue(obj)) {
    case 0:
      result = PyBoolean_False;
      break;
    case 1:
      result = PyBoolean_True;
      break;
    default:
      return NULL;
    }
  }
  Py_INCREF(result);
  return result;
}

static PyObject *PyBoolean_New(PyObject *self, PyObject *args)
{
  PyObject *obj;

  if (!PyArg_ParseTuple(args, "O", &obj))
    return NULL;

  return PyBoolean_FromObject(obj);
}

/* type object functions */

static void boolean_dealloc(PyObject *self)
{
  PyObject_Del(self);
}

static int boolean_print(PyObject *self, FILE *fp, int flags)
{
  fputs(PyBoolean_AsLong(self) ? "true" : "false", fp);
  return 0;
}

static int boolean_compare(PyObject *v, PyObject *w)
{
  register int i = PyBoolean_AsLong(v);
  register int j = PyBoolean_AsLong(w);
  return (i < j) ? -1 : (i > j) ? 1 : 0;
}

static PyObject *boolean_repr(PyObject *self)
{
  static PyObject *true_str = NULL;
  static PyObject *false_str = NULL;
  PyObject *repr;
  
  if (PyBoolean_AsLong(self)) 
    repr = true_str ? true_str :
      (true_str = PyString_InternFromString("true"));
  else
    repr = false_str ? false_str :
      (false_str = PyString_InternFromString("false"));

  Py_XINCREF(repr);
  return repr;
}

static long boolean_hash(PyObject *self)
{
  return PyBoolean_AsLong(self);
}

/* tp_as_number functions */

static int boolean_nonzero(PyObject *v)
{
  return PyBoolean_AsLong(v);
}

static PyObject *boolean_and(PyObject *a, PyObject *b)
{
  if (PyBoolean_Check(a) && PyBoolean_Check(b)) {
    /* both are bools, return a bool */
    return PyBoolean_FromLong(PyBoolean_AsLong(a) & PyBoolean_AsLong(b));
  } 
  else {
    /* only one is a bool, */
    PyObject *result;
    if (PyBoolean_Check(a)) a = PyInt_FromLong(PyBoolean_AsLong(a));
    else Py_INCREF(a);
    
    if (PyBoolean_Check(b)) b = PyInt_FromLong(PyBoolean_AsLong(b));
    else Py_INCREF(b);

    result = PyNumber_And(a, b);
    Py_DECREF(a);
    Py_DECREF(b);
    return result;
  }
}

static PyObject *boolean_xor(PyObject *a, PyObject *b)
{
  if (PyBoolean_Check(a) && PyBoolean_Check(b)) {
    /* both are bools, return a bool */
    return PyBoolean_FromLong(PyBoolean_AsLong(a) ^ PyBoolean_AsLong(b));
  } 
  else {
    /* only one is a bool, */
    PyObject *result;
    if (PyBoolean_Check(a)) a = PyInt_FromLong(PyBoolean_AsLong(a));
    else Py_INCREF(a);
    
    if (PyBoolean_Check(b)) b = PyInt_FromLong(PyBoolean_AsLong(b));
    else Py_INCREF(b);

    result = PyNumber_Xor(a, b);
    Py_DECREF(a);
    Py_DECREF(b);
    return result;
  }
}

static PyObject *boolean_or(PyObject *a, PyObject *b)
{
  if (PyBoolean_Check(a) && PyBoolean_Check(b)) {
    /* both are bools, return a bool */
    return PyBoolean_FromLong(PyBoolean_AsLong(a) | PyBoolean_AsLong(b));
  } 
  else {
    /* only one is a bool, */
    PyObject *result;
    if (PyBoolean_Check(a)) a = PyInt_FromLong(PyBoolean_AsLong(a));
    else Py_INCREF(a);
    
    if (PyBoolean_Check(b)) b = PyInt_FromLong(PyBoolean_AsLong(b));
    else Py_INCREF(b);

    result = PyNumber_Or(a, b);
    Py_DECREF(a);
    Py_DECREF(b);
    return result;
  }
}

static int boolean_coerce(PyObject **pv, PyObject **pw)
{
  /* NOTE - this always succeeds (everything can be true or false) */
  Py_INCREF(*pv);
  if (PyBoolean_Check(*pw)) {
    /* both are boolean objects */
    Py_INCREF(*pw);
  }
  else {
    /* convert it to a boolean */
    *pw = PyBoolean_FromObject(*pw);
  }
  return 0;
}

static PyObject *boolean_int(PyObject *o){
  PyBooleanObject *obj = (PyBooleanObject *)o;
  PyObject *result = NULL;

  result = PyInt_FromLong((long)PyBoolean_AsLong(obj));
  Py_INCREF(result);
  return result;
}

static PyObject *boolean_long(PyObject *o){
  PyBooleanObject *obj = (PyBooleanObject *)o;
  PyObject *result = NULL;

  result = PyLong_FromLong((long)PyBoolean_AsLong(obj));
  Py_INCREF(result);
  return result;
}

static PyObject *boolean_float(PyObject *o){
  PyBooleanObject *obj = (PyBooleanObject *)o;
  PyObject *result = NULL;

  result = PyFloat_FromDouble((double)PyBoolean_AsLong(obj));
  Py_INCREF(result);
  return result;
}

static PyObject *boolean_oct(PyObject *v)
{
  return PyString_FromString(PyBoolean_AsLong(v) ? "01" : "0");
}

static PyObject *boolean_hex(PyObject *v)
{
  return PyString_FromString(PyBoolean_AsLong(v) ? "0x1" : "0x0");
}

static char bool_doc[] = 
"bool(x) -> bool\n\
\n\
Returns True when the argument x is true, False otherwise.";

static PyMethodDef booleanMethods[] = {
  { "bool", PyBoolean_New, METH_VARARGS, bool_doc },
  { NULL, NULL }
};


DL_EXPORT(void) initboolean(void) {
  PyObject *m, *d;

  m = Py_InitModule("boolean", booleanMethods);
  d = PyModule_GetDict(m);

  /* expose the type */
  PyBoolean_Type.ob_type = &PyType_Type;
  Py_INCREF(&PyBoolean_Type);
  if (PyDict_SetItemString(d, "BooleanType", (PyObject *)&PyBoolean_Type))
    return;

  /* create global true value */
  Py_INCREF(PyBoolean_True);
  if (PyDict_SetItemString(d, "true", PyBoolean_True))
    return;

  /* create global false value */
  Py_INCREF(PyBoolean_False);
  if (PyDict_SetItemString(d, "false", PyBoolean_False))
    return;

  return;
}

static PyNumberMethods boolean_as_number = {
  0,       /* binaryfunc nb_add;          __add__ */
  0,       /* binaryfunc nb_subtract;     __sub__ */
  0,       /* binaryfunc nb_multiply;     __mul__ */
  0,       /* binaryfunc nb_divide;       __div__ */
  0,       /* binaryfunc nb_remainder;    __mod__ */
  0,       /* binaryfunc nb_divmod;       __divmod__ */
  0,       /* ternaryfunc nb_power;       __pow__ */
  0,       /* unaryfunc nb_negative;      __neg__ */
  0,       /* unaryfunc nb_positive;      __pos__ */
  0,       /* unaryfunc nb_absolute;      __abs__ */
  boolean_nonzero,   /* inquiry nb_nonzero;         __nonzero__ */
  0,       /* unaryfunc nb_invert;        __invert__ */
  0,       /* binaryfunc nb_lshift;       __lshift__ */
  0,       /* binaryfunc nb_rshift;       __rshift__ */
  boolean_and,       /* binaryfunc nb_and;         __and__ */
  boolean_xor,       /* binaryfunc nb_xor;         __xor__ */
  boolean_or,        /* binaryfunc nb_or;          __or__ */
  boolean_coerce,    /* coercion nb_coerce;        __coerce__ */
  boolean_int,       /* unaryfunc nb_int;          __int__ */
  boolean_long,      /* unaryfunc nb_long;         __long__ */
  boolean_float,     /* unaryfunc nb_float;        __float__ */
  boolean_oct,       /* unaryfunc nb_oct;           __oct__ */
  boolean_hex,       /* unaryfunc nb_hex;           __hex__ */
};

static PyTypeObject PyBoolean_Type = {
    PyObject_HEAD_INIT(0)
    0,
    "boolean",
    sizeof(PyBooleanObject),
    0,
    boolean_dealloc,    /*tp_dealloc*/
    boolean_print,   /*tp_print*/
    0,              /*tp_getattr*/
    0,              /*tp_setattr*/
    &boolean_compare,                          /*tp_compare*/
    &boolean_repr,          /*tp_repr*/
    &boolean_as_number,                          /*tp_as_number*/
    0,              /*tp_as_sequence*/
    0,              /*tp_as_mapping*/
    boolean_hash,              /*tp_hash*/
    0,              /*tp_call*/
    boolean_repr,          /*tp_str*/
    0,                      /*tp_getattro*/
    0,              /*tp_setattro*/
};

static PyBooleanObject _PyBoolean_FalseStruct = {
  PyObject_HEAD_INIT(&PyBoolean_Type)
  0
  };

static PyBooleanObject _PyBoolean_TrueStruct = {
  PyObject_HEAD_INIT(&PyBoolean_Type)
  1
  };
