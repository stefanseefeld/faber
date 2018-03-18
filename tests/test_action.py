#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.feature import feature, incidental, map, join
from faber.action import action
from faber.artefact import artefact, notfile, always
from faber.tools import fileutils
from faber.rule import rule
from faber import scheduler
from faber.utils import capture_output
from test.common import pyecho
from os.path import exists
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_call():
    a = action()
    b = artefact('b', attrs=notfile)
    c = artefact('c', attrs=notfile)
    with pytest.raises(ValueError) as e:
        a(b, c)
    assert 'not implemented' in str(e.value)

    with capture_output() as (out, err):
        a = action('echo', 'echo $(<)')
        a([b])
    assert out.getvalue().strip() == 'test.b'
    assert err.getvalue() == ''


@pytest.mark.usefixtures('module')
def test_recipe():
    """Check that an artefact's __recipe__ method is called to report
    the execution of the recipe updating it."""
    a = artefact('a', attrs=notfile|always)
    b = artefact('b', attrs=notfile|always)
    c = artefact('c', attrs=notfile|always)
    a = rule(pyecho, a)
    b = rule(pyecho, b, a)
    c = rule(pyecho, c, b)
    with patch('faber.scheduler._report_recipe') as recipe:
        assert scheduler.update(b)
        (_, _, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'b <- a'
        assert scheduler.update(c)
        (_, _, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'c <- b'


@pytest.mark.usefixtures('module')
def test_variables():
    """Check that an action's variables are properly substituted."""

    variable = feature('variable', attributes=incidental)

    class A(action):

        var = map(variable, join)
        command = 'echo $(var)'

    a = artefact('a', attrs=notfile|always)
    b = artefact('b', attrs=notfile|always)
    c = artefact('c', attrs=notfile|always)
    echo = action('echo', 'echo $(variable)')
    pye = action('pyecho', pyecho, ['variable'])
    a = rule(A(), a, features=variable('A'))
    b = rule(echo, b, a, features=variable('B'))
    c = rule(pye, c, b, features=variable('C'))
    with patch('faber.scheduler._report_recipe') as recipe:
        assert scheduler.update(a)
        (_, _, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'A'
        assert scheduler.update(b)
        (_, _, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == 'B'
        assert scheduler.update(c)
        (_, _, _, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output.strip() == "c <- b (variable=['C'])"


@pytest.mark.usefixtures('module')
def test_compound():
    """Compound a command and a Python function into a single action."""

    class C(action):

        touch = fileutils.touch

        @staticmethod
        def command(targets, sources):
            f = targets[0]._filename
            if C.touch(targets, sources) and exists(f):
                with open(f, 'w') as out:
                    out.write('something')

    a = rule(C(), 'a')
    scheduler.update(a)
    with open(a._filename, 'r') as f:
        assert f.readlines() == ['something']
