#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)


class InvalidState(Exception):

    def __init__(self, a):
        cln = a.__module__ + '.' + a.__class__.__qualname__
        Exception.__init__(self, f'cannot access unfinished {cln} {a}')
        self.artefact = a


class delayed(object):
    """A delayed value may only be used after a prerequisite artefact has
    been updated."""

    def __init__(self, f, a):
        self._func = f if callable(f) else lambda: f  # the wrapped value
        self._artefact = a  # the artefact on which the value depends

    def apply(self, f):
        """Create a new delayed object representing the value `f(self.result())`"""
        return delayed(lambda: f(self._func()), self._artefact)

    def result(self):
        if self._artefact.status is None:
            raise InvalidState(self._artefact)
        return self._func()

    def __str__(self):
        cln = self.__class__.__name__
        return f'<{cln} func={self._func} artefact={self._artefact}>'


class delayed_property(property):

    def __init__(*args, **kwds):
        property.__init__(*args, **kwds)

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        return delayed(lambda: self.fget(instance), instance)
