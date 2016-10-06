#ifndef XMLSTRING_H
#define XMLSTRING_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"

  typedef struct {
    int (*IsSpace)(PyObject *str);
    int (*IsName)(PyObject *str);
    int (*IsNames)(PyObject *str);
    int (*IsNmtoken)(PyObject *str);
    int (*IsNmtokens)(PyObject *str);
    int (*IsQName)(PyObject *str);
    int (*IsNCName)(PyObject *str);
    int (*SplitQName)(PyObject *qualifiedName, PyObject **prefix,
                      PyObject **localName);
    PyObject *(*NormalizeSpace)(PyObject *str);
  } XmlString_APIObject;

#ifndef XmlString_BUILDING_MODULE

/* --- C API ----------------------------------------------------*/

  static XmlString_APIObject *XmlString_API;

#define XmlString_IMPORT XmlString_API = \
    (XmlString_APIObject *) PyCObject_Import("Ft.Xml.Lib.XmlString", "CAPI")

#define XmlString_IsSpace XmlString_API->IsSpace
#define XmlString_IsName XmlString_API->IsName
#define XmlString_IsNames XmlString_API->IsNames
#define XmlString_IsNmtoken XmlString_API->IsNmtoken
#define XmlString_IsNmtokens XmlString_API->IsNmtokens
#define XmlString_IsQName XmlString_API->IsQName
#define XmlString_IsNCName XmlString_API->IsNCName
#define XmlString_SplitQName XmlString_API->SplitQName
#define XmlString_NormalizeSpace XmlString_API->NormalizeSpace

#endif /* XmlString_BUILDING_MODULE */

#ifdef __cplusplus
}
#endif

#endif /* XMLSTRING_H */
