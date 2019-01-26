#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber import cli
from test.common import tempdir, argv
import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_cli_mixed_args():
    # Mixing positional and non-positional arguments is tricky
    # (see https://bugs.python.org/issue14191) and requires a
    # workaround. Make sure it works as expected...

    with patch('faber.project.project.build'):
        with tempdir() as b:
            build = '--builddir={}'.format(b)
            with argv(['faber', build, 'a', 'a=b', '-s']):
                assert cli.main()
        with tempdir() as b:
            build = '--builddir={}'.format(b)
            with argv(['faber', build, 'a', '-s', 'a=b']):
                assert cli.main()
        with tempdir() as b:
            build = '--builddir={}'.format(b)
            with argv(['faber', build, 'a', '-s', 'a=b', '--with-c=e']):
                assert cli.main()
        with tempdir() as b, pytest.raises(SystemExit):
            build = '--builddir={}'.format(b)
            with argv(['faber', build, 'a', '-s', 'a=b', '--invalid']):
                cli.main()
