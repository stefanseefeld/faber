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
from faber.rule import rule
from faber.module import module
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

def with_module(m):
    def wrap(f):
        def wrapped_f(*args, **kwds):
            with m:
                f(*args, **kwds)
        return wrapped_f
    return wrap

    
# set up a dummy module as lots of objects expect one
module.init(goals={}, config={}, params={})
mod = module('test', '', '', process=False)

@with_module(mod)
def test_implicit_rule():

    a1 = action('a1', 'something')
    a2 = action('a2', 'something')
    a3 = action('a3', 'something')
    c_ = artefact('c', type=c)
    cc = artefact('cc', type=cxx)
    o = artefact('o', type=obj)
    l = artefact('l', type=lib)
    assembly.implicit_rule(obj, c, a1)
    assembly.implicit_rule(obj, cxx, a2)
    assembly.implicit_rule(lib, obj, a3)
    with patch('faber.assembly.explicit_rule') as rule:
        assembly.rule(o, c_)
        assembly.rule(o, cc)
        assert rule.call_count == 2
        assert (rule.call_args_list[0][0][0] is o and
                rule.call_args_list[0][1]['recipe'] is a1)
        assert (rule.call_args_list[1][0][0] is o and
                rule.call_args_list[1][1]['recipe'] is a2)

    with patch('faber.assembly.explicit_rule') as rule:
        assembly.rule(l, cc)
        assert rule.call_count == 2
        assert (rule.call_args_list[0][1]['recipe'] is a2 and
                rule.call_args_list[0][1]['attrs'] & intermediate == True)
        assert (rule.call_args_list[1][0][0] is l and
                rule.call_args_list[1][1]['recipe'] is a3)
