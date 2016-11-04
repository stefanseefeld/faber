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
#include "execcmd.h"
#include "builtins.h"

#ifdef HAVE_PYTHON

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

LIST *list_from_python(PyObject *l)
{
  LIST * result = L0;

  Py_ssize_t n = PySequence_Size(l);
  Py_ssize_t i;
  for (i = 0; i < n; ++i)
  {
    PyObject *v = PySequence_GetItem(l, i);
    result = list_push_back(result, object_new(PyString_AsString(v)));
    Py_DECREF(v);
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

static module_t *module(char const *name)
{
  OBJECT *o = name && name[0] ? object_new(name) : 0;
  module_t *m = bindmodule(o);
  if (o) object_free(o);
  return m;
}

PyObject *bjam_depends(PyObject *self, PyObject *args)
{
  FRAME inner[1];
  make_jam_arguments_from_python(inner, args);
  if (PyErr_Occurred()) return NULL;
  builtin_depends(inner, 0);
  frame_free(inner);
  Py_INCREF(Py_None);
  return Py_None;
}

PyObject *bjam_update_now(PyObject *self, PyObject *args)
{
  FRAME inner[1];
  LIST *result;
  make_jam_arguments_from_python(inner, args);
  if (PyErr_Occurred()) return NULL;
  result = builtin_update_now(inner, 0);
  frame_free(inner);
  if (!result)
  {
    Py_INCREF(Py_False);
    return Py_False;
  }
  else
  {
    Py_INCREF(Py_True);
    return Py_True;
  }
}

PyObject *bjam_set_target_variables(PyObject *self, PyObject *args, PyObject *kwds)
{
  char const *name;
  int flag;
  if (!PyArg_ParseTuple(args, "si:set_target_variables", &name, &flag))
    return NULL;
  TARGET *target = bindtarget(object_new(name));
  if (kwds)
  {
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(kwds, &pos, &key, &value))
    {
      char const *k = PyString_AsString(key);
      if (!k) return NULL;
      char const *v = PyString_AsString(value);
      if (!v) return NULL;
      target->settings = addsettings(target->settings, flag,
				     object_new(k),
				     list_new(object_new(v)));
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

PyObject *bjam_get_target_variable(PyObject *self, PyObject *args)
{
  char const *name;
  char const *varname;
  TARGET *target;
  OBJECT *var;
  SETTINGS *s;
  if (!PyArg_ParseTuple(args, "ss:get_target_variable", &name, &varname))
    return NULL;
  target = bindtarget(object_new(name));
  var = object_new(varname);
  for (s = target->settings; s; s = s->next)
  {
    if (object_equal(s->symbol, var))
    {
      if (list_empty(s->value))
      {
	Py_INCREF(Py_None);
	return Py_None;
      }
      else
	return PyString_FromString(object_str(list_front(s->value)));
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

PyObject *bjam_get_target_variables(PyObject *self, PyObject *args)
{
  char const *name;
  TARGET *target;
  OBJECT *var;
  SETTINGS *s;
  if (!PyArg_ParseTuple(args, "s:get_target_variables", &name))
    return NULL;
  target = bindtarget(object_new(name));
  PyObject *vars = PyDict_New();
  for (s = target->settings; s; s = s->next)
  {
    PyObject *name = PyString_FromString(object_str(s->symbol));
    PyObject *pyvalues = PyList_New(0);
    LIST *values = s->value;
    LISTITER iter = list_begin(values);
    LISTITER const end = list_end(values);
    for (; iter != end; iter = list_next(iter))
      PyList_Append(pyvalues, PyString_FromString(object_str(list_item(iter))));
    PyDict_SetItem(vars, name, pyvalues);
  }
  return vars;
}

PyObject *bjam_call(PyObject *self, PyObject *args, PyObject *kwds)
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

  /* update any target attributes if specified */
  PyObject *attrs = kwds ? PyDict_GetItemString(kwds, "attrs") : 0;
  if (attrs)
  {
    long value = PyInt_AsLong(attrs);
    if (value == -1 && PyErr_Occurred())
    {
      Py_DECREF(attrs);
      return NULL;
    }
    else
      Py_DECREF(attrs);
    if (value)
    {
      LIST *targets = lol_get(inner->args, 0);
      LISTITER iter = list_begin(targets);
      LISTITER const end = list_end(targets);
      for (; iter != end; iter = list_next(iter))
	bindtarget(list_item(iter))->flags |= value;
    }
  }

  /* update any target variables if specified */
  PyObject *vars = kwds ? PyDict_GetItemString(kwds, "vars") : 0;
  if (vars)
  {
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(vars, &pos, &key, &value))
    {
      char const *k = PyString_AsString(key);
      if (!k) return NULL;
      char const *v = PyString_AsString(value);
      if (!v) return NULL;
      LIST *targets = lol_get(inner->args, 0);
      LISTITER iter = list_begin(targets);
      LISTITER const end = list_end(targets);
      for (; iter != end; iter = list_next(iter))
      {
	TARGET *t = bindtarget(list_item(iter));
	t->settings = addsettings(t->settings, VAR_SET,
				  object_new(k),
				  list_new(object_new(v)));
      }
    }
  }

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
PyObject *bjam_define_action(PyObject *self, PyObject *args)
{
  char     *mod;
  char     *name;
  PyObject *body;
  char     *cmd = NULL;
  PyObject *bindlist_python;
  int       flags;
  LIST     *bindlist = L0;
  int       n;
  int       i;
  OBJECT   *name_str;
  FUNCTION *body_func;

  if (!PyArg_ParseTuple(args, "zsOO!i:define_action", &mod, &name, &body,
                        &PyList_Type, &bindlist_python, &flags))
    return NULL;
  if (PyString_Check(body))
    cmd = PyString_AsString(body);
  else if (!PyCallable_Check(body))
  {
    PyErr_SetString(PyExc_RuntimeError, "action is neither string nor callable");
    return NULL;
  }

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
  if (cmd)
    body_func = function_compile_actions(cmd, constant_builtin, -1);
  else
    body_func = function_python(body, 0);
  new_rule_actions(module(mod), name_str, body_func, bindlist, flags);
  function_free(body_func);
  object_free(name_str);
  Py_INCREF(Py_None);
  return Py_None;
}


/*
 * Returns the value of a variable in root Jam module.
 */
PyObject *bjam_variable(PyObject *self, PyObject *args)
{
  char     *mod;
  char     *name;
  LIST     *value;
  PyObject *result;
  int       i;
  OBJECT   *varname;
  LISTITER  iter;
  LISTITER  end;

  if (!PyArg_ParseTuple(args, "zs", &mod, &name))
    return NULL;

  varname = object_new(name);
  value = var_get(module(mod), varname);
  object_free(varname);
  iter = list_begin(value);
  end = list_end(value);

  result = PyList_New(list_length(value));
  for (i = 0; iter != end; iter = list_next(iter), ++i)
    PyList_SetItem(result, i, PyString_FromString(object_str(list_item(iter))));

  return result;
}

struct exec_closure
{
  char const *name;
  char const *target;
  char const *command;
  int status;
};

static void exec_callback(void * const X,
			  int status,
			  timing_info const *time,
			  char const *_stdout,
			  char const *_stderr,
			  int reason)
{
  struct exec_closure *c = (struct exec_closure *)X;
  c->status = status;
  out_action(c->name, c->target, c->command, _stdout, _stderr, reason);
}

static PyObject *bjam_run(PyObject *self, PyObject *args)
{
  struct exec_closure c;
  PyObject *py_result;
  string str;

  if (!PyArg_ParseTuple(args, "sss", &c.name, &c.target, &c.command))
    return NULL;
  string_copy(&str, c.command);
  exec_cmd(&str, exec_callback, &c, NULL);
  exec_wait();
  string_free(&str);
  return PyInt_FromLong(c.status);
}

void bjam_init(int optimize)
{
  PROFILE_ENTER(MAIN_PYTHON);
  Py_OptimizeFlag = optimize;
  Py_Initialize();
  {
    static PyMethodDef BjamMethods[] =
    {
      {"depends", bjam_depends, METH_VARARGS, "Declares a dependency."},
      {"update_now", bjam_update_now, METH_VARARGS, "Request an immediate update."},
      {"set_target_variables", (PyCFunction)bjam_set_target_variables, METH_KEYWORDS,
       "Set variables for the given target."},
      {"get_target_variables", bjam_get_target_variables, METH_VARARGS,
       "Get all variables for the given target."},
      {"get_target_variable", bjam_get_target_variable, METH_VARARGS,
       "Get a variable for the given target."},
      {"call", (PyCFunction)bjam_call, METH_KEYWORDS,
       "Call the specified bjam rule."},
      {"define_action", bjam_define_action, METH_VARARGS,
       "Defines a command line action."},
      {"variable", bjam_variable, METH_VARARGS,
       "Obtains a variable from bjam's global module."},
      {"run", bjam_run, METH_VARARGS,
       "Runs the given command and returns its exit status."},
      {NULL, NULL, 0, NULL}
    };

    Py_InitModule("bjam", BjamMethods);
  }
  PROFILE_EXIT(MAIN_PYTHON);
}

#endif  /* #ifdef HAVE_PYTHON */
