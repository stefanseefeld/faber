#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.package import load_info
from test.common import tempdir
import pytest
from os.path import join


def test_info():

    info = """
package:
  name: the name
  version: 1.0
  description: some text here

a:
  - 1
  - 42
b: bla
c:
  answer: 42
  foo: bar
  key: value
"""

    with tempdir() as dirpath:
        filename = join(dirpath, 'test.pkg')
        with open(filename, 'w') as f:
            f.write(info)

        doc = load_info(filename)
        assert doc.package.name == 'the name'
        assert doc.package.version == 1.0
        assert doc.package.description == 'some text here'
        assert doc.a[0] == 1
        assert doc.c.answer == 42
        assert doc.c.key == 'value'


@pytest.mark.usefixtures('module')
def test_archive():
    pass
