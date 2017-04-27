#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .try_run import check_output
from .. import types


class sizeof(check_output):

    src = """#include <stdio.h>
int main(){{ printf("%i", sizeof({}));}}"""

    def __init__(self, c_type, lang_type=types.c, features=()):
        check_output.__init__(self, 'sizeof_' + c_type, sizeof.src.format(c_type), lang_type,
                              features)

    def post_process(self, output):
        self.result = int(output)
