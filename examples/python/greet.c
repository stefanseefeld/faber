//
// Copyright (c) 2016 Stefan Seefeld
// All rights reserved.
//
// This file is part of Faber. It is made available under the
// Boost Software License, Version 1.0.
// (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

#include "Python.h"

static char const *greet() { return "Hello!";}

static PyObject *py_greet(PyObject *self, PyObject *args)
{
  if (!PyArg_ParseTuple(args, ":greet"))
    return NULL;
  return PyUnicode_FromString(greet());
}

static PyMethodDef methods[] =
{
  {"greet",  py_greet, METH_VARARGS, NULL},
  {NULL, NULL}      /* sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef =
{
  PyModuleDef_HEAD_INIT,
  "greet",
  0, /* doc      */
  -1, //sizeof(struct module_state),
  methods,
  0, /* reload   */
  0, /* traverse */
  0, /* clear    */
  0  /* free     */
};

PyMODINIT_FUNC PyInit_greet()
#else
PyMODINIT_FUNC initgreet()
#endif
{
  PyObject *module;

#if PY_MAJOR_VERSION >= 3
  module = PyModule_Create(&moduledef);
  return module;
#else
  module = Py_InitModule("greet", methods);
#endif
}
