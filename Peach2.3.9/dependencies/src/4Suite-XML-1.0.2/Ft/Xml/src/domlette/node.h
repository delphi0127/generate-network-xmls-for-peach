#ifndef DOMLETTE_NODE_H
#define DOMLETTE_NODE_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "nodetype.h"

  /* PyNode_HEAD defines the initial segment of every Domlette node. */
#define PyNode_HEAD                    \
    PyObject_HEAD                      \
    long flags;                        \
    struct PyNodeObject *parentNode;   \
    struct PyDocumentObject *ownerDocument;

#define PyContainerNode_HEAD           \
    PyNode_HEAD                        \
    int count;                         \
    struct PyNodeObject **nodes;       \
    int allocated;

#include "document.h"

  /* Nothing is actually declared to be a PyNodeObject, but every pointer to
   * a Domlette object can be cast to a PyNodeObject*.  This is inheritance
   * built by hand.
   */
  typedef struct PyNodeObject {
    PyNode_HEAD
  } PyNodeObject;

  typedef struct PyContainerNodeObject {
    PyContainerNode_HEAD
  } PyContainerNodeObject;

#define PyNode_OWNER_DOCUMENT(op) (((PyNodeObject *)(op))->ownerDocument)

#define Node_GET_PARENT(op) (((PyNodeObject *)(op))->parentNode)
#define Node_SET_PARENT(op, v) (Node_GET_PARENT(op) = (v))
#define Node_GET_DOCUMENT(op) (((PyNodeObject *)(op))->ownerDocument)

#define ContainerNode_GET_COUNT(op) (((PyContainerNodeObject *)(op))->count)
#define ContainerNode_GET_CHILD(op, i)          \
  (((PyContainerNodeObject *)(op))->nodes[i])

  extern PyTypeObject DomletteNode_Type;

#define PyNode_Check(op) PyObject_TypeCheck((op), &DomletteNode_Type)
#define PyNode_CheckExact(op) ((op)->ob_type == &DomletteNode_Type)

  /* Module Methods */
  int DomletteNode_Init(PyObject *module);
  void DomletteNode_Fini(void);

  /* PyNodeObject Creatation */
#define Node_FLAGS_CONTAINER (1L<<0)

#define Node_HasFlag(n,f) ((n)->flags & (f))
#define Node_SetFlag(n,f) ((n)->flags |= (f))
#define Node_ClearFlag(n,f) ((n)->flags &= ~(f))

#define _Node_INIT_FLAGS(op, doc, f) \
  ( (op)->flags = (f), \
    (op)->parentNode = (PyNodeObject *) Py_None, \
    (op)->ownerDocument = (doc), Py_INCREF(doc) )

#define _Node_INIT(op, doc) \
  _Node_INIT_FLAGS((op), (doc), 0)
#define _Node_INIT_CONTAINER(op, doc) \
  ( (op)->count = 0, (op)->allocated = 0, (op)->nodes = NULL, \
    _Node_INIT_FLAGS((op), (doc), Node_FLAGS_CONTAINER) )

  PyNodeObject *_Node_New(PyTypeObject *type, PyDocumentObject *ownerDocument,
                          long flags);
#define Node_New(type, typeobj, ownerdoc) \
  ((type *) _Node_New((typeobj), (ownerdoc), 0))
#define Node_NewContainer(type, typeobj, ownerdoc) \
  ((type *) _Node_New((typeobj), (ownerdoc), Node_FLAGS_CONTAINER))

  void _Node_Del(PyNodeObject *node);
#define Node_Del(obj) _Node_Del((PyNodeObject *)(obj))

  int _Node_SetChildren(PyNodeObject *self, PyNodeObject **children, int size);

  /* DOM Node Methods */
  int Node_RemoveChild(PyNodeObject *self, PyNodeObject *oldChild);
  int Node_AppendChild(PyNodeObject *self, PyNodeObject *newChild);
  int Node_InsertBefore(PyNodeObject *self, PyNodeObject *newChild,
                        PyNodeObject *refChild);
  PyNodeObject *Node_CloneNode(PyObject *node, int deep,
			       PyDocumentObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_NODE_H */
