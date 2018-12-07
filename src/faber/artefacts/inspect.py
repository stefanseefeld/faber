#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact, notfile, always
from .. import scheduler


class features(artefact):
    def __init__(self, name, features=()):
        artefact.__init__(self, name, attrs=notfile|always, features=features)

    def __status__(self, status):
        print(self.features.eval(update=False))


class dependency_graph(artefact):
    def __init__(self, name, a, dependencies=[], features=()):
        artefact.__init__(self, name, attrs=notfile|always, features=features)
        scheduler.declare_dependency(self, dependencies)
        self.a = a

    def __status__(self, status):
        scheduler.print_dependency_graph(self.a)
