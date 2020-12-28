#
# Copyright (c) 2020 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.action import CallError
from faber.utils import capture_output
from test.compiler import make_source, check_makedep, check_compile
import pytest
import sys
if not sys.platform.startswith("win"):
    pytest.skip('skipping windows-only tests', allow_module_level=True)
from faber.tools.msvc import msvc  # noqa E402


@pytest.fixture
def cxx():
    if not msvc.instances():
        pytest.skip('no MSVC compiler found')
    else:
        yield msvc.instance()


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
