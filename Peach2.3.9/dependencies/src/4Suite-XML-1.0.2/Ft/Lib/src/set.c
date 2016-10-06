/***********************************************************************
 * $Header: /var/local/cvsroot/4Suite/Ft/Lib/src/set.c,v 1.2 2005/02/14 19:49:40 jkloth Exp $
 ***********************************************************************/

static char module_doc[] = "\
Operations on ordered sets\n\
\n\
Copyright 2005 Fourthought, Inc. (USA).\n\
Detailed license and copyright information: http://4suite.org/COPYRIGHT\n\
Project home, documentation, distributions: http://4suite.org/\n\
";

#include "Python.h"

/** Internal Functions ************************************************/

static PyObject *make_dict(PyObject *iterable)
{
  PyObject *it, *dict, *item;

  it = PyObject_GetIter(iterable);
  if (it == NULL)
    return NULL;

  dict = PyDict_New();
  if (dict == NULL) {
    Py_DECREF(it);
    return NULL;
  }

  while ((item = PyIter_Next(it)) != NULL) {
    if (PyDict_SetItem(dict, item, Py_True) == -1) {
      Py_DECREF(item);
      Py_DECREF(dict);
      Py_DECREF(it);
      return NULL;
    }
    Py_DECREF(item);
  }
  Py_DECREF(it);

  return dict;
}


/* this function consumes a reference from 'set' */
static PyObject *make_ordered_set(PyObject *set)
{
  PyObject *result = PySequence_List(set);
  if (result == NULL) {
    Py_DECREF(set);
  } else {
    Py_DECREF(set);
    if (PyList_Sort(result) == -1) {
      Py_DECREF(result);
      return NULL;
    }
  }    
  return result;
}


/** Python Functions **************************************************/

static char not_doc[] = "\
Not(a, b) -> ordered-set\n\
\n\
Return the difference of the two sets as a new set (i.e., all the elements\n\
from set a that are not in set b).";

static PyObject *set_not(PyObject *module, PyObject *args)
{
  PyObject *a, *b, *item;

  if (!PyArg_ParseTuple(args, "OO:Not", &a, &b))
    return NULL;

  if (PyObject_IsTrue(a) == 0) {
    /* nothing to subtract from, return empty set */
    return PyList_New(0);
  } else if (PyObject_IsTrue(b) == 0) {
    /* nothing to subtract, use original set */
    return PySequence_List(a);
  }

  /* subtract set b from set a */
  a = make_dict(a);
  if (a == NULL)
    return NULL;
  b = PyObject_GetIter(b);
  if (b == NULL) {
    Py_DECREF(a);
    return NULL;
  }
  while ((item = PyIter_Next(b)) != NULL) {
    if (PyDict_DelItem(a, item) == -1) {
      if (PyErr_ExceptionMatches(PyExc_KeyError)) {
        PyErr_Clear();
      } else {
        Py_DECREF(item);
        Py_DECREF(b);
        Py_DECREF(a);
        return NULL;
      }
    }
    Py_DECREF(item);
  }
  Py_DECREF(b);
  return make_ordered_set(a);
}


static char union_doc[] = "\
Union(a, b) -> ordered-set\n\
\n\
Return the union of the two sets as a new set (i.e., all the elements\n\
that are in either set).";

static PyObject *set_union(PyObject *module, PyObject *args)
{
  PyObject *a, *b, *item;

  if (!PyArg_ParseTuple(args, "OO:Union", &a, &b))
    return NULL;

  if (PyObject_IsTrue(a) == 0) {
    /* empty set a, reuse b */
    return PySequence_List(b);
  } else if (PyObject_IsTrue(b) == 0) {
    /* empty set b, reuse a */
    return PySequence_List(a);
  }
  /* create a new set containing the union of a and b */
  a = make_dict(a);
  if (a == NULL)
    return NULL;
  b = PyObject_GetIter(b);
  if (b == NULL) {
    Py_DECREF(a);
    return NULL;
  }
  while ((item = PyIter_Next(b)) != NULL) {
    if (PyDict_SetItem(a, item, Py_True) == -1) {
      Py_DECREF(item);
      Py_DECREF(b);
      Py_DECREF(a);
      return NULL;
    }
    Py_DECREF(item);
  }
  Py_DECREF(b);
  return make_ordered_set(a);
}


static char intersection_doc[] = "\
Intersection(a, b) -> ordered-set\n\
\n\
Return the intersection of the two sets as a new set (i.e., all the elements\n\
that are in both sets).";

static PyObject *set_intersection(PyObject *module, PyObject *args)
{
  PyObject *a, *b, *set, *item;

  if (!PyArg_ParseTuple(args, "OO:Intersection", &a, &b))
    return NULL;

  if (PyObject_IsTrue(a) == 0 || PyObject_IsTrue(b) == 0)
    /* either a or b are empty so the intersection is empty as well */
    return PyList_New(0);

  set = PyDict_New();
  if (set == NULL)
    return NULL;
  a = make_dict(a);
  if (a == NULL) {
    Py_DECREF(set);
    return NULL;
  }
  b = PyObject_GetIter(b);
  if (b == NULL) {
    Py_DECREF(a);
    Py_DECREF(set);
    return NULL;
  }
  while ((item = PyIter_Next(b)) != NULL) {
    if (PyDict_GetItem(a, item) != NULL) {
      if (PyDict_SetItem(set, item, Py_True) == -1) {
        Py_DECREF(item);
        Py_DECREF(b);
        Py_DECREF(a);
        Py_DECREF(set);
        return NULL;
      }
    }
    Py_DECREF(item);
  }
  Py_DECREF(b);
  Py_DECREF(a);
  return make_ordered_set(set);
}


static char unique_doc[] = "\
Unique(a) -> ordered-set\n\
\n\
Return a new set with any duplicates removed.";

static PyObject *set_unique(PyObject *module, PyObject *args)
{
  PyObject *a;

  if (!PyArg_ParseTuple(args, "O:Unique", &a))
    return NULL;

  if (PyObject_IsTrue(a) == 0)
    /* empty set, return new empty set */
    return PyList_New(0);

  a = make_dict(a);
  if (a == NULL)
    return NULL;
  return make_ordered_set(a);
}


static PyMethodDef module_methods[] = {
  { "Not",          set_not,          METH_VARARGS, not_doc },
  { "Union",        set_union,        METH_VARARGS, union_doc },
  { "Intersection", set_intersection, METH_VARARGS, intersection_doc },
  { "Unique",       set_unique,       METH_VARARGS, unique_doc },
  { NULL }
};

DL_EXPORT(void) initSet(void) {
  PyObject *module, *dict;

  module = Py_InitModule3("Set", module_methods, module_doc);
  dict = PyModule_GetDict(module);
}
