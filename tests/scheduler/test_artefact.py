#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.scheduler.artefact import *
from . import make_artefact, touch
import pytest
from os.path import exists, join


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_init():
    a = make_artefact('a')
    assert a.fate == fate.INIT


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_binding():
    """Test an individual artefact's binding state before
    and after calling `a.bind()`."""

    a = make_artefact(name=__file__)
    # initially an artefact is unbound...
    assert a.binding == binding.UNBOUND, 'a is already bound'
    await a.bind()
    # ...binding it will determine whether it exists
    # or is missing.
    assert a.binding == binding.EXISTS, 'a does not exist'
    # generate a filename we know doesn't exist
    b = make_artefact(name=__file__.replace('.py', '.so'))
    await b.bind()
    assert b.binding == binding.MISSING, 'b is not missing'
    c = make_artefact(name='c', attrs=flag.NOTFILE)
    await c.bind()
    # non-file artefacts are never bound
    assert c.binding == binding.UNBOUND, 'c is not bound yet'


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_process(tempdir):
    # nothing to do
    a = make_artefact(join(tempdir, 'a'))
    await a.process()
    assert a.progress == progress.DONE, 'a is still incomplete'
    # nothing to do
    b = make_artefact(join(tempdir, 'b'), touch=True)
    await b.process()
    assert b.progress == progress.DONE, 'b is still incomplete'
    assert exists(b.boundname), 'b does not exist'


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_simple_dep(tempdir):
    """Test that an artefact is correctly updated including its prerequisites"""
    a = make_artefact(join(tempdir, 'a'), touch=True)
    b = make_artefact(join(tempdir, 'b'), touch=True, prerequisites=[a])
    c = make_artefact(join(tempdir, 'c'), touch=True, prerequisites=[b])
    await c.process()
    assert c.progress == progress.DONE, 'c is still incomplete'
    assert exists(c.boundname) and c.recipe.status, 'c was not updated'


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_simple_dep2(tempdir):
    """Test that an artefact is only updated if it is out-of-date"""
    a = make_artefact(join(tempdir, 'a'), touch=True)
    b = make_artefact(join(tempdir, 'b'), touch=True, prerequisites=[a])
    c = make_artefact(join(tempdir, 'c'), touch=True, prerequisites=[b])
    touch(a.name)
    await asyncio.sleep(1)
    touch(b.name)
    await c.process()
    assert c.progress == progress.DONE, 'c is still in progress'
    assert exists(c.boundname) and c.recipe.status
    assert a.recipe.status is None, 'a was wrongly updated'
    assert b.recipe.status is None, 'b was wrongly updated'


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_notfile_dep(tempdir):
    a = make_artefact(join(tempdir, 'a'), touch=True)
    b = make_artefact('b', attrs=flag.NOTFILE, prerequisites=[a])
    await b.process()
    assert b.progress == progress.DONE, 'b is still in progress'


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_temp_dep(tempdir):
    a = make_artefact(join(tempdir, 'a'), touch=True)
    b = make_artefact(join(tempdir, 'b'), attrs=flag.TEMP, touch=True, prerequisites=[a])
    c = make_artefact(join(tempdir, 'c'), touch=True, prerequisites=[b])
    await c.process()
    assert exists(a.boundname) and a.recipe.status, 'a was not updated'
    assert exists(b.boundname) and b.recipe.status, 'b was not updated'
    assert exists(c.boundname) and c.recipe.status, 'c was not updated'


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_temp_dep2(tempdir):
    a = make_artefact(join(tempdir, 'a'), touch=True)
    b = make_artefact(join(tempdir, 'b'), attrs=flag.TEMP, touch=True, prerequisites=[a])
    c = make_artefact(join(tempdir, 'c'), touch=True, prerequisites=[b])
    # update a before c, so c is up-to-date
    touch(a.name)
    await asyncio.sleep(1)
    touch(c.name)
    await c.process()
    assert b.recipe.status is None, 'b was wrongly updated'
    assert c.recipe.status is None, 'c was wrongly updated'


@pytest.mark.asyncio
@pytest.mark.usefixtures('scheduler')
async def test_temp_dep3(tempdir):
    a = make_artefact(join(tempdir, 'a'), touch=True)
    b = make_artefact(join(tempdir, 'b'), attrs=flag.TEMP, touch=True, prerequisites=[a])
    c = make_artefact(join(tempdir, 'c'), touch=True, prerequisites=[b])
    # update c before a, so c needs to be updated
    touch(c.name)
    await asyncio.sleep(1)
    touch(a.name)
    await c.process()
    assert b.recipe.status, 'b was not updated'
    assert c.recipe.status, 'c was not updated'
