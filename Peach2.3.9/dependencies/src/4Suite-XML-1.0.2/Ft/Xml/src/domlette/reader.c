#include "Python.h"
#include "parse_event_handler.h"

static int read_external_dtd;

/*
  These are the external interfaces
*/
char Parse_doc[] = "\
Parse(isrc[, readExtDtd]) -> Document";

PyObject *Domlette_Parse(PyObject *self, PyObject *args, PyObject *kw) {
  PyObject *source, *result;
  int readExtDtd=read_external_dtd;
  static char *kwlist[] = {"isrc", "readExtDtd", NULL};
  
  if (!PyArg_ParseTupleAndKeywords(args, kw, "O|i:Parse", kwlist,
                                   &source, &readExtDtd))
    return NULL;

#ifdef DEBUG_PARSER
  fprintf(stderr, "Start parsing.\n");
#endif

  result = ParseDocument(source, readExtDtd);

#ifdef DEBUG_PARSER
  fprintf(stderr,"Finished parsing\n");
#endif

  return result;
}

char NonvalParse_doc[] = "\
NonvalParse(isrc[, readExtDtd]) -> Document";

PyObject *Domlette_NonvalParse(PyObject *self, PyObject *args, PyObject *kw)
{
  PyObject *isrc, *readExtDtd=NULL;
  static char *kwlist[] = {"isrc", "readExtDtd", NULL};
  int read_ext_dtd=read_external_dtd;
  PyObject *result;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "O|O:NonvalParse", kwlist, 
                                   &isrc, &readExtDtd))
    return NULL;

  if (readExtDtd) {
    read_ext_dtd = PyObject_IsTrue(readExtDtd);
    if (read_ext_dtd == -1) return NULL;
  }

#ifdef DEBUG_PARSER
  fprintf(stderr, "Start parsing.\n");
#endif

  result = ParseDocument(isrc, read_ext_dtd);

#ifdef DEBUG_PARSER
  fprintf(stderr,"Finished parsing\n");
#endif

  return result;
}


char ValParse_doc[] = "\
ValParse(isrc) -> Document";

PyObject *Domlette_ValParse(PyObject *self, PyObject *args, PyObject *kw)
{
  PyObject *isrc;
  static char *kwlist[] = {"isrc", NULL};
  PyObject *result;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "O:ValParse", kwlist, &isrc))
    return NULL;

#ifdef DEBUG_PARSER
  fprintf(stderr, "Start parsing.\n");
#endif

  result = ParseDocument(isrc, PARSE_TYPE_VALIDATE);

#ifdef DEBUG_PARSER
  fprintf(stderr,"Finished parsing\n");
#endif

  return result;
}


char ParseFragment_doc[] = "\
ParseFragment(isrc[, namespaces]) -> Document";

PyObject *Domlette_ParseFragment(PyObject *self, PyObject *args, PyObject *kw)
{
  PyObject *isrc, *namespaces=NULL;
  static char *kwlist[] = {"isrc", "namespaces", NULL};
  PyObject *result;

  if (!PyArg_ParseTupleAndKeywords(args, kw, "O|O:ParseFragment", kwlist, 
                                   &isrc, &namespaces))
    return NULL;

  
#ifdef DEBUG_PARSER
  fprintf(stderr, "Start parsing.\n");
#endif

  result = ParseFragment(isrc, namespaces);

#ifdef DEBUG_PARSER
  fprintf(stderr,"Finished parsing\n");
#endif

  return result;
}


int DomletteReader_Init(PyObject *module)
{
  PyObject *import, *constant;

  import = PyImport_ImportModule("Ft.Xml");
  if (import == NULL) return -1;

  constant = PyObject_GetAttrString(import, "READ_EXTERNAL_DTD");
  if (constant == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  read_external_dtd = PyObject_IsTrue(constant);
  Py_DECREF(constant);
  if (read_external_dtd == -1) return -1;

  return 0;
}

void DomletteReader_Fini(void)
{
  /* no cleanup to perform */
}
