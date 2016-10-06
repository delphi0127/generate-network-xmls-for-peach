/*
 Number extension, by Jeremy Kloth
 Copyright (c) 2001 Fourthought, Inc. USA.   All Rights Reserved.
 See  http://4suite.org/COPYRIGHT  for license and copyright information
*/

#include <Python.h>
#include "number.h"

static PyObject *PyNumber_NaN, *PyNumber_Inf;

static char isnan__doc__[] = "\
isnan(number) -> non-zero if not-a-number";
static PyObject *number_isnan(PyObject *self, PyObject *args) {
  PyObject *number;

  if (!PyArg_ParseTuple(args, "O:isnan", &number)) {
    return NULL;
  }

  if (!PyNumber_Check(number)) {
    PyObject *type = PyObject_Type(number);
    PyObject *name = PyObject_GetAttrString(type, "__name__");
    PyErr_SetObject(PyExc_ValueError, name);
    Py_DECREF(name);
    return NULL;
  }

  return PyInt_FromLong(PyNumber_IsNaN(number));
}

static char isinf__doc__[] = "\
isinf(number) -> -1 if negative infinity,\n\
                  1 if positive infinity,\n\
                  0 otherwise\n";
static PyObject *number_isinf(PyObject *self, PyObject *args) {
  PyObject *number;

  if (!PyArg_ParseTuple(args, "O:isinf", &number)) {
    return NULL;
  }

  if (!PyNumber_Check(number)) {
    PyObject *type = PyObject_Type(number);
    PyObject *name = PyObject_GetAttrString(type, "__name__");
    PyErr_SetObject(PyExc_ValueError, name);
    Py_DECREF(name);
    return NULL;
  }

  return PyInt_FromLong(PyNumber_IsInf(number));
}

static char finite__doc__[] = "\
finite(number) -> non-zero if neither infinite or not-a-number";

static PyObject *number_finite(PyObject *self, PyObject *args) {
  PyObject *number;

  if (!PyArg_ParseTuple(args, "O:finite", &number)) {
    return NULL;
  }

  if (!PyNumber_Check(number)) {
    PyObject *type = PyObject_Type(number);
    PyObject *name = PyObject_GetAttrString(type, "__name__");
    PyErr_SetObject(PyExc_ValueError, name);
    Py_DECREF(name);
    return NULL;
  }

  return PyInt_FromLong(PyNumber_Finite(number));
}

static PyMethodDef numberMethods[] = {
     { "isnan",  number_isnan,  METH_VARARGS, isnan__doc__ },
     { "isinf",  number_isinf,  METH_VARARGS, isinf__doc__ },
     { "finite", number_finite, METH_VARARGS, finite__doc__ },
     { NULL, NULL }
};

DL_EXPORT(void) initnumber(void) {
  PyObject *module, *dict;
  double Inf;

  module = Py_InitModule("number", numberMethods);
  dict = PyModule_GetDict(module);

  /* broken into two lines to prevent compiler warnings */
  Inf = 1e300;
  Inf *= Inf;
  PyNumber_Inf = PyFloat_FromDouble(Inf);
  PyDict_SetItemString(dict, "inf", PyNumber_Inf);

  /* use Python because of "smart" compilers optimizing this to zero */
  /*NaN = Inf - Inf;*/
  PyNumber_NaN = PyNumber_Subtract(PyNumber_Inf, PyNumber_Inf);
  PyDict_SetItemString(dict, "nan", PyNumber_NaN);
}
