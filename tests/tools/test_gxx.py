#
# Copyright (c) 2020 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.tools.gxx import gxx
from faber.action import CallError
from faber.utils import capture_output
from test.compiler import make_source, check_makedep, check_compile
import pytest


@pytest.fixture
def cxx():
    if not gxx.instances():
        pytest.skip('no g++ compiler found')
    else:
        return gxx.instance()


def test_makedep(cxx):
    """Check dependency detection."""

    header = make_source('foo.h', '// nothing')  # noqa F841
    src = make_source('foo.cc', '#include "foo.h"')
    check_makedep(cxx, src, 1)


def test_makedep_error(cxx):
    """Check missing header error."""

    src = make_source('foo.cc', '#include "foo.h"')
    with capture_output() as (out, err), pytest.raises(CallError):
        check_makedep(cxx, src, 1)
    stdout = out.getvalue()
    stderr = err.getvalue()
    print(stdout)
    print(stderr)


def test_compile(cxx):
    """Check dependency detection."""

    src = make_source('foo.cc', 'int main() {}')
    check_compile(cxx, src)


def test_compile_error(cxx):
    """Check dependency detection."""

    src = make_source('foo.cc', 'int main() { error }')
    with capture_output() as (out, err), pytest.raises(CallError):
        check_compile(cxx, src)
    stdout = out.getvalue()
    stderr = err.getvalue()
    print(stdout)
    print(stderr)
