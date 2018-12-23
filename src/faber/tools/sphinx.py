#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..feature import set
from ..tool import tool
import subprocess
import re


def validate(cls, command, version, features):

    features = set.instantiate(features)
    version = version or cls.find_version_requirement(features)
    v = subprocess.check_output([command, '--version']).decode().strip()
    v = re.match('.* ([0-9.]+)', v).group(1)
    if version and v != version:
        raise ValueError('{} version mismatch: expected {}, got {}'
                         .format(command, version, v))
    else:
        version = v
    return command, version, features


class sphinx(tool):

    html = action('sphinx-build -b html $(>) $(<)')

    def __init__(self, name='sphinx', command=None, version='', features=()):

        command, version, features = validate(self.__class__, command or 'sphinx-build',
                                              version, features)
        tool.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            self.html.subst('sphinx-build', command)
