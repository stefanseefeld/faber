#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.scheduler.artefact import *
from faber.scheduler.recipe import recipe
import os


class frontend(object):
    """Emulate a faber.artefact enough to support testing the backend."""

    class fset(object):
        def eval(self, update=True): pass

    def __init__(self, name, attrs):
        self.name = name
        self.boundname = self.name
        self.attrs = attrs
        self.features = frontend.fset()
        self.logfile=False

    def __status__(self, status): pass


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class action(object):

    def __init__(self):
        self.command = lambda targets, sources, **vars: [touch(t.boundname) for t in targets]

    def map(self, features): return {}
    def __status__(self, *args): pass


def make_artefact(name, attrs=0, touch=False, prerequisites=[]):
    a = artefact(frontend(name, attrs), prerequisites=prerequisites)
    a.recipe = recipe(action(), [a], []) if touch else None
    return a
