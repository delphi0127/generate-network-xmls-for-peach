#include "domlette.h"

/** Private Routines **************************************************/


static PyObject *shared_empty_nodelist;
static PyObject *xml_base_key;
static PyObject *is_absolute_function;
static PyObject *absolutize_function;

#define ContainerNode_SET_COUNT(op, v) (ContainerNode_GET_COUNT(op) = (v))
#define ContainerNode_GET_NODES(op) (((PyContainerNodeObject *)(op))->nodes)
#define ContainerNode_SET_NODES(op, v) (ContainerNode_GET_NODES(op) = (v))
#define ContainerNode_GET_ALLOCATED(op)         \
  (((PyContainerNodeObject *)(op))->allocated)
#define ContainerNode_SET_ALLOCATED(op, v)      \
  (ContainerNode_GET_ALLOCATED(op) = (v))
#define ContainerNode_GET_CHILD(op, i)          \
  (((PyContainerNodeObject *)(op))->nodes[i])
#define ContainerNode_SET_CHILD(op, i, v)       \
  (ContainerNode_GET_CHILD((op), (i)) = (v))


static int node_resize(PyContainerNodeObject *self, int newsize) {
  PyNodeObject **nodes;
  size_t new_allocated;
  int allocated = self->allocated;

  /* Bypass realloc() when a previous overallocation is large enough
     to accommodate the newsize.  If the newsize falls lower than half
     the allocated size, then proceed with the realloc() to shrink the list.
  */
  if (allocated >= newsize && newsize >= (allocated >> 1)) {
    self->count = newsize;
    return 0;
  }

  /* This over-allocates proportional to the list size, making room
   * for additional growth.  The over-allocation is mild, but is
   * enough to give linear-time amortized behavior over a long
   * sequence of appends() in the presence of a poorly-performing
   * system realloc().
   * The growth pattern is:  0, 4, 8, 16, 25, 35, 46, 58, 72, 88, ...
   */
  new_allocated = (newsize >> 3) + (newsize < 9 ? 3 : 6) + newsize;
  if (newsize == 0)
    new_allocated = 0;
  nodes = self->nodes;
  if (new_allocated <= ((~(size_t)0) / sizeof(PyNodeObject *)))
    PyMem_Resize(nodes, PyNodeObject *, new_allocated);
  else
    nodes = NULL;
  if (nodes == NULL) {
    PyErr_NoMemory();
    return -1;
  }
  self->nodes = nodes;
  self->count = newsize;
  self->allocated = new_allocated;
  return 0;
}


static int node_clear_nodes(PyContainerNodeObject *self)
{
  PyNodeObject **nodes = self->nodes;
  int i;
  if (nodes != NULL) {
    i = self->count;
    self->nodes = NULL;
    self->count = 0;
    self->allocated = 0;
    while (--i >= 0) {
      Py_DECREF(nodes[i]);
    }
    PyMem_Free(nodes);
  }
  return 0;
}


static int node_validate_child(PyNodeObject *self, PyNodeObject *child)
{
  if (self == NULL || child == NULL || !PyNode_Check(self)) {
    PyErr_BadInternalCall();
    return 0;
  } else if (!Node_HasFlag(self, Node_FLAGS_CONTAINER)) {
    DOMException_HierarchyRequestErr("Not allowed to have children");
    return 0;
  }

  if (!(PyElement_Check(child) ||
        PyProcessingInstruction_Check(child) ||
        PyComment_Check(child) ||
        PyText_Check(child) ||
        PyDocumentFragment_Check(child))) {
    if (!PyNode_Check(child)) {
      /* The child must be a Domlette Node first and foremost. */
      PyErr_BadInternalCall();
    } else {
      PyObject *error =
        PyString_FromFormat("%s nodes cannot be a child of %s nodes",
                            child->ob_type->tp_name, self->ob_type->tp_name);
      if (error != NULL) {
        DOMException_HierarchyRequestErr(PyString_AS_STRING(error));
        Py_DECREF(error);
      }
    }
    return 0;
  }

  /* Everything is OK */
  return 1;
}


/** Public C API ******************************************************/


/* Allocates memory for a new node object of the given type and initializes
   part of it.
*/
PyNodeObject *_Node_New(PyTypeObject *type, PyDocumentObject *ownerDocument,
                        long flags)
{
  PyNodeObject *node;

  if (ownerDocument == NULL || (ownerDocument != (PyDocumentObject *) Py_None
                                && !PyDocument_Check(ownerDocument))) {
    PyErr_BadInternalCall();
    return NULL;
  }

  node = PyObject_GC_New(PyNodeObject, type);
  if (node != NULL) {
#ifdef DEBUG_NODE_CREATION
    printf("Created %s node at 0x%p\n", type->tp_name, node);
#endif
    _Node_INIT_FLAGS(node, ownerDocument, flags);

    if (flags & Node_FLAGS_CONTAINER) {
      ContainerNode_SET_COUNT(node, 0);
      ContainerNode_SET_ALLOCATED(node, 0);
      ContainerNode_SET_NODES(node, NULL);
    }
  }

  return node;
}


void _Node_Del(PyNodeObject *node)
{
#ifdef DEBUG_NODE_CREATION
  printf("Destroyed %s node at 0x%p\n", node->ob_type->tp_name, node);
#endif

  if (node->flags & Node_FLAGS_CONTAINER) {
    PyNodeObject **nodes = ContainerNode_GET_NODES(node);
    if (nodes) {
      int i = ContainerNode_GET_COUNT(node);
      while (--i >= 0) {
        Py_DECREF(nodes[i]);
      }
      PyMem_Free(nodes);
    }
  }

  node->parentNode = NULL;

  if (node->ownerDocument) {
    Py_DECREF(node->ownerDocument);
    node->ownerDocument = NULL;
  }

  PyObject_GC_Del((PyObject *) node);
}


void _Node_Dump(char *msg, PyNodeObject *self)
{
  int add_sep;
  fprintf(stderr, "%s\n"
          "  node    : ", msg);
  if (self == NULL) {
    fprintf(stderr, "NULL\n");
  } else {
    PyObject_Print((PyObject *) self, stderr, 0);
    fprintf(stderr, "\n"
            "  flags   :");
    add_sep = 0;
    if (Node_HasFlag(self, Node_FLAGS_CONTAINER)) {
      fprintf(stderr, " Node_FLAGS_CONTAINER");
      add_sep++;
    }
    if (!add_sep) {
      fprintf(stderr, " (none)");
    }
    fprintf(stderr, "\n"
            "  type    : %s\n"
            "  refcount: %" PY_FORMAT_SIZE_T "d\n"
            "  parent  : %p\n"
            "  document: %p\n",
            self->ob_type == NULL ? "NULL" : self->ob_type->tp_name,
            self->ob_refcnt,
            self->parentNode,
            self->ownerDocument);
    if (Node_HasFlag(self, Node_FLAGS_CONTAINER)) {
      fprintf(stderr, "  children: %d\n", ContainerNode_GET_COUNT(self));
    }
  }
  fprintf(stderr, "----------------------\n");
}


/* Semi-private routine for bulk addition of children to a node.
 * This routine is valid for newly contructed container-style nodes which
 * haven't had any children added to them.
 */
int _Node_SetChildren(PyNodeObject *self, PyNodeObject **array, int size)
{
  PyNodeObject **nodes;
  int i;

  if (!PyNode_Check(self) || !Node_HasFlag(self, Node_FLAGS_CONTAINER) ||
      ContainerNode_GET_NODES(self) != NULL) {
    PyErr_BadInternalCall();
    return -1;
  }

  /* Create a copy of the array */
  nodes = PyMem_New(PyNodeObject *, size);
  if (nodes == NULL) {
    PyErr_NoMemory();
    return -1;
  }
  memcpy(nodes, array, sizeof(PyNodeObject *) * size);

  /* Set the parent relationship */
  for (i = 0; i < size; i++)
    Node_SET_PARENT(nodes[i], self);

  /* Save the new array */
  ContainerNode_SET_NODES(self, nodes);
  ContainerNode_SET_COUNT(self, size);
  ContainerNode_SET_ALLOCATED(self, size);

  return 0;
}


int Node_RemoveChild(PyNodeObject *self, PyNodeObject *oldChild)
{
  PyNodeObject **nodes;
  int count, index, i;

  if (self == NULL || !PyNode_Check(self)) {
    PyErr_BadInternalCall();
    return -1;
  } else if (!Node_HasFlag(self, Node_FLAGS_CONTAINER)) {
    DOMException_HierarchyRequestErr("Not allowed to have children");
    return -1;
  }

#ifdef DEBUG_NODE_REMOVE_CHILD
  _Node_Dump("Node_RemoveChild: initial state of self", self);
  _Node_Dump("Node_RemoveChild: initial state of oldChild", oldChild);
#endif

  /* Find the index of the child to be removed */
  nodes = ContainerNode_GET_NODES(self);
  count = ContainerNode_GET_COUNT(self);
  index = -1;
  for (i = ContainerNode_GET_COUNT(self); --i >= 0;) {
    if (nodes[i] == oldChild) {
      index = i;
      break;
    }
  }
  if (index == -1) {
    DOMException_NotFoundErr("Child not found");
    return -1;
  }

#ifdef DEBUG_NODE_REMOVE_CHILD
  fprintf(stderr, "Node_RemoveChild: oldChild found at %d\n",index);
#endif

  /* Set the parent to Py_None, indicating no parent */
  Node_SET_PARENT(oldChild, (PyNodeObject *) Py_None);

  /* Now shift the nodes in the array over the top of the removed node */
  memmove(&nodes[index], &nodes[index+1],
          (count - (index + 1)) * sizeof(PyNodeObject *));
  node_resize((PyContainerNodeObject *) self, count - 1);

  /* Drop the reference to the removed node as it is no longer in the array */
  Py_DECREF(oldChild);

#ifdef DEBUG_NODE_REMOVE_CHILD
  _Node_Dump("Node_RemoveChild: final state of self", self);
  _Node_Dump("Node_RemoveChild: final state of oldChild", oldChild);
#endif

  return 0;
}


int Node_AppendChild(PyNodeObject *self, PyNodeObject *newChild)
{
  int count;

  if (!node_validate_child(self, newChild)) {
    return -1;
  }

#ifdef DEBUG_NODE_APPEND_CHILD
  _Node_Dump("Node_AppendChild: initial state of self", self);
  _Node_Dump("Node_AppendChild: initial state of child", newChild);
#endif

  /* Perform special processing if the child is a DocumentFragment */
  if (PyDocumentFragment_Check(newChild)) {
#ifdef DEBUG_NODE_APPEND_CHILD
    fprintf(stderr, "Node_AppendChild: processing DocumentFragment\n");
#endif
    /* Add each child of the DocumentFragment as a child of this node.  As
     * the child as added, it is removed from the DocumentFragment.
     */
    while (ContainerNode_GET_COUNT(newChild)) {
      if (Node_AppendChild(self, ContainerNode_GET_CHILD(newChild, 0)) == -1) {
        return -1;
      }
    }
#ifdef DEBUG_NODE_APPEND_CHILD
    fprintf(stderr, "Node_AppendChild: DocumentFragment finished\n");
#endif
  } else {
    /* Add the new child to the end of our array */
    count = ContainerNode_GET_COUNT(self);
    if (node_resize((PyContainerNodeObject *) self, count + 1) == -1)
      return -1;
    Py_INCREF(newChild);
    ContainerNode_SET_CHILD(self, count, newChild);

#ifdef DEBUG_NODE_APPEND_CHILD
    _Node_Dump("Node_AppendChild: newChild after append", newChild);
#endif

    /* If the child has a previous parent, remove it from that parent */
    if (Node_GET_PARENT(newChild) != (PyNodeObject *) Py_None) {
      Node_RemoveChild(Node_GET_PARENT(newChild), newChild);
    }

    /* Set the parent relationship */
    Node_SET_PARENT(newChild, self);
  }

#ifdef DEBUG_NODE_APPEND_CHILD
  _Node_Dump("Node_AppendChild: final state of self", self);
  _Node_Dump("Node_AppendChild: final state of child", newChild);
#endif

  return 0;
}


int Node_InsertBefore(PyNodeObject *self, PyNodeObject *newChild,
                      PyNodeObject *refChild)
{
  PyNodeObject **nodes;
  int count, index, i;

  if (!node_validate_child(self, newChild)) {
    return -1;
  }

  if (refChild == (PyNodeObject *) Py_None) {
#ifdef DEBUG_NODE_INSERT_BEFORE
    fprintf(stderr, "Node_InsertBefore: refChild is None, doing append\n");
#endif
    return Node_AppendChild(self, newChild);
  } else if (!PyNode_Check(refChild)) {
    PyErr_BadInternalCall();
    return -1;
  }

#ifdef DEBUG_NODE_INSERT_BEFORE
  _Node_Dump("Node_InsertBefore: initial state of self", self);
  _Node_Dump("Node_InsertBefore: initial state of newChild", newChild);
  _Node_Dump("Node_InsertBefore: initial state of refChild", refChild);
#endif

  if (PyDocumentFragment_Check(newChild)) {
#ifdef DEBUG_NODE_INSERT_BEFORE
    fprintf(stderr, "Node_InsertBefore: processing DocumentFragment\n");
#endif
    /* Add each child of the DocumentFragment as a child of this node.  As
     * the child as added, it is removed from the DocumentFragment.
     */
    while (ContainerNode_GET_COUNT(newChild)) {
      PyNodeObject *dfChild = ContainerNode_GET_CHILD(newChild, 0);
      if (Node_InsertBefore(self, dfChild, refChild) == -1) {
        return -1;
      }
    }
#ifdef DEBUG_NODE_INSERT_BEFORE
    fprintf(stderr, "Node_InsertBefore: DocumentFragment finished\n");
#endif
  } else {
    /* Find the index of the reference node */
    nodes = ContainerNode_GET_NODES(self);
    count = ContainerNode_GET_COUNT(self);
    index = -1;
    for (i = count; --i >= 0;) {
      if (nodes[i] == refChild) {
        index = i;
        break;
      }
    }
    if (index == -1) {
      DOMException_NotFoundErr("refChild not found");
      return -1;
    }

#ifdef DEBUG_NODE_INSERT_BEFORE
    fprintf(stderr, "Node_InsertBefore: refChild found at %d\n", index);
#endif

    /* Insert the newChild at the found index in the array */
    if (node_resize((PyContainerNodeObject *) self, count + 1) == -1)
      return -1;

    /* The pointer to nodes may have changed do to the resize */
    nodes = ContainerNode_GET_NODES(self);
    /* Shift the effected nodes up one */
    for (i = count; --i >= index;)
      nodes[i+1] = nodes[i];

    /* Set the new child in the array */
    Py_INCREF(newChild);
    ContainerNode_SET_CHILD(self, index, newChild);

#ifdef DEBUG_NODE_INSERT_BEFORE
    _Node_Dump("Node_InsertBefore: newChild after insert", newChild);
#endif
    /* If the child has a previous parent, remove it from that parent */
    if (Node_GET_PARENT(newChild) != (PyNodeObject *) Py_None) {
      Node_RemoveChild(Node_GET_PARENT(newChild), newChild);
    }

    /* Set the parent relationship */
    Node_SET_PARENT(newChild, self);
  }

#ifdef DEBUG_NODE_INSERT_BEFORE
  _Node_Dump("Node_InsertBefore: final state of self", self);
  _Node_Dump("Node_InsertBefore: final state of newChild", newChild);
  _Node_Dump("Node_InsertBefore: final state of refChild", refChild);
#endif

  return 0;
}


PyNodeObject *Node_CloneNode(PyObject *node, int deep,
			     PyDocumentObject *newOwnerDocument)
{
  PyObject *obj;
  int node_type;

  /* Note that this section MUST use attribute lookup and the node type
   * constant (integer) checks instead in simple type checks, as the node
   * to be cloned may be from a different implementation. */

  /* Get the nodeType as a plain integer */
  obj = PyObject_GetAttrString(node, "nodeType");
  if (obj == NULL) return NULL;

  node_type = PyInt_AsLong(obj);
  Py_DECREF(obj);

  switch (node_type) {
  case ELEMENT_NODE:
    return (PyNodeObject *)Element_CloneNode(node, deep, newOwnerDocument);
  case ATTRIBUTE_NODE:
    return (PyNodeObject *)Attr_CloneNode(node, deep, newOwnerDocument);
  case TEXT_NODE:
    return (PyNodeObject *)Text_CloneNode(node, deep, newOwnerDocument);
  case COMMENT_NODE:
    return (PyNodeObject *)Comment_CloneNode(node, deep, newOwnerDocument);
  case DOCUMENT_FRAGMENT_NODE:
    return (PyNodeObject *)DocumentFragment_CloneNode(node, deep,
						      newOwnerDocument);
  case PROCESSING_INSTRUCTION_NODE:
    return (PyNodeObject *)ProcessingInstruction_CloneNode(node, deep,
							   newOwnerDocument);
  default:
    /* FIXME: DOMException */
    DOMException_NotSupportedErr("cloneNode: unknown nodeType %d");
    return NULL;
  }
}


/** Python Methods *****************************************************/


static char normalize_doc[] = "\
Puts all Text nodes in the full depth of the sub-tree underneath this Node,\n\
including attribute nodes, into a \"normal\" form where only structure\n\
(e.g., elements, comments, processing instructions, CDATA sections, and\n\
entity references) separates Text nodes, i.e., there are neither adjacent\n\
Text nodes nor empty Text nodes.";

static PyObject *node_normalize(PyNodeObject *self, PyObject *args)
{
  int ctr;

  if (!PyArg_ParseTuple(args, ":normalize"))
    return NULL;

#ifdef DEBUG_NODE_NORMALIZE
  _Node_Dump("normalize: initial state of self", self);
#endif

  if (!Node_HasFlag(self, Node_FLAGS_CONTAINER)) {
    Py_INCREF(Py_None);
    return Py_None;
  }

  if (ContainerNode_GET_COUNT(self) < 2) {
    Py_INCREF(Py_None);
    return Py_None;
  }

  /*Count from 0 to 1 minus the length (the last node cannot be normalized with anything*/
  for (ctr = 0; ctr < ContainerNode_GET_COUNT(self)-1;) {
    PyNodeObject *current = ContainerNode_GET_CHILD(self, ctr);
#ifdef DEBUG_NODE_NORMALIZE
    _Node_Dump("normalize: current node", current);
#endif
    /* If this node is a Text node, determine of following siblings are also
     * Text nodes.
     */
    if (PyText_Check(current)) {
      PyNodeObject *next = ContainerNode_GET_CHILD(self, ctr+1);
#ifdef DEBUG_NODE_NORMALIZE
      _Node_Dump("normalize: next node", next);
#endif
      if (PyText_Check(next)) {
        /* Adjacent Text nodes, merge their data and delete the second one. */
        PyObject *data = PySequence_Concat(Text_GET_DATA(current),
                                           Text_GET_DATA(next));
        Py_DECREF(Text_GET_DATA(current));
        Text_SET_DATA(current, data);

	if (Node_RemoveChild(self, next) == -1)
          return NULL;

#ifdef DEBUG_NODE_NORMALIZE
        _Node_Dump("normalize: self after merge", self);
	_Node_Dump("normalize: current after merge", current);
#endif
      } else {
	ctr++;
      }
    } else {
      ctr++;
    }
  }

#ifdef DEBUG_NODE_NORMALIZE
  _Node_Dump("normalize: final state of self", self);
#endif

  Py_INCREF(Py_None);
  return Py_None;
}


static char hasChildNodes_doc[] = "\
Returns whether this node has any children.";

static PyObject *node_hasChildNodes(PyNodeObject *self, PyObject *args)
{
  PyObject *rt;

  if (!PyArg_ParseTuple(args, ":hasChildNodes"))
    return NULL;

  rt = (Node_HasFlag(self, Node_FLAGS_CONTAINER) &&
        ContainerNode_GET_COUNT(self) > 0) ? Py_True : Py_False;

  Py_INCREF(rt);
  return rt;
}


static char removeChild_doc[] = "\
Removes the child node indicated by oldChild from the list of children, and\n\
returns it.";

static PyObject *node_removeChild(PyNodeObject *self, PyObject *args)
{
  PyNodeObject *oldChild;

  if (!PyArg_ParseTuple(args, "O!:removeChild", &DomletteNode_Type, &oldChild))
    return NULL;

  if (Node_RemoveChild(self, oldChild) == -1)
    return NULL;

  Py_INCREF(oldChild);
  return (PyObject *) oldChild;
}


static char isSameNode_doc[] = "\
Returns whether this node is the same node as the given one. (DOM Level 3)";

static PyObject *node_isSameNode(PyNodeObject *self, PyObject *args)
{
  PyNodeObject *other;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "O!:isSameNode", &DomletteNode_Type, &other))
    return NULL;

  result = (self == other) ? Py_True : Py_False;
  Py_INCREF(result);
  return result;
}


static char xpath_doc[] = "\
Evaluates an XPath expression string using this node as context.";

static PyObject *node_xpath(PyNodeObject *self, PyObject *args, PyObject *kw)
{
  PyObject *expr_text, *xpath_module, *eval, *result;
  PyObject *explicit_nss = NULL;
  static char *kwlist[] = {"expr", "explicitNss", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kw, "O|O:xpath", kwlist,
                                   &expr_text, &explicit_nss))
    return NULL;

  if (explicit_nss == NULL){
    explicit_nss = Py_None;
    /* No need to Py_INCREF in these circumstances */
  }
  xpath_module = PyImport_ImportModule("Ft.Xml.XPath.Util");
  if (xpath_module == NULL) return NULL;
  eval = PyObject_GetAttrString(xpath_module, "SimpleEvaluate");
  if (eval == NULL) return NULL;
  result = PyObject_CallFunction(eval, "OOO", expr_text, self, explicit_nss);
  if (result == NULL) return NULL;
  /*_PyObject_Dump(result);*/
  return result;
}


static char appendChild_doc[] = "\
Adds the node newChild to the end of the list of children of this node.";

static PyObject *node_appendChild(PyNodeObject *self, PyObject *args)
{
  PyNodeObject *newChild;

  if (!PyArg_ParseTuple(args,"O!:appendChild", &DomletteNode_Type, &newChild))
    return NULL;

  if (Node_AppendChild(self, newChild) == -1)
    return NULL;

  Py_INCREF(newChild);
  return (PyObject *) newChild;
}


static char insertBefore_doc[] = "\
Inserts the node newChild before the existing child node refChild.";

static PyObject *node_insertBefore(PyNodeObject *self, PyObject *args)
{
  PyNodeObject *newChild, *refChild;

  if (!PyArg_ParseTuple(args, "O!O:insertBefore",
                        &DomletteNode_Type, &newChild, &refChild))
    return NULL;

  if (refChild != (PyNodeObject *) Py_None && !PyNode_Check(refChild)) {
    PyErr_SetString(PyExc_TypeError, "arg 2 must be Node or None");
    return NULL;
  }

  if (Node_InsertBefore(self, newChild, refChild) == -1)
    return NULL;

  Py_INCREF(newChild);
  return (PyObject *) newChild;
}


static PyObject *get_next_sibling(PyNodeObject *self, void *arg);

static char replaceChild_doc[] = "\
Replaces the child node oldChild with newChild in the list of children, and\n\
returns the oldChild node.";

static PyObject *node_replaceChild(PyNodeObject *self, PyObject *args)
{
  PyNodeObject *newChild, *oldChild, *sibling;

  if(!PyArg_ParseTuple(args,"O!O!:replaceChild",
                       &DomletteNode_Type, &newChild,
                       &DomletteNode_Type, &oldChild))
    return NULL;

#ifdef DEBUG_NODE_REPLACE_CHILD
  printf("replace child initial state\n");
  printf("self\n");
  _PyObject_Dump(self);
  printf("------------------\n");
  printf("newChild\n");
  _PyObject_Dump(newChild);
  printf("------------------\n");
  printf("oldChild\n");
  _PyObject_Dump(oldChild);
  printf("------------------\n");
#endif

  sibling = (PyNodeObject *) get_next_sibling(oldChild, NULL);

#ifdef DEBUG_NODE_REPLACE_CHILD
  printf("sibling\n");
  _PyObject_Dump(sibling);
  printf("------------------\n");
#endif

  /*INC the return value before we call remove incase this is the last reference*/
  Py_INCREF(oldChild);

  if (Node_RemoveChild(self, (PyNodeObject *)oldChild) == -1) {
    return NULL;
  }

#ifdef DEBUG_NODE_REPLACE_CHILD
  printf("oldChild after remove\n");
  _PyObject_Dump(oldChild);
  printf("------------------\n");
#endif

  /*Now insert it before the sibling (sibling could be Py_None but that is OK)*/
  if (Node_InsertBefore(self, newChild, sibling) == -1)
    return NULL;

#ifdef DEBUG_NODE_REPLACE_CHILD
  printf("newChild after insert\n");
  _PyObject_Dump(oldChild);
  printf("------------------\n");
#endif

  /*DECREF the sibling (getattr added one)*/
  Py_DECREF(sibling);

#ifdef DEBUG_NODE_REPLACE_CHILD
  printf("replace child final state\n");
  printf("self\n");
  _PyObject_Dump(self);
  printf("------------------\n");
  printf("newChild\n");
  _PyObject_Dump(newChild);
  printf("------------------\n");
  printf("oldChild\n");
  _PyObject_Dump(oldChild);
  printf("------------------\n");
  printf("sibling\n");
  _PyObject_Dump(oldChild);
  printf("------------------\n");
#endif
  return (PyObject *) oldChild;
}


static char cloneNode_doc[] = "\
Returns a duplicate of this node, i.e., serves as a generic copy\n\
constructor for nodes.";

static PyObject *node_cloneNode(PyNodeObject *self, PyObject *args)
{
  PyObject *boolean_deep = Py_False;
  int deep;
  PyNodeObject *result;

  if (!PyArg_ParseTuple(args,"|O:cloneNode", &boolean_deep))
    return NULL;

  deep = PyObject_IsTrue(boolean_deep);
  if (deep == -1)
    return NULL;

  if (PyDocument_Check(self)) {
    PyErr_SetString(PyExc_TypeError,"cloneNode not allowed on documents");
    return NULL;
  }

  result = Node_CloneNode((PyObject *) self, deep, Node_GET_DOCUMENT(self));

  return (PyObject *) result;
}

#define PyNode_METHOD(NAME, ARGSPEC) \
  { #NAME, (PyCFunction) node_##NAME, ARGSPEC, NAME##_doc }

static struct PyMethodDef node_methods[] = {
  PyNode_METHOD(normalize,     METH_VARARGS),
  PyNode_METHOD(hasChildNodes, METH_VARARGS),
  PyNode_METHOD(removeChild,   METH_VARARGS),
  PyNode_METHOD(appendChild,   METH_VARARGS),
  PyNode_METHOD(insertBefore,  METH_VARARGS),
  PyNode_METHOD(replaceChild,  METH_VARARGS),
  PyNode_METHOD(cloneNode,     METH_VARARGS),
  PyNode_METHOD(isSameNode,    METH_VARARGS),
  PyNode_METHOD(xpath,         METH_VARARGS | METH_KEYWORDS),
  { NULL }
};


/** Python Members ****************************************************/


static struct PyMemberDef node_members[] = {
  { "parentNode",    T_OBJECT, offsetof(PyNodeObject, parentNode),    RO },
  { "ownerDocument", T_OBJECT, offsetof(PyNodeObject, ownerDocument), RO },
  { "rootNode",      T_OBJECT, offsetof(PyNodeObject, ownerDocument), RO },
  { NULL }
};


/** Python Computed Members ********************************************/


static PyObject *get_child_nodes(PyNodeObject *self, void *arg)
{
  register Py_ssize_t i;
  register Py_ssize_t len;

  PyObject *childNodes;

  if (Node_HasFlag(self, Node_FLAGS_CONTAINER)) {
    len = ContainerNode_GET_COUNT(self);
    childNodes = PyList_New(len);
    if (childNodes == NULL) return NULL;
    for (i = 0; i < len; i++) {
      PyObject *child = (PyObject *) ContainerNode_GET_CHILD(self, i);
      Py_INCREF(child);
      PyList_SET_ITEM(childNodes, i, child);
    }
  } else {
    childNodes = PyList_New(0);
  }
  return childNodes;
}


static PyObject *get_base_uri(PyNodeObject *self, void *arg)
{
  PyNodeObject *node = self;
  PyObject *base, *result;

  /* DOM3 baseURI is calculated according to XML Base */

  while (Node_GET_PARENT(node) != (PyNodeObject *) Py_None) {
    /* 1. the base URI specified by an xml:base attribute on the element,
     *    if one exists, otherwise
     */
    if (PyElement_Check(node)) {
      base = PyDict_GetItem(PyElement_ATTRIBUTES(node), xml_base_key);
      if (base) {
        base = PyAttr_NODE_VALUE(base);
        /* If the xml:base in scope for the current node is not absolute, we find
         * the element where that xml:base was declared, then Absolutize our
         * relative xml:base against the base URI of the parent of declaring
         * element, recursively. */
        result = PyObject_CallFunction(is_absolute_function, "O", base);
        if (result == NULL) return NULL;
        switch (PyObject_IsTrue(result)) {
        case 0:
          Py_DECREF(result);
          result = get_base_uri(Node_GET_PARENT(node), arg);
          if (result == NULL) return NULL;
          else if (result == Py_None) return result;
          base = PyObject_CallFunction(absolutize_function, "OO", base, result);
          if (base == NULL) {
            Py_DECREF(result);
            return NULL;
          }
          /* fall through */
        case 1:
          Py_DECREF(result);
          Py_INCREF(base);
          return base;
        default:
          return NULL;
        }
      }
    }

    /* 2. the base URI of the element's parent element within the document
     *    or external entity, if one exists, otherwise
     */
    node = Node_GET_PARENT(node);
  }

  /* 3. the base URI of the document entity or external entity containing the
   *    element.
   */
  if (PyDocumentFragment_Check(node)) {
    node = (PyNodeObject *) Node_GET_DOCUMENT(node);
  }
  if (PyDocument_Check(node)) {
    base = PyDocument_BASE_URI(node);
    result = PyObject_CallFunction(is_absolute_function, "O", base);
    if (result == NULL) return NULL;
    switch (PyObject_IsTrue(result)) {
    case 0:
      base = Py_None;
      /* fall through */
    case 1:
      break;
    default:
      return NULL;
    }
  } else {
    /* Node does not yet have a parent */
    base = Py_None;
  }

  Py_INCREF(base);
  return base;
}


static PyObject *get_first_child(PyNodeObject *self, void *arg)
{
  PyObject *child;

  if (Node_HasFlag(self, Node_FLAGS_CONTAINER) &&
      ContainerNode_GET_COUNT(self))
    child = (PyObject *) ContainerNode_GET_CHILD(self, 0);
  else
    child = Py_None;

  Py_INCREF(child);
  return child;
}


static PyObject *get_last_child(PyNodeObject *self, void *arg)
{
  PyObject *child;
  int size;

  if (Node_HasFlag(self, Node_FLAGS_CONTAINER))
    size = ContainerNode_GET_COUNT(self);
  else
    size = 0;

  if (size)
    child = (PyObject *) ContainerNode_GET_CHILD(self, size - 1);
  else
    child = Py_None;

  Py_INCREF(child);
  return child;
}


static PyObject *get_next_sibling(PyNodeObject *self, void *arg)
{
  PyNodeObject *parentNode;
  PyNodeObject **nodes;
  PyObject *sibling;
  int count, index;

  parentNode = self->parentNode;
  if (parentNode == (PyNodeObject *) Py_None) {
    Py_INCREF(Py_None);
    return Py_None;
  }

  nodes = ContainerNode_GET_NODES(parentNode);
  count = ContainerNode_GET_COUNT(parentNode);
  for (index = 0; index < count; index++) {
    if (nodes[index] == self) {
      /* advance to the following node */
      index++;
      if (index == count) /* last child */
        sibling = Py_None;
      else
        sibling = (PyObject *) nodes[index];
      Py_INCREF(sibling);
      return sibling;
    }
  }

  return DOMException_InvalidStateErr("lost from parent");
}


static PyObject *get_previous_sibling(PyNodeObject *self, void *arg)
{
  PyNodeObject *parentNode;
  PyNodeObject **nodes;
  PyObject *sibling;
  int count, index;

  parentNode = self->parentNode;
  if (parentNode == (PyNodeObject *) Py_None) {
    Py_INCREF(Py_None);
    return Py_None;
  }

  nodes = ContainerNode_GET_NODES(parentNode);
  count = ContainerNode_GET_COUNT(parentNode);
  for (index = 0; index < count; index++) {
    if (nodes[index] == self) {
      if (index == 0) /* first child */
        sibling = Py_None;
      else
        sibling = (PyObject *) nodes[index - 1];
      Py_INCREF(sibling);
      return sibling;
    }
  }

  return DOMException_InvalidStateErr("lost from parent");
}


/* This is defined as a function to prevent corruption of shared "NodeList" */
static PyObject *get_empty_list(PyNodeObject *self, void *arg)
{
  return PyList_New((Py_ssize_t)0);
}


static struct PyGetSetDef node_getset[] = {
  { "childNodes",      (getter)get_child_nodes },
  { "baseURI",         (getter)get_base_uri },
  { "xmlBase",         (getter)get_base_uri },
  { "firstChild",      (getter)get_first_child },
  { "lastChild",       (getter)get_last_child },
  { "nextSibling",     (getter)get_next_sibling },
  { "previousSibling", (getter)get_previous_sibling },
  { "xpathAttributes", (getter)get_empty_list },
  { "xpathNamespaces", (getter)get_empty_list },
  { NULL }
};


/** Type Object ********************************************************/


static PyObject *node_repr(PyNodeObject *self)
{
  PyObject *name, *repr;

  name = PyObject_GetAttrString((PyObject *)self->ob_type, "__name__");
  if (name == NULL) {
    return NULL;
  }

  repr = PyString_FromFormat("<%s at %p>", PyString_AS_STRING(name), self);
  Py_DECREF(name);

  return repr;
}


static int node_traverse(PyNodeObject *self, visitproc visit, void *arg)
{
#ifdef DEBUG_NODE_CREATION
  printf("Traversing %s node at 0x%p\n", self->ob_type->tp_name, self);
#endif

  Py_VISIT((PyObject *) self->ownerDocument);
  if (self->flags & Node_FLAGS_CONTAINER) {
    PyNodeObject **nodes = ContainerNode_GET_NODES(self);
    int i = ContainerNode_GET_COUNT(self);
    while (--i >= 0) {
      int rt = visit((PyObject *) nodes[i], arg);
      if (rt) return rt;
    }
  }
  return 0;
}


static int node_clear(PyObject *self)
{
#ifdef DEBUG_NODE_CREATION
  printf("Clearing %s node at 0x%p\n", self->ob_type->tp_name, self);
#endif

  Py_CLEAR(((PyNodeObject *)self)->ownerDocument);
  if (((PyNodeObject *)self)->flags & Node_FLAGS_CONTAINER) {
    node_clear_nodes((PyContainerNodeObject *) self);
  }
  return 0;
}


static long node_hash(PyNodeObject *self)
{
#if SIZEOF_LONG >= SIZEOF_VOID_P
  return (long)self;
#else
  /* convert to a Python long and hash that */
  PyObject *longobj;
  long hash;

  if ((longobj = PyLong_FromVoidPtr(self)) == NULL) {
    return -1;
  }

  hash = PyObject_Hash(longobj);
  Py_DECREF(longobj);
  return hash;
#endif
}

#define OPSTR(op) (op == Py_LT ? "Py_LT" : \
                   (op == Py_LE ? "Py_LE" : \
                    (op == Py_EQ ? "Py_EQ" : \
                     (op == Py_NE ? "Py_NE" : \
                      (op == Py_GE ? "Py_GE" : \
                       (op == Py_GT ? "Py_GT" : "?"))))))

#define BOOLSTR(ob) (ob == Py_True ? "Py_True" : \
                     (ob == Py_False ? "Py_False" : \
                      (ob == Py_NotImplemented ? "Py_NotImplemented" : \
                       (ob == NULL ? "NULL" : "?"))))

#define NODESTR(node) PyString_AS_STRING(PyObject_Repr(node))

static PyObject *node_richcompare(PyNodeObject *a, PyNodeObject *b, int op)
{
  PyObject *result;
  PyDocumentObject *doc_a, *doc_b;
  PyNodeObject *parent_a, *parent_b;
  int depth_a, depth_b;

  /* Make sure both arguments are cDomlette nodes */
  if (!(PyNode_Check(a) && PyNode_Check(b))) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }

  if (a == b) {
    /* same objects */
    switch (op) {
    case Py_EQ: case Py_LE: case Py_GE:
      result = Py_True;
      break;
    case Py_NE: case Py_LT: case Py_GT:
      result = Py_False;
      break;
    default:
      result = Py_NotImplemented;
    }

    Py_INCREF(result);
    return result;
  }

  /* if different documents; just compare their creation indices */
  doc_a = PyDocument_Check(a) ? (PyDocumentObject *) a
                              : PyNode_OWNER_DOCUMENT(a);
  doc_b = PyDocument_Check(b) ? (PyDocumentObject *) b
                              : PyNode_OWNER_DOCUMENT(b);
  if (doc_a != doc_b) {
    return PyObject_RichCompare(PyDocument_INDEX(doc_a),
                                PyDocument_INDEX(doc_b),
                                op);
  }

  /* traverse to the top of each tree (document, document fragment, element
     or the node itself)
  */
  parent_a = a;
  depth_a = 0;
  while (Node_GET_PARENT(parent_a) != (PyNodeObject *) Py_None) {
    parent_a = Node_GET_PARENT(parent_a);
    depth_a++;
  }

  parent_b = b;
  depth_b = 0;
  while (Node_GET_PARENT(parent_b) != (PyNodeObject *) Py_None) {
    parent_b = Node_GET_PARENT(parent_b);
    depth_b++;
  }

  /* there is a dangling tree (not appended to the document yet) */
  if (parent_a != parent_b) {
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
  }

  /* if neither node is a document (depth>0), find the nodes common ancestor */
  if (depth_a > 0 && depth_b > 0) {
    PyNodeObject **nodes;
    int i, len;

    /* traverse to the same depth in the tree for both nodes */
    for (i = depth_a; i > depth_b; i--) {
      a = Node_GET_PARENT(a);
    }

    for (i = depth_b; i > depth_a; i--) {
      b = Node_GET_PARENT(b);
    }

    /* find the nodes common parent */
    if (a != b) {
      parent_a = Node_GET_PARENT(a);
      parent_b = Node_GET_PARENT(b);
      while (parent_a != parent_b) {
        a = parent_a;
        parent_a = Node_GET_PARENT(parent_a);
        b = parent_b;
        parent_b = Node_GET_PARENT(parent_b);
      }

      /* get the nodes position in the child list */
      depth_a = depth_b = -1;
      nodes = ContainerNode_GET_NODES(parent_a);
      len = ContainerNode_GET_COUNT(parent_a);
      for (i = 0; i < len; i++) {
        if (nodes[i] == a)
          depth_a = i;
        else if (nodes[i] == b)
          depth_b = i;
      }
    }
  }

  switch (op) {
  case Py_LT:
    result = (depth_a < depth_b) ? Py_True : Py_False;
    break;
  case Py_LE:
    result = (depth_a <= depth_b) ? Py_True : Py_False;
    break;
  case Py_EQ:
    result = (depth_a == depth_b) ? Py_True : Py_False;
    break;
  case Py_NE:
    result = (depth_a != depth_b) ? Py_True : Py_False;
    break;
  case Py_GT:
    result = (depth_a > depth_b) ? Py_True : Py_False;
    break;
  case Py_GE:
      result = (depth_a >= depth_b) ? Py_True : Py_False;
    break;
  default:
    result = Py_NotImplemented;
  }

  /*
    PySys_WriteStdout("op: %s, a <%p>: %d, b <%p>: %d, result: %s\n",
                      OPSTR(op), a, depth_a, b, depth_b, BOOLSTR(result));
  */

  Py_INCREF(result);
  return result;
}


static PyObject *node_iter(PyNodeObject *node);


static char node_doc[] = "\
The Node type is the primary datatype for the entire Document Object Model.";

PyTypeObject DomletteNode_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "Node",
  /* tp_basicsize      */ sizeof(PyNodeObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) _Node_Del,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) node_repr,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) node_hash,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ (Py_TPFLAGS_DEFAULT |
                           Py_TPFLAGS_BASETYPE |
                           Py_TPFLAGS_HAVE_GC),
  /* tp_doc            */ (char *) node_doc,
  /* tp_traverse       */ (traverseproc) node_traverse,
  /* tp_clear          */ node_clear,
  /* tp_richcompare    */ (richcmpfunc) node_richcompare,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) node_iter,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) node_methods,
  /* tp_members        */ (PyMemberDef *) node_members,
  /* tp_getset         */ (PyGetSetDef *) node_getset,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) 0,
  /* tp_free           */ 0,
};


/** Node ChildNodes Iterator ******************************************/

typedef struct {
  PyObject_HEAD
  long index;
  PyNodeObject *node; /* NULL when iterator is done */
} NodeIterObject;

static PyTypeObject NodeIter_Type;

static PyObject *node_iter(PyNodeObject *node)
{
  NodeIterObject *iter;

  iter = PyObject_GC_New(NodeIterObject, &NodeIter_Type);
  if (iter == NULL)
    return NULL;

  iter->index = 0;

  if (Node_HasFlag(node, Node_FLAGS_CONTAINER))
    Py_INCREF(node);
  else
    node = NULL; /* mark iterator as done */
  iter->node = node;

  PyObject_GC_Track(iter);

  return (PyObject *) iter;
}

static void nodeiter_dealloc(NodeIterObject *iter)
{
  PyObject_GC_UnTrack(iter);

  Py_XDECREF(iter->node);

  PyObject_GC_Del(iter);
}

static int nodeiter_traverse(NodeIterObject *iter, visitproc visit, void *arg)
{
  if (iter->node == NULL)
    return 0;
  return visit((PyObject *)iter->node, arg);
}

static PyObject *nodeiter_iter(NodeIterObject *iter)
{
  Py_INCREF(iter);
  return (PyObject *)iter;
}

static PyObject *nodeiter_next(NodeIterObject *iter)
{
  PyNodeObject *node;
  PyObject *item;

  node = iter->node;
  if (node == NULL)
    return NULL;

  if (iter->index < ContainerNode_GET_COUNT(node)) {
    item = (PyObject *) ContainerNode_GET_CHILD(node, iter->index);
    iter->index++;
    Py_INCREF(item);
    return item;
  }

  Py_DECREF(node);
  iter->node = NULL;
  return NULL;
}

static Py_ssize_t nodeiter_length(PyObject *iter)
{
  Py_ssize_t len;
  if (((NodeIterObject *)iter)->node) {
    len = ContainerNode_GET_COUNT(((NodeIterObject *)iter)->node) - ((NodeIterObject *)iter)->index;
    if (len >= 0)
      return len;
  }
  return 0;
}

static PySequenceMethods nodeiter_as_sequence = {
  /* sq_length */ nodeiter_length,
};


static PyTypeObject NodeIter_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ "nodeiter",
  /* tp_basicsize      */ sizeof(NodeIterObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) nodeiter_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) 0,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) &nodeiter_as_sequence,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ (Py_TPFLAGS_DEFAULT |
                           Py_TPFLAGS_HAVE_GC),
  /* tp_doc            */ (char *) 0,
  /* tp_traverse       */ (traverseproc) nodeiter_traverse,
  /* tp_clear          */ 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) nodeiter_iter,
  /* tp_iternext       */ (iternextfunc) nodeiter_next,
};


/** Module Setup & Teardown *******************************************/


int DomletteNode_Init(PyObject *module)
{
  PyObject *node_class, *import, *bases, *dict;

  import = PyImport_ImportModule("Ft.Lib.Uri");
  if (import == NULL) return -1;
  is_absolute_function = PyObject_GetAttrString(import, "IsAbsolute");
  if (is_absolute_function == NULL) {
    Py_DECREF(import);
    return -1;
  }
  absolutize_function = PyObject_GetAttrString(import, "Absolutize");
  if (absolutize_function == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  /* Get the xml.dom.Node class */
  import = PyImport_ImportModule("xml.dom");
  if (import == NULL) return -1;
  node_class = PyObject_GetAttrString(import, "Node");
  if (node_class == NULL) {
    Py_DECREF(import);
    return -1;
  }
  Py_DECREF(import);

  /* Setup the type's base classes */
  DomletteNode_Type.tp_base = &PyBaseObject_Type;
  bases = Py_BuildValue("(ON)", &PyBaseObject_Type, node_class);
  if (bases == NULL) return -1;
  DomletteNode_Type.tp_bases = bases;

  /* Initialize type objects */
  if (PyType_Ready(&DomletteNode_Type) < 0)
    return -1;

  /* Grrrr...MingW32 gcc doesn't support assigning imported functions in a
   * static structure.  This sucks because both gcc/Unix and MSVC both support
   * that.
   */
  NodeIter_Type.tp_getattro = PyObject_GenericGetAttr;
  if (PyType_Ready(&NodeIter_Type) < 0)
    return -1;

  /* Assign "class" constants */
  dict = DomletteNode_Type.tp_dict;
  if (PyDict_SetItemString(dict, "attributes", Py_None)) return -1;
  if (PyDict_SetItemString(dict, "localName", Py_None)) return -1;
  if (PyDict_SetItemString(dict, "namespaceURI", Py_None)) return -1;
  if (PyDict_SetItemString(dict, "prefix", Py_None)) return -1;
  if (PyDict_SetItemString(dict, "nodeValue", Py_None)) return -1;

  shared_empty_nodelist = PyList_New((Py_ssize_t)0);
  if (shared_empty_nodelist == NULL) return -1;

  xml_base_key = Py_BuildValue("(Os)", g_xmlNamespace, "base");
  if (xml_base_key == NULL) return -1;

  Py_INCREF(&DomletteNode_Type);
  return PyModule_AddObject(module, "Node", (PyObject*) &DomletteNode_Type);
}


void DomletteNode_Fini(void)
{
  Py_DECREF(shared_empty_nodelist);
  Py_DECREF(xml_base_key);

  PyType_CLEAR(&DomletteNode_Type);
  PyType_CLEAR(&NodeIter_Type);
}
