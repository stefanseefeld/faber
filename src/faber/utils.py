#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from contextlib import contextmanager
import string
import sys


def add_metaclass(metaclass):

    # This is a minimalist version to satisfy faber's needs only
    def wrapper(cls):
        vars = cls.__dict__.copy()
        vars.pop('__dict__', None)
        vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, vars)
    return wrapper


@contextmanager
def capture_output():
    if sys.version_info < (3, 0):
        from io import StringIO

        class TextIO(StringIO):
            def write(self, data):
                if not isinstance(data, unicode):  # noqa F821
                    data = unicode(data, getattr(self, '_encoding', 'utf-8'), 'replace')  # noqa F821
                StringIO.write(self, data)
    else:
        from io import StringIO as TextIO
    out = TextIO()
    err = TextIO()
    stdout = sys.stdout
    sys.stdout = out
    stderr = sys.stderr
    sys.stderr = err
    try:
        yield out, err
    finally:
        sys.stdout = stdout
        sys.stderr = stderr


def aslist(o):
    return o if isinstance(o, list) else [o]


class path_formatter(string.Formatter):

    def format_field(self, value, spec):
        """Remove path segments corresponding to undefined features."""
        if value is None:
            return ''
        else:
            return super(path_formatter, self).format_field(value, spec)
    def get_value(self, key, args, kwargs):
        """Remove path segments corresponding to non-existent features."""
        try:
            if isinstance(key, int):
                return args[key]
            else:
                return kwargs[key]
        except KeyError:
            return ''

    def get_field(self, field_name, args, kwargs):
        if sys.version_info < (3, 0):
            first, rest = field_name._formatter_field_name_split()
        else:
            first, rest = string._string.formatter_field_name_split(field_name)
        try:
            # if `first` doesn't exist, this throws
            obj = string.Formatter.get_value(self, first, args, kwargs)
            # loop through the rest of the field_name, doing
            #  getattr or getitem as needed
            for is_attr, i in rest:
                if is_attr:
                    obj = getattr(obj, i)
                else:
                    obj = obj[i]

            return obj, first
        except Exception:
            return '', first
