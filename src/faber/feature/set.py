#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..utils import add_metaclass
from . import incidental
from .feature import feature
from .value import value, composite_value
from .condition import value as expr
from ..delayed import delayed
from ..error import ScriptError
from operator import iadd, ior
from functools import reduce


class set_type(type):

    def __getattr__(cls, name):
        # Allow the construction of expressions to support conditional values
        return expr(name)


@add_metaclass(set_type)
class set(object):

    @staticmethod
    def instantiate(features):
        """Convert the argument into a set."""
        if isinstance(features, set):
            return features
        elif not features:
            return set()
        else:
            return set(features)

    def __init__(self, *args):

        # if only one argument is provided and it's not a feature-value,
        # assume it's a container of values.
        if len(args) == 1 and not isinstance(args[0], (value, delayed)):
            args = args[0]

        self._features = {}
        self._delayed = []
        self._conditionals = []
        reduce(lambda s, a: ior(s, a), args, self)

    def keys(self):
        return self._features.keys()

    def values(self):
        return self._features.values()

    def items(self):
        return self._features.items()

    def get(self, name, default):
        return self._features.get(name, default)

    def dependencies(self):
        return [d._artefact for d in self._delayed] + \
            [c._artefact for c in self._conditionals
             if hasattr(c, '_artefact')]  # yuck !!

    def copy(self):
        """Create a copy of this set."""
        return set(*list(self._features.values()) + self._delayed + self._conditionals)

    def essentials(self):
        """Create a copy of this set containing only the essential
        (i.e., non-incidental) features."""
        return set(*[v for v in self._features.values()
                     if isinstance(v, composite_value) or not v._type.attributes & incidental])

    def update(self, other):
        """Add new features from `other`, replacing existing ones."""
        if isinstance(other, delayed):
            self._delayed.append(other)
        elif isinstance(other, value):
            self._features[other._name] = other
        else:
            other = set.instantiate(other)
            # only ordinary values can be updated
            for k, v in other._features.items():
                self._features[k] = v.copy()
            self._delayed[:] = other._delayed
            self._conditionals[:] = other._conditionals
        return self

    def eval(self, update=True):
        if update:
            from .. import scheduler
            # (allow dependencies to fail)
            scheduler.update(self.dependencies())
        # compute any delayed values
        self |= set(*[d.result() for d in self._delayed])
        self._delayed[:] = []
        if not self._conditionals:
            return self
        # evaluate conditional features
        initial = self.copy()
        current = initial.copy()
        for i in range(len(self._conditionals) + 1):
            added = [f for c in self._conditionals for f in c.eval(current)]
            fs = initial + set(*added)
            if current._features == fs._features:
                self |= set(*added)
                return self  # we are done !
            else:
                current = fs
        # didn't converge, conditions can't be met
        raise ScriptError('cannot satisfy conditionals')  # TODO: list location of all conditionals

    def __getattr__(self, name):
        if name in self._features:
            return self._features[name]
        elif name.startswith('__'):  # no special handling of special attributes
            return None
        else:
            raise ScriptError('no feature "{}" in set'.format(name), level=2)

    def __delattr__(self, name):
        del self._features[name]

    def __getitem__(self, name):
        return self._features[name]

    def __contains__(self, name):
        return name in self._features

    def matches(self, other):
        assert isinstance(other, set)
        for k, v in [(k, v) for k, v in self.items()]:
            if k in other and not other[k].matches(v):
                return False
        return True

    def __iadd__(self, other):
        """Add either a feature or merge an entire feature-set."""
        return self._cassign(iadd, other)

    def __add__(self, other):
        """Add either a feature or merge an entire feature-set."""
        fs = self.copy()
        fs += other
        return fs

    def __ior__(self, other):
        """Add either a feature or merge an entire feature-set."""
        return self._cassign(ior, other)

    def __or__(self, other):
        """Add either a feature or merge an entire feature-set."""
        fs = self.copy()
        fs |= other
        return fs

    def _cassign(self, op, other):
        """compound-assign: use `op` to add `other` to `self`"""
        if isinstance(other, delayed):
            self._delayed.append(other)
        elif isinstance(other, value):
            if other._condition is not None:
                self._conditionals.append(other)
            else:
                if other._name not in self._features:
                    self._features[other._name] = other.copy()
                else:
                    op(self._features[other._name], other)
        elif isinstance(other, set):
            for k, v in other._features.items():
                if k not in self._features:
                    self._features[k] = v.copy()
                else:
                    op(self._features[k], v)
            self._delayed += other._delayed
            self._conditionals += other._conditionals
        else:
            raise ValueError('invalid type {}'.format(type(other)))
        return self

    def __iter__(self):
        return iter(self.items())

    def __len__(self):
        return len(self._features)

    def _serialize(self):
        """Helper method for pretty-printing sets."""

        return reduce(lambda d, o: d.update(o.serialize()) or d, self.values(), {})

    def __str__(self):
        cln = self.__class__.__name__
        return '<{} {}>'.format(cln, ' '.join(['{}={}'.format(k, v)
                                               for k, v in sorted(self._serialize().items())]))

    def __repr__(self):
        cln = self.__class__.__name__
        return '<{} {}>'.format(cln, self._features)


def def_lazy_set():
    """Construct a lazy-set class that adds parameters on-demand."""

    def __init__(self, params, *args):
        self._params = params.copy()
        set.__init__(self, *args)

    def copy(self):
        return type(self)(self._params, *list(self._features.values()) + self._delayed + self._conditionals)

    def _parse(self):
        """Parse a dictionary of (command-line) parameters into
        a set of feature values."""
        converted = []
        for k, v in self._params.items():
            c = k.split('.')
            root = c[0]
            if root not in feature._registry:
                continue  # not defined yet, skip
            else:
                converted.append(k)
            # get an instance of the root feature
            if root not in self._features:
                f = feature.lookup(root)()
                self._features[root] = f
            sf = f = self._features[root]
            # find the designated subfeature
            for i in range(1, len(c)):
                sf = getattr(sf, c[i])
            # and set the given value
            sf += sf._type(*v if type(v) is list else [v])
        # clean up
        for c in converted:
            del self._params[c]

    def decorator(f):
        def wrapper(self, *args, **kwds):
            _parse(self)
            return f(self, *args, **kwds)
        return wrapper

    dict = {}
    for a, v in set.__dict__.items():
        if a in ('__add__',
                 '__contains__',
                 '__getattr__',
                 '__getitem__',
                 '__iadd__',
                 '__ior__',
                 '__iter__',
                 '__keys__',
                 '__len__',
                 '__or__',
                 'eval',
                 'items',
                 'matches',
                 'values'):
            dict[a] = decorator(v)
    dict['__init__'] = __init__
    dict['copy'] = copy
    return set_type('lazy_set', (set,), dict)


lazy_set = def_lazy_set()
