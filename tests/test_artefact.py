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


@pytest.mark.usefixtures('module')
def test_graph():
    from faber.artefact import artefact, notfile
    from faber.rule import depend
    from faber.scheduler.graph import walk
    from faber.scheduler.asyncio import artefacts
    a = artefact('a', attrs=notfile)
    b = artefact('b', attrs=notfile)
    c = artefact('c', attrs=notfile)
    d = artefact('d', attrs=notfile)
    depend(b, a)
    depend(c, a)
    depend(d, [b, c])
    for x, y in walk(artefacts[d]):
        print(x.frontend, y.frontend if y else None)
