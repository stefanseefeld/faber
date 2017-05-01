/*
 * Copyright (c) 2016 Stefan Seefeld
 * All rights reserved.
 *
 * This file is part of Faber. It is made available under the
 * Boost Software License, Version 1.0.
 * (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)
 */
#ifndef engine_bjam_h_
#define engine_bjam_h_

#include "lists.h"

#if PY_MAJOR_VERSION >= 3
# define PYSTRING_CHECK PyUnicode_Check
# define PYSTRING_FROM_STRING PyUnicode_FromString
# define PYSTRING_AS_STRING PyUnicode_AsUTF8
#else
# define PYSTRING_CHECK PyString_Check
# define PYSTRING_FROM_STRING PyString_FromString
# define PYSTRING_AS_STRING PyString_AsString
#endif

PyObject *list_to_python(LIST * l);

#endif
