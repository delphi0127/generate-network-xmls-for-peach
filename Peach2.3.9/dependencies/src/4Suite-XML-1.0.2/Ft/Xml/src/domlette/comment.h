#ifndef DOMLETTE_COMMENT_H
#define DOMLETTE_COMMENT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "characterdata.h"

  typedef PyCharacterDataObject PyCommentObject;

#define Comment_GET_DATA(op) PyCharacterData_NODE_VALUE(op)
#define Comment_SET_DATA(op, v) (Comment_GET_DATA(op) = (v))

  extern PyTypeObject DomletteComment_Type;

#define PyComment_Check(op) PyObject_TypeCheck((op), &DomletteComment_Type)
#define PyComment_CheckExact(op) ((op)->ob_type == &DomletteComment_Type)

  /* Module Methods */
  int DomletteComment_Init(PyObject *module);
  void DomletteComment_Fini(void);

  /* Comment Methods */
#define Comment_New(ownerDocument, data) \
  CharacterData_New(PyCommentObject, &DomletteComment_Type, \
                    (ownerDocument), (data))

#define Comment_CloneNode(node, deep, newOwnerDocument) \
  CharacterData_CloneNode(PyCommentObject, &DomletteComment_Type, (node), \
                         (deep), (newOwnerDocument))

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_COMMENT_H */
