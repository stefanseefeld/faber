#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import Artefact
from ..artefacts.library import Library
from ..tool import Tool
from ..feature import Feature, multi, path, incidental
from .. import types
from ..error import ArgumentError
from os.path import basename
from importlib import import_module
import logging

logger = logging.getLogger('tools')

cppflags = Feature('cppflags', attributes=multi|incidental)
define = Feature('define', attributes=multi|incidental)
include = Feature('include', attributes=multi|path|incidental)
cflags = Feature('cflags', attributes=multi|incidental)
cxxflags = Feature('cxxflags', attributes=multi|incidental)
ldflags = Feature('ldflags', attributes=multi|incidental)
link = Feature('link', ['static', 'shared'])
linkpath = Feature('linkpath', attributes=multi|path|incidental)
libs = Feature('libs', attributes=multi|incidental)
target = Feature('target', Feature(name='os', sub=True), Feature(name='arch', sub=True))
runpath = Feature('runpath', attributes=multi|path|incidental)
soname = Feature('soname', attributes=incidental)


class Compiler(Tool):

    path_spec = '{Compiler.name}-{Compiler.version}/{target.arch}/{link}/'

    @classmethod
    def split_libs(cls, sources):
        """split libraries from sources.
        Return (src, linkpath, libs)"""
        src = []
        libs = []
        linkpath = set()
        for s in sources:
            if isinstance(s, Library):
                libs.append(basename(s.libname))
                linkpath.add(s.path)
            elif isinstance(s, Artefact):
                src.append(s)
            else:
                raise ValueError('Unknown type of source {}'.format(s))
        return src, linkpath, libs

    @staticmethod
    def check_instance_for_type(type, features=None):
        """Make sure we have a matching compiler for the given type."""
        name = {types.c: 'CC',
                types.cxx: 'CXX'}[type]
        mod = import_module(f'.{name.lower()}', 'faber.tools')
        return getattr(mod, name).instance(features)

    @classmethod
    def try_instantiate(cls, name, fs=None):
        """Try to instantiate the given compiler, but fail silently."""

        try:
            module_, class_ = name.rsplit('.', 1)
            mod = import_module(f'.{module_}', 'faber.tools')
            getattr(mod, class_)(features=fs)
        except (SyntaxError, ArgumentError):  # these errors need to be reported.
            raise
        except Exception as e:
            logger.info('trying to instantiate {} yields "{}"'.format(name, e))
