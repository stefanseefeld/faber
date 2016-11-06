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
from .cc import *
from os.path import splitext, basename
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
    

class gcc(cc):

    compile = compile()
    archive = action('ar rc $(<) $(>)')
    link = link()

    def __init__(self, name='gcc', command=None, version='', target='', features=()):
        
        command, version, features = validate(command or 'gcc', version, features)
        cc.__init__(self, name=name, version=v)
        self.features |= features
        if command:
            prefix = cmd[:-3] if cmd.endswith('g++') else ''
            self.compile.subst('gcc', cmd)
            self.archive.subst('ar', prefix + 'ar')
            self.link.subst('gcc', cmd)
        
