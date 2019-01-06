#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from .feature import lazy_set
from .artefact import artefact
from .tool import tool
from .utils import add_metaclass
from .error import error_reporter
from os.path import join, exists
from os import makedirs
import logging

logger = logging.getLogger(__name__)


class proxy(object):
    """A module as seen when cross-referenced."""
    def __init__(self, module):
        self.__dict__.update(module._env)


class module_type(type):
    def __call__(cls, name, srcdir=None, builddir=None, process=True, **kwds):
        """Make sure to construct (and process) modules only once."""

        if name.startswith('.'):  # relative import
            if srcdir or builddir:
                raise ValueError('invalid arguments for relative imports')
            name, base = name[1:], module.current
            while name.startswith('.') and base:
                name, base = name[1:], base._parent
            if name.startswith('.'):
                raise ValueError('{} has no parent module'.format(base.name))
            name = '.'.join([base.name, name]) if base.name and name else \
                   name if name else base.name
            return proxy(cls._instances[name])
        elif name in cls._instances:
            return proxy(cls._instances[name])
        else:
            m = super(module_type, cls).__call__(name, srcdir, builddir, process, **kwds)
            return m


@add_metaclass(module_type)
class module(object):

    _instances = {}
    current = None

    @staticmethod
    def init(options, params):
        module.options = options
        module.params = params

    @staticmethod
    def finish():
        tool.finish()
        artefact.finish()
        module._instances.clear()

    def __init__(self, name, srcdir=None, builddir=None, process=True, **kwds):
        """Create a new module."""
        self.name = name
        if 'features' in kwds:
            self._features = kwds.pop('features').copy()
        else:
            self._features = lazy_set(module.params.copy())
        from . import builtin
        self._env = builtin.__dict__.copy()
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
        module._instances[name] = self
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
        with error_reporter(script), open(script) as f:
            exec(f.read(), self._env)
        self._env.setdefault('default', [])
        self.__dict__.update({k: v for k, v in self._env.items() if not k.startswith('_')})
        self.default = self._env['default']

        # make sure the builddir exists
        if not exists(self.builddir):
            makedirs(self.builddir)

        return self.default
