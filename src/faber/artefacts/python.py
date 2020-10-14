#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..feature import set
from ..artefacts.library import library
from ..tools.compiler import link
from ..tools.python import python
from os.path import join, normpath


class extension(library):

    def __init__(self, *args, **kwds):
        library.__init__(self, *args, **kwds)
        p = python.instance(self.features)
        self.features |= set(p.include, p.linkpath, link('shared'))
        self.features |= p.libs(condition=(set.cc.name=='msvc')|(set.cxx.name=='msvc'))
        self._suffix = p.ext_suffix

    @property
    def _filename(self):
        libname = self.name + self._suffix
        return normpath(join(self.module.builddir, self.relpath, libname))
