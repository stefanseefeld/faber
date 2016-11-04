#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .feature import lazy_set
from .artefact import artefact
from os.path import join, exists
from os import makedirs
import logging

logger = logging.getLogger(__name__)


class module(object):

    current = None

    @staticmethod
    def init(goals, options, params):
        module.goals = goals
        module.options = options
        module.params = params

    @staticmethod
    def finish():
        artefact.finish()

    def __init__(self, name, srcdir=None, builddir=None, process=True, **kwds):
        """Create a new module."""
        self.name = name
        if 'features' in kwds:
            self._features = kwds.pop('features').copy()
        else:
            self._features = lazy_set(module.params.copy())
        from . import builtin
        self._env = builtin.__dict__.copy()
        self._env['goals'] = module.goals
        self._env['options'] = module.options
        self._env['features'] = self._features
        self._env.update(kwds)
        self._parent = module.current
        if self._parent:
            self.srcdir = join(self._parent.srcdir, srcdir or name)
            self.builddir = join(self._parent.builddir, builddir or name)
        else:
            self.srcdir = srcdir or name
            self.builddir = builddir or name
        if process:
            with self:
                self.process()

    def __enter__(self):
        if self._parent:
            if self._parent._env['__name__']:
                self._env['__name__'] = self._parent._env['__name__'] + '.' + self.name
            else:
                self._env['__name__'] = self.name
        else:
            self._env['__name__'] = self.name
        self._env['srcdir'] = self.srcdir
        self._env['builddir'] = self.builddir
        module.current = self
        return self

    def __exit__(self, type, value, traceback):
        module.current = self._parent

    @property
    def features(self):
        return self._features

    def qname(self, a):
        """Return the given name, prefixed by this module's name"""
        name = self._env['__name__']
        return '{}.{}'.format(name, a) if name else a

    def process(self):
        script = join(self.srcdir, 'fabscript')
        if not exists(script):
            raise ValueError('{}: no such file'.format(script))
        # Run the script in env
        with open(script) as f:
            exec(f.read(), self._env)
        self._env.setdefault('default', [])
        self.__dict__.update({k: v for k, v in self._env.items() if not k.startswith('_')})
        self.default = self._env['default']

        # make sure the builddir exists
        if not exists(self.builddir):
            makedirs(self.builddir)

        return self.default
