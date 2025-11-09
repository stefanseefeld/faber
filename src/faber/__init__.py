#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from importlib import metadata

try:
    version = metadata.version('faber')
except metadata.PackageNotFoundError:
    version = 'dev'
__version__ = version

debug = False
