#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber import scheduler
import contextlib
import tempfile
import shutil
import os
from os.path import join
import sys


def pyecho(targets, sources):
    vars = scheduler.variables(targets[0])
    vars = ' '.join(['{}={}'.format(n, v) for n, v in vars.items()])
    print('{} <- {}'.format(' '.join([t.name for t in targets]),
                            ' '.join([s.name for s in sources])) +
          (' ({})'.format(vars) if vars else ''))


@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()
    try: yield dirpath
    finally: shutil.rmtree(dirpath)


@contextlib.contextmanager
def cwd(tmp):
    # temporarily change into a working directory
    orig= os.getcwd()
    os.chdir(tmp)
    try: yield
    finally: os.chdir(orig)


def write_fabscript(dirpath, content):
    with open(join(dirpath, 'fabscript'), 'w') as f:
        f.write(content)


@contextlib.contextmanager
def argv(args):

    orig = sys.argv
    sys.argv = type(orig)(args)
    try: yield
    finally: sys.argv = orig
