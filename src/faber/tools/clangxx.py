#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import Action
from ..feature import Set, Map, translate, select_if
from .. import types
from .. import platform
from ..assembly import implicit_rule as irule
from . import compiler
from .cxx import *
from .clang import validate, MakeDepWrapper


class MakeDep(Action):

    command = 'clang++ $(cppflags) -MM -o $(<) $(>)'
    cppflags = Map(compiler.cppflags)
    cppflags += Map(compiler.define, translate, prefix='-D')
    cppflags += Map(compiler.include, translate, prefix='-I')
    cppflags += Map(cxxstd, translate, prefix='-std=c++')


class Compile(Action):

    command = 'clang++ $(cppflags) $(cxxflags) -c -o $(<) $(>)'
    cppflags = Map(compiler.cppflags)
    cppflags += Map(compiler.define, translate, prefix='-D')
    cppflags += Map(compiler.include, translate, prefix='-I')
    cxxflags = Map(compiler.cxxflags)
    cxxflags += Map(cxxstd, translate, prefix='-std=c++')
    cxxflags += Map(compiler.link, select_if, 'shared', '-fPIC')


class Link(Action):

    command = 'clang++ $(ldflags) -o $(<) $(>) $(libs)'
    ldflags = Map(compiler.ldflags)
    ldflags += Map(compiler.linkpath, translate, prefix='-L')
    ldflags += Map(compiler.link, select_if, 'shared', '-shared')
    if platform.os == 'Darwin':
        ldflags += Map(compiler.soname, translate, prefix='-Wl,-install_name -Wl,')
    else:
        ldflags += Map(compiler.soname, translate, prefix='-Wl,-soname -Wl,')
    libs = Map(compiler.libs, translate, prefix='-l')

    def submit(self, targets, sources):
        # sources may contain object files as well as libraries
        # Separate the two, and add the libraries to the libs variable.

        src, linkpath, libs = CLangxx.split_libs(sources)
        linkpath = [compiler.linkpath(l, base='') for l in linkpath]
        libs = [compiler.libs(l) for l in libs]
        fs = Set(*libs + linkpath)
        for t in targets:
            t.features |= fs
        Action.submit(self, targets, src)


class CLangxx(CXX):

    makedep = MakeDepWrapper(MakeDep())
    compile = Compile()
    archive = Action('ar rc $(<) $(>)')
    link = Link()

    def __init__(self, name='clang++', command=None, version='', features=()):

        command, version, features = validate(self.__class__, command or 'clang++',
                                              version, features)
        CXX.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            self.makedep.subst('clang++', command)
            self.compile.subst('clang++', command)
            self.link.subst('clang++', command)

        irule(self.compile, types.obj, types.cxx)
        irule(self.archive, types.lib, types.obj)
        irule(self.link, types.bin, (types.obj, types.dso, types.lib))
        irule(self.link, types.dso, (types.obj, types.dso))
