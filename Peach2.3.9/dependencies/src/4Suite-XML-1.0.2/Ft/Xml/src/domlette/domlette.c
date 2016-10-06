/***********************************************************************
 * $Header: /var/local/cvsroot/4Suite/Ft/Xml/src/domlette/domlette.c,v 1.54.2.3 2006/09/24 17:53:55 uogbuji Exp $
 ***********************************************************************/

static char module_doc[] = "\
cDomlette implementation: a very fast DOM-like library tailored for use in XPath/XSLT\n\
\n\
Copyright 2006 Fourthought, Inc. (USA).\n\
Detailed license and copyright information: http://4suite.org/COPYRIGHT\n\
Project home, documentation, distributions: http://4suite.org/\n\
";

#include "domlette.h"
#include "reader.h"
#include "nss.h"
#include "refcounts.h"
#include "expat_module.h"
#include "content_model.h"
#include "parse_event_handler.h"
#include "xmlparser.h"
#include "domlette_interface.h"

PyObject *g_xmlNamespace;
PyObject *g_xmlnsNamespace;
PyObject *g_xincludeNamespace;

/*
  These are the external interfaces
*/

#define UNICODE_FROM_CHAR(str) PyUnicode_DecodeASCII((str), (Py_ssize_t)strlen(str), NULL);

#define CHECK_DOCUMENT_REFS(num, where) if (doc->ob_refcnt != (num)) {  \
    PyErr_Format(PyExc_MemoryError,                                     \
                 "%s expected %d refcount"          \
                 " found %" PY_FORMAT_SIZE_T "d",                       \
                 (where), (num), doc->ob_refcnt);                       \
    return NULL;                                                        \
}

/* The test tree XML:
test_xml = """<?xml version = "1.0"?>
<?xml-stylesheet href="addr_book1.xsl" type="text/xml"?>
<docelem xmlns:ft="http://fourthought.com">
  <child foo='bar'>Some Text</child>
  <!--A comment-->
  <ft:nschild ft:foo="nsbar">Some More Text</ft:nschild>
  <appendChild/>
</docelem>"""
*/

static PyObject *PyTestTree(PyObject *self, PyObject *args)
{
  /*Build a test tree*/
  PyDocumentObject *doc;
  PyProcessingInstructionObject *pi;
  PyElementObject *documentElement, *element;
  PyTextObject *text;
  PyCommentObject *comment;
  PyAttrObject *attr;
  PyObject *namespaceURI, *qualifiedName, *localName;
  PyObject *target, *data, *value;

  if (!PyArg_ParseTuple(args, ":TestTree")) return NULL;

  doc = Document_New(Py_None);
  CHECK_DOCUMENT_REFS(1, "Doc Creation");

  /* Add processing instruction */
  target = UNICODE_FROM_CHAR("xml-stylesheet");
  data = UNICODE_FROM_CHAR("href=\"addr_book1.xsl\" type=\"text/xml\"");
  pi = ProcessingInstruction_New(doc, target, data);
  Py_DECREF(data);
  Py_DECREF(target);
  if (Node_AppendChild((PyNodeObject *)doc, (PyNodeObject *)pi) < 0)
    return NULL;
  /*We are all done with pi, so DECREF it once*/
  Py_DECREF(pi);

  CHECK_DOCUMENT_REFS(2, "PI Creation");

  /* Add documentElement */
  namespaceURI = Py_None;
  qualifiedName = UNICODE_FROM_CHAR("docelem");
  localName = qualifiedName;
  documentElement = Element_New(doc, namespaceURI, qualifiedName, localName);
  Py_DECREF(qualifiedName);
  Node_AppendChild((PyNodeObject *)doc, (PyNodeObject *)documentElement);

  CHECK_DOCUMENT_REFS(3,"Doc Elem Creation");

  /* Add documentElement namespace declartion */
  namespaceURI = g_xmlnsNamespace;
  qualifiedName = UNICODE_FROM_CHAR("xmlns:ft");
  localName = UNICODE_FROM_CHAR("ft");
  value = UNICODE_FROM_CHAR("http://fourthought.com");
  attr = Element_SetAttributeNS(documentElement, namespaceURI, qualifiedName,
                                localName, value);
  Py_DECREF(attr);
  Py_DECREF(value);
  Py_DECREF(localName);
  Py_DECREF(qualifiedName);

  CHECK_DOCUMENT_REFS(4,"NS DECL");

  /* Add text 1 to documentElement */
  data = UNICODE_FROM_CHAR("\n  ");
  text = Text_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)text);
  /*We are all done with text, so DECREF it once*/
  Py_DECREF(text);
  CHECK_DOCUMENT_REFS(5,"1st Text");

  /* Add element 1 to documentElement */
  namespaceURI = Py_None;
  qualifiedName = UNICODE_FROM_CHAR("child");
  localName = qualifiedName;
  element = Element_New(doc, namespaceURI, qualifiedName, localName);
  Py_DECREF(qualifiedName);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)element);
  CHECK_DOCUMENT_REFS(6,"First Child");

  /* Add element 1 attribute */
  namespaceURI = Py_None;
  qualifiedName = UNICODE_FROM_CHAR("foo");
  localName = qualifiedName;
  value = UNICODE_FROM_CHAR("bar");
  attr = Element_SetAttributeNS(element, namespaceURI, qualifiedName,
                                localName, value);
  Py_DECREF(attr);
  Py_DECREF(qualifiedName);
  Py_DECREF(value);
  CHECK_DOCUMENT_REFS(7,"First Child Attr");

  /* Add element 1 text */
  data = UNICODE_FROM_CHAR("Some Text");
  text = Text_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)element, (PyNodeObject *)text);
  /*We are all done with text, so DECREF it once*/
  Py_DECREF(text);
  CHECK_DOCUMENT_REFS(8,"First Child Text");

  /*We are all done with element 1, so DECREF it once*/
  Py_DECREF(element);

  /* Add text 2 to documentElement */
  data = UNICODE_FROM_CHAR("\n  ");
  text = Text_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)text);
  /*We are all done with text, so DECREF it once*/
  Py_DECREF(text);
  CHECK_DOCUMENT_REFS(9,"2nd Text");

  /* Add comment to documentElement */
  data = UNICODE_FROM_CHAR("A comment");
  comment = Comment_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)comment);
  /*We are all done with comment so DECREF it once*/
  Py_DECREF(comment);
  CHECK_DOCUMENT_REFS(10,"Comment");

  /* Add text 3 to documentElement */
  data = UNICODE_FROM_CHAR("\n  ");
  text = Text_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)text);
  /*We are all done with text, so DECREF it once*/
  Py_DECREF(text);
  CHECK_DOCUMENT_REFS(11,"3rd Text");

  /* Add element 2 to documentElement */
  namespaceURI = UNICODE_FROM_CHAR("http://fourthought.com");
  qualifiedName = UNICODE_FROM_CHAR("ft:nschild");
  localName = UNICODE_FROM_CHAR("nschild");
  element = Element_New(doc, namespaceURI, qualifiedName, localName);
  Py_DECREF(localName);
  Py_DECREF(qualifiedName);
  Py_DECREF(namespaceURI);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)element);
  CHECK_DOCUMENT_REFS(12,"2nd Child");

  /* Add element 2 attribute */
  namespaceURI = UNICODE_FROM_CHAR("http://fourthought.com");
  qualifiedName = UNICODE_FROM_CHAR("ft:foo");
  localName = UNICODE_FROM_CHAR("foo");
  value = UNICODE_FROM_CHAR("nsbar");
  attr = Element_SetAttributeNS(element, namespaceURI, qualifiedName,
                                localName, value);
  Py_DECREF(attr);
  Py_DECREF(value);
  Py_DECREF(localName);
  Py_DECREF(qualifiedName);
  Py_DECREF(namespaceURI);
  CHECK_DOCUMENT_REFS(13,"2nd Child Attr");

  /* Add element 2 text node */
  data = UNICODE_FROM_CHAR("Some More Text");
  text = Text_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)element, (PyNodeObject *)text);
  /*We are all done with text, so DECREF it once*/
  Py_DECREF(text);
  CHECK_DOCUMENT_REFS(14,"2nd Child Text");

  /*We are all done with element 2, so DECREF it once*/
  Py_DECREF(element);

  /* Add text 4 to documentElement */
  data = UNICODE_FROM_CHAR("\n  ");
  text = Text_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)text);
  /*We are all done with text, so DECREF it once*/
  Py_DECREF(text);
  CHECK_DOCUMENT_REFS(15,"4th Text");

  /* Add element 3 to documentElement */
  namespaceURI = Py_None;
  qualifiedName = UNICODE_FROM_CHAR("appendChild");
  localName = qualifiedName;
  element = Element_New(doc, namespaceURI, qualifiedName, localName);
  Py_DECREF(qualifiedName);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)element);
  CHECK_DOCUMENT_REFS(16,"Append Child");

  /* We are all done with element 3, so DECREF it once*/
  Py_DECREF(element);

  /* Add text 5 to documentElement */
  data = UNICODE_FROM_CHAR("\n  ");
  text = Text_New(doc, data);
  Py_DECREF(data);
  Node_AppendChild((PyNodeObject *)documentElement, (PyNodeObject *)text);
  /*We are all done with text, so DECREF it once*/
  Py_DECREF(text);
  CHECK_DOCUMENT_REFS(17,"5th Text");

  /* We are all done with documentElement, so DECREF it once */
  Py_DECREF(documentElement);

  return (PyObject *)doc;

}


/** The external interface definitions ********************************/

#define Domlette_METHOD(name, flags)                            \
  { #name, (PyCFunction) Domlette_##name, flags, name##_doc }

static PyMethodDef cDomlettecMethods[] = {
  /* from reader.c */
  Domlette_METHOD(NonvalParse, METH_VARARGS | METH_KEYWORDS),
  Domlette_METHOD(ValParse, METH_VARARGS | METH_KEYWORDS),
  Domlette_METHOD(Parse, METH_VARARGS | METH_KEYWORDS),
  Domlette_METHOD(ParseFragment, METH_VARARGS | METH_KEYWORDS),

  /* from xmlparser.c */
  Domlette_METHOD(CreateParser, METH_VARARGS | METH_KEYWORDS),

  /* from nss.c */
  Domlette_METHOD(GetAllNs, METH_VARARGS),
  Domlette_METHOD(SeekNss, METH_VARARGS),

  /* defined here (regression tests) */
  { "TestTree",          PyTestTree,         METH_VARARGS,
    "TestTree() -> Document\n\nFor regression testing." },

  { NULL }
};

static Domlette_APIObject Domlette_API = {
  &DomletteDOMImplementation_Type,
  &DomletteDocument_Type,
  &DomletteElement_Type,
  &DomletteAttr_Type,
  &DomletteText_Type,
  &DomletteComment_Type,
  &DomletteProcessingInstruction_Type,
  &DomletteDocumentFragment_Type,
};

static void domlette_fini(void *capi)
{
  DomletteExceptions_Fini();
  DomletteExpat_Fini();
  DomletteValidation_Fini();
  DomletteReader_Fini();
  DomletteParser_Fini();
  DomletteBuilder_Fini();
  DomletteDOMImplementation_Fini();
  DomletteNode_Fini();
  DomletteElement_Fini();
  DomletteAttr_Fini();
  DomletteCharacterData_Fini();
  DomletteText_Fini();
  DomletteProcessingInstruction_Fini();
  DomletteComment_Fini();
  DomletteDocument_Fini();
  DomletteDocumentFragment_Fini();
  DomletteXPathNamespace_Fini();

  Py_DECREF(g_xmlNamespace);
  Py_DECREF(g_xmlnsNamespace);
  Py_DECREF(g_xincludeNamespace);
}

DL_EXPORT(void) initcDomlettec(void)
{
  PyObject *module, *import;
  PyObject *cobj;

  module = Py_InitModule3("cDomlettec", cDomlettecMethods, module_doc);
  if (module == NULL) return;

  /* get the namespace constants */
  import = PyImport_ImportModule("Ft.Xml");
  if (import == NULL) return;
  g_xmlNamespace = PyObject_GetAttrString(import, "XML_NAMESPACE");
  g_xmlNamespace = DOMString_FromObjectInplace(g_xmlNamespace);
  if (g_xmlNamespace == NULL) return;
  g_xmlnsNamespace = PyObject_GetAttrString(import, "XMLNS_NAMESPACE");
  g_xmlnsNamespace = DOMString_FromObjectInplace(g_xmlnsNamespace);
  if (g_xmlnsNamespace == NULL) return;
  Py_DECREF(import);

  import = PyImport_ImportModule("Ft.Xml.XInclude");
  if (import == NULL) return;
  g_xincludeNamespace = PyObject_GetAttrString(import, "XINCLUDE_NAMESPACE");
  g_xincludeNamespace = DOMString_FromObjectInplace(g_xincludeNamespace);
  if (g_xincludeNamespace == NULL) return;
  Py_DECREF(import);

  /* initialize the sub-components */
  if (DomletteExceptions_Init(module) == -1) return;
  if (DomletteExpat_Init(module) == -1) return;
  if (DomletteValidation_Init(module) == -1) return;
  if (DomletteReader_Init(module) == -1) return;
  if (DomletteParser_Init(module) == -1) return;
  if (DomletteBuilder_Init(module) == -1) return;
  if (DomletteDOMImplementation_Init(module) == -1) return;
  /* MUST be before subclasses (all node types) */
  if (DomletteNode_Init(module) == -1) return;
  if (DomletteNamedNodeMap_Init(module) == -1) return;
  if (DomletteElement_Init(module) == -1) return;
  if (DomletteAttr_Init(module) == -1) return;
  /* MUST be before subclasses (Text and Comment) */
  if (DomletteCharacterData_Init(module) == -1) return;
  if (DomletteText_Init(module) == -1) return;
  if (DomletteProcessingInstruction_Init(module) == -1) return;
  if (DomletteComment_Init(module) == -1) return;
  if (DomletteDocument_Init(module) == -1) return;
  if (DomletteDocumentFragment_Init(module) == -1) return;
  if (DomletteXPathNamespace_Init(module) == -1) return;

  /* Export C API - done last to serve as a cleanup function as well */
  cobj = PyCObject_FromVoidPtr((void *)&Domlette_API, domlette_fini);
  if (cobj) {
    PyModule_AddObject(module, "CAPI", cobj);
  }
  return;
}
