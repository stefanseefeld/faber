#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import compiler
from ..feature import set
from ..action import action
import logging
import sys

logger = logging.getLogger('tools')


class cc(compiler.compiler):
    """C compiler base-class.
    As an abstract base-class it declares the actions all subclasses need to provide, without implementing them.

    Build scripts thus can reference `cxx.compile` et al., which the runtime will substitute by an appropriate
    compiler instance, if available (or fail to build)."""

    # Scan source files for header dependencies
    makedep = action()
    # Build object files from C source files.
    compile = action()
    # Build (static) library archives from object files.
    archive = action()
    # Link binaries (executables or shared libraries).
    link = action()

    @classmethod
    def instances(cls, fs=None):
        """Return all known C compiler instances for the current platform."""
        if cls is cc:
            if sys.platform == 'win32':
                from .msvc import msvc
                msvc.instances(fs)
        return super(cc, cls).instances(fs)

    @classmethod
    def instance(cls, fs=None):
        """Try to find a compiler instance for the current platform."""

        fs = set.instantiate(fs)
        if cls is cc and not cc.instantiated(fs):
            # we can't instantiate this class directly, so try to find
            # a subclass...
            logger.info('trying to instantiate a default C compiler')
            if sys.platform == 'win32':
                cc.try_instantiate('msvc', fs)
            cc.try_instantiate('gcc', fs)
            cc.try_instantiate('clang', fs)
            if not cc.instantiated(fs):
                msg = 'no C compiler found'
                msg += ' matching {}.'.format(fs.essentials()) if fs else '.'
                raise RuntimeError(msg)
        return super(cc, cls).instance(fs)
