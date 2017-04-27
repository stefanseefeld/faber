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
  return PyString_FromString(greet());
}

static PyMethodDef methods[] =
{
  {"greet",  py_greet, METH_VARARGS, NULL},
  {NULL, NULL}      /* sentinel */
};

PyMODINIT_FUNC initgreet()
{
  Py_InitModule3("greet", methods, NULL);
}
