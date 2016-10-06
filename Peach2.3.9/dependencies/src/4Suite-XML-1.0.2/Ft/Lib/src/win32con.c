#include "Python.h"
#include <Windows.h>
/***********************************************************************
 * $Header: /var/local/cvsroot/4Suite/Ft/Lib/src/win32con.c,v 1.1 2004/10/28 14:49:45 jkloth Exp $
 ***********************************************************************/

static char module_doc[] = "\
Functions for accessing a Windows console.\
\n\
Copyright 2004 Fourthought, Inc. (USA).\n\
Detailed license and copyright information: http://4suite.org/COPYRIGHT\n\
Project home, documentation, distributions: http://4suite.org/\n\
";

static PyObject *get_screen_buffer_info(PyObject *self, PyObject *args)
{
  HANDLE handle;
  CONSOLE_SCREEN_BUFFER_INFO csbi;

  if (!PyArg_ParseTuple(args, "l:GetConsoleScreenBufferInfo", &handle))
    return NULL;

  if (!GetConsoleScreenBufferInfo(handle, &csbi))
    return PyErr_SetFromWindowsErr(0);

  return Py_BuildValue("((hh)(hh)i(hhhh))",
                       csbi.dwSize.X, csbi.dwSize.Y,
                       csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y,
                       csbi.wAttributes,
                       csbi.srWindow.Left, csbi.srWindow.Top,
                       csbi.srWindow.Right, csbi.srWindow.Bottom);
}

static PyObject *set_text_attribute(PyObject *self, PyObject *args)
{
  HANDLE handle;
  WORD attr;

  if (!PyArg_ParseTuple(args, "lh:SetConsoleTextAttribute", &handle, &attr))
    return NULL;

  if (!SetConsoleTextAttribute(handle, attr))
    return PyErr_SetFromWindowsErr(0);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef module_methods[] = {
  { "GetConsoleScreenBufferInfo", get_screen_buffer_info, METH_VARARGS },
  { "SetConsoleTextAttribute", set_text_attribute, METH_VARARGS },
  { NULL }
};

DL_EXPORT(void) init_win32con(void)
{
  PyObject *m;

  m = Py_InitModule3("_win32con", module_methods, module_doc);
  if (m == NULL) return;

  PyModule_AddIntConstant(m, "FOREGROUND_BLUE", FOREGROUND_BLUE);
  PyModule_AddIntConstant(m, "FOREGROUND_GREEN", FOREGROUND_GREEN);
  PyModule_AddIntConstant(m, "FOREGROUND_RED", FOREGROUND_RED);
  PyModule_AddIntConstant(m, "FOREGROUND_INTENSITY", FOREGROUND_INTENSITY);
  PyModule_AddIntConstant(m, "FOREGROUND", (FOREGROUND_BLUE |
                                            FOREGROUND_GREEN |
                                            FOREGROUND_RED |
                                            FOREGROUND_INTENSITY));

  PyModule_AddIntConstant(m, "BACKGROUND_BLUE", BACKGROUND_BLUE);
  PyModule_AddIntConstant(m, "BACKGROUND_GREEN", BACKGROUND_GREEN);
  PyModule_AddIntConstant(m, "BACKGROUND_RED", BACKGROUND_RED);
  PyModule_AddIntConstant(m, "BACKGROUND", (BACKGROUND_BLUE |
                                            BACKGROUND_GREEN |
                                            BACKGROUND_RED |
                                            BACKGROUND_INTENSITY));
}
