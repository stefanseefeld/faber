#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, notfile
from ..rule import depend
from .. import output
from .. import logging


def init(builddir):
    from .check import cache, logfiles, check
    check.cache = cache(builddir)
    check.logfiles = logfiles()


def finish():
    from .check import check
    if check.cache:
        check.cache.finish()
        check.cache = None
    check.logfiles.clear()


def reset(level):
    from .check import check
    check.logfiles.reset()
    if check.cache:
        check.cache.reset(level)


def clean(level):
    from .check import check
    if level > 1:
        check.logfiles.clean()
        if check.cache:
            check.cache.clean()


class report(artefact):

    def __init__(self, name, checks):
        use = [c.use for c in checks]
        artefact.__init__(self, name, attrs=notfile, use=use)
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
        artefact.__status__(self, status)
        self._report()
