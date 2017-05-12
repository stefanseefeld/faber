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
#include "mem.h"
#include "jam.h"
#include "cwd.h"

#ifdef HAVE_PYTHON

PyObject *list_to_python(LIST *l)
{
  PyObject *result = PyList_New(0);
  LISTITER iter = list_begin(l);
  LISTITER const end = list_end(l);
  for (; iter != end; iter = list_next(iter))
  {
    PyObject *s = PYSTRING_FROM_STRING(object_str(list_item(iter)));
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
    result = list_push_back(result, object_new(PYSTRING_AS_STRING(v)));
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
  return list_new(object_new(PYSTRING_AS_STRING(a)));
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
    char *s = PYSTRING_AS_STRING(e);
    if (!s)
    {
      /* try to get the repr() on the object */
      PyObject *repr = PyObject_Repr(e);
      if (repr)
      {
	const char *str = PYSTRING_AS_STRING(repr);
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
  //inner->module = bindmodule(constant_python_interface);

  size = PyTuple_Size(args);
  for (i = 0 ; i < size; ++i)
  {
    PyObject * a = PyTuple_GetItem(args, i);
    if (a == Py_None)
      lol_add(inner->args, jam_list_from_none());
    else if (PYSTRING_CHECK(a))
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
  PyObject *result;
  TARGETS *targets;
  make_jam_arguments_from_python(inner, args);
  if (PyErr_Occurred()) return NULL;
  (LIST *) builtin_update_now(inner, 0);
  result = PyDict_New();
  targets = targetlist((TARGETS*)0, lol_get(inner->args, 0));
  while (targets)
  {
    PyDict_SetItemString(result, object_str(targets->target->name),
			 PyBool_FromLong(targets->target->status==0));
    targets = targets->next;
  }
  frame_free(inner);
  return result;
}

PyObject *bjam_set_target_variables(PyObject *self, PyObject *args)
{
  char const *name;
  int flag;
  PyObject *vars;
  TARGET *target;
  PyObject *key, *value;
  Py_ssize_t pos = 0;
  if (!PyArg_ParseTuple(args, "siO:set_target_variables", &name, &flag, &vars) ||
      !PyDict_Check(vars))
    return NULL;
  target = bindtarget(object_new(name));
  while (PyDict_Next(vars, &pos, &key, &value))
  {
    char const *k;
    char const *v;
    k = PYSTRING_AS_STRING(key);
    if (!k) return NULL;
    v = PYSTRING_AS_STRING(value);
    if (!v) return NULL;
    target->settings = addsettings(target->settings, flag,
				   object_new(k),
				   list_new(object_new(v)));
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
	return PYSTRING_FROM_STRING(object_str(list_front(s->value)));
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}

PyObject *bjam_get_target_variables(PyObject *self, PyObject *args)
{
  char const *name;
  TARGET *target;
  PyObject *vars;
  SETTINGS *s;
  if (!PyArg_ParseTuple(args, "s:get_target_variables", &name))
    return NULL;
  target = bindtarget(object_new(name));
  vars = PyDict_New();
  for (s = target->settings; s; s = s->next)
  {
    PyObject *name = PYSTRING_FROM_STRING(object_str(s->symbol));
    PyObject *pyvalues = PyList_New(0);
    LIST *values = s->value;
    LISTITER iter = list_begin(values);
    LISTITER const end = list_end(values);
    for (; iter != end; iter = list_next(iter))
      PyList_Append(pyvalues, PYSTRING_FROM_STRING(object_str(list_item(iter))));
    PyDict_SetItem(vars, name, pyvalues);
  }
  return vars;
}

PyObject *bjam_define_recipe(PyObject *self, PyObject *args)
{
  FRAME     inner[1];
  LIST     *result;
  OBJECT   *rulename;
  PyObject *args_proper;

  /* PyTuple_GetItem returns borrowed reference. */
  rulename = object_new(PYSTRING_AS_STRING(PyTuple_GetItem(args, 0)));

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
      PyList_SetItem(pyResult, i, PYSTRING_FROM_STRING(object_str(list_item(iter))));
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
  if (PYSTRING_CHECK(body))
    cmd = PYSTRING_AS_STRING(body);
  else if (!PyCallable_Check(body))
  {
    PyErr_SetString(PyExc_RuntimeError, "action is neither string nor callable");
    return NULL;
  }

  n = PyList_Size(bindlist_python);
  for (i = 0; i < n; ++i)
  {
    PyObject * next = PyList_GetItem(bindlist_python, i);
    if (!PYSTRING_CHECK(next))
    {
      PyErr_SetString(PyExc_RuntimeError, "bind list has non-string type");
      return NULL;
    }
    bindlist = list_push_back(bindlist, object_new(PYSTRING_AS_STRING(next)));
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
    PyList_SetItem(result, i, PYSTRING_FROM_STRING(object_str(list_item(iter))));

  return result;
}

static PyObject *report_callback;

PyObject *bjam_set_report_callback(PyObject *self, PyObject *args)
{
  PyObject *cb;
  if (!PyArg_ParseTuple(args, "O:set_report_callback", &cb) ||
      !PyCallable_Check(cb))
    return NULL;
  report_callback = cb;
  Py_INCREF(Py_None);
  return Py_None;
}

void report_plan(found, temp, updating, notfound, cantmake)
{
  if (report_callback)
    PyObject_CallFunction(report_callback, "ssiiiii", "__plan__", "",
			  found, temp, updating, notfound, cantmake);
}

void report_recipe(TARGET *target, char const *recipe, int status,
		   timing_info const *time, char const *cmd,
		   char const *_stdout, char const *_stderr)
{
  if (report_callback)
    PyObject_CallFunction(report_callback, "sssisss", "__recipe__", object_str(target->name),
			  recipe, status, /*time,*/ cmd, _stdout, _stderr);
}

void report_status(TARGET *target)
{
  if (report_callback)
    PyObject_CallFunction(report_callback, "ssis", "__status__", object_str(target->name),
			  target->status, target->failed);
}

void report_summary(failed, skipped, made)
{
  if (report_callback)
    PyObject_CallFunction(report_callback, "ssiii", "__summary__", "",
			  failed, skipped, made);
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
  TARGET *target = bindtarget(object_new(c->target));
  c->status = status;
  report_recipe(target, c->name, status, time, c->command, _stdout, _stderr);
}

static PyObject *bjam_run(PyObject *self, PyObject *args)
{
  struct exec_closure c;
  string str;

  if (!PyArg_ParseTuple(args, "sss", &c.name, &c.target, &c.command))
    return NULL;
  string_copy(&str, c.command);
  exec_cmd(&str, exec_callback, &c, NULL);
  exec_wait();
  string_free(&str);
  return PyLong_FromLong(c.status);
}

struct globs globs =
{
  0,   /* noexec */
  1,   /* jobs */
  0,   /* quitquick */
  0,   /* newestfirst */
  0,   /* pipes action stdout and stderr merged to action output */
  {0}, /* debug ... */
  0,   /* output commands, not run them */
  0,   /* action timeout */
  0    /* maximum buffer size zero is all output */
};

int anyhow = 0;

static PyObject *bjam_setopts(PyObject *self, PyObject *args)
{
  unsigned long log, noexec, jobs, timeout, force;
  unsigned long i;
  if (!PyArg_ParseTuple(args, "lllll:setopts", &log, &noexec, &jobs, &timeout, &force))
    return NULL;
  for (i = 0; i != DEBUG_MAX; ++i)
    globs.debug[i] = log & (1<<i) ? 1 : 0;
  globs.noexec = noexec;
  globs.jobs = jobs;
  globs.timeout = timeout;
  anyhow = force;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef bjam_methods[] =
{
  {"depends", bjam_depends, METH_VARARGS, "Declares a dependency."},
  {"update_now", bjam_update_now, METH_VARARGS, "Request an immediate update."},
  {"set_target_variables", bjam_set_target_variables, METH_VARARGS,
   "Set variables for the given target."},
  {"get_target_variables", bjam_get_target_variables, METH_VARARGS,
   "Get all variables for the given target."},
  {"get_target_variable", bjam_get_target_variable, METH_VARARGS,
   "Get a variable for the given target."},
  {"define_recipe", bjam_define_recipe, METH_VARARGS,
   "Call the specified bjam rule."},
  {"define_action", bjam_define_action, METH_VARARGS,
   "Defines a command line action."},
  {"variable", bjam_variable, METH_VARARGS,
   "Obtains a variable from bjam's global module."},
  {"run", bjam_run, METH_VARARGS,
   "Runs the given command and returns its exit status."},
  {"setopts", bjam_setopts, METH_VARARGS,
   "Set engine options."},
  {"set_report_callback", bjam_set_report_callback, METH_VARARGS,
   "Set report callback."},
  {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef =
{
  PyModuleDef_HEAD_INIT,
  "bjam",
  0, /* doc      */
  -1, //sizeof(struct module_state),
  bjam_methods,
  0, /* reload   */
  0, /* traverse */
  0, /* clear    */
  0  /* free     */
};

PyMODINIT_FUNC PyInit_bjam()
#else
void initbjam()
#endif
{
  PyObject *module;
  BJAM_MEM_INIT();
  constants_init();
  cwd_init();

#if PY_MAJOR_VERSION >= 3
  module = PyModule_Create(&moduledef);
  return module;
#else
  module = Py_InitModule("bjam", bjam_methods);
#endif
}

#endif  /* #ifdef HAVE_PYTHON */
