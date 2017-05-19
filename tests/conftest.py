#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import, print_function

import pytest

def pytest_addoption(parser):
    parser.addoption('--compiler', action='append', default=[],
                     help='specify a compiler to test with. Ex: "gcc", "msvc", "native"')

def pytest_generate_tests(metafunc):
    if 'compiler' in metafunc.fixturenames:
        compilers = metafunc.config.option.compiler or ['']
        metafunc.parametrize('compiler', compilers)
