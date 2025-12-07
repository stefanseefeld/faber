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
from .cc import *
from .gcc import MakeDepWrapper
import subprocess
import re

# known architectures for each machine type
marchs = dict(x86_64=['x86_64', 'x86'],
              arm64=['arm64'],
              w64=['w64', 'w32'])

# compiler flags per architecture
arch_flags = dict(x86_64=['-m64'],
                  x86=['-m32'],
                  arm64=[],
                  w64=['-m64'],
                  w32=['-m32'])


def validate(cls, command, version, features):

    features = Set.instantiate(features)
    version = version or cls.find_version_requirement(features)
    v = subprocess.check_output([command, '--version']).decode()
    v = re.match('.* version ([0-9.]+)', v).group(1)
    m = subprocess.check_output([command, '-dumpmachine']).decode().strip()
    if version and v != version:
        raise ValueError('{} version mismatch: expected {}, got {}'
                         .format(command, version, v))
    else:
        version = v
    cpu, _, os = platform.split_triplet(m)
    machine = cpu

    if machine not in marchs:
        raise ValueError('Unsupported machine type {}'.format(machine))
    if 'target' in features:
        arch = str(features.target.arch)
        if arch not in marchs[machine]:
            raise ValueError('Unsupported target architecture {}'.format(arch))
    else:
        arch=marchs[machine][0]
        features += compiler.target(arch=arch)

    features |= compiler.cxxflags(*arch_flags[arch])
    features |= compiler.ldflags(*arch_flags[arch])

    return command, version, features


class MakeDep(Action):

    command = 'clang $(cppflags) -MM -o $(<) $(>)'
    cppflags = Map(compiler.cppflags)
    cppflags += Map(compiler.define, translate, prefix='-D')
    cppflags += Map(compiler.include, translate, prefix='-I')


class Compile(Action):

    command = 'clang $(cppflags) $(cflags) -c -o $(<) $(>)'
    cppflags = Map(compiler.cppflags)
    cppflags += Map(compiler.define, translate, prefix='-D')
    cppflags += Map(compiler.include, translate, prefix='-I')
    cflags = Map(compiler.cflags)
    cflags += Map(compiler.link, select_if, 'shared', '-fPIC')


class Link(Action):

    command = 'clang $(ldflags) -o $(<) $(>) $(libs)'
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

        src, linkpath, libs = CLang.split_libs(sources)
        linkpath = [compiler.linkpath(l, base='') for l in linkpath]
        libs = [compiler.libs(l) for l in libs]
        fs = Set(*libs + linkpath)
        for t in targets:
            t.features |= fs
        Action.submit(self, targets, src)


class CLang(CC):

    makedep = MakeDepWrapper(MakeDep())
    compile = Compile()
    archive = Action('ar rc $(<) $(>)')
    link = Link()

    def __init__(self, name='clang', command=None, version='', features=()):

        command, version, features = validate(self.__class__, command or 'clang',
                                              version, features)
        CC.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            self.makedep.subst('clang', command)
            self.compile.subst('clang', command)
            self.link.subst('clang', command)

        irule(self.compile, types.obj, types.cxx)
        irule(self.archive, types.lib, types.obj)
        irule(self.link, types.bin, (types.obj, types.dso, types.lib))
        irule(self.link, types.dso, (types.obj, types.dso))
