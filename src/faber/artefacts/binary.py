#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact
from .. import types
from .. import assembly
from .library import library
from os.path import join

class binary(artefact):
    """Build a binary from one or more source files."""

    def expand(self):
        self.type = types.bin
        assembly.rule(self, self.sources, self.features)

    @property
    def filename(self):
        host = self.features.target.os.value
        name = self.type.synthesize_name(self.name, host)
        return join(self.module.builddir, self.relpath, name)
