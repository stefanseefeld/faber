#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import, division, print_function

import platform as P

os = P.system()
architecture = P.machine()

class platform(object):

    @property
    def os(self):
        return P.system()

    @property
    def architecture(self):
        return P.machine()

