#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
import sys
# by default, use the asyncio backend with Python > 3.6
if sys.version_info >= (3, 6):
    from .asyncio import *  # noqa F401
    __backend__ = 'asyncio'
else:
    from .bjam import *  # noqa F401
    __backend__ = 'bjam'
