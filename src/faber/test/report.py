#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, notfile, always
from ..rule import depend
from .. import output
from . import pass_, fail, xpass, xfail

class report(artefact):
    """A test report runs a set of tests and reports a summary."""

    def __init__(self, *tests):

        artefact.__init__(self, 'report', sources=list(tests), attrs=notfile|always)

    def expand(self):
        depend(self, self.sources)

    def print_summary(self):
        passes = sum(1 for s in self.sources if s.outcome == pass_)
        failures = sum(1 for s in self.sources if s.outcome == fail)
        xfailures = sum(1 for s in self.sources if s.outcome == xfail)
        untested = sum(1 for s in self.sources if s.outcome == None)
        output.log_test_summary(passes, failures, xfailures, untested)

    def __status__(self, *args):

        artefact.__status__(self, *args)
        self.print_summary()
