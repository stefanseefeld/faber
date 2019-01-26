#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, source
from ..rule import rule, depend
from ..tools.compiler import compiler
from os.path import join, splitext


class scan(artefact):
    """Scan a source file for dependencies and inject them into
    the dependency graph."""

    def __init__(self, src, obj, recipe=None, features=(), module=None):

        src = source.instantiate(src, module=module)
        name = join(splitext(src.name)[0] + '.d')
        artefact.__init__(self, name, features=features, module=module,
                          logfile=obj.logfile)
        self._obj = obj
        if not recipe:
            c = compiler.check_instance_for_type(src.type, features)
            recipe = c.makedep
        rule(recipe, self, src)
        depend(self._obj, self)

    def reset(self):
        # do not reset this artefact as we can't undo its action
        pass

    def __status__(self, status):
        # the file format is simply a newline-separated list
        # of (header) filenames
        if status:
            headers = [h.strip() for h in open(self._filename).readlines()]
            depend(self._obj, [source.instantiate(h, module=self.module)
                               for h in headers])
