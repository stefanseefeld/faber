#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact
from ..rule import rule
from os.path import normpath, join, sep


class dir(artefact):

    def __init__(self, recipe, name, sources, *args, **kwds):
        dependencies = kwds.pop('dependencies', [])
        artefact.__init__(self, name, *args, **kwds)
        rule(recipe, self, sources, dependencies=dependencies)

    @property
    def _filename(self):
        # make sure this is recognized by tools (e.g. xsltproc) as a directory,
        # by explicitly appending a '/'
        return normpath(join(self.module.builddir, self.relpath, self.name)) + sep
