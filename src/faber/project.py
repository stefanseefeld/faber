#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import engine
from .artefact import artefact, notfile, always
from .module import module
from .tools.cleaner import cleaner
from . import builtin
import logging
import os.path

logger = logging.getLogger(__name__)

def config(script):
    """Read in a config file and return its content."""

    logger.debug('reading config file {}'.format(script))
    if not os.path.exists(script):
        raise RuntimeError('config file "{}" not found'.format(script))
    env = {}
    with open(script) as f:
        exec(f.read(), env)
    return env

def build(goals, config, parameters, srcdir, builddir):
    """build a project. Parameters:

    * goals: list of artefacts to build
    * config: any config options being passed
    * parameters: dictionary of pre-defined parameters
    * srcdir: the source directory
    * builddir: the build directory
    """

    module.init(goals, config, parameters)
    m = module(None, srcdir, builddir)
    if goals:
        try:
            goals = [a.bound_name for g in goals for a in artefact.lookup(g)]
        except KeyError as e:
            print('don\'t know how to make {}'.format(e))
            goals = []
            result = False
    else:
        goals = [a.bound_name for a in m.default]
        result = True
    if goals:
        result = all(engine.update(goals).values())
    elif result:
        print('no goals given and no "default" artefact defined - nothing to do.')
        result = True
    module.finish()
    return result

def info(goals, config, parameters, srcdir, builddir):
    """print project information, rather than performing a build.
    Parameters are the same as for the `build` function."""

    module.init(goals, config, parameters)
    m = module(None, srcdir, builddir)
    print('known artefacts:')
    for a in artefact.iter():
        print('  {} {}'.format(a.qname,
                               '(bound to: {})'.format(a.bound_name)
                               if not a.attrs & notfile else ''))
    module.finish()
    return True
