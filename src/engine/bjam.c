/*
 * Copyright (c) 2016 Stefan Seefeld
 * All rights reserved.
 *
 * This file is part of Faber. It is made available under the
 * Boost Software License, Version 1.0.
 * (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)
 */
#include "bjam.h"
#include "variable.h"
#include "strings.h"
#include "rules.h"
#include "constants.h"
#include "compile.h"
#include "debug.h"
#include "output.h"

PyObject *list_to_python(LIST *l)
{
  PyObject *result = PyList_New(0);
  LISTITER iter = list_begin(l);
  LISTITER const end = list_end(l);
  for (; iter != end; iter = list_next(iter))
  {
    PyObject *s = PyString_FromString(object_str(list_item(iter)));
    PyList_Append(result, s);
    Py_DECREF(s);
  }

  return result;
}

static LIST *jam_list_from_none()
{
  return list_new(0);
}

static LIST *jam_list_from_string(PyObject *a)
{
  return list_new(object_new(PyString_AsString(a)));
}

static LIST *jam_list_from_sequence(PyObject *a)
{
  LIST *l = 0;

  int i = 0;
  int s = PySequence_Size( a );

  for (; i < s; ++i)
  {
    /* PySequence_GetItem returns new reference. */
    PyObject *e = PySequence_GetItem(a, i);
    char *s = PyString_AsString(e);
    if (!s)
    {
      /* try to get the repr() on the object */
      PyObject *repr = PyObject_Repr(e);
      if (repr)
      {
        const char *str = PyString_AsString(repr);
        PyErr_Format(PyExc_TypeError, "expecting type <str> got %s", str);
      }
      /* fall back to a dumb error */
      else
      {
        PyErr_BadArgument();
      }
      Py_DECREF(e);
      return NULL;
    }
    else
    {
      l = list_push_back(l, object_new(s));
      Py_DECREF(e);
    }
  }

  return l;
}

static void make_jam_arguments_from_python(FRAME *inner, PyObject *args)
{
  int i;
  int size;

  /* Build up the list of arg lists. */
  frame_init(inner);
  inner->prev = 0;
  inner->prev_user = 0;
  inner->module = bindmodule(constant_python_interface);

  size = PyTuple_Size(args);
  for (i = 0 ; i < size; ++i)
  {
    PyObject * a = PyTuple_GetItem(args, i);
    if (a == Py_None)
      lol_add(inner->args, jam_list_from_none());
    else if (PyString_Check(a))
      lol_add(inner->args, jam_list_from_string(a));
    else if (PySequence_Check(a))
      lol_add(inner->args, jam_list_from_sequence(a));
  }
}

static PyObject *bjam_call(PyObject *self, PyObject *args)
{
  FRAME     inner[1];
  LIST     *result;
  OBJECT   *rulename;
  PyObject *args_proper;

  /* PyTuple_GetItem returns borrowed reference. */
  rulename = object_new(PyString_AsString(PyTuple_GetItem(args, 0)));

  args_proper = PyTuple_GetSlice(args, 1, PyTuple_Size(args));
  make_jam_arguments_from_python(inner, args_proper);
  if (PyErr_Occurred())
    return NULL;
  Py_DECREF(args_proper);

  result = evaluate_rule(bindrule(rulename, inner->module), rulename, inner);
  object_free(rulename);
  frame_free(inner);

  /* Convert the bjam list into a Python list result. */
  {
    PyObject *const pyResult = PyList_New(list_length(result));
    int i = 0;
    LISTITER iter = list_begin(result);
    LISTITER const end = list_end(result);
    for (; iter != end; iter = list_next(iter))
    {
      PyList_SetItem(pyResult, i, PyString_FromString(object_str(list_item(iter))));
      i += 1;
    }
    list_free(result);
    return pyResult;
  }
}


/*
 * Accepts four arguments:
 *  - an action name
 *  - an action body
 *  - a list of variable that will be bound inside the action
 *  - integer flags.
 *  Defines an action on bjam side.
 */
static PyObject *bjam_define_action(PyObject *self, PyObject *args)
{
  char     *name;
  char     *body;
  module_t *m;
  PyObject *bindlist_python;
  int       flags;
  LIST     *bindlist = L0;
  int       n;
  int       i;
  OBJECT   *name_str;
  FUNCTION *body_func;

  if (!PyArg_ParseTuple(args, "ssO!i:define_action", &name, &body,
                        &PyList_Type, &bindlist_python, &flags))
    return NULL;

  n = PyList_Size(bindlist_python);
  for (i = 0; i < n; ++i)
  {
    PyObject * next = PyList_GetItem(bindlist_python, i);
    if (!PyString_Check(next))
    {
      PyErr_SetString(PyExc_RuntimeError, "bind list has non-string type");
      return NULL;
    }
    bindlist = list_push_back(bindlist, object_new(PyString_AsString(next)));
  }

  name_str = object_new(name);
  body_func = function_compile_actions(body, constant_builtin, -1);
  new_rule_actions(root_module(), name_str, body_func, bindlist, flags);
  function_free(body_func);
  object_free(name_str);
  Py_INCREF(Py_None);
  return Py_None;
}


/*
 * Returns the value of a variable in root Jam module.
 */
static PyObject *bjam_variable(PyObject *self, PyObject *args)
{
  char     *name;
  LIST     *value;
  PyObject *result;
  int       i;
  OBJECT   *varname;
  LISTITER  iter;
  LISTITER  end;

  if (!PyArg_ParseTuple(args, "s", &name))
    return NULL;

  varname = object_new(name);
  value = var_get(root_module(), varname);
  object_free(varname);
  iter = list_begin(value);
  end = list_end(value);

  result = PyList_New(list_length(value));
  for (i = 0; iter != end; iter = list_next(iter), ++i)
    PyList_SetItem(result, i, PyString_FromString(object_str(list_item(iter))));

  return result;
}

static void bjam_init(int optimize)
{
  PROFILE_ENTER(MAIN_PYTHON);
  Py_OptimizeFlag = optimize;
  Py_Initialize();
  {
    static PyMethodDef BjamMethods[] =
    {
      {"call", bjam_call, METH_VARARGS,
       "Call the specified bjam rule."},
      {"define_action", bjam_define_action, METH_VARARGS,
       "Defines a command line action."},
      {"variable", bjam_variable, METH_VARARGS,
       "Obtains a variable from bjam's global module."},
      {NULL, NULL, 0, NULL}
    };

    Py_InitModule("bjam", BjamMethods);
  }
  PROFILE_EXIT(MAIN_PYTHON);
}
