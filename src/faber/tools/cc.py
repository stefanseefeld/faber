#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import compiler
from ..feature import Set
from ..action import Action
import logging
import sys

logger = logging.getLogger('tools')


class CC(compiler.Compiler):
    """C compiler base-class.
    As an abstract base-class it declares the actions all subclasses need to provide, without implementing them.

    Build scripts thus can reference `cxx.compile` et al., which the runtime will substitute by an appropriate
    compiler instance, if available (or fail to build)."""

    # Scan source files for header dependencies
    makedep = Action()
    # Build object files from C source files.
    compile = Action()
    # Build (static) library archives from object files.
    archive = Action()
    # Link binaries (executables or shared libraries).
    link = Action()

    @classmethod
    def instances(cls, fs=None):
        """Return all known C compiler instances for the current platform."""
        if cls is CC:
            if sys.platform == 'win32':
                from .msvc import msvc
                msvc.instances(fs)
        return super(CC, cls).instances(fs)

    @classmethod
    def instance(cls, fs=None):
        """Try to find a compiler instance for the current platform."""

        fs = Set.instantiate(fs)
        if cls is CC and not CC.instantiated(fs):
            # we can't instantiate this class directly, so try to find
            # a subclass...
            logger.info('trying to instantiate a default C compiler')
            if sys.platform == 'win32':
                CC.try_instantiate('msvc.MSVC', fs)
            CC.try_instantiate('gcc.GCC', fs)
            CC.try_instantiate('clang.CLang', fs)
            if not CC.instantiated(fs):
                msg = 'no C compiler found'
                msg += ' matching {}.'.format(fs.essentials()) if fs else '.'
                raise RuntimeError(msg)
        return super(CC, cls).instance(fs)
