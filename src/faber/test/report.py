#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, notfile, always
from ..rule import rule
from .. import output
from .. import logging
from .suite import suite
from . import pass_, fail, xfail


class report(artefact):
    """A test report runs a set of tests and reports a summary."""

    def __init__(self, name, tests, fail_on_failures=False):
        """Construct a report. Arguments are the tests to be performed."""

        artefact.__init__(self, name, attrs=notfile|always)
        rule(self.print_summary, self, tests)
        self._tests = tests
        self.fail_on_failures = fail_on_failures

    @property
    def tests(self):
        for t in self._tests:
            if isinstance(t, suite):
                # Use `yield from` once we stop supporting Python 2.7
                for i in t:
                    yield i
            else:
                yield t

    def print_summary(self, targets, sources):
        """Print a summary of the report."""

        logger = logging.getLogger('summary')

        passes = sum(1 for s in self.tests if s.outcome == pass_)
        failures = [s for s in self.tests if s.outcome == fail]
        xfailures = sum(1 for s in self.tests if s.outcome == xfail)
        skipped = sum(1 for s in self.tests if s.outcome is None)

        p = passes and '{} pass'.format(passes) or ''
        if passes > 1: p += 'es'
        nfailures = len(failures)
        colour = 'red' if nfailures else 'green'
        f = nfailures and '{} failure'.format(nfailures) or ''
        if nfailures > 1: f += 's'
        x = xfailures and '{} expected failure'.format(xfailures) or ''
        if xfailures > 1: x += 's'
        s = skipped and '{} skipped'.format(skipped) or ''
        line = ', '.join([o for o in [p, f, x, s] if o])

        logger.info(output.coloured('test summary: ' + line, colour, attrs=['bold']))
        if failures:
            logger.info(output.coloured('failures:', 'red', attrs=['bold']))
            for f in failures:
                logger.info(output.coloured(f.qname, 'red', attrs=['bold']))
                if f.output[1]:  # if there is output on stderr...
                    logger.info(f.output[1])
            if self.fail_on_failures:
                return False
        return True
