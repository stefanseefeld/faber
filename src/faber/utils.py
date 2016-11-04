#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

def add_metaclass(metaclass):

    # This is a minimalist version to satisfy faber's needs only
    def wrapper(cls):
        vars = cls.__dict__.copy()
        vars.pop('__dict__', None)
        vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, vars)
    return wrapper
