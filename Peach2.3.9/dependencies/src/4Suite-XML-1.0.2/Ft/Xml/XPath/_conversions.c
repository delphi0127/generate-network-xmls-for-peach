#include "Python.h"

#include "number.h"
#include "domlette/nodetype.h"

static PyObject *PyBoolean_Type;
static PyObject *PyBoolean_False;
static PyObject *PyBoolean_True;
static PyObject *PyNumber_NaN;

#define PyBoolean_Check(op) ((op)->ob_type == (PyTypeObject*)PyBoolean_Type)


static PyObject *string_to_number(PyObject *string)
{
  PyObject *result = PyNumber_Float(string);
  if (result == NULL) {
    PyErr_Clear();
    Py_INCREF(PyNumber_NaN);
    result = PyNumber_NaN;
  }
  return result;
}

static PyObject *node_descendants(PyObject *node, PyObject *descendants)
{
  PyObject *childNodes, *child, *nodeType, *data;
  int i;

  childNodes = PyObject_GetAttrString(node, "childNodes");
  if (childNodes == NULL) return NULL;

  for (i = 0; i < PySequence_Size(childNodes); i++) {
    child = PySequence_GetItem(childNodes, i);
    if (child == NULL) {
      Py_DECREF(childNodes);
      return NULL;
    }

    nodeType = PyObject_GetAttrString(child, "nodeType");
    if (nodeType == NULL) {
      Py_DECREF(child);
      Py_DECREF(childNodes);
      return NULL;
    }

    switch (PyInt_AsLong(nodeType)) {
    case ELEMENT_NODE: 
      if (node_descendants(child, descendants) == NULL) {
        Py_DECREF(nodeType);
        Py_DECREF(child);
        Py_DECREF(childNodes);
        return NULL;
      }
      break;
    case TEXT_NODE: 
      data = PyObject_GetAttrString(child, "data");
      if (data == NULL) {
        Py_DECREF(nodeType);
        Py_DECREF(child);
        Py_DECREF(childNodes);
        return NULL;
      }
      PyList_Append(descendants, data);
      Py_DECREF(data);
      break;
    }
    Py_DECREF(nodeType);
    Py_DECREF(child);
  }

  Py_DECREF(childNodes);
  return descendants;
}

static PyObject *node_to_string(PyObject *node)
{
  PyObject *nodeType, *result, *descendants;

  nodeType = PyObject_GetAttrString(node, "nodeType");
  if (nodeType == NULL) {
    PyErr_Clear();
    return PyUnicode_FromUnicode(NULL, 0);
  }
  
  /* convert DOM node to string */
  switch (PyInt_AsLong(nodeType)) {
  case DOCUMENT_NODE:
  case ELEMENT_NODE:
    /* The concatenation of all text descendants in document order */
    descendants = PyList_New(0);
    if (node_descendants(node, descendants) == NULL) {
      Py_DECREF(descendants);
      return NULL;
    }
    result = PyUnicode_Join(PyUnicode_FromUnicode(NULL, 0), descendants);
    Py_DECREF(descendants);
    break;
  case ATTRIBUTE_NODE:
  case XPATH_NAMESPACE_NODE:
    result = PyObject_GetAttrString(node, "value");
    break;
  case PROCESSING_INSTRUCTION_NODE:
  case COMMENT_NODE:
  case TEXT_NODE:
    result = PyObject_GetAttrString(node, "data");
    break;
  default:
    result = PyUnicode_FromUnicode(NULL, 0);
  }

  Py_DECREF(nodeType);
  return result;
}

static PyObject *object_to_string(PyObject *object)
{
  PyObject *result = NULL;

  if (PyUnicode_Check(object)) {
    Py_INCREF(object);
    result = object;
  }
  
  else if (PyString_Check(object)) {
    /* Python DOM binding: string objects must be UTF-8 */
    result = PyUnicode_FromEncodedObject(object, "UTF-8", "strict");
  }

  else if (PyFloat_Check(object)) {
    double d = PyFloat_AS_DOUBLE(object);
    if (PyNumber_Finite(object)) {
      if (floor(d) == d) {
        /* Format as integer */
        PyObject *num = PyNumber_Long(object);
        if (!num)
          return NULL;
        result = PyObject_Unicode(num);
        Py_DECREF(num);
      } 
      else {
        /* worst case length calc to ensure no buffer overrun:
           fmt = %#.<prec>g
           buf = '-' + [0-9]*prec + '.' + 'e+' + (longest exp for 
                                                  any double rep.) 
           len = 1 + prec + 1 + 2 + 5 = 9 + prec
           If prec=0 the effective precision is 1 (the leading digit is
           always given), therefore increase by one to 10+prec. 
        */
        char buf[32]; /* only 10 + 12 + '\0' is needed, more than enough */
        int len;
        len = sprintf(buf, "%0.12g", d);
        result = PyUnicode_DecodeASCII(buf, len, "strict");
      }
    }
    else if (PyNumber_IsNaN(object)) {
      result = PyUnicode_DecodeASCII("NaN", 3, "strict");
    }
    else if (d < 0) {
      result = PyUnicode_DecodeASCII("-Infinity", 9, "strict");
    }
    else {
      result = PyUnicode_DecodeASCII("Infinity", 8, "strict");
    }
  }

  else if (PyBoolean_Check(object)) {
    if (PyObject_IsTrue(object))
      result = PyUnicode_DecodeASCII("true", 4, "strict");
    else
      result = PyUnicode_DecodeASCII("false", 5, "strict");
  }

  else if (PyInt_Check(object) || PyLong_Check(object)) {
    result = PyObject_Unicode(object);
  }

  else if (PyList_Check(object)) {
    if (PyList_GET_SIZE(object)) 
      result = object_to_string(PyList_GET_ITEM(object, 0));
    else
      result = PyUnicode_FromUnicode(NULL, 0);
  }

  else {
    /* check for pre-computed string value */
    result = PyObject_GetAttrString(object, "stringValue");
    if (result == NULL) {
      /* assume a DOM node, node_to_string() returns empty string if not */
      PyErr_Clear();
      result = node_to_string(object);
    }
  }
  return result;
}

static char string_doc[] = 
"StringValue(object) -> XPath string\n\
\n\
Implementation of the XPath 1.0 Recommendation's string function";

static PyObject *StringValue(PyObject *self, PyObject *args)
{
  PyObject *object;

  if (!PyArg_ParseTuple(args, "O:StringValue", &object))
    return NULL;
  
  return object_to_string(object);
}

static char number_doc[] = 
"NumberValue(object) -> XPath number\n\
\n\
Implementation of the XPath 1.0 Recommendation's number function";

static PyObject *NumberValue(PyObject *self, PyObject *args)
{
  PyObject *object;
  PyObject *result = NULL;

  if (!PyArg_ParseTuple(args, "O:NumberValue", &object))
    return NULL;
  
  result = PyNumber_Float(object);
  if (result)
    return result;

  PyErr_Clear();

  if (PyString_Check(object) || PyUnicode_Check(object))
    return string_to_number(object);

  /* convert it to a string */
  object = object_to_string(object);
  if (object) {
    result = string_to_number(object);
    Py_DECREF(object);
  }
  else result = NULL;

  return result;
}

static char boolean_doc[] = 
"BooleanValue(object) -> XPath boolean\n\
\n\
Implementation of the XPath 1.0 Recommendation's boolean function";

static PyObject *BooleanValue(PyObject *self, PyObject *args)
{
  PyObject *object, *result;

  if (!PyArg_ParseTuple(args, "O:BooleanValue", &object))
    return NULL;
  
  if (PyBoolean_Check(object)) {
    result = object;
  } else if (PyNumber_IsNaN(object)) {
    result = PyBoolean_False;
  } else {
    /* use Python's boolean rules (the same as XPath primitive types) */
    switch (PyObject_IsTrue(object)) {
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

static PyMethodDef conversions[] = {
  { "StringValue", StringValue, METH_VARARGS, string_doc },
  { "NumberValue", NumberValue, METH_VARARGS, number_doc },
  { "BooleanValue", BooleanValue, METH_VARARGS, boolean_doc },
  { NULL, NULL }
};

DL_EXPORT(void) init_conversions(void) {
  PyObject *module;

  module = Py_InitModule("_conversions", conversions);

  /* we just need to make sure these are loaded */
  module = PyImport_ImportModule("Ft.Lib.number");
  if (module == NULL) return;
  PyNumber_NaN = PyObject_GetAttrString(module, "nan");
  if (PyNumber_NaN == NULL) return;
  Py_DECREF(module);

  module = PyImport_ImportModule("Ft.Lib.boolean");
  if (module == NULL) return;
  /* PyBoolean_Type */
  PyBoolean_Type = PyObject_GetAttrString(module, "BooleanType");
  if (PyBoolean_Type == NULL) return;
  PyBoolean_False = PyObject_GetAttrString(module, "false");
  if (PyBoolean_False == NULL) return;
  PyBoolean_True = PyObject_GetAttrString(module, "true");
  if (PyBoolean_True == NULL) return;
  Py_DECREF(module);
}
