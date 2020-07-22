#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact
from ..artefacts.library import library
from ..tool import tool
from ..feature import feature, multi, path, incidental
from .. import types
from ..error import ArgumentError
from os.path import basename
from importlib import import_module
import logging

logger = logging.getLogger('tools')

cppflags = feature('cppflags', attributes=multi|incidental)
define = feature('define', attributes=multi|incidental)
include = feature('include', attributes=multi|path|incidental)
cflags = feature('cflags', attributes=multi|incidental)
cxxflags = feature('cxxflags', attributes=multi|incidental)
ldflags = feature('ldflags', attributes=multi|incidental)
link = feature('link', ['static', 'shared'])
linkpath = feature('linkpath', attributes=multi|path|incidental)
libs = feature('libs', attributes=multi|incidental)
target = feature('target', feature(name='os', sub=True), feature(name='arch', sub=True))
runpath = feature('runpath', attributes=multi|path|incidental)
soname = feature('soname', attributes=incidental)


class compiler(tool):

    path_spec = '{compiler.name}-{compiler.version}/{target.arch}/{link}/'

    @classmethod
    def split_libs(cls, sources):
        """split libraries from sources.
        Return (src, linkpath, libs)"""
        src = []
        libs = []
        linkpath = set()
        for s in sources:
            if isinstance(s, library):
                libs.append(basename(s.libname))
                linkpath.add(s.path)
            elif isinstance(s, artefact):
                src.append(s)
            else:
                raise ValueError('Unknown type of source {}'.format(s))
        return src, linkpath, libs

    @staticmethod
    def check_instance_for_type(type, features=None):
        """Make sure we have a matching compiler for the given type."""
        name = {types.c: 'cc',
                types.cxx: 'cxx'}[type]
        mod = import_module('.{}'.format(name), 'faber.tools')
        return getattr(mod, name).instance(features)

    @classmethod
    def try_instantiate(cls, name, fs=None):
        """Try to instantiate the given compiler, but fail silently."""

        try:
            mod = import_module('.{}'.format(name), 'faber.tools')
            getattr(mod, name)(features=fs)
        except (SyntaxError, ArgumentError):  # these errors need to be reported.
            raise
        except Exception as e:
            logger.info('trying to instantiate {} yields "{}"'.format(name, e))
