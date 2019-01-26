#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

pass_ = 0x1
fail = 0x2
xpass = 0x3
xfail = 0x4

from .test import test  # noqa F401
from .suite import suite  # noqa F401
from .report import report  # noqa F401
