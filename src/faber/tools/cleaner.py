#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..tool import tool
from ..action import action
from .. import platform

class cleaner(tool):

    rm = action('rm', 'rm -f $(>)' if platform.os != 'Windows' else 'del /f /q $(>)')
