#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import inspect

_script = None


class ScriptError(ValueError):

    def __init__(self, msg, location=None, level=0):
        if not location:
            f, filename, lineno, f, c, i = inspect.stack()[level]
            if filename == '<string>':
                filename = _script
            location = filename, lineno
        self.filename, self.lineno = location
        self.message = msg
        ValueError.__init__(self, '{}:{}: {}'.format(self.filename, self.lineno, msg))


class ArgumentError(ValueError): pass
