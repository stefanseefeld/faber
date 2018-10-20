#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import artefact
from faber.artefact import notfile, always, intermediate
from faber.rule import rule, depend, alias
from faber.tools import fileutils
from faber import scheduler
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_composite():
    """Test the workflow of faber.config.try_compile"""

    src = rule(fileutils.touch, 'src', attrs=intermediate|always)
    obj = artefact('obj', attrs=intermediate)
    check = artefact('check', attrs=notfile)

    def assemble(targets, sources):
        rule(fileutils.copy, obj, src,
             attrs=intermediate, module=targets[0].module)

    # make a dependency graph
    ass = rule(assemble, 'ass', attrs=notfile|always)
    # make a binary
    depend(obj, dependencies=ass)
    # and test it
    check = alias(check, obj)

    with patch('faber.action.action.__status__') as recipe:
        scheduler.update([check])
        (_, status, _, _, _, _), kwds = recipe.call_args_list[-1]
        assert recipe.call_count == 3
        assert status is True
