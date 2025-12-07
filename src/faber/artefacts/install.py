#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import Artefact, Source, notfile
from ..tools.installer import Installer, prefix, stage  # noqa F401
from ..rule import rule, alias
from .. import platform
from os.path import normpath, join, splitdrive
import os

if platform.os == 'Windows':
    default_prefix = prefix(os.environ['ProgramFiles'])
else:
    default_prefix = prefix('/usr/local')


class Installed(Artefact):
    """An installed artefact has a filename outside the build directory."""

    def __init__(self, a, subdir, features):
        """Create an installed artefact."""
        a = Source.instantiate(a)
        self.a = a
        self.subdir = subdir or ''
        Artefact.__init__(self, a.name, type=a.type, module=a.module, features=features)
        # set a default installation prefix
        if 'prefix' not in self.features:
            self.features += default_prefix
        self._define_rule()

    def __call__(self, features):
        clone = Artefact.__call__(self, features)
        clone._define_rule()
        return clone

    @property
    def relpath(self):
        # combine stage with prefix to form the actual path
        stage = str(self.features.get('stage', ''))  # noqa F811
        prefix = str(self.features.get('prefix', ''))  # noqa F811
        if stage:
            if stage[-1] != '/':
                stage += '/'
            prefix = splitdrive(prefix)[1]
        return join(stage + prefix, self.subdir)

    @property
    def _filename(self):
        # use the name of the upstream artefact, combined with
        # our relpath
        return normpath(join(self.relpath, self.a.name))

    def _define_rule(self):
        rule(Installer.install, self, self.a)


def installed(artefact, subdir=None, features=()):
    """Make an installed copy of the given artefact."""

    from . import library
    # TODO: Find an extensible mechanism to make this polymorphic
    if isinstance(artefact, library.Library):
        return library.InstalledLibrary(artefact, subdir, features)
    else:
        return Installed(artefact, subdir, features)


class Manifest(Artefact):

    def create(t, sources):
        stage = str(t[0].features.stage) if 'stage' in t[0].features else ''  # noqa F811
        files = [s._filename[len(stage):] for s in sources
                 if s._filename.startswith(stage)]
        with open(t[0]._filename, 'w') as manifest:
            for f in files:
                manifest.write(f + '\n')
    create.__name__ = 'manifest.create'
    create = staticmethod(create)

    def __init__(self, name, installed, features=()):
        # HACK: this works around a Windows filesystem limitation
        # TODO: Find a real solution for this, including establishing
        #       and documenting artefact naming requirements, etc.
        name = name.replace(':', '_')
        Artefact.__init__(self, name, features=features)
        rule(Manifest.create, self, installed)


class Installation(Artefact):

    def __init__(self, name, installed, features=()):
        Artefact.__init__(self, name, attrs=notfile, features=features)
        self.installed = installed
        self.manifest = Manifest(self.name + '.manifest', installed, features=features)
        alias(self, self.manifest)

    def __call__(self, features):
        clone = Artefact.__call__(self, features)
        clone.installed = [i(features) for i in self.installed]
        clone.manifest = Manifest(self.name + '.manifest', clone.installed, features=features)
        alias(clone, clone.manifest)
        return clone
