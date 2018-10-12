#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.scheduler.artefact import artefact
from faber.scheduler.recipe import recipe
import pytest
import tempfile
import shutil


@pytest.fixture()
def scheduler():
    artefact.init()
    recipe.init()
    yield
    recipe.finish()
    artefact.finish()


@pytest.fixture()
def tempdir():
    dirpath = tempfile.mkdtemp()
    try: yield dirpath
    finally: shutil.rmtree(dirpath)
