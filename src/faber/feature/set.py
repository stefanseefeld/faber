#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..utils import add_metaclass
from .feature import feature, incidental
from .value import value
from .condition import value as expr
from operator import iadd, ior
from collections import defaultdict
from functools import reduce
import copy

class feature_type(type):

    def __getattr__(cls, name):
        # Allow the construction of expressions to support conditional values
        return expr(name)

@add_metaclass(feature_type)
class set(object):

    def __init__(self, *args):

        # if only one argument is provided and it's not a feature-value,
        # assume it's a container of values.
        if len(args) == 1 and type(args[0]) != value:
            args = args[0]

        self._features = {}
        self._lazy = []
        reduce(lambda s,a:ior(s, a), args, self)

    def keys(self):
        return self._features.keys()

    def values(self):
        return self._features.values()

    def items(self):
        return self._features.items()
    
    def copy(self):
        """Create a copy of this set."""
        return set(*[copy.copy(v)
                     for v in list(self._features.values()) + self._lazy])

    def essentials(self):
        """Create a copy of this set containing only the essential
        (i.e., non-incidental) features."""
        return set(*[copy.copy(v)
                     for v in list(self._features.values()) + self._lazy
                     if not v._type.attributes & incidental])
    
    def update(self, other):
        """Add new features from `other`, replacing existing ones."""
        if type(other) == value:
            if other._condition is None:
                self._features[other._type.name] = other
            else:
                self._lazy.append(other)
        else:
            for k,v in other._features.items():
                self._features[k] = v
            self._lazy += other._lazy


    def eval(self):
        # evaluate conditional features
        while self._lazy:
            l = self._lazy.pop()
            if l._condition(self):
                l = copy.copy(l)
                l._condition = None
                self += l # just add it again, unconditionally
        
    def __getattr__(self, name):
        if name in self._features:
            return self._features[name]
        else:
            raise AttributeError(name)

    def __delattr__(self, name):
        if name in self._features:
            del self._features[name]
        else:
            raise AttributeError(name)

    def __getitem__(self, name):
        return self._features[name]
    
    def __contains__(self, other):
        from . import incidental
        if type(other) is str:
            return other in self._features
        elif isinstance(other, set):
            # make sure non-incidental features match
            for k,v in [(k,v) for k,v in self._features.items()
                        if not v._type.attributes & incidental]:
                if k in other and other[k] not in v:
                    return False
            return True
        else:
            raise ValueError('invalid argument for set.__contains__')

    def __iadd__(self, other):
        """Add either a feature or merge an entire feature-set."""
        return self._cassign(iadd, other)

    def __ior__(self, other):
        """Add either a feature or merge an entire feature-set."""
        return self._cassign(ior, other)

    def _cassign(self, op, other):

        if type(other) == value:
            if other._condition is not None and other not in self._lazy:
                self._lazy.append(other)
            elif other._type.name in self._features:
                op(self._features[other._type.name], other)
            else:
                self._features[other._type.name] = other
        else:
            for k,v in other._features.items():
                if k not in self._features:
                    self._features[k] = v
                else:
                    op(self._features[k], v)
                    self._lazy += other._lazy
        return self

    def __iter__(self):
        return iter(self._features.items())

    def __len__(self):
        return len(self._features)


    def _serialize(self):
        """Helper method for pretty-printing sets."""

        return reduce(lambda d,o:d.update(o.serialize()) or d, self._features.values(), {})

    def __str__(self):
        return '<fs {}>'.format(' '.join(['{}={}'.format(k,v)
                                          for k,v in self._serialize().items()]))
    
    def __repr__(self):
        return '<feature-set {}>'.format(self._features)


def lazy_set():
    """Construct a lazy-set class that adds parameters on-demand."""

    def __init__(self, params, *args):
        self._params = params.copy()
        set.__init__(self, *args)
    
    def _convert(self):
        """Convert a dictionary of (command-line) parameters into
        a set of feature values."""

        converted = []
        for k,v in self._params.items():
            c = k.split('.')
            root = c[0]
            if root not in feature._registry:
                continue  # not defined yet, skip
            else:
                converted.append(k)
            # get an instance of the root feature
            if root not in self._features:
                self._features[root] = feature.lookup(root)()
            sf = f = self._features[root]
            # find the designated subfeature
            for i in range(1, len(c)):
                sf = getattr(sf, c[i])
            # and set the given value
            v = v if type(v) is list else [v]
            if sf.value is not None:
                sf.value += sf._type._validate(*v)
            else:
                sf.value = sf._type._validate(*v)
        # clean up
        for c in converted:
            del self._params[c]

    def decorator(f):
        def wrapper(self, *args, **kwds):
            _convert(self)
            return f(self, *args, **kwds)
        return wrapper

    dict = {}
    for a in set.__dict__:
        value = set.__dict__[a]
        if callable(value):
            dict[a] = decorator(value)
    dict['__init__'] = __init__
    return feature_type('lazy_set', (set,), dict)

lazy_set = lazy_set()
