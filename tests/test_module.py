#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.module import module
from test.common import tempdir, write_fabscript
import os
import os.path
import pytest


@pytest.mark.usefixtures('module')
def test_simple():

    script="""
from faber.tools.compiler import include
i = include('.')"""

    with tempdir() as dirpath:
        write_fabscript(dirpath, script)
        m = module(dirpath)
        assert dirpath in m.i


@pytest.mark.usefixtures('module')
def test_paths():

    outer="""
from faber.tools.compiler import include, linkpath
i = include('.')
l = linkpath('.', base=builddir)
inner = module('inner')"""

    inner="""
from faber.tools.compiler import include, linkpath
i = include('.')
l = linkpath('.', base=builddir)
outer = module('..')
"""

    srcdir = module.current.srcdir
    subdir = os.path.join(srcdir, 'inner')
    os.mkdir(subdir)
    write_fabscript(srcdir, outer)
    write_fabscript(subdir, inner)
    m = module(srcdir, builddir='build')
    assert m.i == [srcdir]
    assert m.l == [m.builddir]
    assert m.inner.i == [subdir]
    assert m.inner.l == [os.path.join(m.builddir, 'inner')]
    assert m.inner.outer.i == [srcdir]
    assert m.inner.outer.l == [m.builddir]


@pytest.mark.usefixtures('module')
def test_kwds():

    outer="""
from faber.tools.compiler import include, linkpath
value = 24
inner = module('inner', value=value)"""

    inner="""
"""

    with tempdir() as root:
        subdir = os.path.join(root, 'inner')
        os.mkdir(subdir)
        write_fabscript(root, outer)
        write_fabscript(subdir, inner)
        m = module(root, builddir='build')
        assert m.inner.value == m.value
