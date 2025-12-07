#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..feature import Feature, path, incidental
from ..action import Action
from ..tool import Tool
import os
import os.path
import stat
import shutil

prefix = Feature('prefix', attributes=path|incidental)
stage = Feature('stage', attributes=path|incidental)


def copyfile(source, target):
    assert os.path.isfile(source)
    # copy content,...
    shutil.copyfile(source, target)
    # ...stat,...
    shutil.copystat(source, target)
    # ...owner, and group
    st = os.stat(source)
    if hasattr(os, 'chown'):  # not available on Windows
        os.chown(target, st[stat.ST_UID], st[stat.ST_GID])


def copydir(source, target):
    assert os.path.isdir(source)
    shutil.copytree(source, target, symlinks=True)


class Install(Action):

    def __init__(self, mode=None):
        Action.__init__(self)
        self.mode = mode

    @staticmethod
    def command(targets, sources):
        t = targets[0]
        s = sources[0]
        if os.path.isfile(s._filename):
            copyfile(s._filename, t._filename)
        elif os.path.isdir(s._filename):
            copydir(s._filename, t._filename)
        else:
            raise ValueError('Cannot install "{}"; neither a file nor directory.'.format(s._filename))


def create_manifest(t, sources):
    stage = str(t[0].features.stage) if 'stage' in t[0].features else ''
    files = [s._filename[len(stage):] for s in sources
             if s._filename.startswith(stage)]
    with open(t[0]._filename, 'w') as manifest:
        for f in files:
            manifest.write(f + '\n')


class Installer(Tool):

    install_exe = Install()
    install_data = Install()
    install = install_data
