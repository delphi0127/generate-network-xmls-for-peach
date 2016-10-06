/*
 Escape Quotes written by Mike Olson
 Copyright (c) 2001 Fourthought, Inc. USA.   All Rights Reserved.
 See  http://4suite.org/COPYRIGHT  for license and copyright information
*/

#include <Python.h>
#include <string.h>

static char escape__doc__[] = 
"escape(string)\n\
\n\
Replace all ' with \\' and \\ with \\\\";

static PyObject *escape(PyObject *self, PyObject *args) {
  PyObject *py_src, *result;
  Py_UNICODE *src;
  int size, i, add;

  if (!PyArg_ParseTuple(args, "O:escape", &py_src)) {
    return NULL;
  }

  if (py_src == Py_None) {
    return PyUnicode_FromUnicode(NULL, 0);
  }

  if (!PyUnicode_CheckExact(py_src)) {
    py_src = PyUnicode_FromObject(py_src);
    if (py_src == NULL) return NULL;
  } else {
    Py_INCREF(py_src);
  }
    
  /* First pass, determine how many characters need to be added */
  src = PyUnicode_AS_UNICODE(py_src);
  size = PyUnicode_GET_SIZE(py_src);
  for (i = 0, add = 0; i < size; i++) {
    if (src[i] == '\'' || src[i] == '\\') add++;
  }

  /* Nothing to escape, return original string */
  if (add == 0) {
    return py_src;
  }

  /* Second pass, replace characters */
  result = PyUnicode_FromUnicode(NULL, (size + add));
  if (result) {
    Py_UNICODE *p = PyUnicode_AS_UNICODE(result);
    for (i = 0; i < size; i++) {
      Py_UNICODE ch = src[i];
      if (ch == '\'' || ch == '\\') {
        *p++ = '\\';
        if (--add <= 0) {
          /* copy remaining part */
          Py_UNICODE_COPY(p, src+i, size-i);
          break;
        }
      }
      *p++ = ch;
    }
  }
  return result;
}


static PyMethodDef escapeQuotesMethods[] = {
     { "escape",  escape,  METH_VARARGS, escape__doc__ },
     { NULL, NULL }
};

DL_EXPORT(void) initEscapeQuotesc(void) {
  PyObject *module, *dict;
  module = Py_InitModule("EscapeQuotesc", escapeQuotesMethods);
  dict = PyModule_GetDict(module);
}
