#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import scheduler
from .artefact import artefact
from .module import module
from .cache import optioncache
from .utils import aslist
import logging
import warnings
from os.path import exists

builtin_formatwarning = warnings.formatwarning


def formatwarning(message, category, *args, **kwds):
    if category is UserWarning:
        # ignore everything except the message
        return 'Warning: {}\n'.format(message)
    else:
        return builtin_formatwarning(message, category, *args, **kwds)


warnings.formatwarning = formatwarning
logger = logging.getLogger(__name__)


def config(script):
    """Read in a config file and return its content."""

    logger.debug('reading config file {}'.format(script))
    if not exists(script):
        raise RuntimeError('config file "{}" not found'.format(script))
    env = {}
    with open(script) as f:
        exec(f.read(), env)
    return env


def build(goals, options, parameters, srcdir, builddir):
    """build a project. Parameters:

    * goals: list of artefacts to build
    * options: any config options being passed (--with=, --without=)
    * parameters: dictionary of pre-defined parameters
    * srcdir: the source directory
    * builddir: the build directory
    """

    options = optioncache(builddir, options)
    module.init(goals, options, parameters)
    m = module('', srcdir, builddir)
    if goals:
        try:
            goals = [a for g in goals for a in artefact.lookup(g)]
        except KeyError as e:
            print('don\'t know how to make {}'.format(e))
            goals = []
            result = False
    else:
        goals = aslist(m.default)
        result = True
    if goals:
        result = scheduler.update(goals)
    elif result:
        print('no goals given and no "default" artefact defined - nothing to do.')
        result = True
    module.finish()
    return result


def clean(level, options, parameters, srcdir, builddir):
    """Clean up file artefacts."""

    options = optioncache(builddir, options)
    scheduler.clean(level)
    if level > 1:
        options.clean()
    return True


def info(goals, options, parameters, srcdir, builddir):
    """print project information, rather than performing a build.
    Parameters are the same as for the `build` function."""

    options = optioncache(builddir, options)
    module.init(goals, options, parameters)
    m = module('', srcdir, builddir)
    print('known artefacts:')
    for a in sorted(artefact.iter(), key=lambda a: a.qname):
        print('  {}'.format(a.qname))
    if goals:
        try:
            goals = [a for g in goals for a in artefact.lookup(g)]
            result = True
        except KeyError as e:
            print('don\'t know how to make {}'.format(e))
            goals = []
            result = False
    else:
        goals = aslist(m.default)
        result = True
    if goals:
        scheduler.print_dependency_graph(goals)

    module.finish()
    return result
