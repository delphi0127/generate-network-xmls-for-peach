/***********************************************************************
 * $Header: /var/local/cvsroot/4Suite/Ft/Xml/src/StreamWriter.c,v 1.14.2.1 2006/09/24 15:54:39 uogbuji Exp $
 ***********************************************************************/

static char module_doc[] = "\
Encoding character stream writer that makes substitutions of illegal\n\
and unencodable characters\n\
\n\
Copyright 2003 Fourthought, Inc. (USA).\n\
Detailed license and copyright information: http://4suite.org/COPYRIGHT\n\
Project home, documentation, distributions: http://4suite.org/\n\
";

#include "Python.h"
#include "cStringIO.h"
#include "common.h"

#if defined(_WIN32) || defined(__WIN32__) && !defined(__CYGWIN__)
#  define strcasecmp stricmp
#endif

/* Printer type */
typedef struct PyStreamWriterObject {
  PyObject_HEAD
  
  PyObject *stream;
  PyObject *encoding;

  FILE *fp;
  PyObject *write;
  int (*write_func)(struct PyStreamWriterObject *, const char *, int);

  PyObject *encode;
  signed char write_bom;
  char encode_ascii;
} PyStreamWriterObject;

typedef struct PyEntityMapObject {
  PyObject_HEAD

  PyObject **entity_table;
  Py_UNICODE max_entity;
} PyEntityMapObject;

staticforward PyTypeObject PyStreamWriter_Type;
staticforward PyTypeObject PyEntityMap_Type;

/** StreamWriter internal functions ************************************/

static int write_none(PyStreamWriterObject *self, const char *s, int n)
{
  return n;
}

static int write_file(PyStreamWriterObject *self, const char *s, int n) 
{
  int byteswritten;

  Py_BEGIN_ALLOW_THREADS
  byteswritten = fwrite(s, sizeof(char), n, self->fp);
  Py_END_ALLOW_THREADS

  if (byteswritten != n) {
    PyErr_SetFromErrno(PyExc_IOError);
    return -1;
  }

  return n;
}

static int write_cStringIO(PyStreamWriterObject *self, const char *s, int  n) 
{
  if (PycStringIO->cwrite((PyObject *)self->stream, (char *)s, n) != n) {
    return -1;
  }

  return n;
}

static int write_other(PyStreamWriterObject *self, const char *s, int  n)
{
  PyObject *result;

  result = PyObject_CallFunction(self->write, "s#", s, n);
  if (!result) {
    return -1;
  }

  Py_DECREF(result);
  return n;
}

static PyObject *encode_unicode(PyStreamWriterObject *self, PyObject *unicode)
{
  PyObject *args, *result, *data;
 
  /* create the arguments tuple */
  args = PyTuple_New((Py_ssize_t)1);
  if (!args) {
    Py_DECREF(unicode);
    return NULL;
  }
  Py_INCREF(unicode);
  PyTuple_SET_ITEM(args, 0, unicode);

  /* call the encoder */
  result = PyEval_CallObject(self->encode, args);
  Py_DECREF(args);
  if (!result) return NULL;
  
  if (!PyTuple_Check(result) || PyTuple_GET_SIZE(result) != 2) {
    PyErr_SetString(PyExc_TypeError,
                    "encoder must return a tuple (object,integer)");
  }
   
  /* borrowed reference */
  data = PyTuple_GET_ITEM(result, 0);
  if (!PyString_Check(data)) {
    PyErr_Format(PyExc_TypeError,
                 "encoder did not return a string object (type=%.400s)",
                 data->ob_type->tp_name);
    Py_DECREF(result);
    return NULL;
  }

  Py_INCREF(data);
  Py_DECREF(result);
  return data;
}

static int write_encode(PyStreamWriterObject *self, PyObject *string, PyObject *where) {
  PyObject *data;
  int result;

  data = encode_unicode(self, string);
  if (!data) {
    if (PyErr_ExceptionMatches(PyExc_ValueError)) {
      /* assume encoding error */
      PyObject *repr, *str;

      repr = PyObject_Repr(string);
      if (!repr) return -1;

      if (where)
        str = PyObject_Str(where);
      else
        str = PyString_FromString("output");

      if (!str) {
        Py_DECREF(repr);
        return -1;
      }
        
      PyErr_Format(PyExc_ValueError, "Invalid character in %s %s",
                   PyString_AS_STRING(str), PyString_AS_STRING(repr));
      Py_DECREF(str);
      Py_DECREF(repr);
    }
    return -1;
  }
      
  result = self->write_func(self, PyString_AS_STRING(data), 
                            PyString_GET_SIZE(data));
  Py_DECREF(data);
  return result;
}

static int write_escaped(PyStreamWriterObject *self, PyObject *unicode)
{
  PyObject *data;
  Py_UNICODE *unistr;
  int size;
  char charref[14]; /* charref: 10 digits (32-bits) plus '&#' and ';\0' */

  data = encode_unicode(self, unicode);
  if (!data) {
    /* Replace any characters not representable in this encoding with
     * their numerical character entity.
     */
    PyErr_Clear();
    size = PyUnicode_GET_SIZE(unicode);
    unistr = PyUnicode_AS_UNICODE(unicode);
    while (size-- > 0) {
      PyObject *unichar = PyUnicode_FromUnicode(unistr, (Py_ssize_t)1);
      data = encode_unicode(self, unichar);
      Py_DECREF(unichar);
      if (!data) {
        /* Found an offending character */
        PyErr_Clear();
        /* Note: use decimal form due to some broken browsers. */
        sprintf(charref, "&#%ld;", (long) *unistr);
        data = PyString_FromString(charref);
        if (!data) {
          return -1;
        }
      }
      if (self->write_func(self, PyString_AS_STRING(data),
                           PyString_GET_SIZE(data)) < 0) {
        Py_DECREF(data);
        return -1;
      }
      Py_DECREF(data);
      unistr++;
    }
  } else {
    if (self->write_func(self, PyString_AS_STRING(data),
                         PyString_GET_SIZE(data)) < 0) {
      Py_DECREF(data);
      return -1;
    }
    Py_DECREF(data);
  }

  return 0;
}

static int write_ascii(PyStreamWriterObject *self, PyObject *string) {
  int result = -1;

  if (!self->encode_ascii) {
    /* shortcut, write it directly */
    result = self->write_func(self, PyString_AS_STRING(string),
                              PyString_GET_SIZE(string));
  } else {
    /* ASCII must be encoded before writing it to the stream */
    PyObject *unicode = PyUnicode_DecodeASCII(PyString_AS_STRING(string),
                                              PyString_GET_SIZE(string),
                                              "strict");
    if (unicode) {
      result = write_encode(self, unicode, NULL);
      Py_DECREF(unicode);
    }
  }
  return result;
}

/** StreamWriter methods ***********************************************/

static PyObject *writer_new(PyObject *stream, PyObject *encoding)
{
  PyStreamWriterObject *self;
  static PyObject *ascii;
  PyObject *test;

  if (ascii == NULL) {
    ascii = \
      PyUnicode_DecodeASCII("\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09" \
                            "\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13" \
                            "\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d" \
                            "\x1e\x1f !\"#$%&\'()*+,-./0123456789:;<=" \
                            ">?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcd" \
                            "efghijklmnopqrstuvwxyz{|}~\x7f", (Py_ssize_t)128, "strict");
    if (ascii == NULL) return NULL;
  }

  self = PyObject_New(PyStreamWriterObject, &PyStreamWriter_Type);
  if (self == NULL)
    return NULL;

  self->stream = NULL;
  self->encoding = NULL;
  self->write = NULL;
  self->encode = NULL;

  if (PyFile_Check(stream)) {
    self->fp = PyFile_AsFile(stream);
    if (self->fp == NULL) {
      PyErr_SetString(PyExc_ValueError, "I/O operation on closed file");
      Py_DECREF(self);
      return NULL;
    }
    self->write_func = write_file;
  }
  else if (PycStringIO_OutputCheck(stream)) {
    self->write_func = write_cStringIO;
  }
  else if (stream == Py_None) {
    self->write_func = write_none;
  }
  else {
    self->write_func = write_other;
    self->write = PyObject_GetAttrString(stream, "write");
    if (!self->write) {
      PyErr_SetString(PyExc_TypeError, "argument must have 'write' "
                      "attribute");
      Py_DECREF(self);
      return NULL;
    }
  }
    
  if (strcasecmp(PyString_AS_STRING(encoding), "utf-16") == 0) {
    /* use either utf-16le or utf-16be to prevent BOM on every encode */
    /* this test is taken from Python's sysmodule for sys.byteorder */
    unsigned long number = 1;
    char *s = (char *) &number;
    if (s[0] == 0) {
      /* big endian */
      self->write_bom = 1;
      self->encode = PyCodec_Encoder("utf-16be");
    } else {
      /* little endian */
      self->write_bom = -1;
      self->encode = PyCodec_Encoder("utf-16le");
    }
  } else {
    self->write_bom = 0;
    self->encode = PyCodec_Encoder(PyString_AsString(encoding));
  }
  if (self->encode == NULL) {
    Py_DECREF(self);
    return NULL;
  }

  Py_INCREF(stream);
  self->stream = stream;

  Py_INCREF(encoding);
  self->encoding = encoding;

  /* Determine if we can write ASCII directly to the stream */
  test = encode_unicode(self, ascii);
  if (test && PyString_Check(test) && PyString_GET_SIZE(test) == 128) {
    self->encode_ascii = 0;
  } else {
    self->encode_ascii = 1;
  }
  Py_XDECREF(test);

  return (PyObject*)self;
}

static char writeAscii_doc[] =
"writeAscii(string)\n\
\n\
Writes the ASCII string as is to the stream.";

static PyObject *writer_writeAscii(PyStreamWriterObject *self, PyObject *args)
{
  PyObject *data;

  if (!PyArg_ParseTuple(args, "S:writeAscii", &data))
    return NULL;

  if (self->write_bom) {
    if (self->write_func(self, 
                         (self->write_bom == -1) ? "\xff\xfe" : "\xfe\xff",
                         2) < 0) {
      return NULL;
    }
    self->write_bom = 0;
  }

  if (write_ascii(self, data) < 0)
    return NULL;

  Py_INCREF(Py_None);
  return Py_None;
}

static char writeEncode_doc[] =
"writeEncode(unicode[, where])\n\
\n\
Writes the unicode string encoded to the stream.\n\
\n\
Raises ValueError if the string cannot be encoded with where specifying\n\
the place of the error.  If not given the string 'output' is used.";

static PyObject *writer_writeEncode(PyStreamWriterObject *self, PyObject *args)
{
  PyObject *string, *where=NULL;

  if (!PyArg_ParseTuple(args, "U|O:writeEncode", &string, &where))
    return NULL;

  if (self->write_bom) {
    if (self->write_func(self, 
                         (self->write_bom == -1) ? "\xff\xfe" : "\xfe\xff",
                         2) < 0) {
      return NULL;
    }
    self->write_bom = 0;
  }

  if (write_encode(self, string, where) < 0)
    return NULL;

  Py_INCREF(Py_None);
  return Py_None;
}

static char writeEscape_doc[] =
"writeEscape(unicode, entityMap])\n\
\n\
Writes the unicode string encoded to the stream.\n\
\n\
entityMap contains the characters which will be escaped by charrefs.\n\
Additional, any character that cannot be encoded is replaced with its\n\
numerical character entity.  Illegal XML characters are replaced by '?'.";

/* Legal XML characters are:
 *   0x09 0x0A 0x0D 0x20-0xD7FF 0xE000-0xFFFD 0x10000-0x10FFFF */
#define LEGAL_UCS2(c) ((c) == 0x09 || (c) == 0x0A || (c) == 0x0D || \
                       (((c) >= 0x20) && ((c) <= 0xD7FF)) || \
                       (((c) >= 0xE000) && ((c) <= 0xFFFD)))
#define LEGAL_UCS4(c) (((c) >= 0x10000) && ((c) <= 0x10FFFF))

#ifdef Py_UNICODE_WIDE
#define LEGAL_XML_CHAR(c) (LEGAL_UCS2(c) || LEGAL_UCS4(c))
#else
#define LEGAL_XML_CHAR LEGAL_UCS2
#endif
                           
static PyObject *writer_writeEscape(PyStreamWriterObject *self, PyObject *args)
{
  PyObject *string;
  PyEntityMapObject *entities;
  PyObject *newstr = NULL;
  Py_UNICODE *p, *chunk_start;
  int size;
  Py_ssize_t chunk_size;

  if (!PyArg_ParseTuple(args, "UO!:writeEscape", &string, &PyEntityMap_Type, &entities))
    return NULL;

  if (self->write_bom) {
    if (self->write_func(self, 
                         (self->write_bom == -1) ? "\xff\xfe" : "\xfe\xff",
                         2) < 0) {
      return NULL;
    }
    self->write_bom = 0;
  }

  /* this might get replaced */
  Py_INCREF(string);

  /* Replace any illegal characters with '?' */
  size = PyUnicode_GET_SIZE(string);
  p = PyUnicode_AS_UNICODE(string);
  while (size-- > 0) {
    if (!LEGAL_XML_CHAR(*p)) {
      /* replace it */
      if (newstr == NULL) {
        /* create a copy to work with */
        newstr = PyUnicode_FromUnicode(PyUnicode_AS_UNICODE(string),
                                       PyUnicode_GET_SIZE(string));
        if (newstr == NULL) return NULL;

        /* move pointer to the correct location in the copy */
        p = PyUnicode_AS_UNICODE(newstr) + (p - PyUnicode_AS_UNICODE(string));

        /* replaced passed in unicode object with the copy */
        Py_DECREF(string);
        string = newstr;
      }
      *p = '?';
    }
    p++;
  }

  /* Write out the string replacing the entities given by EntityMap as we go */
  size = PyUnicode_GET_SIZE(string);
  p = chunk_start = PyUnicode_AS_UNICODE(string);
  while (size-- > 0) {
    if (*p <= entities->max_entity && entities->entity_table[*p]) {
      PyObject *repl = entities->entity_table[*p];

      /* write out everything up to the character to replace */
      chunk_size = p - chunk_start;
      if (chunk_size > 0) {
        newstr = PyUnicode_FromUnicode(chunk_start, chunk_size);
        if (write_escaped(self, newstr) < 0) {
          Py_DECREF(newstr);
          Py_DECREF(string);
          return NULL;
        }
        Py_DECREF(newstr);
      }
      
      /* the entities are stored as PyStrings or callable objects */
      if (PyString_Check(repl)) {
        /* a direct string replacement */
        Py_INCREF(repl);
      } else {
        /* a callable that generates the replacement string */
        repl = PyObject_CallFunction(repl, "Oi", string, 
                                     (p - PyUnicode_AS_UNICODE(string)));
        if (repl == NULL) {
          Py_DECREF(string);
          return NULL;
        } else if (!PyString_Check(repl)) {
          PyErr_Format(PyExc_TypeError,
                       "expected string, but %.200s found", 
                       repl->ob_type->tp_name);
          Py_DECREF(repl);
          Py_DECREF(string);
          return NULL;
        }
      }
     
      /* write the replacement string */
      if (write_ascii(self, repl) < 0) {
        Py_DECREF(string);
        Py_DECREF(repl);
        return NULL;
      }
      Py_DECREF(repl);

      /* skip over the replaced character */
      chunk_start = p + 1;
    }
    p++;
  }

  chunk_size = p - chunk_start;
  /* write out remaining text */
  if (chunk_size > 0) {
    newstr = PyUnicode_FromUnicode(chunk_start, chunk_size);
    if (write_escaped(self, newstr) < 0) {
      Py_DECREF(newstr);
      Py_DECREF(string);
      return NULL;
    }
    Py_DECREF(newstr);
  }
  
  Py_DECREF(string);
  Py_INCREF(Py_None);
  return Py_None;
}

/* StreamWriter Python interface */

static struct PyMethodDef writer_methods[] = {
  { "writeAscii", (PyCFunction) writer_writeAscii, 1, writeAscii_doc },
  { "writeEncode", (PyCFunction) writer_writeEncode, 1, writeEncode_doc },
  { "writeEscape", (PyCFunction) writer_writeEscape, 1, writeEscape_doc },
  {NULL, NULL}
};
   
static void writer_dealloc(PyStreamWriterObject *self)
{
  Py_XDECREF(self->write);
  Py_XDECREF(self->encode);
  Py_XDECREF(self->stream);
  Py_XDECREF(self->encoding);

  PyObject_Del(self);
}

static PyObject *writer_getattr(PyStreamWriterObject *self, char *name)
{
  if (strcmp(name, "stream") == 0) {
    Py_INCREF(self->stream);
    return self->stream;
  }
  else if (strcmp(name, "encoding") == 0) {
    Py_INCREF(self->encoding);
    return self->encoding;
  }
  
  else if (strcmp(name, "__members__") == 0) {
    PyObject *members = PyList_New((Py_ssize_t)0);
    PyObject *member;
    if (members == NULL) return NULL;

    member = PyString_FromString("stream");
    if (member == NULL) {
      Py_DECREF(members);
      return NULL;
    }
    PyList_Append(members, member);
    Py_DECREF(member);

    member = PyString_FromString("encoding");
    if (member == NULL) {
      Py_DECREF(members);
      return NULL;
    }
    PyList_Append(members, member);
    Py_DECREF(member);

    return members;
  }
  return Py_FindMethod(writer_methods, (PyObject *)self, name);
}

static PyObject *writer_repr(PyStreamWriterObject *self)
{
  char buf[512];
  PyObject *repr = PyObject_Repr(self->stream);
  if (!repr) return NULL;

  sprintf(buf, "<%s at %p, stream=%.256s, encoding='%.128s'>", 
          self->ob_type->tp_name, self, PyString_AsString(repr),
          PyString_AsString(self->encoding));
  Py_DECREF(repr);

  return PyString_FromString(buf);
}

static int writer_print(PyStreamWriterObject *self, FILE *fp, int flags)
{
  PyObject *repr = writer_repr(self);
  fprintf(fp, PyString_AS_STRING(repr));
  Py_DECREF(repr);
  return 0;
}

static PyTypeObject PyStreamWriter_Type = {
  PyObject_HEAD_INIT(NULL)
  0,                            /*ob_size*/
  "cStreamWriter",              /*tp_name*/
  sizeof(PyStreamWriterObject), /*tp_basicsize*/
  0,                            /*tp_itemsize*/
  /* methods */
  (destructor)writer_dealloc,   /*tp_dealloc*/
  (printfunc)writer_print,      /*tp_print*/
  (getattrfunc)writer_getattr,  /*tp_getattr*/
  (setattrfunc)0,               /*tp_setattr*/
  (cmpfunc)0,                   /*tp_compare*/
  (reprfunc)writer_repr,        /*tp_repr*/
  0,                            /*tp_as_number*/
  0,                            /*tp_as_sequence*/
  0,                            /*tp_as_mapping*/
  (hashfunc)0,                  /*tp_hash*/
  (ternaryfunc)0,               /*tp_call*/
  (reprfunc)0,                  /*tp_str*/
};

/***********************************************************************
 ***********************************************************************
 ***********************************************************************/

/* EntityMap Python interface */

static struct PyMethodDef entitymap_methods[] = {
  {NULL, NULL}
};

/* EntityMap methods */

static PyObject *entitymap_new(PyObject *entities)
{
  PyEntityMapObject *self;
  PyObject *keys, *seq;
  PyObject *key, *value;
  int i;
  Py_UNICODE ord;

  self = PyObject_New(PyEntityMapObject, &PyEntityMap_Type);
  if (self == NULL)
    return NULL;

  self->entity_table = NULL;
  self->max_entity = 0;

  /* create a copy of the mapping (doesn't need to be a dictionary) */
  keys = PyMapping_Keys(entities);
  if (keys == NULL) {
    Py_DECREF(self);
    return NULL;
  }
  seq = PySequence_Tuple(keys);
  Py_DECREF(keys);
  if (seq == NULL) {
    Py_DECREF(self);
    return NULL;
  }
    
  /* find the largest character ordinal also do validation */
  for (i = 0; i < PyTuple_GET_SIZE(seq); i++) {
    key = PyTuple_GET_ITEM(seq, i);

    if (PyString_Check(key)) {
      if (PyString_GET_SIZE(key) == 1) {
        ord = (Py_UNICODE)((unsigned char)*PyString_AS_STRING(key));
      } else {
        PyErr_Format(PyExc_TypeError,
                     "expected a character, but string of length %" PY_FORMAT_SIZE_T "d found",
                     PyString_GET_SIZE(key));
        Py_DECREF(self);
        return NULL;
      }
    } else if (PyUnicode_Check(key)) {
      if (PyUnicode_GET_SIZE(key) == 1) {
        ord = *PyUnicode_AS_UNICODE(key);
      } else {
        PyErr_Format(PyExc_TypeError,
                     "expected a character, but string of length %" PY_FORMAT_SIZE_T "d found",
                     PyUnicode_GET_SIZE(key));
        Py_DECREF(self);
        return NULL;
      }
    } else {
      PyErr_Format(PyExc_TypeError,
                   "expected string of length 1, but %.200s found", 
                   key->ob_type->tp_name);
      Py_DECREF(self);
      return NULL;
    }
    
    if (ord > self->max_entity) self->max_entity = ord;

    value = PyObject_GetItem(entities, key);
    if (value == NULL) {
      Py_DECREF(seq);
      Py_DECREF(self);
      return NULL;
    } else if (!(PyString_Check(value) || PyCallable_Check(value))) {
      PyErr_Format(PyExc_TypeError, 
                   "expected string or callable object, but %.200s found", 
                   value->ob_type->tp_name);
      Py_DECREF(value);
      Py_DECREF(seq);
      Py_DECREF(self);
      return NULL;
    }

    Py_DECREF(value);
  }

  /* create the access table */
  self->entity_table = (PyObject **)calloc(self->max_entity + 1,
                                           sizeof(PyObject *));
  if (self->entity_table == NULL) {
    Py_DECREF(seq);
    Py_DECREF(self);
    return PyErr_NoMemory();
  }

  for (i = 0; i < PyTuple_GET_SIZE(seq); i++) {
    key = PyTuple_GET_ITEM(seq, i);

    if (PyString_Check(key)) {
      ord = (Py_UNICODE)((unsigned char)*PyString_AS_STRING(key));
    } else {
      ord = *PyUnicode_AS_UNICODE(key);
    }

    value = PyObject_GetItem(entities, key);
    if (value == NULL) {
      Py_DECREF(seq);
      Py_DECREF(self);
      return NULL;
    }

    self->entity_table[ord] = value;
  }
  Py_DECREF(seq);

  return (PyObject *)self;
}

static void entitymap_dealloc(PyEntityMapObject *self)
{
  if (self->entity_table != NULL) {
    /* destroy the entity lookup table */
    Py_UNICODE i;

    for (i = 0; i <= self->max_entity; i++) {
      Py_XDECREF(self->entity_table[i]);
    }
    free(self->entity_table);
  }

  PyObject_Del(self);
}

static PyObject *entitymap_getattr(PyEntityMapObject *self, char *name)
{
  if (strcmp(name, "entities") == 0) {
    /* build a dictionary from the entity lookup table */
    PyObject *entities = PyDict_New();
    Py_UNICODE i;

    if (entities != NULL) {
      for (i = 0; i <= self->max_entity; i++) {
        PyObject *value = self->entity_table[i];
        if (value != NULL) {
          PyObject *key = PyInt_FromLong(i);
          if (key == NULL) {
            Py_DECREF(entities);
            return NULL;
          }
          if (PyDict_SetItem(entities, key, value) < 0) {
            Py_DECREF(key);
            Py_DECREF(entities);
            return NULL;
          }
          Py_DECREF(key);
        }
      }
    }
    return entities;
  } 
  else if (strcmp(name, "__members__") == 0) {
    return Py_BuildValue("[s]", "entities");
  }

  return Py_FindMethod(entitymap_methods, (PyObject *)self, name);
}

static PyObject *entitymap_repr(PyEntityMapObject *self)
{
  char buf[512];
  sprintf(buf, "<%.200s at %p>", self->ob_type->tp_name, self);

  return PyString_FromString(buf);
}

static int entitymap_print(PyEntityMapObject *self, FILE *fp, int flags)
{
  PyObject *repr = entitymap_repr(self);
  fprintf(fp, PyString_AS_STRING(repr));
  Py_DECREF(repr);
  return 0;
}

static PyTypeObject PyEntityMap_Type = {
  PyObject_HEAD_INIT(NULL)
  0,                              /*ob_size*/
  "cEntityMap",                   /*tp_name*/
  sizeof(PyEntityMapObject),      /*tp_basicsize*/
  0,                              /*tp_itemsize*/
  /* methods */
  (destructor)entitymap_dealloc,  /*tp_dealloc*/
  (printfunc)entitymap_print,     /*tp_print*/
  (getattrfunc)entitymap_getattr, /*tp_getattr*/
  (setattrfunc)0,                 /*tp_setattr*/
  (cmpfunc)0,                     /*tp_compare*/
  (reprfunc)entitymap_repr,       /*tp_repr*/
  0,                              /*tp_as_number*/
  0,                              /*tp_as_sequence*/
  0,                              /*tp_as_mapping*/
  (hashfunc)0,                    /*tp_hash*/
  (ternaryfunc)0,                 /*tp_call*/
  (reprfunc)0,                    /*tp_str*/
};

/* External functions */

static char StreamWriter_doc[] = \
"StreamWriter(stream, encoding)\n\
\n\
stream must be a file-like object open for writing (binary) data.\n\
encoding specifies the encoding which is to be used for the stream.\n\
";

static PyObject *PyStreamWriter_StreamWriter(PyObject *self, PyObject *args)
{
  PyObject *stream, *encoding;

  if (!PyArg_ParseTuple(args, "OS:StreamWriter", &stream, &encoding))
    return NULL;

  return writer_new(stream, encoding);
}

static char EntityMap_doc[] = \
"EntityMap(mapping)\n\
\n\
Creates an EntityMap used for writing escaped characters.  The key in the\n\
mapping represents the character to escape and the value is the replacement.";
/*
If pattern is supplied, only those characters that match the pattern will\n\
be replaced.  Otherwise all characters in the mapping keys will be replaced.";
*/
static PyObject *PyStreamWriter_EntityMap(PyObject *self, PyObject *args)
{
  PyObject *dict;

  if (!PyArg_ParseTuple(args, "O!:EntityMap", &PyDict_Type, &dict))
    return NULL;

  return entitymap_new(dict);
}

/* The external interface definitions */
static PyMethodDef module_methods[] = {

  { "StreamWriter", PyStreamWriter_StreamWriter, 1, StreamWriter_doc },
  { "EntityMap", PyStreamWriter_EntityMap, 1, EntityMap_doc },
  { NULL, NULL }
};

DL_EXPORT(void) initcStreamWriter(void) {
  PyObject *module;

  PyStreamWriter_Type.ob_type = &PyType_Type;
  PyEntityMap_Type.ob_type = &PyType_Type;

  module = Py_InitModule3("cStreamWriter", module_methods, module_doc);
  if (!module) return;
 
  PycString_IMPORT;
  return;
}



