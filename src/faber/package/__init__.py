#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import source
import yaml


class node(object):
    """Convert a (nested) dictionary into an ordinary object."""
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [node(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, node(b) if isinstance(b, dict) else b)


def load_info(filename):
    """Load a package metadata file."""
    with open(filename) as f:
        data = yaml.safe_load(f)
        return node(data)


class info(source):

    def __init__(self, name):
        source.__init__(self, name)
        self.doc = load_info(self._filename)
