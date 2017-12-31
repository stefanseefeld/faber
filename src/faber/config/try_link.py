#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .check import check
from ..artefact import intermediate, always
from ..tools.compiler import compiler
from ..rule import rule, alias
from ..artefacts.binary import binary


class try_link(check):
    """Try to compile and link a chunk of source code."""

    def __init__(self, name, source, type, features=(), if_=(), ifnot=()):

        check.__init__(self, name, features, if_, ifnot)
        compiler.check_instance_for_type(type, features)
        if not self.cached:
            # create source file
            src = type.synthesize_name(self.name)

            def generate(targets, _):
                with open(targets[0]._filename, 'w') as os:
                    os.write(source)
            src = rule(generate, src, attrs=intermediate|always,
                       logfile=self.logfile)
            bin = binary(self.name, src, attrs=intermediate,
                         features=self.features, logfile=self.logfile)
            alias(self, bin)
