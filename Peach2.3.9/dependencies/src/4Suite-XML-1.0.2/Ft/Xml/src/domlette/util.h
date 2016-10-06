#ifndef DOMLETTE_UTIL_H
#define DOMLETTE_UTIL_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "../common.h"
#include "xmlchar.h"

  PyObject *DOMString_FromObject(PyObject *obj);
  PyObject *DOMString_FromObjectInplace(PyObject *obj);
  PyObject *DOMString_ConvertArgument(PyObject *arg, char *name, int null_ok);

#define DOMString_Check PyUnicode_CheckExact
#define DOMString_NullCheck(op) ((op) == Py_None || DOMString_Check(op))

  typedef struct {
    int size;
    int allocated;
    PyObject **items;
  } Stack;

  Stack *Stack_New(void);
  void Stack_Del(Stack *stack);
  int Stack_Push(Stack *stack, PyObject *item);
  PyObject *Stack_Pop(Stack *stack);
  PyObject *Stack_Peek(Stack *stack);

#ifdef Py_DEBUG
#define Stack_PEEK Stack_Peek
#else
#define Stack_PEEK(stack) ((stack)->items[(stack)->size - 1])
#endif

  typedef struct {
    long hash;
    XML_Char *key;
    size_t len;
    PyObject *value;
  } HashTableEntry;

  typedef struct {
    int used;

    /* The table contains (mask + 1)**2 slots.
     * We store the mask instead of the size because the mask is more
     * frequently needed.
     */
    int mask;

    HashTableEntry *table;
  } HashTable;

  HashTable *HashTable_New(void);
  void HashTable_Del(HashTable *table);
  PyObject *HashTable_Lookup(HashTable *table, const XML_Char *str, size_t len,
                             PyObject *(*buildvalue)(const XML_Char *str,
                                                     Py_ssize_t len, void *arg),
                             void *buildarg);

/* See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/67112 */
#if defined(DEBUG_PARSER)
#define Py_DEBUG
extern void _Py_CountReferences(FILE*);
#define CURIOUS(x) { fprintf(stderr, __FILE__ ":%d ", __LINE__); x; }
#else
#define CURIOUS(x)
#endif
#define NEWLINE()       CURIOUS(fprintf(stderr, "\n"))
#define DESCRIBE(x)     CURIOUS(fprintf(stderr, "  " #x "=%d\n", x))
#define DESCRIBE_HEX(x) CURIOUS(fprintf(stderr, "  " #x "=%08x\n", x))
#define COUNTREFS()     CURIOUS(_Py_CountReferences(stderr))

#define PRINT_OBJECT(label, obj)                \
  fputs((label), stderr);                       \
  PyObject_Print((obj), stderr, Py_PRINT_RAW);  \
  fputs("\n", stderr);

#ifndef Py_VISIT
#define Py_VISIT(op)                            \
  do {                                          \
    if (op) {                                   \
      int vret = visit((op), arg);              \
      if (vret) return vret;                    \
    }                                           \
  } while (0)
#endif

#ifndef Py_CLEAR
#define Py_CLEAR(op)                            \
  do {                                          \
    if (op) {                                   \
      PyObject *tmp = (PyObject *)(op);         \
      (op) = NULL;                              \
      Py_DECREF(tmp);                           \
    }                                           \
  } while (0)
#endif

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_UTIL_H */
