#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import Action
from ..tool import Tool
from ..feature import Feature, multi, incidental, Map


xsltflags = Feature('xsltflags', attributes=multi|incidental)


class Process(Action):

    command = 'xsltproc $(xsltflags) -o $(<) $(stylesheet) $(>)'

    xsltflags = Map(xsltflags)


class XSLTProc(Tool):

    process = Process()

    def __init__(self, name='xsltproc', command=None, version='', features=()):
        Tool.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            self.process.subst('xsltproc', command)
