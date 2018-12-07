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
from ..artefact import artefact, delayed_property
from ..action import action
from ..rule import rule
from .. import platform
from ..tools.installer import installer
from .install import _installed
from os.path import dirname, basename, normpath, join


class library(composite):

    # This command assumes that source an target live in the same directory.
    symlink = action('symlink', 'cd `dirname $(>)` && ln -s `basename $(>)` `basename $(<)`')

    def __init__(self, *args, **kwds):
        version = kwds.pop('version', None)
        self.version = [str(v) for v in version] if version else None
        self._versioned = None  # to be set in _assemble
        composite.__init__(self, *args, type=types.lib, **kwds)

    def _assemble(self):
        # make sure all compiler features are instantiated
        from ..tools.compiler import compiler, link, soname  # noqa F401
        self.features.eval(update=False)
        if 'link' not in self.features:
            self.features += link('shared')
        self.type = types.dso if self.features.link == 'shared' else types.lib
        if (self.version and self.features.link == 'shared'):
            target = str(self.features.target.os) if 'target' in self.features else platform.os
            if target not in ('Windows'):
                base = basename(self._filename)
                # a versioned shared library allows multiple versions to coexist.
                # set SONAME if there is a bugfix version included
                if len(self.version) == 3:
                    self.features += soname('{}.{}.{}'.format(base, self.version[0], self.version[1]))
                a = artefact(base + '.' + '.'.join(self.version),
                             type=self.type, features=self.features, path_spec=self.path_spec, module=self.module)
                self._versioned = assembly.rule(a, self.sources, features=self.features, module=self.module)
                suffixes = list(reversed(['.'.join(self.version[:i]) for i in range(len(self.version))]))
                links = [join(a.relpath, '{}.{}'.format(base, suffixes[i])) for i in range(len(suffixes) - 1)]
                self.path_spec = a.path_spec
                self.features = a.features
                links.append(self)
                for l in links:
                    a = rule(library.symlink, l, a)
                return
        assembly.rule(self, self.sources, self.features, module=self.module)

    @property
    def libname(self):
        return basename(self.name)

    @property
    def _filename(self):
        dir, base = dirname(self.name), self.libname
        host = str(self.features.target.os) if 'target' in self.features else ''
        libname = join(dir, self.type.synthesize_name(base, host))
        return normpath(join(self.module.builddir, self.relpath, libname))

    @delayed_property
    def path(self):
        return dirname(self._filename)


class installed(_installed):
    # installing a library may require creating symbolic links, if the library is versioned

    @property
    def _filename(self):
        # use the name of the upstream artefact, combined with our relpath
        dir, base = dirname(self.a.name), self.a.libname
        host = str(self.a.features.target.os) if 'target' in self.a.features else ''
        libname = join(dir, self.a.type.synthesize_name(base, host))
        return normpath(join(self.relpath, libname))

    def _define_rule(self):
        if self.a._versioned:
            v = _installed(self.a._versioned, self.subdir, self.features)
            base = basename(self._filename)
            suffixes = list(reversed(['.'.join(self.a.version[:i]) for i in range(len(self.a.version))]))
            links = [join(self.relpath, '{}.{}'.format(base, suffixes[i])) for i in range(len(suffixes) - 1)]
            for l in links:
                v = rule(library.symlink, l, v)
            rule(library.symlink, self, v)
        else:
            rule(installer.install, self, self.a)
