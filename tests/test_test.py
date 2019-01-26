#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.test import test, report, pass_, fail, xpass, xfail
from faber.artefact import always, notfile
from faber.action import action
from faber.rule import rule
from faber import cli
from test.common import tempdir, write_fabscript, argv
import pytest


@pytest.mark.usefixtures('module')
def test_outcome():
    passing = rule(action('true', 'echo 1'), 'passing', attrs=always|notfile)
    failing = rule(action('false', 'unknown'), 'failing', attrs=always|notfile)
    test1 = test('test1', passing)
    test2 = test('test2', failing)
    test3 = test('test3', passing, expected=fail)
    test4 = test('test4', failing, expected=fail)
    assert not all([t.update() for t in [test1, test2, test3, test4]])
    assert test1.outcome == pass_
    assert test2.outcome == fail
    assert test3.outcome == xpass
    assert test4.outcome == xfail


@pytest.mark.usefixtures('module')
def test_report():
    passing = rule(action('true', 'echo 1'), 'passing', attrs=always|notfile)
    failing = rule(action('false', 'unknown'), 'failing', attrs=always|notfile)
    test1 = test('t1', passing)
    test2 = test('t2', failing)
    test3 = test('t3', passing, expected=fail)
    test4 = test('t4', failing, expected=fail)
    test5 = test('t5', failing, condition=False)
    r = report('report', [test1, test2, test3, test4, test5])
    assert r.update()
    assert test1.outcome == pass_
    assert test2.outcome == fail
    assert test3.outcome == xpass
    assert test4.outcome == xfail
    assert test5.outcome is None


@pytest.mark.parametrize('fail', [False, True])
def test_failure(fail):

    script="""
from faber.test import test, report
passing = rule(action('true', 'echo 1'), 'passing', attrs=always|notfile)
failing = rule(action('false', 'unknown'), 'failing', attrs=always|notfile)
test1 = test('t1', passing)
test2 = test('t2', failing)
r = report('report', [test1, test2], fail_on_failures={})
default = r
""".format(fail)

    with tempdir() as dirpath:
        write_fabscript(dirpath, script)
        command = ['faber']
        command.append('--srcdir={}'.format(dirpath))
        command.append('--builddir={}'.format(dirpath))
        with argv(command):
            if fail:
                assert not cli.main()
            else:
                assert cli.main()
