#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import, print_function
from faber.project import init, config, project, buildinfo
from faber.module import module as M
from faber import logging
from test.common import tempdir
from os.path import join, exists, expanduser
from os import mkdir
import pytest


def pytest_addoption(parser):
    parser.addoption('--faber-log', action='append',
                     choices=logging.topics.keys(),
                     help='add log topic')
    parser.addoption('--compiler', action='append', default=[],
                     help='specify a compiler to test with. Ex: "gcc", "msvc", "native"')


def pytest_configure(config):
    logging.setup(log=config.getoption('faber_log'))


def pytest_generate_tests(metafunc):
    if 'compiler' in metafunc.fixturenames:
        compilers = metafunc.config.option.compiler or ['']
        metafunc.parametrize('compiler', compilers)


@pytest.fixture(autouse=True)
def session():
    # reset global state
    init()
    if exists(expanduser('~/.faber')):
        config(expanduser('~/.faber'))


@pytest.fixture()
def module():
    with tempdir() as root:
        srcdir = join(root, 'test-source')
        mkdir(srcdir)
        builddir = join(root, 'test-build')
        info = buildinfo(builddir, srcdir)
        with project(info):
            with M('test', srcdir, builddir, process=False):
                yield
