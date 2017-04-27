//
// Copyright (c) 2016 Stefan Seefeld
// All rights reserved.
//
// This file is part of Faber. It is made available under the
// Boost Software License, Version 1.0.
// (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

#include <iostream>

#ifdef HAS_CXX11
# define cxx11 "defined"
#else
# define cxx11 "undefined"
#endif
#ifdef HAS_CXX14
# define cxx14 "defined"
#else
# define cxx14 "undefined"
#endif
#ifdef HAS_CXX17
# define cxx17 "defined"
#else
# define cxx17 "undefined"
#endif


int main()
{
    std::cout << "HAS_PYTHON=" << HAS_PYTHON << '\n'
	      << "HAS_CXX11 " << cxx11 << '\n'
	      << "HAS_CXX14 " << cxx14 << '\n'
	      << "HAS_CXX17 " << cxx17 << '\n'
	      << std::endl;
}
