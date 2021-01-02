#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..utils import capture_output
from .artefact import dependency_error
import asyncio
from concurrent.futures import TimeoutError
import subprocess
import tempfile
import sys
import logging
import os
import re
import locale

logger = logging.getLogger('scheduler')
encoding = locale.getpreferredencoding(False)


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


class recipe(object):

    @classmethod
    def init(cls, jobs=1, timeout=0, noexec=False):
        cls.semaphore = asyncio.BoundedSemaphore(jobs)
        cls.timeout = timeout or None
        cls.noexec = noexec

    @classmethod
    def finish(cls): pass

    def __init__(self, action, targets, sources):
        self.action = action
        self.targets = targets
        self.sources = sources
        self.status = None
        self.stdout = None
        self.stderr = None

    async def __call__(self):

        if callable(self.action.command):
            self.status, self.stdout, self.stderr = self.run_callable()
        else:
            self.status, self.stdout, self.stderr = await self.run_async_subprocess()
        return self.status

    def variables(self):
        return {k: [v] for k, v in self.action.map(self.targets[0].frontend.features).items()}

    def run_callable(self):

        from ..action import CallError
        # Setting '__noexec__' allows a function to be run even in noexec mode.
        if recipe.noexec and not hasattr(self.action.command, '__noexec__'):
            return True, '', ''
        targets = [t.frontend for t in self.targets]
        sources = [s.frontend for s in self.sources]
        vars = self.variables()
        cmd = command_string(self.action.command, targets, sources, vars)
        with capture_output() as (out, err):
            status = True
            try:
                status = self.action.command(targets, sources)
                # let users indicate failure by explicitly returning 'False'
                if status is not False:
                    status = True
            except dependency_error:
                # dependency errors are fatal - there is no point
                # in carrying on...
                raise
            except CallError as e:
                status = False
                cmd = e.cmd
            except Exception as e:
                # while normal exceptions simply result in update
                # failures.
                print(e)
                import traceback as tb
                tb.print_exc()
                status = False
        stdout = out.getvalue()
        stderr = err.getvalue()
        self.action.__status__([t.frontend for t in self.targets],
                               status, cmd, 0, stdout, stderr)
        return status, stdout, stderr

    async def run_async_subprocess(self):
        vars = self.variables()
        async with recipe.semaphore:
            cmd = self.action.command
            # substitute $(<[N])
            for m in re.findall(r'(\$\(<\[(\d+)\]\))', cmd):
                cmd = cmd.replace(m[0], self.targets[int(m[1])].boundname)
            # substitute $(>[N])
            for m in re.findall(r'(\$\(>\[(\d+)\]\))', cmd):
                cmd = cmd.replace(m[0], self.sources[int(m[1])].boundname)

            vars.update([('<', [t.boundname for t in self.targets])])
            vars.update([('>', [s.boundname for s in self.sources])])
            for v in vars:
                cmd = cmd.replace('$({})'.format(v), ' '.join(vars.get(v, [])))
            # cmd.exe can't deal with multi-line commands, so use a temporary bat file.
            bat = None
            if sys.platform == 'win32' and ('\n' in cmd or '\r' in cmd):
                bat = tempfile.NamedTemporaryFile(suffix='.bat', mode='w', delete=False)
                with bat:
                    bat.write(cmd)
                process = await asyncio.create_subprocess_exec(f'{bat.name}',
                                                               stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
            else:
                process = await asyncio.create_subprocess_shell(cmd,
                                                                stdout=asyncio.subprocess.PIPE,
                                                                stderr=asyncio.subprocess.PIPE)
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=recipe.timeout)
                stdout = stdout and stdout.decode(encoding).strip()
                stderr = stderr and stderr.decode(encoding).strip()
                status = process.returncode == 0
            except TimeoutError:
                status, stdout, stderr = False, '', ''
            finally:
                if bat:
                    os.unlink(bat.name)
            self.action.__status__([t.frontend for t in self.targets],
                                   status, cmd, 0, stdout, stderr)
        return status, stdout, stderr

    @staticmethod
    def run_subprocess(cmd):
        # cmd.exe can't deal with multi-line commands, so use a temporary bat file.
        bat = None
        if sys.platform == 'win32' and ('\n' in cmd or '\r' in cmd):
            bat = tempfile.NamedTemporaryFile(suffix='.bat', mode='w', delete=False)
            with bat:
                bat.write(cmd)
            process = subprocess.Popen(['cmd.exe', '/Q', '/C', bat.name],
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(cmd,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = stdout and stdout.decode(encoding).strip()
        stderr = stderr and stderr.decode(encoding).strip()
        status = process.returncode == 0
        if bat:
            os.unlink(bat.name)
        return status, stdout, stderr
