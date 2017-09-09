#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import sys
import inspect
from contextlib import contextmanager

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


@contextmanager
def error_reporter(script):
    global _script
    from . import debug

    _script = script
    try:
        yield
    except SyntaxError as e:
        if debug:
            raise
        filename, lineno = e.filename, e.lineno
        offset = e.offset or 1  # sometimes e.offset is None...
        value = 'invalid syntax:\n{}{}\n{}'.format(e.text, (offset - 1) * ' ' + '^', e.msg)
        if filename == '<string>':
            filename = script
        raise ScriptError(value, location=(filename, lineno))
    except (ScriptError, SystemExit, KeyboardInterrupt):
        raise  # pass through
    except Exception:
        if debug:
            raise
        type_, value, tb = sys.exc_info()
        f, filename, lineno, f, c, i = inspect.getinnerframes(tb)[-1]
        if filename == '<string>':
            filename = script
        raise ScriptError(str(value), location=(filename, lineno))
