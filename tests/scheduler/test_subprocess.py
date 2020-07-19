#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import asyncio
import pytest


@pytest.mark.asyncio
async def test_timeout():
    """Test that timeout settings are respected, i.e. a command taking too long
    will be aborted and generate an appropriate error."""
    try:
        await asyncio.wait_for(asyncio.sleep(1), timeout=0.1)
    except asyncio.TimeoutError:
        pass
