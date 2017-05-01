#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import engine
from .feature import feature, set
from .artefact import artefact, notfile, intermediate
from .module import module, ScriptError
import logging

logger = logging.getLogger(__name__)

def _rule(artefacts, sources, recipe, depends, clean, attrs, features):
    m = module.current
    fs = m.features
    fs.update(features)

    # 'recipe' may be one of:
    # 
    # * None, in which case this rule is merely declaring a dependency
    # * an unbound action, i.e., a command
    # * an action bound to a tool without an instance
    # * a tool method
    #
    # If the action has a tool class but no instance,
    # substitute it by the corresponding tool method
    path_spec = ''
    if recipe and recipe._cls:
        if not recipe._tool:
            tool = recipe._cls.instance(fs)
            logger.debug('instantiating action {} with tool {}'.
                         format(recipe.qname, tool.id))
            recipe = getattr(tool, recipe.name)
            fs.update(tool.features)
        # Set the artefact filename, based on the tool being used to generate it.
        # This includes any path prefixes to disambiguate variants, as well as
        # file extensions in case this is a cross-compiler.
        path_spec = recipe._tool.path_spec

    # now instantiate artefacts
    artefacts = type(artefacts) is list and artefacts or [artefacts]
    def instantiate(t):
        if isinstance(t, artefact):
            t._update(fs, path_spec)
        else:
            t = artefact(t, sources, attrs, features=list(fs.values()), path_spec=path_spec)
        return t
    artefacts = [instantiate(t) for t in artefacts]
    sources = sources if type(sources) is list else [sources]
    depends = depends if type(depends) is list else [depends]

    # register
    for a in artefacts:
        artefact.register(a)
    sources = [m.qsource(s) for s in sources]
    depends = [m.qsource(d) for d in depends]
    engine.declare_dependency([a.bound_name for a in artefacts],
                              [s.bound_name if isinstance(s, artefact) else s
                               for s in sources + depends],
                              attrs=attrs)
    if recipe:
        a = recipe
        if not a.command:
            raise ScriptError(None, ': {} is not implemented'.format(a.qname))
        a.define(m)
        a.submit(artefacts, sources, m)

    for a in artefacts:
        # if this is a file artefact, remember it in case the user wants to clean up
        if a.attrs & intermediate:
            module._intermediate.add(a.filename)
        elif not a.attrs & notfile:
            module._clean.add(a.filename)

    return artefacts

def rule(artefacts, sources=[], recipe=None, depends=[],
         clean=None, attrs=0, features=()):
    """Express how to generate `artefacts`. In the simplest case this involves a
    source and a recipe...

    Arguments:
      * artefacts: what to make. This can be a string (typically a filename),
                   an existing `artefact` object, or a list of either strings or
                   artefacts (or a mix thereof).

      * sources: the source to make the artefact from. As with `artefacts`, this
                 may be a string, a artefact, or a list of those.

      * recipe: an action taking `sources` as input and producing `artefacts`.
      * depends: additional dependencies not to be used as source.
      * clean:  an action used to remove the artefact.
      * attrs:  flags
      * features: a set of features"""

    if not isinstance(features, set):
        features = set(features)
    artefacts = _rule(artefacts, sources, recipe, depends, clean, attrs, features)
    return len(artefacts) == 1 and artefacts[0] or artefacts


def alias(artefact, source, attrs=notfile):
    """This is a special rule with no recipe whose artefact does not correspond to
    a file."""
    return rule(artefact, source, attrs=attrs|notfile)


def depend(artefact, source):
    """This is a special rule to make `artefact` dependent on `source`."""

    return rule(artefact, source)
