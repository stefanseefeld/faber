#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefacts import install
from faber.rule import rule
from faber.tools import fileutils
from faber.feature import set
from faber.module import module
from os import mkdir
from os.path import join, exists, splitdrive
import pytest


def relpath(stage='', prefix=''):
    # combine stage with prefix to form the actual path
    if stage:
        if stage[-1] != '/':
            stage += '/'
        prefix = splitdrive(prefix)[1]
    return join(stage + prefix)


@pytest.mark.parametrize('stage, prefix', [('stage', None),
                                           ('stage', 'my/prefix'),
                                           ('stage', '/my/prefix')])
@pytest.mark.usefixtures('module')
def test_installation(stage, prefix):
    """Install a (source) file, directory, as well as a generated
    file, using different stage and prefix settings."""

    srcdir = module.current.srcdir
    filename = 'file'
    with open(join(srcdir, filename), 'w') as o:
        o.write('something')
    dirname = 'directory'
    mkdir(join(srcdir, dirname))

    assert exists(join(srcdir, filename))
    assert exists(join(srcdir, dirname))

    fs = set()
    if prefix is not None:
        fs += install.prefix(prefix, base='')
    if stage is not None:
        stage = join(module.current.builddir, stage)
        fs += install.stage(stage, base='')
    a = install.installed(rule(fileutils.touch, 'empty-file'), 'bin', features=fs)
    b = install.installed(filename, 'src', features=fs)
    c = install.installed(dirname, 'src', features=fs)
    i = install.installation('install', [a, b, c], features=fs)
    assert i.update()
    manifest = [relpath(stage, f.strip())
                for f in open(i.manifest._filename).readlines()]
    print('manifest:', manifest)
    assert len(manifest) == 3
    for f in [a, b, c]:
        print(f._filename)
    for f in manifest:
        assert exists(f)
