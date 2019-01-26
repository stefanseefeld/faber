#
# Copyright (c) 2019 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ... import test
from ...artefact import notfile, always, internal
from ...rule import rule, depend
from ...action import action
from ...tools import compiler
from ...feature import map, join
from ... import platform
from ...utils import capture_output
import re


class test_module(test.suite):
    """A test module represents all the test cases contained
    in a single Boost.Test executable."""

    class run(action):

        runpath = map(compiler.runpath, join)
        if platform.os == 'Windows':
            command = """set PATH=$(runpath);%PATH%
$(>)"""
        else:
            command = 'LD_LIBRARY_PATH=$(runpath) $(>)'

        def __init__(self, args):
            super(test_module.run, self).__init__(test_module.run.command + ' ' + ' '.join(args))

    def __init__(self, name, exe, **kwds):
        super(test_module, self).__init__(name, [], **kwds)
        self.exe = exe
        a = rule(self.query, 't:' + self.name, sources=self.exe,
                 attrs=notfile|always|internal)
        depend(self, a)

    def reset(self):
        pass

    def query(self, target, source):

        runpath = 'linkpath' in target[0].features and compiler.runpath(str(target[0].features.linkpath))
        target[0].features += runpath
        a = self.run(['--list_content'])
        with capture_output() as (out, err):
            result = a(target, source)
        if result:
            stdout = out.getvalue()
            for name in self.parse(stdout):
                t = test.test(name, self.exe, run=self.run(['-x', 'no', '-t', name]),
                              module=self.module,
                              features=runpath)
                self.tests.append(t)
                depend(self, t)

    @staticmethod
    def parse(output):
        """Parse the output generated from boost.test using the --list_content option."""

        stack = []
        indents = [-1]
        for line in output.split('\n'):
            m = re.match(r'(?P<indent>\s*)(?P<name>[^*:\s]*)', line)
            indent, name = len(m.group(1)), m.group(2)
            if indent > indents[-1]:
                indents.append(indent)
                stack.append(name)
            elif indent == indents[-1]:
                yield '/'.join(stack)
                stack[-1] = name
            else:
                yield '/'.join(stack)
                while indent < indents[-1]:
                    indents.pop()
                    stack.pop()
                stack[-1] = name
