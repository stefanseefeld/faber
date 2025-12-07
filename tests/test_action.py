#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.feature import Feature, incidental, Map, join
from faber.action import Action
from faber.artefact import Artefact, notfile, always
from faber.tools import fileutils
from faber.rule import rule
from faber.utils import capture_output
from test.common import pyecho
from os.path import exists
import sys
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_call():
    a = Action()
    b = Artefact('b', attrs=notfile)
    c = Artefact('c', attrs=notfile)
    with pytest.raises(ValueError) as e:
        a(b, c)
    assert 'not implemented' in str(e.value)

    with capture_output() as (out, err):
        a = Action('echo', 'echo $(<)')
        a([b])
    assert out.getvalue().strip(' \t\n"') == 'test.b'
    assert err.getvalue() == ''


@pytest.mark.usefixtures('module')
def test_call_index():
    """Check that commands can index target and source variables."""
    b = Artefact('b', attrs=notfile)
    c = Artefact('c', attrs=notfile)
    d = Artefact('d', attrs=notfile)
    with capture_output() as (out, err):
        a = Action('echo', 'echo $(<[1]) $(>[0])')
        a([b, c], [d])
    if sys.platform == 'win32':
        assert out.getvalue().strip() == '"test.c" "test.d"'
    else:
        assert out.getvalue().strip() == 'test.c test.d'
    assert err.getvalue() == ''


@pytest.mark.usefixtures('module')
def test_recipe():
    """Check that an artefact's __recipe__ method is called to report
    the execution of the recipe updating it."""
    a = Artefact('a', attrs=notfile|always)
    b = Artefact('b', attrs=notfile|always)
    c = Artefact('c', attrs=notfile|always)
    a = rule(pyecho, a)
    b = rule(pyecho, b, a)
    c = rule(pyecho, c, b)
    with patch('faber.action.Action.__status__') as recipe:
        assert b.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'b <- a'
        assert c.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'c <- b'


@pytest.mark.usefixtures('module')
def test_variables():
    """Check that an action's variables are properly substituted."""

    variable = Feature('variable', attributes=incidental)

    class A(Action):

        var = Map(variable, join)
        command = 'echo $(var)'

    a = Artefact('a', attrs=notfile|always)
    b = Artefact('b', attrs=notfile|always)
    c = Artefact('c', attrs=notfile|always)
    echo = Action('echo', 'echo $(variable)')
    pye = Action('pyecho', pyecho, ['variable'])
    a = rule(A(), a, features=variable('A'))
    b = rule(echo, b, a, features=variable('B'))
    c = rule(pye, c, b, features=variable('C'))
    with patch('faber.action.Action.__status__') as recipe:
        assert a.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'A'
        assert b.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'B'
        assert c.update()
        (_, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == "c <- b (variable=['C'])"


@pytest.mark.usefixtures('module')
def test_compound():
    """Compound a command and a Python function into a single action."""

    class C(Action):

        touch = fileutils.touch

        @staticmethod
        def command(targets, sources):
            f = targets[0]._filename
            if C.touch(targets, sources) and exists(f):
                with open(f, 'w') as out:
                    out.write('something')

    a = rule(C(), 'a')
    a.update()
    with open(a._filename, 'r') as f:
        assert f.readlines() == ['something']
