#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.feature import Feature, multi, path, incidental, Set
from faber.artefact import Artefact
from faber.artefact import notfile, always
from faber.rule import rule, depend
from faber import scheduler
from test.common import pyecho
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class placeholder(Artefact):
    # a placeholder takes the place of a conditional dependency until
    # the condition is evaluated and the substition made (or not)
    def __init__(self, d, p, c):
        Artefact.__init__(self, p.name, features=p.features, attrs=notfile)
        self.prereq = p
        self.dep = d
        self.cond = c

    def __status__(self, status):
        Artefact.__status__(self, status)
        self.prereq.features.eval(update=False)
        if self.cond(self.prereq.features):
            depend(self.dep, [self.prereq])


@pytest.mark.usefixtures('module')
def test_conditional_dependency():
    """Test the workflow of conditional dependencies"""

    name = Feature('name', attributes=multi|path|incidental)
    # artefact to compute the condition
    a = rule(None, 'a', attrs=notfile|always)
    fs = Set(name(a.filename))
    # conditional artefact
    b1 = rule(pyecho, 'b1', features=fs, attrs=notfile|always)
    b2 = rule(pyecho, 'b2', features=fs, attrs=notfile|always)
    # c gets built unconditionally
    # but will include b1 or b2 only if condition is met
    c = Artefact('c', attrs=notfile)
    c = rule(pyecho, c, dependencies=[placeholder(c, b1, Set.name == ''),
                                      placeholder(c, b2, Set.name != '')])
    with patch('faber.action.Action.__status__') as recipe:
        scheduler.update(c)
        output = [i[0][4].strip() for i in recipe.call_args_list]
        assert 'b1 <-' not in output and 'b2 <-' in output
