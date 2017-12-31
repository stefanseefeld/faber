#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.module import module
from faber.error import ScriptError
from test.common import tempdir, write_fabscript
import pytest


@pytest.mark.usefixtures('module')
def test_no_feature():

    script="""
from faber.feature import set
from faber.tools.compiler import include

fs = set()
d = fs.define"""

    with tempdir() as dirpath:
        write_fabscript(dirpath, script)
        with pytest.raises(ScriptError) as e:
            m = module(dirpath)  # noqa F841
        assert e.value.lineno == 6 and 'no feature' in e.value.message


@pytest.mark.usefixtures('module')
def test_no_compiler():

    script="""
from faber.types import cxx
from faber.tools.compiler import target
from faber.config.try_compile import try_compile
features |= target(arch='impossible')
src='int main() {}'
t=try_compile('test', src, cxx, features=features)
default=t
"""

    with tempdir() as dirpath:
        write_fabscript(dirpath, script)
        with pytest.raises(ScriptError) as e:
            m = module(dirpath)  # noqa F841
        assert 'no C++ compiler found' in e.value.message
        # close open files so we can remove dirpath
        from faber import config
        config.finish()
