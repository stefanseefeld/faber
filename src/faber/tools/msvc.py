#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action, CallError
from ..feature import set as fset, map, translate, select_if
from ..artefact import artefact
from .. import types
from ..assembly import implicit_rule as irule
from ..utils import capture_output
from . import compiler
from .cc import cc
from .cxx import cxx, cxxstd
from ..artefacts.library import library
from os.path import basename, splitext, join, normpath, pathsep, exists, isabs, relpath
try:
    import winreg
except ImportError:  # python 2
    import _winreg as winreg
from collections import OrderedDict
from subprocess import *
from xml.dom.minidom import parseString
import logging
import os
import sys

logger = logging.getLogger('tools')


class makedep(action):

    # /showIncludes emits to stderr !
    command = 'cl /nologo $(cppflags) /showIncludes /EP $(>)'
    cppflags = map(compiler.cppflags)
    cppflags += map(compiler.define, translate, prefix='/D')
    cppflags += map(compiler.include, translate, prefix='/I"', suffix='"')


class makedep_wrapper(action):
    """This is a wrapper around `cl /showIncludes ...` to normalize the output and
    make it portable across compilers."""

    def __init__(self):
        self.cmd = makedep()
        action.__init__(self, self.cmd.name, self.makedep)

    def map(self, fs):
        return self.cmd.map(fs)  # just forward variables from makedep

    def makedep(self, targets, sources):
        with capture_output() as (out, err):
            try:
                status = self.cmd(targets, sources)
            except CallError:
                status = False
        stderr = err.getvalue()
        if status is False:
            # on error make sure to report stderr,
            # but only after stripping off the inclusion notes
            stderr = '\n'.join([l for l in stderr.split('\n')
                                if not l.startswith('Note: including file: ')])
            print(stderr, file=sys.stderr)
            return status
        # skip 'Note: including file: ', and remove dupliates
        headers = set([l[22:].lstrip() for l in stderr.split('\n')
                       if l.startswith('Note: including file: ')])
        # header paths are relative to the toplevel srcdir,
        # while we need them to be relative to the current module
        base = targets[0].module.srcdir
        rp = lambda f, base: f if isabs(f) else relpath(f, base)
        headers = [rp(h, base) + '\n' for h in headers]
        dfile = targets[0]._filename
        with open(dfile, 'w') as f:
            f.writelines(headers)


class compile(action):

    command = 'cl /nologo $(cppflags) $(cflags) $(cxxflags) /GR /MD /EHsc /c /Fo$(<) $(>)'
    cppflags = map(compiler.cppflags)
    cppflags += map(compiler.define, translate, prefix='/D')
    cppflags += map(compiler.include, translate, prefix='/I"', suffix='"')
    cflags = map(compiler.cflags)
    cxxflags = map(compiler.cxxflags)
    cxxflags += map(cxxstd, translate, prefix='/std:c++')


class link(action):

    command = 'link /nologo $(ldflags) /out:$(<) $(>) $(libs)'
    ldflags = map(compiler.ldflags)
    ldflags += map(compiler.linkpath, translate, prefix='/libpath:"', suffix='"')
    ldflags += map(compiler.link, select_if, 'shared', '/DLL')
    libs = map(compiler.libs, translate, suffix='.lib')

    def submit(self, targets, sources):
        # sources may contain object files as well as libraries
        # Separate the two, and add the libraries to the libs variable.

        src, linkpath, libs = msvc.split_libs(sources)
        linkpath = [compiler.linkpath(l, base='') for l in linkpath]
        libs = [compiler.libs(l) for l in libs]
        fs = fset(*libs + linkpath)
        for t in targets:
            t.features |= fs
        action.submit(self, targets, src)


class archive(action):

    command = 'lib /nologo /out:$(<) $(>)'


class msvc(cc, cxx):

    # available toolchains by version
    _toolchains = OrderedDict()
    known_archs = ['x86_64', 'x86']
    win_archs = {'x86_64': 'x64',
                 'x86': 'x86'}

    makedep = makedep_wrapper()
    compile = compile()
    archive = archive()
    link = link()

    @classmethod
    def split_libs(cls, sources):
        """split libraries from sources.
        Return (src, linkpath, libs)"""

        src = []
        libs = []
        linkpath = set()
        for s in sources:
            if isinstance(s, library):
                libs.append(s.filename.apply(lambda x: splitext(basename(x))[0]))
                linkpath.add(s.path)
            elif isinstance(s, artefact):
                src.append(s)
            else:
                raise ValueError('Unknown type of source {}'.format(s))
        return src, linkpath, libs

    def __init__(self, name='msvc', command=None, version='', features=()):

        features = fset.instantiate(features)
        if not version:
            version = self.find_version_requirement(features)
        if not version and len(msvc._toolchains):
            version = list(msvc._toolchains)[0]
        if version not in msvc._toolchains:
            raise ValueError(f'unknown MSVC version {version}')
        arch = str(features.target.arch) if 'target' in features else None
        if arch and arch not in msvc._toolchains[version]:
            raise ValueError(f'MSVC {version} does not support target architecture {arch}')
        if arch:
            product_dir, path = msvc._toolchains[version][arch]
            features |= compiler.target(os='Windows')
        else:
            arch, (product_dir, path) = list(msvc._toolchains[version].items())[0]
            features |= compiler.target(arch=arch, os='Windows')
        super(msvc, self).__init__(name=name, version=version)
        self.features |= features

        self.makedep.cmd.subst('cl', '"{}\\{}"'.format(path, 'cl'))
        self.compile.subst('cl', '"{}\\{}"'.format(path, 'cl'))
        self.archive.subst('lib', '"{}\\{}"'.format(path, 'lib'))
        self.link.subst('link', '"{}\\{}"'.format(path, 'link'))

        # Extract INCLUDE, LIB, and LIBPATH from setup script
        setup = join(product_dir, 'vcvarsall.bat')
        output = check_output([setup, msvc.win_archs[arch], '&', 'set']).decode()
        vars = dict(line.split('=', 1) for line in output.splitlines() if '=' in line)
        self.vars = {k: vars[k] for k in ('INCLUDE', 'LIB', 'LIBPATH')}
        include = compiler.include(*[i for i in self.vars['INCLUDE'].split(pathsep) if i])
        linkpath = compiler.linkpath(*[l for l in self.vars['LIB'].split(pathsep) if l])
        linkpath += compiler.linkpath(*[l for l in self.vars['LIBPATH'].split(pathsep) if l])
        self.features += include
        self.features += linkpath

        irule(self.compile, types.obj, types.c)
        irule(self.compile, types.obj, types.cxx)
        irule(self.archive, types.lib, types.obj)
        irule(self.link, types.bin, (types.obj, types.dso, types.lib))
        irule(self.link, types.dso, (types.obj, types.dso, types.lib))

    @classmethod
    def find_path(cls, product_dir, arch):
        setup = join(product_dir, 'vcvarsall.bat')
        output = check_output([setup, arch, '&', 'set']).decode()
        vars = dict(line.split('=', 1) for line in output.splitlines() if '=' in line)
        path = vars['Path']
        for p in path.split(pathsep):
            if exists(join(p, 'cl.exe')):
                return p

    @classmethod
    def discover(cls):

        # start with versions reported by `vswhere`
        root = os.environ['ProgramFiles(x86)']
        vswhere = join(root, 'Microsoft Visual Studio', 'Installer', 'vswhere.exe')
        try:
            vswhere_cmd = [vswhere,
                           '-products', '*',
                           '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                           '-format', 'xml']
            logger.debug(f"executing {' '.join(vswhere_cmd)}")
            output = check_output(vswhere_cmd).decode()
            instances = parseString(output).getElementsByTagName('instance')
            for i in instances:
                installation_path = i.getElementsByTagName('installationPath')[0].childNodes[0].data
                version = i.getElementsByTagName('productDisplayVersion')[0].childNodes[0].data
                logger.debug(f'result: installation_path={installation_path}, version={version}')
                ipath = join(installation_path, 'VC', 'Auxiliary', 'Build')
                # This reports a different version, though the meaning of it isn't clear:
                # version = open(join(ipath, 'Microsoft.VCToolsVersion.default.txt')).read().strip()
                cls._toolchains[version] = OrderedDict()
                for arch in msvc.known_archs:
                    product_dir, path = ipath, None
                    try:
                        path = cls.find_path(ipath, msvc.win_archs[arch])
                    except Exception:
                        pass
                    if path:
                        cls._toolchains[version][arch] = (normpath(product_dir), normpath(path))
                        logger.info(f'vswhere discovered MSVC version={version} arch={arch}')
                if not cls._toolchains[version]:
                    # remove empty entries
                    del cls._toolchains[version]
        except Exception as e:
            logger.debug(f'{e}')
            pass

        # Known toolset versions, in order of preference.
        known_versions = ['15.0',
                          '14.0',
                          '12.0',
                          '11.0',
                          '10.0',
                          '10.0express',
                          '9.0',
                          '9.0express',
                          '8.0',
                          '8.0express',
                          '7.1',
                          '7.1toolkit',
                          '7.0',
                          '6.0']

        # Names of registry keys containing the Visual C++ installation path (relative
        # to "HKEY_LOCAL_MACHINE\SOFTWARE\\Microsoft").
        reg_keys = {'6.0': 'VisualStudio\\6.0\\Setup\\Microsoft Visual C++',
                    '7.0': 'VisualStudio\\7.0\\Setup\\VC',
                    '7.1': 'VisualStudio\\7.1\\Setup\\VC',
                    '8.0': 'VisualStudio\\8.0\\Setup\\VC',
                    '8.0express': 'VCExpress\\8.0\\Setup\\VC',
                    '9.0': 'VisualStudio\\9.0\\Setup\\VC',
                    '9.0express': 'VCExpress\\9.0\\Setup\\VC',
                    '10.0': 'VisualStudio\\10.0\\Setup\\VC',
                    '10.0express': 'VCExpress\\10.0\\Setup\\VC',
                    '11.0': 'VisualStudio\\11.0\\Setup\\VC',
                    '12.0': 'VisualStudio\\12.0\\Setup\\VC',
                    '14.0': 'VisualStudio\\14.0\\Setup\\VC',
                    '15.0': 'VisualStudio\\15.0\\Setup\\VC'}

        for version in known_versions:
            cls._toolchains[version] = OrderedDict()
            for arch in msvc.known_archs:
                product_dir, path = None, None
                for x64elt in ('', 'Wow6432Node\\'):
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                            'SOFTWARE\\{}Microsoft\\{}'
                                            .format(x64elt, reg_keys[version])) as key:
                            product_dir = winreg.QueryValueEx(key, "ProductDir")[0]
                            path = cls.find_path(product_dir, msvc.win_archs[arch])
                    except Exception:
                        pass
                if path:
                    cls._toolchains[version][arch] = (normpath(product_dir), normpath(path))
                    logger.info(f'discovered via registry MSVC version={version} arch={arch}')
            if not cls._toolchains[version]:
                # remove empty entries
                del cls._toolchains[version]

    @classmethod
    def instances(cls, fs=None):
        """Return all known MSVC instances."""

        if not msvc.instantiated():
            for v in msvc._toolchains:
                for a, _ in msvc._toolchains[v].items():
                    msvc(version=v, features=compiler.target(arch=a))
        return super(cc, cls).instances(fs)


# If this module is imported, assume we are running inside Windows
msvc.discover()
