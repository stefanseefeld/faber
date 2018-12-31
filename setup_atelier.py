#!/usr/bin/env python
#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from setuptools import setup, find_packages
import faber


setup(name='atelier',
      python_requires='>=3.6',
      version=faber.__version__,
      author='Stefan Seefeld',
      author_email='stefan@seefeld.name',
      maintainer='Stefan Seefeld',
      maintainer_email='stefan@seefeld.name',
      description='Atelier is a GUI for Faber.',
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
      package_dir={'': 'src'},
      packages=find_packages(where='src', include=['atelier*']),
      entry_points=dict(gui_scripts=['atelier=atelier.cli:cli_main']),
      install_requires=['faber', 'PyQt5', 'qasync', 'pydot', 'pygments'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'pytest-qt'],
      )
