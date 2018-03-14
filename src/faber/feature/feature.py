#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import multi, path
from operator import iadd
from functools import partial
import os.path
import logging

logger = logging.getLogger('features')


class feature(object):

    _registry = dict()

    def _constr(self, v):
        from .value import value
        if type(v) is value:
            return v
        elif type(v) is tuple:
            return value(self, v, None)
        else:
            return value(self, v, None)

    @staticmethod
    def register(f):
        feature._registry[f.name] = f
        logger.info('defining feature "{}"'.format(f.name))

    @staticmethod
    def lookup(name):
        return feature._registry[name]

    def __new__(cls, *args, **kwds):
        # if any of the keyword arguments are features, construct a compound-feature
        composite = any([isinstance(a, feature) for a in kwds.values()])
        if composite:
            cls = composite_feature
        inst = object.__new__(cls)
        return inst

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
        sig = {str: None, tuple: None, int: None}
        for a in args:
            sig[type(a)] = a

        def pop(kwds, n, t, v):
            if n in kwds and type(kwds[n]) == t:
                sig[t] = kwds.pop(n)
            return sig[t] or v
        self.name = pop(kwds, 'name', str, '')
        self.values = pop(kwds, 'values', tuple, None)
        self.attributes = pop(kwds, 'attributes', int, 0)
        self.subfeatures = {}

        if self.name:
            feature.register(self)

    def __call__(self, *args, **kwds):
        """Instantiate a feature value."""
        from .value import value
        from ..delayed import delayed
        cond = kwds.pop('condition', None)
        # HACK: we need to define what argument types to allow
        if args and isinstance(args[0], delayed):
            # simply resubmit the value in the delayed's `eval`
            return args[0].apply(partial(self.__call__, **kwds))
        else:
            return value(self, self._validate(*args, **kwds), cond)

    def _join(self, values):
        # create a new value by joining the given arguments
        if self.attributes & multi:
            kwds = {'base': ''} if self.attributes & path else {}
            return self(*tuple([v for value in values for v in value._value]), **kwds)
        else:
            return values[0]  # only one is allowed. Assuming all are identical, return the first.

    def _cassign(self, op, v1, v2):

        from .value import value
        assert v1._type is self
        t2 = v2._type if isinstance(v2, value) else self
        if self is not t2:
            raise ValueError('cannot assign values from different features "{}" and "{}"'
                             .format(self.name, t2.name))
        v2 = v2._value if isinstance(v2, value) else v2
        if self.attributes & multi:
            if op is iadd:
                v1._value += v2
            else:
                v1._value += tuple(v for v in v2 if v not in v1._value)
        else:
            v1._value = v2
        return v1

    def _validate(self, *args, **kwds):
        def adjust_path(path, base):
            # At this point 'base' may only be None if there is no current module
            if base is None and not os.path.isabs(path):
                raise ValueError('relative path "{}" in feature "{}" may not be defined outside module'
                                 .format(path, self.name))
            else:
                return os.path.normpath(os.path.join(base or '', path))

        if self.attributes & multi:
            if self.values is not None:
                for a in args:
                    if a not in self.values:
                        raise ValueError('invalid value "{}" in feature "{}"'
                                         .format(a, self.name))
                value = args
            elif self.attributes & path:
                base = kwds.get('base', None)
                if base is None:
                    from ..module import module
                    base = module.current.srcdir if module.current else None
                value = [adjust_path(a, base) for a in args]
            else:
                value = args[:]
        elif len(args) > 1:
            raise ValueError('feature "{}" requires a single value'.format(self.name))
        elif args:
            if self.values is not None and args[0] not in self.values:
                raise ValueError('invalid value "{}" in feature "{}"'
                                 .format(args[0], self.name))
            elif self.attributes & path:
                base = kwds.get('base', None)
                if base is None:
                    from ..module import module
                    base = module.current.srcdir if module.current else None
                value = adjust_path(args[0], base)
            else:
                value = args[0]
        else:
            value = None
        return value


class composite_feature(feature):

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
        sig = {str: None, tuple: None, int: None}
        for a in args:
            sig[type(a)] = a

        def pop(kwds, n, t, v):
            if n in kwds and type(kwds[n]) == t:
                sig[t] = kwds.pop(n)
            return sig[t] or v
        self.name = pop(kwds, 'name', str, '')
        self.values = pop(kwds, 'values', tuple, None)
        self.attributes = pop(kwds, 'attributes', int, 0)
        self.subfeatures = {}
        # ...then handle the keyword arguments as subfeatures.
        for k, v in kwds.items():
            assert type(v) == feature
            v.name = k
            self.subfeatures[k] = v

        if self.name:
            feature.register(self)

    def __call__(self, *args, **kwds):
        """Instantiate a feature value."""
        from .value import value
        values = {k: None for k in self.subfeatures}
        values.update({k: self.subfeatures[k]._constr(kwds.get(k))
                       for k in self.subfeatures})
        return value(self, None, None, **values)

    def _join(self, values):
        # create a new value by joining the given arguments
        return self(**{k: self.subfeatures[k]._join([getattr(v, k) for v in values])
                       for k in self.subfeatures})

    def _cassign(self, op, v1, v2):

        from .value import value
        assert v1._type is self
        t2 = v2._type if isinstance(v2, value) else self
        if self is not t2:
            raise ValueError('cannot join values from different features "{}" and "{}"'
                             .format(self.name, t2.name))
        assert isinstance(v2, value)
        for k, f in self.subfeatures.items():
            f._cassign(op, getattr(v1, k), getattr(v2, k))
        return v1
