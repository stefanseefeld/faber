#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from .artefact import Artefact
from .artefact import DependencyError  # noqa F401
from .recipe import Recipe
from ..cache import FileCache
from ..utils import aslist
import asyncio
import sys

__all__ = ['init', 'reset', 'clean', 'finish',
           'variables', 'define_artefact', 'add_dependency', 'define_recipe',
           'run', 'update', 'print_dependency_graph', 'DependencyError']

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
else:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


artefacts = {}  # map frontends to backends


def init(params, builddir, readonly=False, **options):
    noexec = options.get('noexec', False)
    files = FileCache(builddir, params) if not readonly else ()
    intermediates = options.get('intermediates', False)
    jobs = options.get('parallel', 1)
    timeout = options.get('timeout', 0)
    force = options.get('force', False)
    Artefact.init(files, intermediates, force)
    Recipe.init(jobs, timeout, noexec)


def reset():
    for b, f in artefacts.items():
        b.reset()
        f.reset()


def clean(level=1):
    Artefact.clean(level)


def finish():
    Artefact.finish()


def variables(a):
    recipe = artefacts[a].recipe
    return recipe.variables() if recipe else {}


def define_artefact(a, bind=False):
    artefacts[a] = Artefact(a)


def add_dependency(a, deps):
    for d in [artefacts[d] for d in aslist(deps)]:
        artefacts[a].add_prerequisite(d)


def define_recipe(a, targets, sources=[]):
    targets = [artefacts[t] for t in targets]
    sources = [artefacts[s] for s in sources]
    r = Recipe(action=a, targets=targets, sources=sources)
    for t in targets:
        t.recipe = r


def run(command):
    return Recipe.run_subprocess(command)


def update(aa):
    try:
        loop = asyncio.get_event_loop()
        aa = [artefacts[a] for a in aslist(aa)]
        loop.run_until_complete(asyncio.gather(*[a.process() for a in aa]))
        return all([a.status for a in aa])
    except Exception:
        raise


def print_dependency_graph(aa=[]):
    from . import graph
    graph.visualize(*[artefacts[a] for a in aslist(aa)], filename='dependencies.png')
