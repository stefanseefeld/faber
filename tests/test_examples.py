#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber import cli
from test.common import cwd, argv
import pytest
import sys
from os.path import join

compilers = {'gcc': {'cc': 'gcc', 'cxx': 'g++'},
             'clang': {'cc': 'clang', 'cxx': 'clang++'},
             'msvc': {'cc': 'msvc', 'cxx': 'msvc'}}
if sys.platform=='win32':
    compilers['native'] = compilers['msvc']
else:
    compilers['native'] = compilers['gcc']


def get_cc_opt(name):
    return 'cc.name={}'.format(compilers[name]['cc'])


def get_cxx_opt(name):
    return 'cxx.name={}'.format(compilers[name]['cxx'])


def faber(*args):
    with argv(('faber',) + args):
        return cli.main()


if sys.platform=='win32':
    # on Windows we can't clean up the config cache while
    # it is still being accessed via the test module itself
    clean = '-c'  # clean
else:
    clean = '-cc'  # extra clean


@pytest.mark.skipif(sys.platform == 'win32', reason='requires a "c++" tool')
def test_action():

    with cwd(join('examples', 'action')):
        assert faber()
        assert faber(clean)


def test_tool(compiler):

    args = []
    if compiler:
        args.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'tool')):
        assert faber(*args)
        assert faber(clean)


def test_implicit_rules(compiler):

    args = []
    if compiler:
        args.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'implicit_rules')):
        assert faber(*args)
        assert faber(clean)


def test_modular(compiler):

    args = []
    if compiler:
        args.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'modular')):
        assert faber(*args)
        assert faber(clean)


def test_config(compiler):

    args = []
    if compiler:
        args.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'config')):
        assert faber(*args)
        assert faber(clean)


def test_python(compiler):

    args = []
    if compiler:
        args.append(get_cc_opt(compiler))
    with cwd(join('examples', 'python')):
        assert faber(*args)
        assert faber(clean)


def test_test(compiler):

    args = []
    if compiler:
        args.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'test')):
        assert faber(*args)
        assert faber(clean)


def test_package(compiler):

    args = []
    if compiler:
        args.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'package')):
        assert faber(*args + ['tgz', 'stgz'])
        assert faber(clean)
