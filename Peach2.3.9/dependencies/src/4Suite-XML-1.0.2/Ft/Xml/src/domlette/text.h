#ifndef DOMLETTE_TEXT_H
#define DOMLETTE_TEXT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "characterdata.h"

  typedef PyCharacterDataObject PyTextObject;

#define Text_GET_DATA(op) PyCharacterData_NODE_VALUE(op)
#define Text_SET_DATA(op, v) (Text_GET_DATA(op) = (v))

  extern PyTypeObject DomletteText_Type;

#define PyText_Check(op) PyObject_TypeCheck(op, &DomletteText_Type)
#define PyText_CheckExact(op) ((op)->ob_type == &DomletteText_Type)

  /* Module Methods */
  int DomletteText_Init(PyObject *module);
  void DomletteText_Fini(void);

  /* Text Methods */
#define Text_New(ownerDocument, data) \
  CharacterData_New(PyTextObject, &DomletteText_Type, ownerDocument, data)

#define Text_CloneNode(node, deep, newOwnerDocument) \
  CharacterData_CloneNode(PyTextObject, &DomletteText_Type, (node), \
                         (deep), (newOwnerDocument))

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_TEXT_H */
