#
# Copyright (c) 2019 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.project import *
from test.common import tempdir, write_fabscript
import pytest
from os.path import join, exists
from os import mkdir


def test_no_args():

    with tempdir():
        info = buildinfo(None)
        assert info.srcdir is None
        assert info.builddir is None


def test_new_project():

    with tempdir() as root:
        # setup
        srcdir = join(root, 'test-source')
        mkdir(srcdir)
        write_fabscript(srcdir, '')
        builddir = join(root, 'test-build')

        # test
        info = buildinfo(builddir, srcdir)
        assert info.srcdir == srcdir
        assert info.builddir == builddir
        info.store()
        assert exists(join(builddir, '.faber', 'info'))


def test_existing_project():

    with tempdir() as root:
        # setup
        srcdir = join(root, 'test-source')
        mkdir(srcdir)
        write_fabscript(srcdir, '')
        builddir = join(root, 'test-build')
        info = buildinfo(builddir, srcdir)
        info.store()

        # test
        info = buildinfo(builddir, srcdir)
        assert info.srcdir == srcdir
        assert info.builddir == builddir


def test_parameters():

    with tempdir() as root:
        # setup
        srcdir = join(root, 'test-source')
        mkdir(srcdir)
        write_fabscript(srcdir, '')
        builddir = join(root, 'test-build')
        info = buildinfo(builddir, srcdir)
        info.parameters = dict(answer='42')
        info.store()

        # test
        info = buildinfo(builddir, srcdir)
        assert info.parameters == dict(answer='42')


def test_inplace_project():

    with tempdir() as root:
        # setup
        srcdir = join(root, 'test-source')
        mkdir(srcdir)
        write_fabscript(srcdir, '')

        # test
        info = buildinfo(srcdir)
        assert info.srcdir == srcdir
        assert info.builddir == srcdir


def test_invalid_project():

    with tempdir() as root:
        # setup
        srcdir = join(root, 'test-source')
        mkdir(srcdir)
        write_fabscript(srcdir, '')
        builddir = join(root, 'test-build')
        info = buildinfo(builddir, srcdir)
        info.store()

        # test
        with pytest.raises(Exception):
            info = buildinfo(builddir, srcdir + '-other')
