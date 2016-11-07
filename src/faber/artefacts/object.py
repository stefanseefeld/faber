#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .. import types
from . import composite
from os.path import join, normpath


class object(composite):
    """Compile an object from one or more source files."""

    def __init__(self, *args, **kwds):
        composite.__init__(self, *args, type=types.obj, **kwds)

    @property
    def _filename(self):
        host = str(self.features.target.os) if 'target' in self.features else ''
        name = self.type.synthesize_name(self.name, host)
        return normpath(join(self.module.builddir, self.relpath, name))
