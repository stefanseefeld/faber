#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..feature import Set
from ..artefacts.library import Library
from ..tools.compiler import link, ldflags
from ..tools.python import Python
from os.path import join, normpath


class Extension(Library):

    def __init__(self, *args, **kwds):
        Library.__init__(self, *args, **kwds)
        p = Python.instance(self.features)
        self.features |= Set(p.include, p.linkpath, link('shared'))
        # on windows we need to link with libpython
        self.features |= p.libs(condition=(Set.cc.name=='msvc')|(Set.cxx.name=='msvc'))
        # on darwin we need to add `-undefined dynamic_lookup` to prevent undefined symbols errors
        self.features |= ldflags('-undefined dynamic_lookup', condition=(Set.target.os.matches('darwin.*')))
        self._suffix = p.ext_suffix

    @property
    def _filename(self):
        libname = self.name + self._suffix
        return normpath(join(self.module.builddir, self.relpath, libname))
