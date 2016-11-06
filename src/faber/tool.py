#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .utils import add_metaclass
from .feature import feature, set
from .action import action
from collections import defaultdict
from copy import copy
import logging

logger = logging.getLogger(__name__)


class tool_type(type):
    def __init__(cls, name, bases, dict):
        """For any attribute of type 'action', set the action's name
        to the attribute name. Further, set the action's 'tool' attribute
        to be cls. This provides a means to look up virtual overloads. For
        example, if a rule refers to 'compiler.link', and the build is invoked
        with 'compiler=gcc', we can substitute 'gcc.link' for 'compiler.link'.
        """

        cls.tool = feature(name, name=feature(), version=feature())

        for k,v in dict.iteritems():
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
            a = copy(a)
            a._cls = cls
        return a


@add_metaclass(tool_type)
class tool(object):

    _instances = defaultdict(list)
    path_spec = ''
    target = '' # only needed for cross-compilers
    
    def __init__(self, name='', version=''):
        name = name or self.__class__.__name__
        self.features = set()
        # Register the tool with all base classes
        for c in self.__class__.__mro__:
            if issubclass(c, tool):
                tool._instances[c].append(self)
                self.features += c.tool(name=name, version=version)

        # Clone all actions, so tool instances can fine-tune them individually.
        for a in dir(self):
            o = getattr(self, a)
            if isinstance(o, action):
                o = copy(o)
                o._cls = self.__class__
                o._tool = self
                setattr(self, a, o)
        logger.debug('instantiate {} (name={}, version={})'
                     .format(self.__class__.__name__, name, version))

    @property
    def name(self):
        return self.features.tool.name.value

    @property
    def version(self):
        return self.features.tool.version.value

    @property
    def id(self):
        v = self.version
        return '{}-{}'.format(self.name, v) if v else self.name
    
    @classmethod
    def instance(cls, features=None):
        """Find an instance of cls that meets the feature requirements."""

        # make sure we have at least one instance of cls
        if not tool._instances[cls]: cls()

        features = features or feature_set()
        tools = [t for t in tool._instances[cls] if t.features in features]
        if tools:
            return tools[0]
        else:
            raise ValueError('No matching tool "{}" found'.format(cls.__name__))
