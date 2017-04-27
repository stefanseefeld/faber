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


class report(artefact):

    def __init__(self, name, checks):
        use = [c.use for c in checks]
        artefact.__init__(self, name, attrs=notfile, use=use)
        depend(self, checks)
        self.checks = checks

    def _report(self):

        max_name_length = max(len(c.qname) for c in self.checks)
        print(output.coloured('configuration check results:', attrs=['bold']))
        for c in self.checks:
            print('  {:{}} : {} {}'
                  .format(c.qname, max_name_length, c.result, '(cached)' if c.cached else ''))

    def __status__(self, status):
        artefact.__status__(self, status)
        self._report()
