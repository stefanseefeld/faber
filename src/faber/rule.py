#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from . import scheduler
from .action import action
from .feature import set
from .feature.condition import expr as fexpr
from .artefact import artefact, source, conditional, notfile
from .utils import aslist
from types import FunctionType, MethodType
import logging

logger = logging.getLogger('rules')
feature_logger = logging.getLogger('features')


def conditional_dependency(a, d):
    if d.condition is None:
        # unconditional
        return d
    elif not isinstance(d.condition, fexpr):
        # eval using builtin __bool__
        return d if d.condition else None
    elif not d.features.dependencies():
        # eval using feature.condition
        result = d.condition(d.features.eval(update=False))
        feature_logger.info('condition "{}" yields {}'.format(d.condition, result))
        return d if result else None
    else:
        # postpone eval using feature.condition
        feature_logger.info('postponing evaluation of condition "{}"'
                            .format(d.condition))
        if not isinstance(d, conditional):
            d = conditional(d, d.condition)
        d.dependent.append(a)
        return d


def depend(target, dependencies):
    """Declare `target` to depend on `dependencies`."""

    dependencies = aslist(dependencies)
    # wrap conditional dependencies
    dependencies = list(filter(None, [conditional_dependency(target, d)
                                      for d in dependencies]))
    scheduler.add_dependency(target, dependencies)


def _rule(recipe, targets, sources, deps, attrs, features, module, path_spec, logfile):

    targets = aslist(targets)
    sources = aslist(sources)
    logger.info('rule: {} <- {} with {}'.format(targets, sources, recipe))
    if not features and isinstance(targets[0], artefact):
        features = targets[0].features.copy()
    else:
        features = module.features | set.instantiate(features)

    if recipe:
        # instantiate recipe
        if type(recipe) in (FunctionType, MethodType):
            recipe = action(recipe.__name__, recipe)
        elif recipe and recipe.abstract:
            # look up an appropriate tool providing the action
            recipe = recipe.instantiate(features.essentials())
        features |= recipe.features
        path_spec = recipe.path_spec if not path_spec else path_spec

    deps = aslist(deps)
    # instantiate artefacts for sources and dependencies
    sources = [source.instantiate(s, module) for s in sources]
    deps = [artefact.instantiate(d, module) for d in deps]

    # instantiate artefacts for targets
    def instantiate(a):
        if isinstance(a, artefact):
            a.attrs |= attrs
            a.features |= features
            a.features |= artefact.combine_use(sources)
            a.path_spec = path_spec if path_spec else a.path_spec
        else:
            a = artefact(a, attrs, features=features, path_spec=path_spec,
                         module=module, logfile=logfile)
        return a
    targets = [instantiate(t) for t in targets]
    deps = deps + sources
    if deps:
        for t in targets:
            depend(t, deps)
    if recipe:
        recipe.submit(targets, sources)

    return targets


def rule(recipe, targets, sources=[], dependencies=[],
         attrs=0, features=(), module=None, path_spec='', logfile=None):
    """Express how to generate `artefacts`. In the simplest case this involves a
    source and a recipe...

    Arguments:
      * recipe: an action taking `sources` as input and producing `targets`.
      * targets: what to make. This can be a string (typically a filename),
                 an existing `artefact` object, or a list of either strings or
                 artefacts (or a mix thereof).

      * sources: the source to make the artefact from. As with `artefacts`, this
                 may be a string, a artefact, or a list of those.

      * depends: additional dependencies not to be used as source.
      * attrs:  flags
      * features: a set of features
      * module: the module to instantiate the artefact in"""

    from .module import module as M
    module = module or M.current
    targets = _rule(recipe, targets, sources, dependencies, attrs, features, module,
                    path_spec, logfile)
    return targets[0] if len(targets) == 1 else targets


def alias(target, source, attrs=notfile, module=None):
    """Declare `target` to be an alias for `source`, i.e., update `source` whenever
    updating `target` is requested."""
    return rule(None, target, dependencies=source, attrs=attrs|notfile, module=module)
