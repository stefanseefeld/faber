#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, source, notfile, always, nopropagate
from ..rule import rule, depend
from ..action import action
from ..utils import aslist
from .. import assembly
from .. import output
import logging
import sys

action_logger = logging.getLogger('actions')
command_logger = logging.getLogger('commands')


class assemble(action):

    def call(target, source, **kwds):
        self = composite._targets[target[0]]
        # create the real dependency graph...
        self._assemble()

    # run even in 'noexec' mode.
    # (see ..scheduler._pyaction)
    call.__noexec__ = True
    command = staticmethod(call)

    def __status__(self, targets, status, command, time, stdout, stderr):
        # suppress output unless we are in debug mode
        if action_logger.isEnabledFor(logging.DEBUG):
            if isinstance(targets, list):
                targets = ' '.join([t.qname for t in targets])
            else:
                targets = targets.qname
            action_logger.debug(output.coloured('{} {}'.format(self.qname, targets), attrs=['bold']))
        command_logger.debug(command)
        if not status:
            print(stderr, file=sys.stderr)


class composite(artefact):
    """A composite artefact is built in stages using one or more intermediates."""

    _targets = {}  # map assembler artefact to composite

    def __init__(self, name, sources, *args, **kwds):
        dependencies = kwds.pop('dependencies', [])
        artefact.__init__(self, name, *args, **kwds)
        self.sources = [source.instantiate(a, self.module) for a in aslist(sources)]
        self.dependencies = aslist(dependencies)
        self.features |= artefact.combine_use(self.sources)
        if self.features.dependencies():
            # postpone assembly until after dependencies are updated
            self._submit()
        else:
            # without any delayed values, assemble immediately
            self._assemble()

    def reset(self):
        # do not reset this artefact as we can't undo the assembly
        pass

    def __call__(self, features):
        c = artefact.__call__(self, features)
        if c.features.dependencies():
            c._submit()
        else:
            c._assemble()
        return c

    def _submit(self):
        a = rule(assemble(), 'a:' + self.name, attrs=notfile|always|nopropagate,
                 dependencies=self.sources + self.dependencies + self.features.dependencies())
        composite._targets[a] = self
        depend(self, a)

    def _assemble(self):
        from ..tools import compiler  # noqa F401
        if self.status is None:
            self.features.eval(update=False)
            assembly.rule(self, self.sources, self.features, module=self.module)
