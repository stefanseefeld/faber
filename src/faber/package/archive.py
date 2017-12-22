#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact
from ..rule import rule
from ..tools.archiver import archiver
from ..artefacts.install import installed, installation as I
from ..artefacts.install import prefix, stage
from . import info
from .manifest import manifest
from os.path import join


class archive(artefact):

    def __init__(self, pkg, installation=None, format=None):
        """Create an archive.
        If 'installation' is None, make a source archive,
        otherwise a binary archive."""

        meta = info(pkg)
        name = '{}-{}'.format(meta.doc.name, meta.doc.version)
        self.format = format
        artefact.__init__(self, name + '.src' if not installation else name)
        s = join(self.module.builddir, 'packaging', self.id)
        if installation:
            # clone the installation into our own staging area
            i = installation(stage(s))
        else:
            features = (prefix(name), stage(s))
            m = manifest(self.module.srcdir, meta.doc.source)
            i = I('i:sinst',
                  [installed(f, features=features) for f in m],
                  features=features)
        rule(archiver.archive(format), self, i)

    @property
    def _filename(self):
        return self.name + archiver.extension(self.format)
