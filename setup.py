#!/usr/bin/env python
#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from setuptools import setup
from setuptools.command.build import build
from subprocess import check_output
import re
import os

def get_version_from_git():
    try:
        out = check_output('git describe --tags --long --match release/*'.split()).decode().strip()
        match = re.match(r'release/'
                         r'(?P<version>[a-zA-Z0-9.]+)'
                         r'(?:-(?P<post>\d+)-g(?P<hash>[0-9a-f]{7,}))$',
                         out)
        version, post, hash = match.groups()
        return version if post == '0' else '{0}.post{1}+{2}'.format(version, post, hash)
    except Exception:
        raise ValueError('unable to extract version from git tag')


data = [('share/doc/faber', ('LICENSE', 'README.md'))]


class build_doc(build):

    description = "build documentation"

    def run(self):

        self.announce('building documentation')
        orig = sys.argv
        sys.argv = ['faber', '--srcdir=doc', '--builddir=doc']
        try: cli.main()
        finally: sys.argv = orig


docs = []
if os.path.exists('doc/html'):
    for root, dirs, files in os.walk('doc/html'):
        dest = root.replace('doc/html', 'share/doc/faber')
        docs.append((dest,
                    [os.path.join(root, file) for file in files
                     if os.path.isfile(os.path.join(root, file))]))


setup(data_files=data + docs)
