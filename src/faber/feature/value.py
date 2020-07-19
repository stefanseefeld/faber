#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import multi, incidental
from operator import iadd, ior
import copy


class value(object):

    def __init__(self, type, v, condition, **kwds):
        """Construct a feature value.
        Arguments:

          * type: the feature
          * v: the value (list if this is a 'multi' feature, a single value otherwise)
          * condition: a condition in case this is a conditional feature
          * kwds: subfeatures, if this is a composite feature value"""
        self._type = type
        self._name = type.name
        self._value = v
        assert not isinstance(v, value)
        self._condition = condition

    def __bool__(self):
        return bool(self._value)

    __nonzero__ = __bool__  # python 2

    def __copy__(self):
        v = copy.copy(self._value)
        return value(self._type, v, self._condition)

    def copy(self):
        return self.__copy__()

    def __call__(self, condition):
        """Create a conditionalized version of self."""
        clone = self.copy()
        clone._condition = condition
        return clone

    def __iadd__(self, other):
        return self._type._cassign(iadd, self, other)

    def __ior__(self, other):
        return self._type._cassign(ior, self, other)

    def __eq__(self, other):
        if type(other) is value:
            if self._type != other._type:
                return False
            return self._value == other._value
        else:
            # allow 'other' to be raw data
            if self._type.attributes & multi:
                return other == self._value or other in self._value
            else:
                return self._value == other

    def __ne__(self, other):
        return not self == other

    def __contains__(self, v):
        return v in self._value

    def matches(self, other):
        """Report whether 'other' matches 'self', when used as a spec.
        For incidental features this unconditionally returns True.
        Otherwise this reports true iff all defined values in self equal
        the corresponding values in 'other'."""
        if isinstance(other, value):
            assert self._type == other._type

        if self._type.attributes & incidental:
            return True
        else:
            if not isinstance(other, value):
                return other in self._value if self._type.attributes & multi else other == self._value
            else:
                return (self._value is None or
                        other._value is None or
                        self._value == other._value)

    def __repr__(self):
        value = self._value
        return '<value {}={}>'.format(self._type.name, value)

    def __str__(self):
        if self._type.attributes & multi:
            return ' '.join(str(v) for v in self._value)
        else:
            return str(self._value)

    def serialize(self, prefix=''):
        if prefix: prefix += '.'
        return {prefix + self._type.name: self._value}

    def eval(self, set):

        if self._condition is not None and self._condition(set):
            clone = self.copy()
            clone._condition = None
            return (clone,)
        else:
            return ()


class composite_value(value):

    def __init__(self, type, **kwds):
        """Construct a feature value.
        Arguments:

          * type: the feature
          * kwds: subfeatures"""
        self._type = type
        self._name = type.name
        self.__dict__.update({s.name: kwds.get(s.name) for s in self._type.subfeatures})
        self._condition = None  # FIXME

    def __bool__(self):
        return any([bool(self.__dict__[s.name]) for s in self._type.subfeatures])

    __nonzero__ = __bool__  # python 2

    def __copy__(self):
        # make sure to copy all values
        kwds = {s.name: self.__dict__[s.name].copy() for s in self._type.subfeatures
                if self.__dict__[s.name] is not None}
        return composite_value(self._type, **kwds)

    def __eq__(self, other):
        if isinstance(other, composite_value):
            for s in self._type.subfeatures:
                if getattr(self, s.name) != getattr(other, s.name):
                    return False
            return True
        else:
            return False

    def __contains__(self, v):
        return False

    def matches(self, other):
        """Report whether 'other' matches 'self', when used as a spec.
        For incidental features this unconditionally returns True.
        Otherwise this reports true iff all defined values in self equal
        the corresponding values in 'other'."""
        if not isinstance(other, composite_value):
            return False  # comparison to raw data is only allows for non-compound values.
        elif self._type != other._type:
            return False
        for s in self._type.subfeatures:
            if not getattr(other, s.name).matches(getattr(self, s.name)):
                return False
        return True

    def __repr__(self):
        value = '<...>'
        return '<value {}={}>'.format(self._type.name, value)

    def __str__(self):
        values = [getattr(self, s.name) for s in self._type.subfeatures]
        return '<{}>'.format('.'.join([str(v) for v in values]))

    def serialize(self, prefix=''):
        if prefix: prefix += '.'
        d = {}
        for s in self._type.subfeatures:
            sf = getattr(self, s.name)
            d.update(sf.serialize(prefix + self._type.name) if sf else {})
        return d

    def eval(self, set):

        return ()
