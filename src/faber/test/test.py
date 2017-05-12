#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, notfile, nocare, always
from ..action import action
from ..rule import rule, depend
from .. import output
from . import pass_, fail, xpass, xfail

class test(artefact):
    """A test is an artefact that may fail, and which reports success."""

    run = action('run', '$(>)')

    def __init__(self, name, sources, run=False, depends=[], features=(), expected=pass_):

        self.run = run
        self.depends = depends
        artefact.__init__(self, name, sources, attrs=notfile|nocare|always,
                          features=features)
        self.xoutcome = expected
        self.outcome = None

    def expand(self):
        if self.run is True:
            rule(self, self.sources, recipe=test.run, depends=self.depends)
        elif isinstance(self.run, action):
            rule(self, self.sources, recipe=self.run, depends=self.depends)
        else:
            depend(self, self.sources + self.depends)

    def __status__(self, *args):

        artefact.__status__(self, *args)
        if self.status == 1:
            self.outcome = xfail if self.xoutcome == fail else fail
        else:
            self.outcome = xpass if self.xoutcome == fail else pass_
        output.log_test_status(self.name, self.outcome)
