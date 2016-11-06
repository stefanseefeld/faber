#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import incidental
from operator import iadd, ior

class value(object):
    def __init__(self, type, value, condition, **kwds):
        from .feature import feature
        self._type = type
        sf = type.subfeatures
        if sf:  # a composite value
            self.__dict__.update({k:sf[k](*feature._constr(v))
                                  for k,v in kwds.items()})
        else:   # an ordinary value
            self.value = value
        self._condition = condition

    def __iadd__(self, other):
        return self._type._cassign(iadd, self, other)

    def __ior__(self, other):
        return self._type._cassign(ior, self, other)

    def __eq__(self, other):
        if type(other) is value:
            if self._type != other._type:
                return False
            elif not self._type.subfeatures:
                return self.value == other.value
            for s in self._type.subfeatures:
                if getattr(self, s) != getattr(other, s):
                    return False
        else: # allow 'other' to be raw data
            return not self._type.subfeatures and self.value == other

    def __ne__(self, other):
        return not self == other

    def __contains__(self, other):
        """Report whether 'other' matches 'self', when used as a spec.
            For incidental features this unconditionally returns True.
            Otherwise this reports true iff all defined values in self equal
            the corresponding values in 'other'."""
        if self._type != other._type:
            return False
        elif not self._type.subfeatures:
            return (self._type.attributes & incidental or
                    self.value is None or
                    self.value == other.value)
        for s in self._type.subfeatures:
            if getattr(other, s) not in getattr(self, s):
                return False
        return True
        
    def __repr__(self):
        value = self.value if not self._type.subfeatures else '<...>'
        return '<value {}={}>'.format(self._type.name, value)

    def __str__(self):
        return str(self.value) if not self._type.subfeatures else '<...>'
        
    def serialize(self, prefix=''):
        if prefix: prefix += '.'
        if self._type.subfeatures:
            d = {}
            for s in self._type.subfeatures:
                sf = getattr(self, s)
                d.update(sf.serialize(prefix + self._type.name) if sf else {})
            return d
        else:
            return {prefix + self._type.name: self.value}
