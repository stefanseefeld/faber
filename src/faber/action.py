#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from .utils import add_metaclass
from . import scheduler
from .feature import set, map
from .utils import aslist
from . import output
import re
import logging
import sys

action_logger = logging.getLogger('actions')
command_logger = logging.getLogger('commands')
output_logger = logging.getLogger('output')


class CallError(Exception):
    """CallErrors may be used to pass the command string back
    up the call chain so it can be reported."""

    def __init__(self, cmd):
        Exception.__init__(self, 'Error calling {}'.format(cmd))
        self.cmd = cmd


class action_type(type):
    def __new__(cls, name, bases, dict):
        """Collect all maps in a private dict so we don't have to
        look them up each time we need them."""
        dict['_maps'] = {k: v for k, v in dict.items() if isinstance(v, map)}
        return super(action_type, cls).__new__(cls, name, bases, dict)


@add_metaclass(action_type)
class action(object):
    """An action is executed in order to (re-)generate an 'artefact'."""

    var_ex = re.compile(r'\$\((?P<variable>\w+)\)')

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
    def features(self):
        return self._tool.features if self._tool else set()

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

        # Make sure this action is instantiated.
        self = self.instantiate()

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
            # substitute $(<[N])
            for m in re.findall(r'(\$\(<\[(\d+)\]\))', cmd):
                cmd = cmd.replace(m[0], tnames[int(m[1])])
            # substitute $(>[N])
            for m in re.findall(r'(\$\(>\[(\d+)\]\))', cmd):
                cmd = cmd.replace(m[0], snames[int(m[1])])
            # substitute $(<)
            cmd = cmd.replace('$(<)', ' '.join(tnames))
            # substitute $(>)
            cmd = cmd.replace('$(>)', ' '.join(snames))
            if targets:
                vars = self.map(targets[0].features)
                for v in self.vars:
                    cmd = cmd.replace('$({})'.format(v), vars.get(v) or '')
            status, stdout, stderr = scheduler.run(cmd)
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            if not status:
                raise CallError(cmd)
            return status

    def submit(self, targets, sources):
        if not self.command:
            raise RuntimeError(None, ': {} is not implemented'.format(self.qname))
        scheduler.define_recipe(self, targets, sources)

    def map(self, fs):
        """translate the given feature-set using any map this action has defined."""
        fs.eval(update=False)
        if self._maps:
            return {k: v(fs) for k, v in self._maps.items()}
        else:
            return {v: str(fs[v]) if v in fs else '' for v in self.vars}

    def __status__(self, targets, status, command, time, stdout, stderr):
        """Report completion of the recipe."""
        logfile = targets[0].logfile
        targets = ' '.join([t.qname for t in targets])
        alog = output.coloured('{} {}'.format(self.qname, targets), attrs=['bold'])
        if logfile:
            logfile.write(alog + '\n')
            logfile.write(command + '\n')
            if stdout:
                logfile.write(stdout)
            if stderr:
                logfile.write(stderr)
        else:
            action_logger.info(alog)
            command_logger.info(command, extra={'time': time})
            if stdout:
                output_logger.info(stdout)
            if stderr:
                output_logger.info(stderr)
