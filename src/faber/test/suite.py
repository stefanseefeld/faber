#
# Copyright (c) 2019 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .test import *
from ..artefact import artefact, notfile


class suite(artefact):
    """A test suite provides an alias to a set of tests."""

    def __init__(self, name, tests, attrs=notfile, module=None):
        """tests consists of either test objects or other suites."""
        super(suite, self).__init__(name, attrs=attrs|notfile, module=module)
        self.tests = tests
        depend(self, self.tests)

    def __iter__(self):
        for t in self.tests:
            if isinstance(t, suite):
                # Use `yield from` once we stop supporting Python 2.7
                for i in t:
                    yield i
            else:
                yield t
