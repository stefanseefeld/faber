#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import subprocess
import pytest
import shutil
import sys
import os
from os.path import join, normpath, abspath
import contextlib
from six import raise_from

compilers = {'gcc': {'cc':'gcc', 'cxx':'g++'},
             'clang': {'cc':'clang', 'cxx':'clang++'},
             'msvc': {'cc':'msvc', 'cxx':'msvc'}}
if sys.platform=='win32':
    compilers['native'] = compilers['msvc']
else:
    compilers['native'] = compilers['gcc']

def get_cc_opt(name):
    return 'cc.name={}'.format(compilers[name]['cc'])

def get_cxx_opt(name):
    return 'cxx.name={}'.format(compilers[name]['cxx'])


@contextlib.contextmanager
def cwd(tmp):
    # temporarily change into a working directory
    orig= os.getcwd()
    os.chdir(tmp)
    try: yield
    finally: os.chdir(orig)

def check_output(*cmd):
    # Report the output of the failing process rather
    # than the traceback of the check_output call.
    try:
        subprocess.check_output(*cmd)
    except subprocess.CalledProcessError as e:
        raise_from(Exception(e.output), None)

python = sys.executable
faber = abspath(join('scripts', 'faber'))

@pytest.mark.skipif(sys.platform == 'win32', reason='requires a "c++" tool')
def test_action():

    with cwd(join('examples', 'action')):
        check_output([python, faber])
        check_output([python, faber, 'clean'])
            

def test_tool(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'tool')):
        check_output(cmd)
        check_output(cmd + ['clean'])

def test_implicit_rules(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'implicit_rules')):
        check_output(cmd)
        check_output(cmd + ['clean'])

def test_modular(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'modular')):
        check_output(cmd)
        check_output(cmd + ['clean'])

def test_config(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cxx_opt(compiler))
    with cwd(join('examples', 'config')):
        check_output(cmd)
        check_output(cmd + ['clean'])
        check_output(cmd + ['config-clean'])

def test_test(compiler):

    cmd = [python, faber]
    if compiler:
        cmd.append(get_cc_opt(compiler))
    with cwd(join('examples', 'test')):
        # subprocess.CalledProcessError
        with pytest.raises(Exception):
            check_output(cmd)
        check_output(cmd + ['clean'])
