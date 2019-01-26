#!/usr/bin/env python
#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from setuptools import setup, find_packages
from distutils.command import build, install_data, sdist
import sys
import os
import subprocess

if sys.version_info < (3, 6, 0):
    sys.exit('Faber requires Python 3.6 or newer.')

# allow the in-place import of the version
sys.path.insert(0, 'src')
from faber import cli, version  # noqa E402

data = [('share/doc/faber-{}'.format(version), ('LICENSE', 'README.md'))]


class build_doc(build.build):

    description = "build documentation"

    def run(self):

        self.announce('building documentation')
        orig = sys.argv
        sys.argv = ['faber', '--srcdir=doc', '--builddir=doc']
        try: cli.main()
        finally: sys.argv = orig


class finstall_data(install_data.install_data):
    """Install VERSION file."""

    def finalize_options(self):
        self.set_undefined_options('install', ('install_lib', 'install_dir'),)
        install_data.install_data.finalize_options(self)

    def run(self):
        install_data.install_data.run(self)
        vf = os.path.join(self.install_dir, 'faber', 'VERSION')
        open(vf, 'w').write(version)
        self.outfiles.append(vf)


class fsdist(sdist.sdist):

    def make_release_tree(self, base_dir, files):
        sdist.sdist.make_release_tree(self, base_dir, files)
        print('base_dir=', base_dir)
        open(os.path.join(base_dir, 'src', 'faber', 'VERSION'), 'w').write(version)


docs = []
if os.path.exists('doc/html'):
    for root, dirs, files in os.walk('doc/html'):
        dest = root.replace('doc/html', 'share/doc/faber-{}'.format(version))
        docs.append((dest,
                    [os.path.join(root, file) for file in files
                     if os.path.isfile(os.path.join(root, file))]))


setup(name='faber',
      python_requires='>=3.6',
      version=version,
      author='Stefan Seefeld',
      author_email='stefan@seefeld.name',
      maintainer='Stefan Seefeld',
      maintainer_email='stefan@seefeld.name',
      description='Faber is a construction tool.',
      url='https://stefanseefeld.github.io/faber',
      download_url='https://github.com/stefanseefeld/faber/releases',
      license='BSL',
      classifiers=['Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Build Tools',
                   'Topic :: Software Development :: Testing',
                   'Programming Language :: Python'],
      cmdclass={'build_doc': build_doc,
                'install_data': finstall_data,
                'sdist': fsdist},
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      entry_points=dict(console_scripts=['faber=faber.cli:cli_main']),
      data_files=data + docs,
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      )
