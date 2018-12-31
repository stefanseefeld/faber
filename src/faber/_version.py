#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from subprocess import check_output
import re
from os.path import join, dirname


def _get_version_from_git(path):
    try:
        out = check_output('git describe --tags --long --match release/*'.split(),
                           cwd=path).decode().strip()
        match = re.match(r'release/'
                         r'(?P<version>[a-zA-Z0-9.]+)'
                         r'(?:-(?P<post>\d+)-g(?P<hash>[0-9a-f]{7,}))$',
                         out)
        version, post, hash = match.groups()
        return version if post == '0' else '{0}.post{1}+{2}'.format(version, post, hash)
    except Exception:
        return None


def _get_version_from_file(path):
    try:
        with open(join(path, 'VERSION'), 'r') as f:
            return f.read().strip()
    except Exception:
        return None


def get_version():
    here = dirname(__file__)
    version = _get_version_from_file(here) or _get_version_from_git(here)
    return version or 'unknown'
