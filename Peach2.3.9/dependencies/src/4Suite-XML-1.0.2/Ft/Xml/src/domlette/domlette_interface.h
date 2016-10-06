#ifndef DOMLETTE_INTERFACE_H
#define DOMLETTE_INTERFACE_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

/*

  This header provides access to Domlette's interface from C.

  Before calling any of the functions or macros, you must initialize
  the routines with:

    Domlette_IMPORT

  This would typically be done in your init function.

*/
  typedef struct {
    /* Domlette Node C Types */
    PyTypeObject *DOMImplementation_Type;
    PyTypeObject *Document_Type;
    PyTypeObject *Element_Type;
    PyTypeObject *Attr_Type;
    PyTypeObject *Text_Type;
    PyTypeObject *Comment_Type;
    PyTypeObject *ProcessingInstruction_Type;
    PyTypeObject *DocumentFragment_Type;
  } Domlette_APIObject;

#ifndef Domlette_BUILDING_MODULE

/* --- C API ----------------------------------------------------*/

  static Domlette_APIObject *Domlette;

#define Domlette_IMPORT Domlette =                                      \
    (Domlette_APIObject *) PyCObject_Import("Ft.Xml.cDomlettec", "CAPI")

#endif /* !Domlette_BUILDING_MODULE */

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_INTERFACE_H */
