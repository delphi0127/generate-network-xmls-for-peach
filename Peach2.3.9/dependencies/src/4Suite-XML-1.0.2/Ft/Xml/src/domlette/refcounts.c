#include "domlette.h"

/* Reference counting scheme *****************************************
 *
 * Domlette Nodes save a reference to their ownerDocument but use a
 * borrowed reference to their parentNode.
 *
 *********************************************************************/

static int do_test(PyObject *tester, char *title, Py_ssize_t expected,
                   Py_ssize_t actual)
{
  PyObject *rv;

  rv = PyObject_CallMethod(tester, "startTest", "s", title);
  if (rv == NULL)
    return 0;
  Py_DECREF(rv);

  rv = PyObject_CallMethod(tester, "compare", "ll", expected, actual);
  if (rv == NULL)
    return 0;
  Py_DECREF(rv);

  rv = PyObject_CallMethod(tester, "testDone", "");
  if (rv == NULL)
    return 0;
  Py_DECREF(rv);

  return 1;
}

static int node_refcounts(PyObject *tester, PyNodeObject *node,
                          Py_ssize_t *counter)
{
  Py_ssize_t expected;
  char buf[256];

  /* increment total node count */
  (*counter)++;

  if (PyElement_Check(node)) {
    Py_ssize_t i;
    PyObject *k;
    PyNodeObject *v;

    /* test element's children */
    for (i = 0; i < ContainerNode_GET_COUNT(node); i++) {
      v = ContainerNode_GET_CHILD(node, i);
      if (node_refcounts(tester, v, counter) == 0) return 0;
    }

    /* test element's attributes */
    i = 0;
    while (PyDict_Next(PyElement_ATTRIBUTES(node), &i, &k, (PyObject **)&v)) {
      if (node_refcounts(tester, v, counter) == 0) return 0;
    }

    /* refcount = this */
    expected = 1;
  }
  else if (PyText_Check(node)) {
    /* refcount = this */
    expected = 1;
  }
  else if (PyComment_Check(node)) {
    /* refcount = this */
    expected = 1;
  }
  else if (PyAttr_Check(node)) {
    /* refcount = this */
    expected = 1;
  }
  else if (PyProcessingInstruction_Check(node)) {
    /* refcount = this */
    expected = 1;
  }
  else {
    sprintf(buf, "Unexpected object type '%.200s'" ,node->ob_type->tp_name);
    Py_XDECREF(PyObject_CallMethod(tester, "error", "s", buf));
    return 0;
  }

  sprintf(buf, "%.200s refcounts", node->ob_type->tp_name);
  return do_test(tester, buf, expected, node->ob_refcnt);
}

int test_refcounts(PyObject *tester, PyObject *doc)
{
  Py_ssize_t expected;
  int i;
  char buf[256];

  /* refcount = 2  + counter (ownerDocument) */
  expected = 2;

  for (i = 0; i < ContainerNode_GET_COUNT(doc); i++) {
    PyNodeObject *node = ContainerNode_GET_CHILD(doc, i);
    if (node_refcounts(tester, (PyNodeObject *)node, &expected) == 0) return 0;
  }

  sprintf(buf, "%.200s refcounts", doc->ob_type->tp_name);
  return do_test(tester, buf, expected, doc->ob_refcnt);
}
