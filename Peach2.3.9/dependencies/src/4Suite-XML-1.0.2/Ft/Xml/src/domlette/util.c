#include "util.h"

/** DOMString *********************************************************/

PyObject *DOMString_FromObject(PyObject *obj)
{
  /* sanity check */
  if (obj == NULL) {
    PyErr_BadInternalCall();
    return NULL;
  }

  if (obj == Py_None) {
    Py_INCREF(obj);
    return obj;
  }

#ifdef PyUnicode_CheckExact
  /* Python 2.2 and newer */
  if (PyUnicode_CheckExact(obj)) {
    Py_INCREF(obj);
    return obj;
  }
#endif
  if (PyUnicode_Check(obj)) {
    /* For a Unicode subtype that's not a Unicode object,
       return a true Unicode object with the same data. */
    return PyUnicode_FromUnicode(PyUnicode_AS_UNICODE(obj),
                                 PyUnicode_GET_SIZE(obj));
  }

  /* Python DOM bindings specify byte-strings (PyString) must be
     UTF-8 encoded.

     Using "utf-8" instead of "UTF-8" as it is used as the shortcut name
     for the UTF-8 codec in Python's Unicode internals.
  */
  return PyUnicode_FromEncodedObject(obj, "utf-8", "strict");
}

PyObject *DOMString_FromObjectInplace(PyObject *obj)
{
  PyObject *result;

  /* allow for inlining */
  if (obj == NULL) return obj;

  if ((result = DOMString_FromObject(obj)) != NULL) {
    Py_DECREF(obj);
  }

  return result;
}

PyObject *DOMString_ConvertArgument(PyObject *arg, char *name, int null_ok)
{
  PyObject *result;

  if (null_ok) {
    result = DOMString_FromObject(arg);
    if (result == NULL) {
      if (PyErr_ExceptionMatches(PyExc_TypeError))
        PyErr_Format(PyExc_TypeError,
                     "%s must be None, unicode or UTF-8 string, %.80s found.",
                     name, arg->ob_type->tp_name);
    } else if (result != Py_None && PyUnicode_GET_SIZE(result) == 0) {
      if (PyErr_Warn(PyExc_SyntaxWarning,
                     "The null string should be None, not empty.") == -1) {
        /* warnings as exceptions is enabled */
        Py_DECREF(result);
        result = NULL;
      }
      /* From DOM L3, 1.3.3 XML Namespaces, empty strings are converted to
         the programming language's null.
      */
      Py_DECREF(result);
      Py_INCREF(Py_None);
      result = Py_None;
    }
  }
  else if (arg != Py_None) {
    result = DOMString_FromObject(arg);
    if (result == NULL) {
      if (PyErr_ExceptionMatches(PyExc_TypeError))
        PyErr_Format(PyExc_TypeError,
                     "%s must be unicode or UTF-8 string, %.80s found.",
                     name, arg->ob_type->tp_name);
    }
  }
  else {
    /* arg == Py_None and not null_ok */
    PyErr_Format(PyExc_TypeError,
                 "%s must be non-null unicode or UTF-8 string.", name);
    result = NULL;
  }

  return result;
}

/** Stack *************************************************************/

#define STACK_INITIAL_SIZE 10
Stack *Stack_New(void)
{
  Stack *stack = PyMem_New(Stack, 1);
  if (stack != NULL) {
    stack->size = 0;
    stack->allocated = STACK_INITIAL_SIZE;
    if ((stack->items = PyMem_New(PyObject *, STACK_INITIAL_SIZE)) == NULL) {
      PyErr_NoMemory();
      PyMem_Free(stack);
      return NULL;
    }
  }
  return stack;
}

void Stack_Del(Stack *stack)
{
  while (stack->size-- > 0) {
    Py_DECREF(stack->items[stack->size]);
  }
  PyMem_Free(stack->items);
  PyMem_Free(stack);
}

int Stack_Push(Stack *stack, PyObject *item)
{
  int allocated, new_allocated;
  int new_size = stack->size + 1;
  PyObject **items;

  /* Bypass realloc() when a previous overallocation is large enough
     to accommodate the newsize.
  */
  allocated = stack->allocated;
  items = stack->items;
  if (new_size >= allocated) {
    /* This over-allocates proportional to the list size, making room
     * for additional growth.  The over-allocation is mild, but is
     * enough to give linear-time amortized behavior over a long
     * sequence of appends() in the presence of a poorly-performing
     * system realloc().
     * The growth pattern is:  0, 4, 8, 16, 25, 35, 46, 58, 72, 88, ...
     */
    new_allocated = (new_size >> 3) + (new_size < 9 ? 3 : 6) + new_size;
    if (PyMem_Resize(items, PyObject *, new_allocated) == NULL) {
      PyErr_NoMemory();
      return -1;
    }
    stack->allocated = new_allocated;
    stack->items = items;
  }
  Py_INCREF(item);
  stack->items[stack->size] = item;
  stack->size = new_size;

  return 0;
}

PyObject *Stack_Pop(Stack *stack)
{
  if (stack->size == 0) {
    return NULL;
  }

  stack->size--;
  return stack->items[stack->size];
}

PyObject *Stack_Peek(Stack *stack)
{
  assert(stack->size > 0);
  return stack->items[stack->size - 1];
}


/** HashTable *********************************************************/

/* A hashtable implementation for storing XML_Char keys */

/*
To ensure the lookup algorithm terminates, there must be at least one Unused
slot (NULL key) in the table.
used is the number of non-NULL keys (== the number of Active items).
To avoid slowing down lookups on a near-full table, we resize the table when
it's two-thirds full.
*/

/* Must be a power of 2 */
#define HashTable_INITIAL_SIZE 64

HashTable *HashTable_New(void)
{
  HashTable *self = PyMem_New(HashTable, 1);
  if (self == NULL)
    return (HashTable *) PyErr_NoMemory();

  self->table = PyMem_New(HashTableEntry, HashTable_INITIAL_SIZE);
  if (self->table == NULL)
    return (HashTable *) PyErr_NoMemory();

  memset(self->table, 0, sizeof(HashTableEntry) * HashTable_INITIAL_SIZE);
  self->used = 0;
  self->mask = HashTable_INITIAL_SIZE - 1;

  return self;
}

void HashTable_Del(HashTable *table)
{
  register HashTableEntry *ep;
  register int used;

  for (ep = table->table, used = table->used; used > 0; ep++) {
    if (ep->key) {
      used--;
      PyMem_Free(ep->key);
      Py_DECREF(ep->value);
    }
  }
  PyMem_Free(table->table);
  PyMem_Free(table);
}


#define CHECK_ENTRY(entry, key, len, hash)              \
  ((entry)->hash == (hash) &&                           \
   (entry)->len == (len) &&                             \
   memcmp((entry)->key, (key), (len)*sizeof(XML_Char)) == 0)

static HashTableEntry *lookup_entry(HashTable *self, const XML_Char *key,
                                    size_t len, register long hash)
{
  register int i;
  register unsigned int perturb;
  register unsigned int mask = self->mask;
  HashTableEntry *table = self->table;
  register HashTableEntry *ep;

  i = hash & mask;
  ep = &table[i];
  if (ep->key == NULL)
    return ep;
  if (CHECK_ENTRY(ep, key, len, hash))
    return ep;

  for (perturb = hash; ; perturb >>= 5) {
    i = (i << 2) + i + perturb + 1;
    ep = &table[i & mask];
    if (ep->key == NULL)
      return ep;
    if (CHECK_ENTRY(ep, key, len, hash))
      return ep;
  }
}

/* Restructure the table by allocating a new table and reinserting all
 * items again.
 */
static int table_resize(HashTable *self)
{
  int newsize = (self->mask + 1) << 2;
  HashTableEntry *oldtable, *newtable;
  HashTableEntry *oldentry, *newentry;
  int i;

  /* Get space for a new table. */
  newtable = PyMem_New(HashTableEntry, newsize);
  if (newtable == NULL) {
    PyErr_NoMemory();
    return -1;
  }

  /* Make the dict empty, using the new table. */
  oldtable = self->table;
  self->table = newtable;
  self->mask = newsize - 1;
  memset(newtable, 0, sizeof(HashTableEntry) * newsize);

  /* Copy the data over */
  for (oldentry = oldtable, i = self->used; i > 0; oldentry++) {
    if (oldentry->key != NULL) {
      i--;
      newentry = lookup_entry(self, oldentry->key, oldentry->len, 
                              oldentry->hash);
      memcpy(newentry, oldentry, sizeof(HashTableEntry));
    }
  }

  PyMem_Free(oldtable);
  return 0;
}


PyObject *HashTable_Lookup(HashTable *self, const XML_Char *str, size_t len,
                           PyObject *(*buildvalue)(const XML_Char *str,
                                                   Py_ssize_t len, void *arg),
                           void *buildarg)
{
  register int i = len;
  register const XML_Char *p = str;
  register long hash;
  HashTableEntry *entry;
  XML_Char *key;
  PyObject *value;

  /* Calcuate the hash value */
  hash = *p << 7;
  while (--i >= 0)
    hash = (1000003*hash) ^ *p++;
  hash ^= len;

  entry = lookup_entry(self, str, len, hash);
  if (entry->key) {
    return entry->value;
  }

  /* not found in table, populate the entry */
  key = PyMem_New(XML_Char, len + 1);
  if (key == NULL)
    return PyErr_NoMemory();
  memcpy(key, str, len * sizeof(XML_Char));
  key[len] = 0;

  if (buildvalue) 
    value = buildvalue(str, len, buildarg);
  else
    value = Unicode_FromXMLCharAndSize(str, len);
  if (value == NULL) {
    PyMem_Free(key);
    return NULL;
  }

  entry->key = key;
  entry->len = len;
  entry->hash = hash;
  entry->value = value;

  /* Resize the table if it is more than 2/3 used */
  self->used++;
  if (self->used * 3 >= (self->mask + 1) * 2) {
    if (table_resize(self) == -1) {
      return NULL;
    }
  }

  return value;
}
