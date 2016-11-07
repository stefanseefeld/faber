#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .utils import add_metaclass
from . import engine
from .feature import map
from .artefact import artefact
from copy import copy
import re

class action_type(type):
    def __new__(cls, name, bases, dict):
        """Collect all maps in a private dict so we don't have to 
        look them up each time we need them."""
        dict['_maps'] = {k:v for k,v in dict.iteritems() if isinstance(v,map)}
        return super(action_type, cls).__new__(cls, name, bases, dict)

@add_metaclass(action_type)
class action(object):
    """An action is executed in order to (re-)generate an 'artefact'."""

    var_ex = re.compile(r'\$\((?P<variable>\w+)\)')
    # make sure recipes are only defined once
    _defined_recipes = set()
    
    def __init__(self, *args):
        """Construct an action with one of these signatures:

          * action(command)
          * action(name, command)
          * action(name, command, vars)"""

        self.command = hasattr(self, 'command') and self.command
        self.name = self.__class__.__name__
        self.vars = []
        if len(args) == 0:
            pass
        elif len(args) == 1:
            self.command = args[0]
        elif len(args) == 2:
            self.name, self.command = args
        else:
            self.name, self.command, self.vars = args[:3]
        if type(self.command) is str and not self.vars:
            self.vars = action.var_ex.findall(self.command) if self.command else []
        self._cls = None
        self._tool = None
        self._qname = None

    def subst(self, old, new):
        self.command = self.command.replace(old, new)

    def __call__(self, *args, **kwds):
        if not self.command:
            raise ValueError('{} not implemented'.format(self.qname))
        elif callable(self.command):
            self.command(*args, **kwds)
        elif type(self.command) is str:
            artefact= len(args) and ' '.join(args[0]) or ''
            source= len(args) > 1 and ' '.join(args[1]) or ''
            cmd = self.command
            cmd = cmd.replace('$(<)', artefact)
            cmd = cmd.replace('$(>)', source)
            if artefact:
                vars = engine.variables(args[0][0])
                for v in self.vars:
                    cmd = cmd.replace('$({})'.format(v), ' '.join(vars[v]))
            return engine.run(self.name, artefact, cmd)

    @property
    def qname(self):
        if self._qname:
            return self._qname
        elif self._cls:
            return '{}.{}'.format(self._cls.__name__, self.name)
        else:
            return self.name

    def define(self, module):
        if not self._qname:
            engine.define_action(self.qname, self.command, module=module.qname())
            self._qname = module.qname(self.qname)

    def submit(self, artefacts, sources, module):
        if (self.qname, tuple([a.bound_name for a in artefacts])) in action._defined_recipes:
            return # already submitted
        else:
            action._defined_recipes.add((self.qname, tuple([a.bound_name for a in artefacts])))
        for a in artefacts:
            engine.set_variables(a.bound_name, **self.map(a.features))
        artefacts = [a.bound_name for a in artefacts]
        src = [s.bound_name if isinstance(s, artefact) else s for s in sources]
        engine.define_recipe(self.qname, artefacts, src)

    def map(self, fs):
        """translate the given feature-set using any map this action has defined."""
        return {k:v(fs) for k,v in self._maps.iteritems()}
