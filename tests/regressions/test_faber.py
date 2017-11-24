#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import pytest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


def test_cli_mixed_args():
    # Mixing positional and non-positional arguments is tricky
    # (see https://bugs.python.org/issue14191) and requires a
    # workaround. Make sure it works as expected...

    import imp
    with open('scripts/faber') as script, patch('faber.project.build'):
        faber = imp.load_module('script', script, 'scripts/faber', ('', '', imp.PY_SOURCE))
        assert faber.main(['faber', 'a', 'a=b', '-s'])
        assert faber.main(['faber', 'a', '-s', 'a=b'])
        assert faber.main(['faber', 'a', '-s', 'a=b', '--with-c=e'])
        with pytest.raises(SystemExit):
            faber.main(['faber', 'a', '-s', 'a=b', '--invalid'])
