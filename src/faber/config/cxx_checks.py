#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .try_compile import TryCompile
from .. import types


class HasCXX11(TryCompile):

    src = r"""#if __cplusplus < 201103L
#error no C++11
#endif"""

    def __init__(self, features=(), if_=(), ifnot=()):
        TryCompile.__init__(self, 'has_cxx11', self.src, types.cxx, features,
                            if_, ifnot)


class HasCXX14(TryCompile):

    src = r"""#if __cplusplus < 201402L
#error no C++14
#endif"""

    def __init__(self, features=(), if_=(), ifnot=()):
        TryCompile.__init__(self, 'has_cxx14', self.src, types.cxx, features,
                            if_, ifnot)


class HasCXX17(TryCompile):

    src = r"""#if __cplusplus < 201500L
#error no C++17
#endif"""

    def __init__(self, features=(), if_=(), ifnot=()):
        TryCompile.__init__(self, 'has_cxx17', self.src, types.cxx, features,
                            if_, ifnot)


has_cxx11 = HasCXX11
has_cxx14 = HasCXX14
has_cxx17 = HasCXX17
