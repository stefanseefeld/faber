#
# Copyright (c) 2020 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.project import Project, BuildInfo
from faber.module import Module as M
from os.path import join
from test.common import tempdir
from os import mkdir
import pytest


@pytest.fixture(autouse=True)
def module():
    with tempdir() as root:
        srcdir = join(root, 'test-source')
        mkdir(srcdir)
        builddir = join(root, 'test-build')
        info = BuildInfo(builddir, srcdir)
        with Project(info):
            with M('test', srcdir, builddir, process=False):
                yield
