#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import multi
import os


class map(object):
    """A map maps a feature-set to variables."""

    def __init__(self, feature, func=None, *args, **kwds):
        """Create a map from a function that takes a feature value and returns a list of strings.
        The default function returns the feature value as-is."""

        if func is None:
            func = lambda fv: fv._value if fv is not None else []

        def wrapper(fs):
            fv = next(iter(filter(lambda v: v._type is feature, fs.values())), None)
            return func(fv, *args, **kwds)
        self._funcs = [wrapper]

    def __iadd__(self, other):
        self._funcs += other._funcs
        return self

    def __add__(self, other):
        self._funcs += other._funcs
        return self

    def __call__(self, fs):
        return ' '.join([i for func in self._funcs for i in func(fs)])


def translate(fv, prefix='', suffix=''):
    """Map a multi feature to a list of strings, using a prefix and suffix."""

    if not fv:
        return []
    elif fv._type.attributes & multi:
        return ['{}{}{}'.format(prefix, v, suffix) for v in fv._value] if fv else []
    else:
        return ['{}{}{}'.format(prefix, fv._value, suffix)] if fv else []


def join(fv, char=os.pathsep):

    return [char.join([v for v in fv._value] if fv else [])]


def select_if(fv, ref, value):
    """Return a given value if a given feature has a specific value"""

    return [value] if fv and fv._value == ref else []
