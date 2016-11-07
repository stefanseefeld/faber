#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import types
from .feature import set
from .artefact import intermediate
from .rule import rule as explicit_rule
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class _candidate(object):

    def __init__(self, artefact, sources, recipe, features, intermediate):
        self.artefact = artefact
        self.sources = sources
        self.recipe = recipe
        self.features = features
        self.intermediate = intermediate
        
    def instantiate(self):
        """Apply the recipe to the given artefact and source object."""

        sources = [s.instantiate() for s in self.sources]
        return explicit_rule(self.artefact, sources=sources, recipe=self.recipe,
                             features=list(self.features.values()),
                             attrs=intermediate if self.intermediate else 0)
        

    def __repr__(self):
        return '{} <- {}'.format(self.artefact, self.sources)


class _noop(_candidate):

    def __init__(self, artefact):
        _candidate.__init__(self, artefact, [], None, None, False)

    def instantiate(self):
        return self.artefact

    def __repr__(self):
        return repr(self.artefact)


class _implicit_rule(object):
    """An implicit rule instantiates transformations by binding artefact and
    sources."""

    def __init__(self, artefact, source, recipe, features):
        """Define an implicit rule to map source types to artefact types.
        Arguments:
          * artefact, source: output and input types of this generator
          * recipe: the action to perform
          * features: any features to apply."""

        self.artefact = artefact
        self.source = source if isinstance(source, tuple) else (source,)
        self.recipe = recipe
        self.features = features

    def bind(self, a, source, features, intermediate):
        """Instantiate the rule by binding artefact and source to the recipe."""

        # unwrap artefact and source
        artefact = a.name if type(a) is types.typed_name else a
        source = [s.name if type(s) is types.typed_name else s for s in source]
        logger.debug('bind {}: {} <- {}'.format(self.recipe.qname, artefact, source))

        fs = self.features.copy()
        fs |= features
        return _candidate(artefact, source, self.recipe, fs, intermediate)

    def __repr__(self):
        return '<{} {} <- {}>'.format(self.recipe.qname,
                                      self.artefact.name,
                                      ','.join([s.name for s in self.source]))


_repository = defaultdict(list)

class NoRuleError(NotImplementedError): pass

def connect(artefact, source, features, intermediate=False):
    """Create a chain of implicit rules that maps the given sources 
    to the requested artefact."""

    # Find all rules able to produce the requested artefact...
    rules = _repository[artefact.type]
    # ...then iterate over those that match the given features
    for r in iter(r for r in rules if r.features in features):
        try:
            f = features.copy()
            f |= r.features # propagate feature requirements up
            # now transform the sources to the expected input type(s).
            def recurse(e, s, f):
                if s.type in e:
                    return _noop(s.name if type(s) is types.typed_name else s)
                else:
                    # try to generate the first expected type from the source
                    etype = e[0]
                    artefact = etype.typed_name(etype.synthesize_name(s.name))
                    return connect(artefact, [s], f, intermediate=True)
            source = [recurse(r.source, s, f) for s in source]
            return r.bind(artefact, source, f, intermediate)
        except NoRuleError as e:
            pass
    # If we didn't find a match, give up.
    raise NoRuleError('No implicit rule to generate {} matching {}'
                      .format(artefact.type.name, features.essentials()))


def implicit_rule(artefact, source, recipe):
    """Define an implicit rule to build artefact type from source type using recipe."""

    fs = recipe._tool.features if recipe._tool else set()
    r = _implicit_rule(artefact, source, recipe, fs)
    _repository[artefact].append(r)
    logger.debug('irule {}: {} <- {} ({})'
                 .format(recipe.qname, artefact, source, fs))


def rule(artefact, source, features=set(), intermediate=False):
    """Construct a rule using a chain of implicit rules to build artefact from source."""

    # convert artefact and source to the proper types...
    if type(artefact) is str:
        artefact = types.type.typed_name(artefact)
    source = source if type(source) is list else [source]
    source = [types.type.typed_name(s) if type(s) is str else s for s in source]
    if not isinstance(features, set):
        features = set(features)

    # now look at the source types to see what tools we may need.
    if any([s.type is types.c for s in source]):
        from .tools.cc import cc
        cc.instance(features)
    if any([s.type is types.cxx for s in source]):
        from .tools.cxx import cxx
        cxx.instance(features)

    # now build the chain
    chain = connect(artefact, source, features, intermediate)
    return chain.instantiate()

