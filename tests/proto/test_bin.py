#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import artefact
from faber.artefact import notfile, always, intermediate
from faber.rule import rule, depend
from faber.tools import fileutils
from faber import scheduler
from os.path import exists
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_composite():
    """Test the workflow of faber.artefacts.binary"""

    src = rule(fileutils.touch, 'src')
    bin = artefact('bin')

    def assemble(targets, sources):
        obj = rule(fileutils.copy, 'obj', src,
                   attrs=intermediate, module=targets[0].module)
        rule(fileutils.copy, bin, obj,
             attrs=intermediate, module=targets[0].module)

    def test(targets, sources):
        print('testing {}'.format(sources[0].name))
        assert exists(sources[0]._filename)

    # make a dependency graph
    ass = rule(assemble, 'ass', attrs=notfile|always)
    # make a binary
    depend(bin, ass)
    # and test it
    test = rule(test, 'test', bin, attrs=notfile)

    with patch('faber.action.action.__status__') as recipe:
        scheduler.update([test])
        (_, status, _, _, output, _), kwds = recipe.call_args_list[-1]
        assert output == 'testing bin\n'
        assert status is True
