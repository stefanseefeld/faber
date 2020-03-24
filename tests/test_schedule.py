#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.action import action
from faber.artefact import artefact, notfile, always, nocare, intermediate
from faber.rule import rule, depend
from faber.tools import fileutils
from faber import scheduler
from test.common import pyecho
from os.path import exists
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_action():
    """Check that an action's status is reported upon completion."""
    a = artefact('a', attrs=notfile|always)
    b = artefact('b', attrs=notfile)
    c = artefact('c', attrs=notfile)
    a = rule(pyecho, a)
    b = rule(pyecho, b, a)
    c = rule(pyecho, c, b)
    with patch('faber.action.action.__status__') as recipe:
        assert b.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'b <- a'
        assert c.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'c <- b'


@pytest.mark.usefixtures('module')
def test_noop():
    """Check that an artefact won't be updated if a dependent artefact is up to date."""
    a = artefact('a', attrs=notfile)
    b = artefact('b', attrs=notfile)
    b = rule(pyecho, b, a)
    with patch('faber.action.action.__status__') as recipe:
        assert b.update()
        assert not recipe.called


@pytest.mark.usefixtures('module')
def test_fail():
    """Check that an artefact won't be updated if a dependent artefact's recipe failed."""
    a = artefact('a', attrs=notfile|always)
    b = artefact('b', attrs=notfile)
    fail = action('failing', 'fail')
    a = rule(fail, a)
    b = rule(pyecho, b, a)
    with patch('faber.action.action.__status__'):
        assert not b.update()


@pytest.mark.usefixtures('module')
def test_nocare():
    """Check that an artefact will be updated if a dependent artefact's recipe failed
    but was marked as nocare."""
    a = artefact('a', attrs=notfile|always|nocare)
    b = artefact('b', attrs=notfile)
    fail = action('failing', 'fail')
    a = rule(fail, a)
    b = rule(pyecho, b, a)
    with patch('faber.action.action.__status__') as recipe:
        assert b.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'b <- a'


@pytest.mark.usefixtures('module')
def test_dynamic_dependencies():
    """Test whether it's possible to add dependencies while the scheduler is already running."""

    c = artefact('c', attrs=notfile)

    def inject_deps(self, *args, **kwds):
        d=rule(pyecho, 'd', attrs=notfile|always)
        depend(c, d)
        print('ddeps.b')

    a = rule(pyecho, 'a', attrs=notfile|always)
    b = rule(action('dg', inject_deps), 'b', a, attrs=notfile)
    c = rule(pyecho, c, b)
    with patch('faber.action.action.__status__') as recipe:
        assert b.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'ddeps.b'
        assert c.update()
        # verify that d is actually updated before c
        output = [i[0][4].strip() for i in recipe.call_args_list]
        assert 'd <-' in output


@pytest.mark.usefixtures('module')
def test_dynamic_recipe():
    """Test whether it's possible to add a recipe while the scheduler is already running."""

    c = artefact('c', attrs=notfile)

    def generate(*args, **kwds):
        """generate the graph for c."""
        a = rule(pyecho, 'a', attrs=notfile|always)
        a1 = rule(pyecho, 'a1', a, attrs=notfile|always)
        a2 = rule(pyecho, 'a2', a1, attrs=notfile|always)
        rule(pyecho, c, a2, )

    b = rule(generate, 'b', attrs=notfile|always)
    depend(c, b)
    with patch('faber.action.action.__status__') as recipe:
        assert c.update()
        output = [i[0][4].strip() for i in recipe.call_args_list]
        assert output[-1] == 'c <- a2'


@pytest.mark.usefixtures('module')
def test_multi():
    """TBD"""

    # workflow:
    # b1 needs to be updated, but doing that also updates b2
    # this means c2 (dependent on b2) will also be updated.
    a = artefact('a', attrs=notfile)
    b1 = artefact('b1', attrs=notfile)
    b2 = artefact('b2', attrs=notfile|always)
    c1 = artefact('c1', attrs=notfile)
    c2 = artefact('c2', attrs=notfile)
    d = artefact('d', attrs=notfile)
    rule(pyecho, a)
    rule(pyecho, [b1, b2], a)
    rule(pyecho, c1, b1)
    rule(pyecho, c2, b2)
    rule(pyecho, d, [c1, c2])
    with patch('faber.action.action.__status__') as recipe:
        assert d.update()
        output = [i[0][4].strip() for i in recipe.call_args_list]
        assert output[0] == 'b1 b2 <- a'
        assert 'c2 <- b2' in output
        # sets aren't ordered, so we check for both possibilities
        assert output[-1] in ('d <- c1 c2', 'd <- c2 c1')


@pytest.mark.usefixtures('module')
def test_intermediate():
    """Test that intermediate files are properly updated."""

    a = rule(fileutils.touch, 'a', attrs=intermediate)
    b = rule(fileutils.touch, 'b', a, attrs=intermediate)
    c = rule(pyecho, 'c', b, attrs=notfile|always)
    assert c.update()
    assert exists(a._filename)
    assert exists(b._filename)


@pytest.mark.usefixtures('module')
def test_late():
    """Test that a "late" dependency raises an error."""

    a = artefact('a', attrs=notfile|always)
    assert a.update()
    with pytest.raises(scheduler.DependencyError):
        b = artefact('b', attrs=notfile)
        depend(a, b)


@pytest.mark.usefixtures('module')
def test_cycle():
    """Test that the scheduler detects dependency cycles."""

    echo = action('echo', 'echo $(<) $(>)')
    a = artefact('a', attrs=notfile|always)
    b = rule(echo, 'b', a, attrs=notfile)
    with pytest.raises(scheduler.DependencyError):
        a = rule(echo, a, b)


@pytest.mark.usefixtures('module')
def test_late_cycle():
    """Test that the scheduler detects dependency cycles
    created in recipes."""

    a = artefact('a', attrs=notfile|always)
    b = artefact('b', attrs=notfile|always)
    c = artefact('c', attrs=notfile|always)

    def generator(targets, sources):
        depend(b, c)  # create cycle !
    b = rule(generator, b, a)
    echo = action('echo', 'echo $(<) $(>)')
    c = rule(echo, c, b)
    with pytest.raises(scheduler.DependencyError):
        assert c.update()
