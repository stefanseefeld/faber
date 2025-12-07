#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import Artefact
from ..rule import rule
from ..tools.archiver import Archiver
from ..artefacts.install import installed, Installation as I
from ..artefacts.install import prefix, stage
from . import Info
from .manifest import Manifest
from os.path import join


class Archive(Artefact):

    def __init__(self, pkg, installation=None, format=None):
        """Create an archive.
        If 'installation' is None, make a source archive,
        otherwise a binary archive."""

        meta = Info(pkg)
        name = '{}-{}'.format(meta.doc.name, meta.doc.version)
        self.format = format
        Artefact.__init__(self, name + '.src' if not installation else name)
        s = join(self.module.builddir, 'packaging', self.id)
        if installation:
            # clone the installation into our own staging area
            i = installation(stage(s))
        else:
            features = (prefix(name), stage(s))
            m = Manifest(self.module.srcdir, meta.doc.source)
            i = I('i:sinst',
                  [installed(f, features=features) for f in m],
                  features=features)
        rule(Archiver.archive(format), self, i)

    @property
    def _filename(self):
        return self.name + Archiver.extension(self.format)
