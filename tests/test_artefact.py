#
# Copyright (c) 2019 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import source
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.mark.usefixtures('module')
def test_unique_src():
    """Check that two sources associated with the same name actually
yield the same object."""

    with patch('faber.scheduler.define_artefact') as define:
        s1 = source('foo')
        s2 = source('foo')
        assert s1 is s2
    define.assert_called_once()
