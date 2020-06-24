/*
 * Copyright (c) 2016 Stefan Seefeld
 * All rights reserved.
 *
 * This file is part of Faber. It is made available under the
 * Boost Software License, Version 1.0.
 * (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)
 */
#include "bjam.h"
#include "graph.h"
#include "make.h"
#include "variable.h"
#include "strings.h"
#include "rules.h"
#include "command.h"
#include "constants.h"
#include "compile.h"
#include "debug.h"
#include "output.h"
#include "execcmd.h"
#include "mem.h"
#include "jam.h"
#include "cwd.h"

static PyObject *DependencyError;

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

static LIST *list_from_sequence(PyObject *a)
{
  LIST *l = 0;

  int i = 0;
  int s = PySequence_Size(a);

  for (; i < s; ++i)
  {
    PyObject *e = PySequence_GetItem(a, i);
    char *s = (char *)PYSTRING_AS_STRING(e);
    if (!s)
    {
      PyErr_BadArgument();
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

static PyObject *bjam_define_target(PyObject *self, PyObject *args)
{
  char *name;
  int flags = 0;
  if (!PyArg_ParseTuple(args, "si:define_target", &name, &flags))
    return NULL;
  set_flags(list_new(object_new(name)), flags);
  Py_RETURN_NONE;
}

static PyObject *bjam_bind_filename(PyObject *self, PyObject *args)
{
  char *name;
  char *boundname;
  int exists;
  TARGET *target;
  if (!PyArg_ParseTuple(args, "ssi:bind_filename", &name, &boundname, &exists))
    return NULL;
  target = bindtarget(object_new(name));
  object_free(target->boundname);
  target->boundname = object_new(boundname);
  target->binding = exists ? T_BIND_EXISTS : T_BIND_MISSING;
  timestamp_from_path(&target->time, target->boundname);
  Py_RETURN_NONE;
}

static PyObject *bjam_add_dependency(PyObject *self, PyObject *args)
{
  char *target;
  PyObject *sources;
  if (!PyArg_ParseTuple(args, "sO:add_dependency", &target, &sources) ||
      !PySequence_Check(sources))
    return NULL;
  switch (add_dependency(target, list_from_sequence(sources)))
  {
    case -1:
      PyErr_SetString(DependencyError, "cannot add dependencies to a bound artefact");
      break;
    case -2:
      PyErr_SetString(DependencyError, "dependency cycle detected");
      break;
  }
  if (PyErr_Occurred()) return NULL;
  else Py_RETURN_NONE;
}

static PyObject *bjam_update(PyObject *self, PyObject *args)
{
  PyObject *targets;
  int status;
  if (!PyArg_ParseTuple(args, "O:update", &targets) ||
      !PySequence_Check(targets))
    return NULL;

  status = update_targets(list_from_sequence(targets));
  /* check for exceptions from any of the callbacks... */
  if (PyErr_Occurred()) return NULL;
  else return PyLong_FromLong(status);
}

static PyObject *bjam_print_dependency_graph(PyObject *self, PyObject *args)
{
  PyObject *targets;
  if (!PyArg_ParseTuple(args, "O:print_dependency_graph", &targets) ||
      !PySequence_Check(targets))
    return NULL;
  print_dependency_graph(list_from_sequence(targets));
  Py_RETURN_NONE;
}

static PyObject *bjam_get_target_variables(PyObject *self, PyObject *args)
{
  char const *name;
  TARGET *target;
  PyObject *vars;
  SETTINGS *s;
  if (!PyArg_ParseTuple(args, "s:get_target_variables", &name))
    return NULL;
  target = bindtarget(object_new(name));
  vars = PyDict_New();
  pushsettings(root_module(), target->settings);
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
  popsettings(root_module(), target->settings);
  return vars;
}

static PyObject *bjam_define_recipe(PyObject *self, PyObject *args)
{
  char *id;
  PyObject *targets;
  PyObject *sources;
  OBJECT   *rulename;
  FRAME     inner[1];
  LIST     *result;
  if (!PyArg_ParseTuple(args, "sOO:define_recipe", &id, &targets, &sources) ||
      !PySequence_Check(targets) ||
      !PySequence_Check(sources))
    return NULL;
  rulename = object_new(id);
  frame_init(inner);
  lol_add(inner->args, list_from_sequence(targets));
  lol_add(inner->args, list_from_sequence(sources));
  result = evaluate_rule(bindrule(rulename, inner->module), rulename, inner);
  list_free(result);
  frame_free(inner);
  object_free(rulename);
  Py_RETURN_NONE;
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
  PyObject *body;
  char     *cmd = NULL;
  PyObject *bindlist_python;
  LIST     *bindlist = L0;
  int       n;
  int       i;
  OBJECT   *name_str;
  FUNCTION *body_func;

  if (!PyArg_ParseTuple(args, "sOO!:define_action", &name, &body,
                        &PyList_Type, &bindlist_python))
    return NULL;
  if (PYSTRING_CHECK(body))
    cmd = (char *)PYSTRING_AS_STRING(body);
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
  new_rule_actions(bindmodule(0), name_str, body_func, bindlist, 0);
  function_free(body_func);
  object_free(name_str);
  Py_RETURN_NONE;
}

static PyObject *target_callback;
static PyObject *report_callback;

static void check_errors(void)
{
  if (PyErr_Occurred())
  {
    if (!PyErr_ExceptionMatches(PyExc_KeyboardInterrupt))
    {
      PyErr_Print();
      PyErr_Clear();
    }
  }
}

void bind_target(TARGET *target)
{
  PyObject *vars = 0;
  int flag = 0; /* set, rather than append */
  PyObject *key, *value;
  Py_ssize_t pos = 0;
  RULE *rule;
  rule = target->actions->action->rule;
  if (target_callback)
    vars = PyObject_CallFunction(target_callback, "ss",
				 object_str(rule->name),
				 object_str(target->name));
  if (!vars || !PyDict_Check(vars))
  {
    check_errors();
    return;
  }
  while (PyDict_Next(vars, &pos, &key, &value))
  {
    char const *k = PYSTRING_AS_STRING(key);
    char const *v = PYSTRING_AS_STRING(value);
    if (!k || !v) return;
    target->settings = addsettings(target->settings, flag,
				   object_new(k),
				   list_new(object_new(v)));
  }
}

void report_recipe(TARGET *target, char const *recipe, int status,
		   timing_info const *time, char const *cmd,
		   char const *_stdout, char const *_stderr)
{
  PyObject *o = 0;
  double t = timestamp_delta_seconds(&time->start, &time->end);
  o = PyObject_CallFunction(report_callback, "sssisdss", "__recipe__",
			    recipe, target->name, status, cmd, t,
			    _stdout ? _stdout : "", _stderr ? _stderr : "");
  if (!o)
    check_errors();
  else
    Py_DECREF(o);
}

void report_status(TARGET *target)
{
  PyObject *o = 0;
  o = PyObject_CallFunction(report_callback, "ssis", "__artefact__",
			    object_str(target->name),
			    target->status, target->failed);
  if (!o)
    check_errors();
  else
    Py_DECREF(o);
}

void report_summary(int failed, int skipped, int made)
{
  PyObject *o = 0;
  o = PyObject_CallFunction(report_callback, "siii", "__summary__",
			    failed, skipped, made);
  if (!o)
    check_errors();
  else
    Py_DECREF(o);
}

struct exec_closure
{
  int status;
  int done;
  string _stdout;
  string _stderr;
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
  c->done = 1;
  string_copy(&c->_stdout, _stdout ? _stdout : "");
  string_copy(&c->_stderr, _stderr ? _stderr : "");
}

static PyObject *bjam_run(PyObject *self, PyObject *args)
{
  char const *command;
  string str;
  struct exec_closure c;
  PyObject *result;

  if (!PyArg_ParseTuple(args, "s", &command))
    return NULL;
  string_copy(&str, command);
  c.done = 0;
  exec_cmd(&str, exec_callback, &c, NULL);
  while (!c.done)
    exec_wait();
  result = Py_BuildValue("lss", c.status, c._stdout.value, c._stderr.value);
  string_free(&c._stderr);
  string_free(&c._stdout);
  string_free(&str);
  return result;
}

struct globs globs =
{
  0,   /* noexec */
  0,   /* force */
  1,   /* jobs */
  0,   /* quitquick */
  0,   /* newestfirst */
  0,   /* pipes action stdout and stderr merged to action output */
  {0}, /* debug ... */
  0,   /* output commands, not run them */
  0,   /* action timeout */
  0    /* maximum buffer size zero is all output */
};

static PyObject *bjam_init(PyObject *self, PyObject *args)
{
  unsigned long log, noexec, jobs, timeout, force;
  unsigned long i;
  if (!PyArg_ParseTuple(args, "OOlllll:init",
			&target_callback, &report_callback,
			&log, &noexec, &jobs, &timeout, &force) ||
      !PyCallable_Check(target_callback) ||
      !PyCallable_Check(report_callback))
    return NULL;
  for (i = 0; i != DEBUG_MAX; ++i)
    globs.debug[i] = log & (1<<i) ? 1 : 0;
  globs.noexec = noexec;
  globs.force = force;
  globs.jobs = jobs;
  globs.timeout = timeout;
  BJAM_MEM_INIT();
  constants_init();
  Py_RETURN_NONE;
}

static PyObject *bjam_finish(PyObject *self, PyObject *args)
{
  clear_targets_to_update();
  rules_done();
  timestamp_done();
  function_done();
  exec_done();
  list_done();
  constants_done();
  object_done();
  BJAM_MEM_CLOSE();
  Py_RETURN_NONE;
}

static PyMethodDef bjam_methods[] =
{
  {"define_target", bjam_define_target, METH_VARARGS, "Define target."},
  {"bind_filename", bjam_bind_filename, METH_VARARGS, "Bind target name."},
  {"add_dependency", bjam_add_dependency, METH_VARARGS, "Declare a dependency."},
  {"update", bjam_update, METH_VARARGS, "Request an update."},
  {"print_dependency_graph", bjam_print_dependency_graph, METH_VARARGS, "Print dependency graph."},
  {"get_target_variables", bjam_get_target_variables, METH_VARARGS, "Get all variables for the given target."},
  {"define_recipe", bjam_define_recipe, METH_VARARGS, "Define a recipe."},
  {"define_action", bjam_define_action, METH_VARARGS, "Define an action."},
  {"run", bjam_run, METH_VARARGS, "Run the given action."},
  {"init", bjam_init, METH_VARARGS, "Initialize bjam."},
  {"finish", bjam_finish, METH_VARARGS, "Finalize bjam."},
  {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef =
{
  PyModuleDef_HEAD_INIT,
  "_bjam",
  0, /* doc      */
  -1, //sizeof(struct module_state),
  bjam_methods,
  0, /* reload   */
  0, /* traverse */
  0, /* clear    */
  0  /* free     */
};

PyMODINIT_FUNC PyInit__bjam(void)
#else
void init_bjam(void)
#endif
{
  PyObject *module;
  DependencyError = PyErr_NewException("_bjam.DependencyError", NULL, NULL);
  Py_INCREF(DependencyError);
#if PY_MAJOR_VERSION >= 3
  module = PyModule_Create(&moduledef);
  PyModule_AddObject(module, "DependencyError", DependencyError);
  return module;
#else
  module = Py_InitModule("_bjam", bjam_methods);
  PyModule_AddObject(module, "DependencyError", DependencyError);
#endif
}
