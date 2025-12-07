#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import Artefact, notfile
from ..rule import depend
from .. import output
from .. import logging


def init(builddir):
    from .check import Cache, Logfiles, Check
    Check.cache = Cache(builddir)
    Check.logfiles = Logfiles()


def finish():
    from .check import Check
    if Check.cache:
        Check.cache.finish()
        Check.cache = None
    Check.logfiles.clear()


def reset(level):
    from .check import Check
    Check.logfiles.reset()
    if Check.cache:
        Check.cache.reset(level)


def clean(level):
    from .check import Check
    if level > 1:
        Check.logfiles.clean()
        if Check.cache:
            Check.cache.clean()


class Report(Artefact):

    def __init__(self, name, checks):
        use = [c.use for c in checks]
        Artefact.__init__(self, name, attrs=notfile, use=use)
        depend(self, checks)
        self.checks = checks

    def _report(self):

        logger = logging.getLogger('summary')

        max_name_length = max(len(c.qname) for c in self.checks)
        logger.info(output.coloured('configuration check results:', attrs=['bold']))
        for c in self.checks:
            logger.info('  {:{}} : {} {}'
                        .format(c.qname, max_name_length, c.result, '(cached)' if c.cached else ''))

    def __status__(self, status):
        Artefact.__status__(self, status)
        self._report()
