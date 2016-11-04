#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .utils import aslist
from . import scheduler
from . import output
import logging

action_logger = logging.getLogger('actions')
command_logger = logging.getLogger('commands')


class CallError(Exception):
    """CallErrors may be used to pass the command string back
    up the call chain so it can be reported."""

    def __init__(self, cmd):
        Exception.__init__(self, 'Error calling {}'.format(cmd))
        self.cmd = cmd


class action(object):
    """An action is executed in order to (re-)generate an 'artefact'."""

    @staticmethod
    def command_string(func, targets, sources, kwds):
        """Make a string of the command to be executed,
        for reporting purposes."""
        args= [repr(targets[0])] if len(targets) == 1 \
            else [] if not targets else [repr(targets)]
        if sources:
            args.append(repr(sources[0]) if len(sources) == 1
                        else repr(sources))
        if kwds:
            args.append(', '.join(['{}={}'.format(k, repr(v))
                                   for k, v in kwds.items()]))
        return '{}({})'.format(func.__name__, ', '.join(args))

    @property
    def qname(self):
        """The qualified name of this action."""
        if self._cls:
            return '{}.{}'.format(self._cls.__name__, self.name)
        else:
            return self.name

    @property
    def id(self):
        """Yield a unique identifier for this action."""
        return '%s-%x' % (self.qname, id(self))

    @property
    def tool(self):
        """The tool this action is a method of. (May be None)"""
        return self._tool

    @property
    def abstract(self):
        """The action is 'abstract' if it is a tool method
        without a tool instance."""
        return self._cls and not self._tool

    @property
    def path_spec(self):
        return self._tool.path_spec if self._tool else ''

    def __init__(self, *args):
        """Construct an action with one of these signatures:

          * action(command)
          * action(name, command)
          * action(name, command, vars)"""

        self.command = hasattr(self, 'command') and self.command
        self.name = self.__class__.__name__
        if len(args) == 0:
            pass
        elif len(args) == 1:
            self.command = args[0]
        elif len(args) == 2:
            self.name, self.command = args
        else:
            self.name, self.command, self.vars = args[:3]
        self._cls = None
        self._tool = None

    def instantiate(self, features=()):
        """If this action is abstract, find a tool matching the given
        features and return the corresponding concrete action."""

        if self._cls and not self._tool:
            tool = self._cls.instance(features)
            return getattr(tool, self.name)
        else:
            return self

    def subst(self, old, new):
        self.command = self.command.replace(old, new, 1)

    def __call__(self, targets, sources=[], **kwds):
        """Explicitly call the action with the given artefacts."""

        tnames = [t.boundname for t in aslist(targets)]
        snames = [s.boundname for s in aslist(sources)]
        if not self.command:
            raise ValueError('{} not implemented'.format(self.qname))
        elif callable(self.command):
            status = self.command(targets, sources, **kwds)
            if status is False:
                cmd = action.command_string(self.command, tnames, snames, kwds)
                raise CallError(cmd)
            return status
        elif type(self.command) is str:
            cmd = self.command
            cmd = cmd.replace('$(<)', ' '.join(tnames))
            cmd = cmd.replace('$(>)', ' '.join(snames))
            status, stdout, stderr = scheduler.run(cmd)
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            if not status:
                raise CallError(cmd)
            return status

    def submit(self, targets, sources):
        if not self.command:
            raise RuntimeError(None, ': {} is not implemented'.format(self.qname))
        scheduler.define_action(self)
        scheduler.define_recipe(self, targets, sources)

    def __status__(self, targets, status, command, stdout, stderr):
        """Report completion of the recipe."""
        targets = ' '.join([t.qname for t in targets])
        action_logger.info(output.coloured('{} {}'.format(self.qname, targets), attrs=['bold']))
        command_logger.info(command)
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
