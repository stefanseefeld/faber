#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from . import platform
from os.path import split, splitext, join
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class typed_name(object):
    """adorn a (file-)name with a type"""

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self): return '<{} {}>'.format(self.type.name, self.name)


class type(object):

    # a dictionary mapping host names to extension->type mappings
    # As there are potentially multiple types using the same extension,
    # we only remember the first for reverse (extension->type) lookup.
    _register = defaultdict(dict)

    class maybemethod(object):
        """A descritor that allows a member to be accesses as either
        a method or a classmethod"""

        def __init__(self, f):
            self.f = f
        def __get__(self, obj, cls):
            return lambda *args: self.f(obj, *args)

    @staticmethod
    def discover(filename, host=''):
        """Discover a file's type from its file extension."""

        ext = splitext(filename)[1]
        ext = ext and ext[1:]
        if not ext: return None
        elif host in type._register and ext in type._register[host]:
            return type._register[host][ext]
        else:
            return type._register[''].get(ext)

    @maybemethod
    def typed_name(self, name, host=''):
        """Create a typed object. If this is called as a classmethod,
        look up the appropriate type from the file extension. Otherwise
        use `self` as type."""

        host = host or platform.os
        t = self or type.discover(name, host)
        if not t:
            raise RuntimeError('Cannot discover type for {} on {}'
                               .format(name, host))
        return typed_name(name, t)

    def synthesize_name(self, name, host=''):
        """Synthesize a new filename from an existing filename and the given type."""

        stem, ext = splitext(name)
        ext = ext and ext[1:]
        host = host or platform.os
        if self:
            t = self
        elif ext in type._register[host]:
            t = type._register[host][ext]
        else:
            t = type._register[''][ext]
        ext = t.ext(host)[0]
        return ext and stem + '.' + ext or stem

    def ext(self, host=''):

        return self._ext[host] if host in self._ext else self._ext['']

    def __init__(self, name, ext=None, **host_specific):
        """Define a (named) type with one or more filename extensions."""
        self.name = name
        self._ext = defaultdict(list)
        if ext is not None:
            host_specific[''] = ext
        for h in host_specific:
            for e in host_specific[h]:
                self._ext[h].append(e)
                if e not in type._register[h]:
                    type._register[h][e] = self
                    logger.debug('registering {} on {}'.format(name, h))
                else:
                    logger.debug('not registering {} on {}'.format(name, h))

    def __repr__(self):
        return '<type {}>'.format(self.name)


class library(type):
    """library names not only have a file extension, but may also be prefixed with 'lib'."""

    def synthesize_name(self, name, host=''):

        dir, base = split(name)
        host = host or platform.os
        base = type.synthesize_name(self, base, host)
        if host != 'Windows' or self.name == 'lib':
            # on Windows, only static libs get the 'lib' prefix
            base = 'lib' + base
        return dir and join(dir, base) or base


c = type('c', ['c'])
cxx = type('cxx', ['cc', 'cxx', 'cpp', 'C'])
obj = type('obj', ['o'], Windows=['obj'])
bin = type('bin', [''], Windows=['exe'])
lib = library('lib', ['a'], Windows=['lib'])
dso = library('dso', ['so'], Windows=['dll'], Darwin=['dylib'])
pyd = type('pyd', ['so'], Windows=['pyd'])
