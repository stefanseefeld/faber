#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .check import check
from ..artefact import artefact, intermediate
from .. import types
from .. import assembly
from ..rule import rule, alias
from ..action import action
from .. import engine
from ..module import module

class try_link(check):
    """Try to compile and link a given source file."""

    def __init__(self, name, source, type, features=(), if_=(), ifnot=()):

        self.data = source
        self.filetype = type
        check.__init__(self, name, features, if_, ifnot)

    def expand(self):
        check.expand(self)
        if self.result is not None:
            return # nothing to do
            
        # create source file
        src = self.filetype.synthesize_name(self.name)
        def write_file(artefact, _):
            with open(artefact[0], 'w') as os:
                os.write(self.data)
        src = rule(src, recipe=action('create-{}-src'.format(self.name), write_file), attrs=intermediate)
        # use assembly to find rules to make bin
        bin = artefact(types.bin.synthesize_name(self.name), features=self.features, type=types.bin)
        self.test = assembly.rule(bin, src, self.features, intermediate=True)
        alias(self, self.test)
