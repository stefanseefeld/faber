#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import, division, print_function

import platform as P
import re

os = P.system()
architecture = P.machine()


class platform(object):

    @property
    def os(self):
        return P.system()

    @property
    def architecture(self):
        return P.machine()


def split_triplet(value):
    """Split host triplet into (cpu, manufacturer, os) components."""

    # In the simplest cases the triplet uses the form <cpu>-<manufacturer>-<os>
    # However, the OS part may itself contain a hyphen (notably when the 'kernel'
    # is split into its own component), and the manufacturer may be left out,
    # leading to ambiguous names, e.g. <cpu>-<kernel>-<os>.
    # Try to detect such cases

    if re.match(r'(\w+)-(\w+)-linux-(\w+)', value):
        # re-merge the 'linux' kernel with the rest of the os spec.
        cpu, manufacturer, os = re.match(r'(\w+)-(\w+)-(.*)', value).groups()
    elif re.match(r'(\w+)-linux-(\w+)', value):
        manufacturer = 'unknown'
        # re-merge the 'linux' kernel with the rest of the os spec.
        cpu, os = re.match(r'(\w+)-(.*)', value).groups()
    else:
        cpu, manufacturer, os = re.match(r'(\w+)-(\w+)-(\w+)', value).groups()
    return cpu, manufacturer, os


if __name__ == '__main__':

    print('Platform: os={}, architecture={}'.format(os, architecture))
