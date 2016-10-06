#ifndef DOMLETTE_PARSER_H
#define DOMLETTE_PARSER_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

  extern char CreateParser_doc[];
  extern PyObject *Domlette_CreateParser(PyObject *, PyObject *, PyObject *);

  extern int DomletteParser_Init(PyObject *module);
  extern void DomletteParser_Fini(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_PARSER_H */
