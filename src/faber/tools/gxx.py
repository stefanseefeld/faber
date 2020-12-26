#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..feature import set, map, translate, select_if
from .. import types
from .. import platform
from ..assembly import implicit_rule as irule
from . import compiler
from .cxx import *
from .gcc import validate, makedep_wrapper


class makedep(action):

    command = 'g++ $(cppflags) -MM -o $(<) $(>)'
    cppflags = map(compiler.cppflags)
    cppflags += map(compiler.define, translate, prefix='-D')
    cppflags += map(compiler.include, translate, prefix='-I')
    cppflags += map(cxxstd, translate, prefix='-std=c++')


class compile(action):

    command = 'g++ $(cppflags) $(cxxflags) -c -o $(<) $(>)'
    cppflags = map(compiler.cppflags)
    cppflags += map(compiler.define, translate, prefix='-D')
    cppflags += map(compiler.include, translate, prefix='-I')
    cxxflags = map(compiler.cxxflags)
    cxxflags += map(cxxstd, translate, prefix='-std=c++')
    cxxflags += map(compiler.link, select_if, 'shared', '-fPIC')


class link(action):

    command = 'g++ $(ldflags) -o $(<) $(>) $(libs)'
    ldflags = map(compiler.ldflags)
    ldflags += map(compiler.linkpath, translate, prefix='-L')
    ldflags += map(compiler.link, select_if, 'shared', '-shared')
    if platform.os == 'Darwin':
        ldflags += map(compiler.soname, translate, prefix='-Wl,-install_name -Wl,')
    else:
        ldflags += map(compiler.soname, translate, prefix='-Wl,-soname -Wl,')
    libs = map(compiler.libs, translate, prefix='-l')

    def submit(self, targets, sources):
        # sources may contain object files as well as libraries
        # Separate the two, and add the libraries to the libs variable.

        src, linkpath, libs = gxx.split_libs(sources)
        linkpath = [compiler.linkpath(l, base='') for l in linkpath]
        libs = [compiler.libs(l) for l in libs]
        fs = set(*libs + linkpath)
        for t in targets:
            t.features |= fs
        action.submit(self, targets, src)


class gxx(cxx):

    makedep = makedep_wrapper(makedep())
    compile = compile()
    archive = action('ar rc $(<) $(>)')
    link = link()

    def __init__(self, name='g++', command=None, version='', features=()):

        command, version, features = validate(self.__class__, command or 'g++',
                                              version, features)
        cxx.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            # if command is of the form <prefix>-g++, make sure
            # to adjust the names of the other tools of the toolchain.
            prefix = command[:-3] if command.endswith('g++') else ''
            self.makedep.subst('g++', command)
            self.compile.subst('g++', command)
            self.archive.subst('ar', prefix + 'ar')
            self.link.subst('g++', command)

        irule(self.compile, types.obj, types.cxx)
        irule(self.archive, types.lib, types.obj)
        irule(self.link, types.bin, (types.obj, types.dso, types.lib))
        irule(self.link, types.dso, (types.obj, types.dso))
