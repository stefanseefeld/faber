#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..feature import feature, multi, path, incidental
from ..feature import set, map, join as fjoin
from ..tool import tool
from .compiler import include, ldflags, linkpath, libs, target, runpath
from .. import platform
from os.path import join
import subprocess
import re
import logging

logger = logging.getLogger('tools')

pythonpath = feature('pythonpath', attributes=multi|path|incidental)


class run(action):

    pythonpath = map(pythonpath, fjoin)
    runpath = map(runpath, fjoin)
    if platform.os == 'Windows':
        command = """set PATH=$(runpath);%PATH%
set PYTHONPATH=$(pythonpath)
python $(>)"""
    else:
        command = 'LD_LIBRARY_PATH=$(runpath) PYTHONPATH=$(pythonpath) python $(>)'


class python(tool):

    run = run()

    def check_python(self, cmd):
        return subprocess.check_output([self.command, '-c', cmd], universal_newlines=True).strip()

    def check_sysconfig(self, cmd):
        r = self.check_python(f'import sysconfig as c; print(c.{cmd})')
        return r if r != 'None' else ''

    def __init__(self, name='python', command=None, version='', features=()):
        if not isinstance(features, set):
            features = set(features)
        self.command = command or 'python'
        v = self.check_python('import platform; print(platform.python_version())')
        if version and v != version:
            raise ValueError(f'{self.command} version mismatch: expected {version}, got {v}')
        a = self.check_python('import platform; print(platform.machine())')
        b = int(self.check_python('import struct;print(struct.calcsize("P") * 8)'))
        if a == 'AMD64':  # Windows...
            a = 'x86_64'
        if a == 'x86_64' and b == 32:
            a = 'x86'
        if 'target' in features:
            arch = str(features.target.arch)
            if arch != a:
                raise ValueError(f'{self.command} architecture mismatch: expected {arch}, got {a}')
        else:
            features += target(arch=a)
        tool.__init__(self, name=name, version=v)
        self.features |= features
        self.run.subst('python ', self.command + ' ')
        # Now determine all the flags we may need to compile C / C++ extensions
        self.include = include(self.check_sysconfig('get_config_var("INCLUDEPY")'))
        platform = self.check_python('import platform; print(platform.system())')
        impl = self.check_python('import platform; print(platform.python_implementation())')
        prefix = self.check_python('import sys; print(sys.prefix)')
        if platform == 'Windows':
            if impl == 'CPython':
                version = self.check_sysconfig('get_config_var("py_version_nodot")')
                self.libfile = join(prefix, 'libs', f'python{version}.lib')
                self.libpath = join(prefix, 'libs')
                self.lib = 'python' + version
            elif impl == 'PyPy':
                version = self.check_python('import sys; print(sys.version_info[0])')
                self.libfile = join(prefix, 'libs', f'libpypy{version}-c.lib')
                self.libpath = join(prefix, 'libs')
                self.lib = 'libpypy' + version + '-c'
            else:
                raise ValueError('unsupported Python implementation')
        else:
            self.libpath = self.check_sysconfig('get_config_var("LIBDIR")')
            if impl == 'CPython':
                self.libfile = self.check_sysconfig('get_config_var("LIBRARY")')
                match = re.search(r'(python.*)\.(a|so|dylib)', self.libfile)
                if match:
                    self.lib = match.group(1)
                    if match.group(2) == 'a':
                        flags = self.check_sysconfig('get_config_var("LINKFORSHARED")')
                        if flags is not None:
                            flags=flags.split()
                            self.ldflags = ldflags(*flags)  # TODO: use them !
            elif impl == 'PyPy':
                version = self.check_python('import sys; print(sys.version_info[0])')
                suffix = self.check_sysconfig('get_config_var("SHLIB_SUFFIX")')
                self.libfile = join(prefix, 'libs', f'libpypy{version}-c{suffix}')
                self.libpath = join(prefix, 'libs')
                self.lib = 'pypy' + version + '-c'
            else:
                raise ValueError('unsupported Python implementation')

            # Only publish the libpath if it isn't a system path
            if self.libpath in ['/usr/lib', '/usr/lib64']:
                self.libpath = None
        self.linkpath = linkpath(self.libpath) if self.libpath else linkpath()
        # FIXME: figure out the exact conditions under which this needs to be defined
        # condition=(set.cc.name=='msvc')|(set.cxx.name=='msvc'))
        self.libs = libs(self.lib)
        flags = self.check_sysconfig('get_config_var("MODLIBS")')
        flags += ' ' + self.check_sysconfig('get_config_var("SHLIBS")')
        flags = [f[2:] for f in flags.strip().split() if f.startswith('-l')]
        self.libs += libs(*flags)
        version = self.check_sysconfig('get_config_var("py_version")')
        if version >= '3.5':
            self.ext_suffix = self.check_sysconfig('get_config_var("EXT_SUFFIX")')
        else:
            self.ext_suffix = self.check_sysconfig('get_config_var("SO")')
