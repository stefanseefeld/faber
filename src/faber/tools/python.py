#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..feature import feature, multi, path, incidental
from ..feature import set, map, translate, select_if, join as fjoin
from .. import types
from ..artefact import artefact
from ..artefacts.library import library
from .. import engine
from ..tool import tool
from .compiler import include, ldflags, link, linkpath, libs, target
from os.path import join
import subprocess
import re

pythonpath = feature('pythonpath', attributes=multi|path|incidental)

class run(action):

    pythonpath = map(pythonpath, fjoin)
    # TODO: figure out how to set PYTHONPATH portably
    command = 'PYTHONPATH=$(pythonpath) python $(>)'

class python(tool):

    run = run()
    
    def check_python(self, cmd):
        return subprocess.check_output([self.command, '-c', cmd]).decode().strip()

    def check_sysconfig(self, cmd):
        r = self.check_python('import distutils.sysconfig as c; print(c.%s)'%cmd)
        return r if r != 'None' else ''

    def __init__(self, name='python', command=None, version='', features=()):
        if not isinstance(features, set):
            features = set(features)
        self.command = command or 'python'
        v = self.check_python('import platform; print(platform.python_version())')
        if version and v != version:
            raise ValueError('{} version mismatch: expected {}, got {}'
                             .format(cmd, version, v))
        a = self.check_python('import platform; print(platform.machine())')
        b = self.check_python('import struct;print(struct.calcsize("P") * 8)')
        if a == 'AMD64': # Windows...
            a = 'x86_64'
        if a == 'x86_64' and b ==32:
            a == 'x86'
        if 'target' in features:
            arch = features.target.arch.value
            if arch != a:
                raise ValueError('{} architecture mismatch: expected {}, got {}'
                                 .format(cmd, arch, a))
        else:
            features += target(arch=a)
        tool.__init__(self, name=name, version=v)
        self.features |= features
        self.run.subst('python ', self.command + ' ')
        # Now determine all the flags we may need to compile C / C++ extensions
        self.include = include(self.check_sysconfig('get_python_inc()'))
        platform = self.check_python('import platform; print(platform.system())')
        if platform == 'Windows':
            version = self.check_python('import sys; print("%d%d"%sys.version_info[0:2])')
            prefix = self.check_python('import sys; print(sys.prefix)')
            self.libfile = join(prefix, 'libs', 'python%s.lib'%version)
            self.libpath = join(prefix, 'libs')
            self.lib = 'python%s'%version
        else:
            self.libpath = self.check_sysconfig('get_config_var("LIBDIR")')
            self.libfile = self.check_sysconfig('get_config_var("LIBRARY")')
            match = re.search('(python.*)\.(a|so|dylib)', self.libfile)
            lib = None
            if match:
                self.lib = match.group(1)
                if match.group(2) == 'a':
                    flags = self.check_sysconfig('get_config_var("LINKFORSHARED")')
                    if flags is not None:
                        flags=flags.split()
                        self.ldflags = ldflags(*flags) # TODO: use them !
            # Only publish the libpath if it isn't a system path
            if self.libpath in ['/usr/lib', '/usr/lib64']:
                self.libpath = None
        self.linkpath = linkpath(self.libpath) if self.libpath else linkpath()
        self.libs = libs(self.lib, condition=(set.cc.name=='msvc')|(set.cxx.name=='msvc'))
        flags = self.check_sysconfig('get_config_var("MODLIBS")')
        flags += ' ' + self.check_sysconfig('get_config_var("SHLIBS")')
        flags = [f[2:] for f in flags.strip().split() if f.startswith('-l')]
        self.libs += libs(*flags)
