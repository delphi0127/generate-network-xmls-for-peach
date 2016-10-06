#ifndef DOMLETTE_H
#define DOMLETTE_H

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) || defined(__WIN32__)
#  define strcasecmp stricmp
#endif

#include "Python.h"
#include "structmember.h"

#include "debug.h"
#include "util.h"

#include "exceptions.h"
#include "node.h"
#include "namednodemap.h"
#include "document.h"
#include "element.h"
#include "attr.h"
#include "documentfragment.h"
#include "domimplementation.h"
#include "text.h"
#include "processinginstruction.h"
#include "comment.h"
#include "xpathnamespace.h"

#include "../common.h"


  /* namespace constants */
  extern PyObject *g_xmlNamespace;
  extern PyObject *g_xmlnsNamespace;
  extern PyObject *g_xincludeNamespace;


#define PyNode_Children_Check(op) (PyDocument_Check(op) ||              \
                                   PyElement_Check(op) ||               \
                                   PyDocumentFragment_Check(op))

#define PyNode_Childless_Check(op) (PyText_Check(op) ||                 \
                                    PyProcessingInstruction_Check(op) || \
                                    PyComment_Check(op))

#define DOMLETTE_PACKAGE  "Ft.Xml.cDomlette."

#ifdef __cplusplus
}
#endif
#endif /* !DOMLETTEOBJECT_H */

