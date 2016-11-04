#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import engine
from .artefact import artefact, notfile
from .module import module
import logging

logger = logging.getLogger(__name__)

def _rule(artefacts, sources, recipe, depends, clean, attrs):
    m = module.current
    artefacts = type(artefacts) is list and artefacts or [artefacts]
    def instantiate(t):
        if not isinstance(t, artefact):
            t = artefact(t, sources, attrs)
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
        if not a.attrs & notfile:
            module._clean.add(a.filename)

    return artefacts

def rule(artefacts, sources=[], recipe=None, depends=[], clean=None, attrs=0):
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
      * attrs:  flags"""

    artefacts = _rule(artefacts, sources, recipe, depends, clean, attrs)
    return len(artefacts) == 1 and artefacts[0] or artefacts


def alias(artefact, source, attrs=notfile):
    """This is a special rule with no recipe whose artefact does not correspond to
    a file."""
    return rule(artefact, source, attrs=attrs|notfile)


def depend(artefact, source):
    """This is a special rule to make `artefact` dependent on `source`."""

    return rule(artefact, source)
