//
// Copyright (c) 2016 Stefan Seefeld
// All rights reserved.
//
// This file is part of Faber. It is made available under the
// Boost Software License, Version 1.0.
// (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

#ifndef greet_h_
#define greet_h_

#if (defined(_WIN32) || defined(__WIN32__) || defined(WIN32)) && !defined(__CYGWIN__)
#  if defined(GREET_EXPORTS)
#    define GREET_API __declspec(dllexport)
#  elif defined(GREET_IMPORTS)
#    define GREET_API __declspec(dllimport)
#  else
#    define GREET_API
#  endif
#else
#  define GREET_API
#endif

GREET_API void greet();

#endif
