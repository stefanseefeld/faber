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
          * item: the value (list if this is a 'multi' feature, a single value otherwise)
          * condition: a condition in case this is a conditional feature
          * kwds: subfeatures, if this is a composite feature value"""
        self._type = type
        self._name = type.name
        if not self._type.subfeatures:  # an ordinary value
            self._value = v
            assert not isinstance(v, value)
        else:
            self.__dict__.update({k: kwds.get(k) for k in self._type.subfeatures})
        self._condition = condition

    def __bool__(self):
        if self._type.subfeatures:
            return any([bool(self.__dict__[k]) for k in self._type.subfeatures])
        else:
            return bool(self._value)

    __nonzero__ = __bool__  # python 2

    def __copy__(self):
        # make sure to copy all values
        v = None if self._type.subfeatures else copy.copy(self._value)
        kwds = {k: self.__dict__[k].copy() for k in self._type.subfeatures
                if self.__dict__[k] is not None}
        return value(self._type, v, self._condition, **kwds)

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
            elif not self._type.subfeatures:
                return self._value == other._value
            for s in self._type.subfeatures:
                if getattr(self, s) != getattr(other, s):
                    return False
            return True
        elif not self._type.subfeatures:
            # allow 'other' to be raw data
            if self._type.attributes & multi:
                return other == self._value or other in self._value
            else:
                return self._value == other
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __contains__(self, v):
        return v in self._value

    def matches(self, other):
        """Report whether 'other' matches 'self', when used as a spec.
            For incidental features this unconditionally returns True.
            Otherwise this reports true iff all defined values in self equal
            the corresponding values in 'other'."""
        if not isinstance(other, value):
            if self._type.subfeatures:
                return False  # comparison to raw data is only allows for non-compound values.
            else:
                return other in self._value
        elif self._type != other._type:
            return False
        elif not self._type.subfeatures:
            return (self._type.attributes & incidental or
                    self._value is None or other._value is None or
                    self._value == other._value)
        for s in self._type.subfeatures:
            if not getattr(other, s).matches(getattr(self, s)):
                return False
        return True

    def __repr__(self):
        value = self._value if not self._type.subfeatures else '<...>'
        return '<value {}={}>'.format(self._type.name, value)

    def __str__(self):
        if self._type.subfeatures:
            return '<...>'
        elif self._type.attributes & multi:
            return ' '.join(str(v) for v in self._value)
        else:
            return str(self._value)

    def serialize(self, prefix=''):
        if prefix: prefix += '.'
        if self._type.subfeatures:
            d = {}
            for s in self._type.subfeatures:
                sf = getattr(self, s)
                d.update(sf.serialize(prefix + self._type.name) if sf else {})
            return d
        else:
            return {prefix + self._type.name: self._value}

    def eval(self, set):

        if self._condition is not None and self._condition(set):
            clone = self.copy()
            clone._condition = None
            return (clone,)
        else:
            return ()
