#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .. import types
from .. import assembly
from . import composite
from ..artefact import delayed_property
from os.path import dirname, normpath, join, split


class library(composite):

    def __init__(self, *args, **kwds):
        composite.__init__(self, *args, type=types.lib, **kwds)

    def _assemble(self):
        # make sure all compiler features are instantiated
        from ..tools.compiler import compiler, link  # noqa F401
        self.features.eval()
        if 'link' not in self.features:
            self.features += link('shared')
        self.type = types.dso if self.features.link == 'shared' else types.lib
        assembly.rule(self, self.sources, self.features, module=self.module)

    @property
    def _filename(self):
        dir, base = split(self.name)
        host = str(self.features.target.os) if 'target' in self.features else ''
        libname = join(dir, self.type.synthesize_name(base, host))
        return normpath(join(self.module.builddir, self.relpath, libname))

    @delayed_property
    def path(self):
        return dirname(self._filename)
