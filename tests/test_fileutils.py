#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import notfile, always
from faber.rule import rule
from faber.tools import fileutils
from os.path import exists
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_touch():
    """Check that 'touch' and 'rm' actions work across platforms."""

    a = rule(fileutils.touch, 'empty-file')
    with patch('faber.action.action.__status__'):
        assert a.update()
        assert exists(a._filename)


@pytest.mark.usefixtures('module')
def test_copy():
    """Check that 'touch' and 'rm' actions work across platforms."""

    a = rule(fileutils.touch, 'empty-file')
    b = rule(fileutils.copy, 'clone', a)
    with patch('faber.action.action.__status__'):
        assert b.update()
        assert exists(b._filename)


@pytest.mark.usefixtures('module')
def test_remove():
    """Check that 'touch' and 'rm' actions work across platforms."""

    a = rule(fileutils.touch, 'empty-file')
    b = rule(fileutils.remove, 'cleanup', a, attrs=notfile|always)
    with patch('faber.action.action.__status__'):
        assert a.update()
        assert exists(a._filename)
        assert b.update()
        assert not exists(a._filename)
