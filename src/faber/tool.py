#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from .utils import add_metaclass
from .feature import feature, set
from .action import action
from .error import ArgumentError
from collections import defaultdict
from copy import deepcopy
import logging

logger = logging.getLogger('tools')


class tool_type(type):
    def __init__(cls, name, bases, dict):
        """For any attribute of type 'action', set the action's name
        to the attribute name. Further, set the action's 'tool' attribute
        to be cls. This provides a means to look up virtual overloads. For
        example, if a rule refers to 'compiler.link', and the build is invoked
        with 'compiler=gcc', we can substitute 'gcc.link' for 'compiler.link'.
        """

        cls.tool = feature(name, feature('name', sub=True), feature('version', sub=True))

        for k, v in dict.items():
            if isinstance(v, action):
                v._cls = cls
                v.name = k

    def __getattribute__(cls, name):
        """Re-define action lookup.

        If 'A' defines 'action', a lookup via a subclass 'B' as 'B.action'
        needs to result in an action that is aware of it belonging to 'B'.

        To that end we make sure that 'B.action' and 'A.action' return
        distinct objects (each referring to the appropriate class 'A' and 'B'
        respectively)."""

        a = type.__getattribute__(cls, name)
        if isinstance(a, action) and a._cls is not cls:
            a = deepcopy(a)
            a._cls = cls
        return a


@add_metaclass(tool_type)
class tool(object):

    _instances = defaultdict(list)
    path_spec = ''

    @staticmethod
    def finish():
        tool._instances.clear()

    @classmethod
    def find_version_requirement(cls, features):
        """Find (and validate) any version requirements for 'cls' in 'features'."""
        f1 = None
        for c in cls.__mro__:
            if issubclass(c, tool) and c != tool:
                f2 = features[c.__name__] if (c.__name__ in features and
                                              features[c.__name__].version) else None
                if f2:
                    if f1 and f1.version != f2.version:
                        n1, n2 = f1._type.name, f2._type.name
                        raise ArgumentError('conflicting version requirements '
                                            '{}.version={} and {}.version={}'
                                            .format(n1, f1.version, n2, f2.version))
                    else:
                        f1 = f2
        return str(f1.version) if f1 and f1.version is not None else ''

    def __init__(self, name='', version='', features=()):
        name = name or self.__class__.__name__
        self.features = set.instantiate(features).copy()
        # Set built-in features
        for c in self.__class__.__mro__:
            if issubclass(c, tool) and c != tool:
                self.features += c.tool(name=name, version=version)

        # Clone all actions, so tool instances can fine-tune them individually.
        for a in dir(self):
            o = getattr(self, a)
            if isinstance(o, action):
                o = deepcopy(o)
                o._cls = self.__class__
                o._tool = self
                setattr(self, a, o)

        # Register the tool with all base classes
        for c in self.__class__.__mro__:
            if issubclass(c, tool) and c != tool:
                tool._instances[c].append(self)

        logger.info('instantiate {} (name={}, version={})'
                    .format(self.__class__.__name__, name, version))

    @property
    def name(self):
        return str(self.features[self.__class__.__name__].name)

    @property
    def version(self):
        return str(self.features[self.__class__.__name__].version)

    @property
    def id(self):
        v = self.version
        return '{}-{}'.format(self.name, v) if v else self.name

    @classmethod
    def instantiated(cls, fs=None):
        """Check whether a tool of the given type and feature-set
        is already instantiated."""
        if fs is None:
            return tool._instances[cls]
        else:
            fs = set.instantiate(fs)
            return any([t for t in tool._instances[cls] if t.features.matches(fs)])

    @classmethod
    def instances(cls, fs=None):
        """Return all known instances of cls that meet the feature requirements."""

        fs = set.instantiate(fs)
        try:  # Lookup failure is not an error
            cls.instance(fs)
        except Exception:
            pass
        return [t for t in tool._instances[cls] if t.features.matches(fs)]

    @classmethod
    def instance(cls, fs=None):
        """Find an instance of cls that meets the feature requirements."""

        fs = set.instantiate(fs)
        if not cls.instantiated(fs):
            try:
                cls(features=fs)
            except Exception as e:
                from . import debug
                logger.info('trying to instantiate {} yields "{}"'
                            .format(cls.__name__, e))
                if debug:
                    import traceback
                    traceback.print_exc()
        tools = [t for t in tool._instances[cls] if t.features.matches(fs)]
        if tools:
            return tools[0]
        else:
            raise ValueError('No matching tool "{}" found'.format(cls.__name__))


def info(name, fs=()):

    from importlib import import_module
    tools = []
    try:
        import faber.tools  # noqa F401
        mod = import_module('.{}'.format(name), 'faber.tools')
        tool = getattr(mod, name)
        tools += tool.instances(fs)
    except Exception:
        pass
    if not tools:
        msg = 'no tools of type {} found'.format(name)
        msg += ' matching {}.'.format(fs.essentials()) if fs else '.'
        print(msg)
        return
    table = [['tool', 'name', 'version']]
    for t in tools:
        table.append([t.__class__.__name__, t.name, t.version])
    width = map(max, zip(*[map(len, t) for t in table]))
    format = '{{:{}}}\t{{:{}}}\t{{:{}}}'.format(*width)
    for t in table:
        print(format.format(*t))
