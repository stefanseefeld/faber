#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import engine
from .artefact import artefact
from copy import copy

class action(object):
    """An action is executed in order to (re-)generate an 'artefact'."""

    def __init__(self, *args):
        """Construct an action with one of these signatures:

          * action(command)
          * action(name, command)"""

        if len(args) == 0:
            self.name = self.command = None
        elif len(args) == 1:
            self.name, self.command = None, args[0]
        elif len(args) == 2:
            self.name, self.command = args
        else:
            self.name, self.command = args[:2]
        self._cls = None

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
            return engine.run(self.name, artefact, cmd)

    @property
    def qname(self):
        if self._cls:
            return '{}.{}'.format(self._cls.__name__, self.name)
        else:
            return self.name

    def define(self, module):
        if not self._qname:
            engine.define_action(self.qname, self.command, module=module.qname())
            self._qname = module.qname(self.qname)

    def submit(self, artefacts, sources, module):
        artefacts = [a.bound_name for a in artefacts]
        src = [s.bound_name if isinstance(s, artefact) else s for s in sources]
        engine.define_recipe(self.qname, artefacts, src)

