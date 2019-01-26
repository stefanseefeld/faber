#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, notfile, nocare, always
from ..action import action
from ..feature import map, join
from ..rule import rule, depend
from ..tools import compiler
from .. import platform
from .. import output
from ..utils import aslist
from . import pass_, fail, xpass, xfail
import logging

logger = logging.getLogger('actions')


class test(artefact):
    """A test is an artefact that is typically performed as part of a test suite, with
    special support to collect and report the test outcome."""

    class run(action):

        runpath = map(compiler.runpath, join)
        if platform.os == 'Windows':
            command = """set PATH=$(runpath);%PATH%
$(>)"""
        else:
            command = 'LD_LIBRARY_PATH=$(runpath) $(>)'

    def __init__(self, name, sources, run=False, dependencies=[], features=(),
                 condition=None, expected=pass_, module=None):
        """Create a test.

        Arguments:
          * name: the test's name
          * sources: artefact(s) to be tested
          * run: Specify what to do. Possible values:

             - `False` (default): do nothing (but report whether source was updated successfully)
             - `True`: Run sources
             - an action: Perform action

          * depends: any prerequisite artefacts that have to be completed
          * features: additional features needed to perform this test
          * condition: either a boolean or a feature condition to indicate if this test is to be performed or skipped.
          * expected: the expected outcome"""

        artefact.__init__(self, name, attrs=notfile|nocare|always, features=features, condition=condition, module=module)
        sources = aslist(sources)
        self.xoutcome = expected
        self.outcome = None
        self.command = ''
        self.output = ('', '')
        if run is True:
            rule(test.run(), self, sources, dependencies=dependencies)
        elif run is False:
            depend(self, sources + dependencies)
        else:
            rule(run, self, sources, dependencies=dependencies)

    def __status__(self, status):

        artefact.__status__(self, status)
        if self.status is True:
            self.outcome = xpass if self.xoutcome == fail else pass_
        else:
            self.outcome = xfail if self.xoutcome == fail else fail
        colour = {pass_: 'green',
                  fail: 'red',
                  xpass: 'yellow',
                  xfail: 'green'}[self.outcome]
        label = {pass_: 'PASS',
                 fail: 'FAIL',
                 xpass: 'XPASS',
                 xfail: 'XFAIL'}[self.outcome]
        logger.info('{}: {}'.format(self.qname, output.coloured(label, colour)))
