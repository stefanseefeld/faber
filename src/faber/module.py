#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import engine
from .feature import feature, lazy_set
from .artefact import artefact, notfile, always
from .tools.cleaner import cleaner
from os.path import join, exists, normpath
from os import makedirs
import string
import logging
import os

logger = logging.getLogger(__name__)

class ScriptError(ValueError):

    def __init__(self, script, msg):
        ValueError.__init__(self, '{}: {}'.format(script, msg))

class module(object):

    current = None

    @staticmethod
    def init(goals, config, params):
        module.goals = goals
        module.config = config
        module.params = params
        module._parents = []
        module._clean = set()
        module._intermediate = set()

    @staticmethod
    def finish():
        # Remove intermediate files
        for t in module._intermediate:
            if os.path.exists(t):
                os.remove(t)

    def __init__(self, name, srcdir=None, builddir=None, process=True):
        """Create a new module."""
        self.name = name
        from . import builtin
        self._env = builtin.__dict__.copy()
        self._env['goals'] = module.goals
        self._features = lazy_set(module.params.copy())
        parent = module.current
        if parent:
            self.srcdir = join(parent.srcdir, srcdir or name)
            self.builddir = join(parent.builddir, builddir or name)
        else:
            self.srcdir = srcdir or name
            self.builddir = builddir or name
        if process:
            with self:
                self.process()

    def __enter__(self):
        parent = module.current
        module._parents.append(parent)
        if parent:
            if parent._env['__name__']:
                self._env['__name__'] = parent._env['__name__'] + '.' + self.name
            else:
                self._env['__name__'] = self.name
        else:
            self._env['__name__'] = self.name
        self._env['features'] = self._features
        module.current = self
        if not module._parents[-1]:
            # do this once, after the root module has been created
            from . import builtin
            builtin.clean = self._env['clean'] = artefact('.clean', attrs=notfile|always)
        else:
            self._env['clean'] = module._parents[-1]._env['clean']
        return self

    def __exit__(self, type, value, traceback):
        parent = module._parents.pop()
        if not module._parents:
            rm = cleaner.rm
            rm.define(self)
            rm.submit([self._env['clean']], module._clean, self)
        module.current = parent

    @property
    def features(self):
        return self._features

    def qname(self, a = '', full=True):
        # qualified name (full or relative)
        name = full and self._env['__name__'] or self.name
        if name and a:
            return name + '.' + a
        elif a:
            return a
        else:
            return name

    def qsource(self, source):
        # qualified source name

        # sources are looked up relative to the builddir,
        # unless they already exist in the srcdir
        if isinstance(source, artefact):
            return source
        elif exists(join(self.srcdir, source)):
            return join(self.srcdir, source)
        else:
            return join(self.builddir, source)

    def process(self):
        script = join(self.srcdir, 'fabscript')
        if not exists(script):
            raise ScriptError(script, ' no such file')
        # Run the script in env
        execfile(script, self._env)
        self._env.setdefault('default', [])
        # FIXME: find a cleaner way to do this !
        self.__dict__.update({k:v for k,v in self._env.items() if isinstance(v, artefact)})
        self.default = self._env['default']
        self.default = self.default if type(self.default) is list else [self.default]

        # make sure the builddir exists
        if not exists(self.builddir):
            makedirs(self.builddir)

        return self.default
