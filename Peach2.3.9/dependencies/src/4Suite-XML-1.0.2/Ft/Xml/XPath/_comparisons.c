#include "Python.h"
#include "number.h"

static PyObject *cmp_lt(PyObject *module, PyObject *args)
{
  PyObject *a, *b;

  if (!PyArg_ParseTuple(args, "OO:lt", &a, &b)) return NULL;

  if (PyNumber_IsNaN(a) || PyNumber_IsNaN(b)) {
    Py_INCREF(Py_False);
    return Py_False;
  }

  return PyObject_RichCompare(a, b, Py_LT);
}

static PyObject *cmp_le(PyObject *module, PyObject *args)
{
  PyObject *a, *b;

  if (!PyArg_ParseTuple(args, "OO:le", &a, &b)) return NULL;

  if (PyNumber_IsNaN(a) || PyNumber_IsNaN(b)) {
    Py_INCREF(Py_False);
    return Py_False;
  }

  return PyObject_RichCompare(a, b, Py_LE);
}

static PyObject *cmp_eq(PyObject *module, PyObject *args)
{
  PyObject *a, *b;

  if (!PyArg_ParseTuple(args, "OO:eq", &a, &b)) return NULL;

  if (PyNumber_IsNaN(a) || PyNumber_IsNaN(b)) {
    /* Not-A-Number doesn't equal anything, even itself */
    Py_INCREF(Py_False);
    return Py_False;
  }

  return PyObject_RichCompare(a, b, Py_EQ);
}

static PyObject *cmp_ne(PyObject *module, PyObject *args)
{
  PyObject *a, *b;

  if (!PyArg_ParseTuple(args, "OO:ne", &a, &b)) return NULL;

  if (PyNumber_IsNaN(a) || PyNumber_IsNaN(b)) {
    /* Not-A-Number doesn't equal anything, even itself */
    Py_INCREF(Py_True);
    return Py_True;
  }

  return PyObject_RichCompare(a, b, Py_NE);
}

static PyObject *cmp_ge(PyObject *module, PyObject *args)
{
  PyObject *a, *b;

  if (!PyArg_ParseTuple(args, "OO:ge", &a, &b)) return NULL;

  if (PyNumber_IsNaN(a) || PyNumber_IsNaN(b)) {
    Py_INCREF(Py_False);
    return Py_False;
  }

  return PyObject_RichCompare(a, b, Py_GE);
}

static PyObject *cmp_gt(PyObject *module, PyObject *args)
{
  PyObject *a, *b;

  if (!PyArg_ParseTuple(args, "OO:gt", &a, &b)) return NULL;

  if (PyNumber_IsNaN(a) || PyNumber_IsNaN(b)) {
    Py_INCREF(Py_False);
    return Py_False;
  }

  return PyObject_RichCompare(a, b, Py_GT);
}

static PyMethodDef cmp_methods[] = {
  { "lt" , cmp_lt, METH_VARARGS, "lt(a, b) -- Same as a < b" },
  { "le" , cmp_le, METH_VARARGS, "le(a, b) -- Same as a <= b" },
  { "eq" , cmp_eq, METH_VARARGS, "eq(a, b) -- Same as a == b" },
  { "ne" , cmp_ne, METH_VARARGS, "ne(a, b) -- Same as a != b" },
  { "ge" , cmp_ge, METH_VARARGS, "ge(a, b) -- Same as a >= b" },
  { "gt" , cmp_gt, METH_VARARGS, "gt(a, b) -- Same as a > b" },
  { NULL, NULL }
};

DL_EXPORT(void) init_comparisons(void) {
  (void) Py_InitModule("_comparisons", cmp_methods);
}
