#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..feature import set, map, translate, select_if
from ..artefact import artefact
from .. import engine
from . import compiler
from .clang import validate
from .cxx import *
from os.path import splitext, basename
import re
import subprocess

class compile(action):

    command = 'clang++ $(cppflags) $(cxxflags) -c -o $(<) $(>)'
    cppflags = map(compiler.cppflags)
    cppflags += map(compiler.define, translate, prefix='-D')
    cppflags += map(compiler.include, translate, prefix='-I')
    cxxflags = map(compiler.cxxflags)
    cxxflags += map(compiler.link, select_if, 'shared', '-fPIC')


class link(action):

    command = 'clang++ $(ldflags) -o $(<) $(>) $(libs)'
    ldflags = map(compiler.ldflags)
    ldflags += map(compiler.linkpath, translate, prefix='-L')
    ldflags += map(compiler.link, select_if, 'shared', '-shared')
    libs = map(compiler.libs, translate, prefix='-l')
    

class clangxx(cxx):

    compile = compile()
    archive = action('ar rc $(<) $(>)')
    link = link()

    def __init__(self, name='clang++', command=None, version='', target='', features=()):

        command, version, features = validate(command or 'clang++', version, features)
        cxx.__init__(self, name=name, version=version)
        self.features |= features

