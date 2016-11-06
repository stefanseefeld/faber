#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import multi, path, incidental
from operator import iadd, ior
import os.path
import logging

logger = logging.getLogger(__name__)

class feature(object):

    _registry = dict()

    @staticmethod
    def _constr(v):
        return v if type(v) is tuple else (v,)

    @staticmethod
    def register(f):
        feature._registry[f.name] = f
        logger.debug('defining feature "{}"'.format(f.name))

    @staticmethod
    def lookup(name):
        return feature._registry[name]
    
    def __init__(self, *args, **kwds):
        """Create a feature. The constructor takes up to three non-keyword
        arguments (in arbitrary order):

         * a name (string, defaults to '')
         * a set of valid values (set, defaults to None)
         * attributes (int, defaults to 0)

        Alternatively, a composite feature may be constructed passing sub-features
        as keyword arguments:

        feature(name, <name>=feature(...), ...)"""

        # First identify and assign the non-keyword arguments,...
        sig = {str:None, tuple:None, int:None}
        for a in args: sig[type(a)] = a
        def pop(kwds, n, t, v):
            if n in kwds and type(kwds[n]) == t:
                sig[t] = kwds.pop(n)
            return sig[t] or v
        self.name = pop(kwds, 'name', str, '')
        self.values = pop(kwds, 'values', tuple, None)
        self.attributes = pop(kwds, 'attributes', int, 0)
        self.subfeatures = {}
        # ...then handle the keyword arguments as subfeatures.
        for k,v in kwds.items():
            assert type(v) == feature
            v.name = k
            self.subfeatures[k] = v

        if self.name:
            feature.register(self)
        
    def __call__(self, *args, **kwds):
        """Instantiate a feature value."""

        from .value import value
        if self.subfeatures: # this is a composite value
            values = {k:None for k in self.subfeatures}
            values.update({k:self.subfeatures[k]._validate(*feature._constr(v))
                           for k,v in kwds.items()})
            return value(self, None, None, **values)
        else:
            cond = kwds.get('condition', None)
            return value(self, self._validate(*args), cond)

    def _cassign(self, op, v1, v2):

        if self is not v1._type or self is not v2._type:
            raise ValueError('cannot join values from different features "{}" and "{}"'
                             .format(v1._type.name, v2._type.name))
        elif self.subfeatures:
            for k,f in self.subfeatures.items():
                f._cassign(op, getattr(v1, k), getattr(v2, k))
        elif self.attributes & multi:
            if op is iadd:
                v1.value += v2.value
            else: # ior is synonym for 'add once'
                v1.value += tuple(v for v in v2.value if v not in v1.value)
        elif v1.value is None:
            v1.value = v2.value
        elif v2.value and v1.value != v2.value:
            raise ValueError('cannot join incompatible values "{}" and "{}" in feature "{}"'
                             .format(v1.value, v2.value, v1._type.name))
        else:
            pass # do nothing
        return v1
    
    def _validate(self, *args):

        def adjust_path(path, base):
            if not base and not os.path.isabs(path):
                raise ValueError('relative path "{}" in feature "{}" may not be defined outside module'
                                 .format(path, self.name))
            else:
                return os.path.normpath(os.path.join(base, path))

        if self.attributes & multi:
            if self.values is not None:
                for a in args:
                    if a not in self.values:
                        raise ValueError('invalid value "{}" in feature "{}"'
                                         .format(a, self.name))
            elif self.attributes & path:
                from ..module import module
                base = module.current.srcdir if module.current else ''
                value = [adjust_path(a, base) for a in args]
            else:
                value = args
        elif len(args) > 1:
            raise ValueError('feature "{}" requires a single value'.format(self.name))
        elif args:
            if self.values is not None and args[0] not in self.values:
                raise ValueError('invalid value "{}" in feature "{}"'
                                 .format(args[0], self.name))
            elif self.attributes & path:
                from ..module import module
                base = module.current.srcdir if module.current else ''
                value = [adjust_path(a, base) for a in args]
            else:
                value = args[0]
        else:
            value = None
        return value
