#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import bjam
import logging

logger = logging.getLogger(__name__)


def init(**options):
    return bjam.init(options.get('log', 0),
                     options.get('noexec', False),
                     options.get('jobs', 1),
                     options.get('timeout', 0),
                     options.get('force', False))


def set_variables(artefact, **vars):
    logger.debug('set variables for {}: {}'.format(artefact, vars))
    return bjam.set_target_variables(artefact, 0, vars)


def append_variables(artefact, **vars):
    logger.debug('append variables for {}: {}'.format(artefact, vars))
    return bjam.set_target_variables(artefact, 1, vars)


def variables(artefact):
    return bjam.get_target_variables(artefact)


def variable(artefact, name):
    return bjam.get_target_variable(artefact, name)


def define_action(name, func, module='', flag=0):
    logger.debug('define action {} = {}'.format(name, func))
    return bjam.define_action(module, name, func, [], flag)


def declare_dependency(artefacts, sources, attrs=0):
    logger.debug('declare dependency {} -> {}'.format(artefacts, sources))
    return bjam.depends(artefacts, sources, attrs)


def define_recipe(name, artefacts, sources=[]):
    logger.debug('define recipe {}({}, {})'.format(name, artefacts, sources))
    return bjam.define_recipe(name, artefacts, sources)


def run(name, artefacts, command):
    logger.debug('run {} {} ({})'.format(name, artefacts, command))
    return bjam.run(name, artefacts, command)


def update(artefacts=[], *args):
    return bjam.update(artefacts, *args)
