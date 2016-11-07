#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import compiler
from ..action import action
import logging

logger = logging.getLogger(__name__)

class cc(compiler.compiler):
    """C compiler base-class.
    As an abstract base-class it declares the actions all subclasses need to provide, without implementing them.

    Build scripts thus can reference `cxx.compile` et al., which the runtime will substitute by an appropriate
    compiler instance, if available (or fail to build)."""

    # Build object files from C source files.
    compile = action()
    # Build (static) library archives from object files.
    archive = action()
    # Link binaries (executables or shared libraries).
    link = action()

    @classmethod
    def instance(cls, fs=None):
        """Try to find a compiler instance for the current platform."""

        if cls is cc and not cls.instantiated(fs):
            # we can't instantiate this class directly, so try to find
            # a subclass...
            logger.debug('trying to instantiate a default C compiler')
            import sys
            if sys.platform == 'win32':
                compiler.try_instantiate('msvc', fs)
            compiler.try_instantiate('gcc', fs)
            compiler.try_instantiate('clang', fs)
            if not cls.instantiated(fs):
                raise RuntimeError('no C compiler found.')
        return super(cc, cls).instance(fs)
