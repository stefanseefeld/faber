#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import compiler
from ..action import action


class cc(compiler.compiler):
    """C compiler base-class.
    As an abstract base-class it declares the actions all subclasses need to provide, without implementing them.

    Build scripts thus can reference `cxx.compile` et al., which the runtime will substitute by an appropriate
    compiler instance, if available (or fail to build)."""

    # Build object files from C++ source files.
    compile = action()
    # Build (static) library archives from object files.
    archive = action()
    # Link binaries (executables or shared libraries).
    link = action()

