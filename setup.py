#!/usr/bin/env python
#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from distutils.core import setup
from distutils.command import build, install_scripts, install_data, sdist
import sys, os, os.path
import subprocess
# allow the in-place import of the version
sys.path.insert(0, 'src')
from faber import version

scripts = ['scripts/faber']
data = [('share/doc/faber-{}'.format(version), ('LICENSE', 'README.md'))]

def find_packages(root_dir, root_name):
    packages = []
    def record(path, pkg_name):
        packages.append(pkg_name)
        for filename in sorted(os.listdir(path)):
            subpath = os.path.join(path, filename)
            if os.path.exists(os.path.join(subpath, '__init__.py')):
                subname = '{}.{}'.format(pkg_name, filename)
                record(subpath, subname)
    record(root_dir, root_name)
    return packages

class build_doc(build.build):

   description = "build documentation"

   def run(self):

       self.announce('building documentation')
       python = sys.executable
       faber = os.path.abspath(os.path.join('scripts', 'faber'))
       subprocess.check_call([python, faber,
                              '--srcdir={}'.format('doc'),
                              '--builddir={}'.format('doc')])


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

class install_faber(install_scripts.install_scripts):

    bat = r"""@echo off
REM wrapper to use shebang first line of {FNAME}
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call "%py_exe%" %pyscript% %*
"""

    def run(self):
        install_scripts.install_scripts.run(self)
        if os.name != 'nt':  # done
            return
        for filepath in self.get_outputs():
            pth, fname = os.path.split(filepath)
            froot, ext = os.path.splitext(fname)
            bat_file = os.path.join(pth, froot + '.bat')
            bat_contents = install_faber.bat.format(FNAME=fname)
            if self.dry_run:
                continue
            with open(bat_file, 'wt') as fobj:
                fobj.write(bat_contents)

class test(build.build):

   description = "run tests"

   def run(self):

       self.announce('running tests')
       python = sys.executable
       faber = os.path.abspath(os.path.join('scripts', 'faber'))
       subprocess.check_call([python, '-m', 'pytest'])

setup(name='faber',
      version=version,
      author='Stefan Seefeld',
      author_email='stefan@seefeld.name',
      maintainer='Stefan Seefeld',
      maintainer_email='stefan@seefeld.name',
      description='Faber is a construction tool.',
      url='https://stefanseefeld.github.io/faber',
      download_url='https://github.com/stefanseefeld/faber/releases',
      license='BSL',
      classifiers = ['Environment :: Console',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)',
                     'Operating System :: OS Independent',
                     'Topic :: Software Development :: Build Tools',
                     'Topic :: Software Development :: Testing',
                     'Programming Language :: Python'],
      cmdclass={'build_doc': build_doc,
                'install_data': finstall_data,
                'install_scripts': install_faber,
                'test': test,
                'sdist': fsdist},
      package_dir={'':'src'},
      packages=find_packages('src/faber', 'faber'),
      scripts=scripts,
      data_files=data + docs,
      )
