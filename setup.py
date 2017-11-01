#!/usr/bin/env python
#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from distutils.core import setup, Extension
import sys, os, os.path, glob, shutil
import subprocess
import re

try:
    out = subprocess.check_output('git describe --tags --match release/*'.split(),
                                  stderr=subprocess.STDOUT).decode().strip()
    version=re.match('release/(.+)', out).group(1)
except Exception as e:
    version='snapshot'

def prefix(pref, list): return [pref + x for x in list]

sources=['bjam.c', 'rules.c', 'hash.c', 'modules.c',
         'frames.c', 'constants.c',
         'lists.c', 'timestamp.c', 'function.c',
         'pathsys.c', 'builtins.c',
         'md5.c', 'filesys.c', 'variable.c',
         'strings.c', 'output.c', 'execcmd.c', 'debug.c',
         'graph.c', 'make.c', 'make1.c', 'command.c',
         'cwd.c', 'native.c', 'compile.c', 'object.c']
libraries=[]
if sys.platform == 'win32':
    sources+=['execnt.c', 'pathnt.c', 'filent.c']
    libraries=['kernel32', 'advapi32', 'user32']
else:
    sources+=['execunix.c', 'pathunix.c', 'fileunix.c']

bjam = Extension(name='faber.bjam',
                 sources=prefix('src/bjam/', sources),
                 define_macros=[('HAVE_PYTHON', None),
                                ('OPT_SEMAPHORE', None),
                                ('OPT_GRAPH_DEBUG_EXT', None)],
                 libraries=libraries)
scripts = []
data = [('share/doc/faber-{}'.format(version), ('LICENSE', 'README.md'))]

def find_packages(root_dir, root_name):
    packages = []
    def record(path, pkg_name):
        packages.append(pkg_name)
        for filename in sorted(os.listdir(path)):
            subpath = os.path.join(path, filename)
            if os.path.exists(os.path.join(subpath, '__init__.py')):
                subname = '{}.{}'.format(pkg_name, filename)
                record(subpath, subname)
    record(root_dir, root_name)
    return packages


setup(name='faber',
      version=version,
      author='Stefan Seefeld',
      author_email='stefan@seefeld.name',
      maintainer='Stefan Seefeld',
      maintainer_email='stefan@seefeld.name',
      url='http://github.com/stefanseefeld/faber',
      description='Faber is a construction tool.',
      package_dir={'':'src'},
      packages=find_packages('src/faber', 'faber'),
      ext_modules=[bjam],
      scripts=scripts,
      data_files=data,
      )
