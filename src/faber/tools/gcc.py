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
from .. import types
from ..assembly import implicit_rule as irule
from .. import engine
from . import compiler
from .cc import *
import subprocess
import re

# known architectures for each machine type
marchs = dict(x86_64=['x86_64', 'x86'],
              w64=['w64', 'w32'])

# compiler flags per architecture
arch_flags = dict(x86_64=['-m64'],
                  x86=['-m32'],
                  w64=['-m64'],
                  w32=['-m32'])

def validate(command, version, features):

    if not isinstance(features, set):
        features = set(features)
    v = subprocess.check_output([command, '-dumpversion']).decode().strip()
    m = subprocess.check_output([command, '-dumpmachine']).decode().strip()
    if version and v != version:
        raise ValueError('{} version mismatch: expected {}, got {}'
                         .format(command, version, v))
    else:
        version = v
    cpu, vendor, os = re.match('(\w+)-(\w+)-(\w+)', m).groups()
    if os == 'mingw32':
        os = 'Windows'
        machine = 'w64'
    else:
        machine = cpu

    if machine not in marchs:
        raise ValueError('Unsupported machine type {}'.format(machine))
    if 'target' in features:
        arch = features.target.arch.value
        if arch not in marchs[machine]:
            raise ValueError('Unsupported target architecture {}'.format(arch))
        features |= compiler.target(os=os)
    else:
        arch=marchs[machine][0]
        features |= compiler.target(arch=arch, os=os)

    features |= compiler.cxxflags(*arch_flags[arch])
    features |= compiler.ldflags(*arch_flags[arch])
    
    return command, version, features

class compile(action):

    command = 'gcc $(cppflags) $(cflags) -c -o $(<) $(>)'
    cppflags = map(compiler.cppflags)
    cppflags += map(compiler.define, translate, prefix='-D')
    cppflags += map(compiler.include, translate, prefix='-I')
    cflags = map(compiler.cflags)
    cflags += map(compiler.link, select_if, 'shared', '-fPIC')


class link(action):

    command = 'gcc $(ldflags) -o $(<) $(>) $(libs)'
    ldflags = map(compiler.ldflags)
    ldflags += map(compiler.linkpath, translate, prefix='-L')
    ldflags += map(compiler.link, select_if, 'shared', '-shared')
    libs = map(compiler.libs, translate, prefix='-l')
    
    def submit(self, artefacts, sources, module):
        # sources may contain object files as well as libraries
        # Separate the two, and add the libraries to the libs variable.

        src, linkpath, libs = gcc.split_libs(sources)
        fs = set(compiler.libs(*libs), compiler.linkpath(*linkpath))
        for t in artefacts:
            t.features += fs
        action.submit(self, artefacts, src, module)


class gcc(cc):

    compile = compile()
    archive = action('ar rc $(<) $(>)')
    link = link()

    def __init__(self, name='gcc', command=None, version='', features=()):

        command, version, features = validate(command or 'gcc', version, features)
        cc.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            # if command is of the form <prefix>-g++, make sure
            # to adjust the names of the other tools of the toolchain.
            prefix = command[:-3] if command.endswith('gcc') else ''
            self.compile.subst('gcc', command)
            self.archive.subst('ar', prefix + 'ar')
            self.link.subst('gcc', command)

        irule(types.obj, types.c, self.compile)
        irule(types.lib, types.obj, self.archive)
        irule(types.bin, (types.obj, types.dso, types.lib), self.link)
        irule(types.dso, (types.obj, types.dso), self.link)
