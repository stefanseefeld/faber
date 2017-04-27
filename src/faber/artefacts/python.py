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
from os.path import join

class extension(library):

    def expand(self):

        p = python.instance(self.features)
        self.features |= set(p.include, p.linkpath, p.libs, link('shared'))
        library.expand(self)
        
    @property
    def filename(self):
        host = self.features.target.arch.value
        # FIXME: This assumes that DSOs use the 'lib' prefix on all platforms.
        libname = self.type.synthesize_name(self.name, host)[3:]
        return join(self.module.builddir, self.relpath, libname)        
