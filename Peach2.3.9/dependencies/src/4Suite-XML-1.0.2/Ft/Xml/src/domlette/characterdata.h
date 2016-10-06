#ifndef DOMLETTE_CHARACTERDATA_H
#define DOMLETTE_CHARACTERDATA_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"

  typedef struct {
    PyNode_HEAD
    PyObject *nodeValue;
  } PyCharacterDataObject;

#define PyCharacterData_NODE_VALUE(op) (((PyCharacterDataObject *)(op))->nodeValue)

  extern PyTypeObject DomletteCharacterData_Type;

#define PyCharacterData_Check(op) \
  PyObject_TypeCheck((op), &DomletteCharacterData_Type)
#define PyCharacterData_CheckExact(op) \
  ((op)->ob_type, &DomletteCharacterData_Type)

  /* Module Methods */
  int DomletteCharacterData_Init(PyObject *module);
  void DomletteCharacterData_Fini(void);

  /* CharacterData Methods */
  PyCharacterDataObject *_CharacterData_New(PyTypeObject *type,
                                            PyDocumentObject *ownerDocument,
                                            PyObject *data);
#define CharacterData_New(type, typeobj, ownerdoc, data) \
  ((type *) _CharacterData_New((typeobj), (ownerdoc), (data)))

  PyCharacterDataObject *_CharacterData_CloneNode(
    PyTypeObject *type, PyObject *node, int deep,
    PyDocumentObject *newOwnerDocument);
#define CharacterData_CloneNode(type, typeobj, node, deep, ownerdoc) \
  ((type *) _CharacterData_CloneNode((typeobj), (node), (deep), (ownerdoc)))

  PyObject *CharacterData_SubstringData(PyCharacterDataObject *node,
                                        int offset, int count);

  int CharacterData_AppendData(PyCharacterDataObject *node,
                               PyObject *arg);

  int CharacterData_InsertData(PyCharacterDataObject *node,
                               int offset, PyObject *arg);

  int CharacterData_DeleteData(PyCharacterDataObject *node,
                               int offset, int count);

  int CharacterData_ReplaceData(PyCharacterDataObject *node,
                                int offset, int count, PyObject *arg);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_CHARACTERDATA_H */
