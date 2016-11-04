#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.action import action
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

def test_call():
    a = action()
    with pytest.raises(ValueError) as e:
        a()
    assert 'not implemented' in e.value.message

    with patch('faber.engine.run') as run:
        a = action('compile', 'c++ -c -o $(<) $(>)')
        a()
        run.assert_called_with('compile', '', 'c++ -c -o  ')


