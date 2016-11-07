#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import artefact, intermediate
from faber import assembly
from faber.action import action
from faber.types import *
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_implicit_rule():

    a1 = action('a1', 'something')
    a2 = action('a2', 'something')
    a3 = action('a3', 'something')
    c_ = artefact('c', type=c)
    cc = artefact('cc', type=cxx)
    o = artefact('o', type=obj)
    l = artefact('l', type=lib)
    assembly.implicit_rule(a1, obj, c)
    assembly.implicit_rule(a2, obj, cxx)
    assembly.implicit_rule(a3, lib, obj)
    with patch('faber.assembly.explicit_rule') as rule:
        assembly.rule(o, c_)
        assembly.rule(o, cc)
        assert rule.call_count == 2
        assert (rule.call_args_list[0][0][0] is a1 and
                rule.call_args_list[0][0][1] is o)
        assert (rule.call_args_list[1][0][0] is a2 and
                rule.call_args_list[1][0][1] is o)

    with patch('faber.assembly.explicit_rule') as rule:
        assembly.rule(l, cc)
        assert rule.call_count == 2
        assert (rule.call_args_list[0][0][0] is a2 and
                rule.call_args_list[0][1]['attrs'] & intermediate)
        assert (rule.call_args_list[1][0][0] is a3 and
                rule.call_args_list[1][0][1] is l)
