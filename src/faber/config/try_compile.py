#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .check import check
from ..artefact import intermediate
from .. import types
from .. import assembly
from ..rule import rule, alias
from ..action import action
from .. import engine
from ..module import module

class try_compile(check):
    """Try to compile a given source file."""

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
        # use assembly to find rule to make obj
        obj = types.obj.synthesize_name(self.name)
        self.test = assembly.rule(obj, [src], self.features, intermediate=True)
        alias(self, self.test)
