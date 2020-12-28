#
# Copyright (c) 2020 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.tools.clang import clang
from faber.action import CallError
from faber.utils import capture_output
from test.compiler import make_source, check_makedep, check_compile
import pytest


@pytest.fixture
def cc():
    if not clang.instances():
        pytest.skip('no clang compiler found')
    else:
        return clang.instance()


def test_makedep(cc):
    """Check dependency detection."""

    header = make_source('foo.h', '// nothing')  # noqa F841
    src = make_source('foo.c', '#include "foo.h"')
    check_makedep(cc, src, 1)


def test_makedep_error(cc):
    """Check missing header error."""

    src = make_source('foo.c', '#include "foo.h"')
    with capture_output() as (out, err), pytest.raises(CallError):
        check_makedep(cc, src, 1)
    stdout = out.getvalue()
    stderr = err.getvalue()
    print(stdout)
    print(stderr)


def test_compile(cc):
    """Check dependency detection."""

    src = make_source('foo.c', 'int main() {}')
    check_compile(cc, src)


def test_compile_error(cc):
    """Check dependency detection."""

    src = make_source('foo.c', 'int main() { error }')
    with capture_output() as (out, err), pytest.raises(CallError):
        check_compile(cc, src)
    stdout = out.getvalue()
    stderr = err.getvalue()
    print(stdout)
    print(stderr)
