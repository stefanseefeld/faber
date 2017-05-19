#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from test.common import cwd
import subprocess
import pytest
import sys
from os.path import join, abspath
from six import raise_from

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


def check_output(*cmd):
    # Report the output of the failing process rather
    # than the traceback of the check_output call.
    try:
        subprocess.check_output(*cmd)
    except subprocess.CalledProcessError as e:
        raise_from(Exception(e.output), None)


python = sys.executable
faber = abspath(join('scripts', 'faber'))

if sys.platform=='win32':
    # on Windows we can't clean up the config cache while
    # it is still being accessed via the test module itself
    clean = ['-c']  # clean
else:
    clean = ['-cc']  # extra clean


@pytest.mark.skipif(sys.platform == 'win32', reason='requires a "c++" tool')
def test_action():

    with cwd(join('examples', 'action')):
        cmd = [python, faber]
        check_output(cmd)
        check_output(cmd + clean)


def test_tool(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'tool')):
        check_output(cmd)
        check_output(cmd + clean)


def test_implicit_rules(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'implicit_rules')):
        check_output(cmd)
        check_output(cmd + clean)


def test_modular(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'modular')):
        check_output(cmd)
        check_output(cmd + clean)


def test_config(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'config')):
        check_output(cmd)
        check_output(cmd + clean)


@pytest.mark.skip(reason='this requires a bit more work...')
def test_python(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cc_opt(compiler))
    with cwd(join('examples', 'python')):
        check_output(cmd)
        check_output(cmd + clean)


def test_test(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'test')):
        check_output(cmd)
        check_output(cmd + clean)
