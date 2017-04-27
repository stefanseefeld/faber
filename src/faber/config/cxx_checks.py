#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .try_compile import try_compile
from .. import types


class has_cxx11(try_compile):

    src = r"""#if __cplusplus < 201103L
#error no C++11
#endif"""

    def __init__(self, features=(), if_=(), ifnot=()):
        try_compile.__init__(self, 'has_cxx11', has_cxx11.src, types.cxx, features,
                             if_, ifnot)


class has_cxx14(try_compile):

    src = r"""#if __cplusplus < 201402L
#error no C++14
#endif"""

    def __init__(self, features=(), if_=(), ifnot=()):
        try_compile.__init__(self, 'has_cxx14', has_cxx14.src, types.cxx, features,
                             if_, ifnot)


class has_cxx17(try_compile):

    src = r"""#if __cplusplus < 201500L
#error no C++17
#endif"""

    def __init__(self, features=(), if_=(), ifnot=()):
        try_compile.__init__(self, 'has_cxx17', has_cxx17.src, types.cxx, features,
                             if_, ifnot)
