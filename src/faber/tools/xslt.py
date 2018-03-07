#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..tool import tool
from ..feature import feature, multi, incidental, map


xsltflags = feature('xsltflags', attributes=multi|incidental)


class process(action):

    command = 'xsltproc $(xsltflags) -o $(<) $(stylesheet) $(>)'

    xsltflags = map(xsltflags)


class xsltproc(tool):

    process = process()

    def __init__(self, name='xsltproc', command=None, version='', features=()):
        tool.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            self.process.subst('xsltproc', command)
