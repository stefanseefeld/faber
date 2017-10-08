#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import notfile, intermediate
from faber.rule import rule
from faber.tools import fileutils
from faber import scheduler
from test.common import pyecho
from os.path import exists
import pytest


@pytest.mark.usefixtures('module')
def test_intermediate():
    """This is a reduced version of the config example.
    It shows a bug in bjam's state engine. The test passes
    if all files are non-intermediate."""

    c = rule(fileutils.touch, 'c', attrs=intermediate)
    d = rule(fileutils.touch, 'd', c)
    o = rule(fileutils.touch, 'o', [c, d], attrs=intermediate)
    b = rule(fileutils.touch, 'b', o, attrs=intermediate)
    t = rule(pyecho, 't', b, attrs=notfile)
    assert scheduler.update(t)
    assert exists(b._filename)
