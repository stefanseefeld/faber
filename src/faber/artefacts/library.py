#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, notfile
from .. import types
from .. import assembly
from os.path import dirname, relpath, join

class library(artefact):

    def expand(self):
        # make sure all compiler features are instantiated
        from ..tools.compiler import compiler, link

        if 'link' not in self.features:
            self.features += link('shared')

        # Set the proper artefact type, depending on the 'link' feature
        if self.features.link.value == 'shared':
            self.type = types.dso
        else:
            self.type = types.lib
        # Construct the proper build chain
        assembly.rule(self, self.sources, self.features)

    @property
    def filename(self):
        host = self.features.target.os.value
        libname = self.type.synthesize_name(self.name, host)
        return join(self.module.builddir, self.relpath, libname)

    @property
    def path(self):
        return relpath(dirname(self.filename) or '.', self.module.builddir)
