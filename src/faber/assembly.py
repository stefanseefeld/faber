#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from . import types
from .feature import set
from .artefact import source, intermediate
from .rule import rule as explicit_rule
from .utils import aslist
from collections import defaultdict
import logging

logger = logging.getLogger('rules')


class _candidate(object):

    def __init__(self, recipe, type, target, sources, features, intermediate, scan=None, logfile=None):
        self.recipe = recipe
        self.type = type
        self.target = target
        self.sources = sources
        self.features = features
        self.intermediate = intermediate
        self.scan = scan  # this might be a recipe for include-scanning
        self.logfile = logfile

    def instantiate(self, module):
        """Apply the recipe to the given artefact and source object."""

        sources = [s.instantiate(module) for s in self.sources]
        t = explicit_rule(self.recipe, self.target, sources=sources,
                          features=self.features,
                          attrs=intermediate if self.intermediate else 0, module=module, logfile=self.logfile)
        if self.scan:
            from .artefacts.include_scan import scan
            for s in sources:
                scan(s, t, self.scan, features=self.features, module=module)
        return t

    def __repr__(self):
        return '{} <- {}'.format(self.target, self.sources)


class _noop(_candidate):

    def __init__(self, type, target):
        _candidate.__init__(self, None, type, target, [], None, False)

    def instantiate(self, module):
        return self.target

    def __repr__(self):
        return repr(self.target)


class _implicit_rule(object):
    """An implicit rule instantiates transformations by binding artefact and
    sources."""

    def __init__(self, recipe, target, source, features):
        """Define an implicit rule to map source types to target types.
        Arguments:
          * recipe: the action to perform
          * target, source: output and input types of this generator
          * features: any features to apply."""

        self.recipe = recipe
        self.target = target
        self.source = source if isinstance(source, tuple) else (source,)
        self.features = features

    def bind(self, t, source, features, intermediate, logfile):
        """Instantiate the rule by binding target and source to the recipe.

        Arguments:
        * t: typed_name or artefact
        * source: list of candidates
        * features: a feature set
        * intermediate: boolean
        * logfile:
        """
        # unwrap artefact and source
        target = t.name if type(t) is types.typed_name else t
        src = [s.name if type(s) is types.typed_name else s for s in source]
        logger.info('bind {}: {} <- {}'.format(self.recipe.qname, target, src))

        fs = self.features.copy()
        fs |= features
        # hack: if this is a C/C++ source compilation, inject a header-scan
        #       to track the additional header dependencies
        scan = None
        if source[0].type in (types.c, types.cxx) and t.type is types.obj:
            tool = self.recipe.tool
            scan = tool.makedep if tool else None
        return _candidate(self.recipe, t.type, target, src, fs, intermediate, scan=scan, logfile=logfile)

    def __repr__(self):
        return '<{} {} <- {}>'.format(self.recipe.qname,
                                      self.target.name,
                                      ','.join([s.name for s in self.source]))


_repository = defaultdict(list)


def init():
    _repository.clear()


class NoRuleError(NotImplementedError): pass


def connect(target, source, features, intermediate=False, logfile=None):
    """Create a chain of implicit rules that maps the given sources
    to the requested target."""

    # Find all rules able to produce the requested target...
    rules = _repository[target.type]
    # ...then iterate over those that match the given features
    for r in iter(r for r in rules if r.features.matches(features)):
        try:
            f = features.copy()
            f |= r.features  # propagate feature requirements up

            # now transform the sources to the expected input type(s).
            def recurse(e, s, f):
                if s.type in e:
                    return _noop(s.type, s.name if type(s) is types.typed_name else s)
                else:
                    # try to generate the first expected type from the source
                    etype = e[0]
                    target = etype.typed_name(etype.synthesize_name(s.name))
                    return connect(target, [s], f, intermediate=True, logfile=logfile)
            source = [recurse(r.source, s, f) for s in source]
            return r.bind(target, source, f, intermediate, logfile=logfile)
        except NoRuleError:
            pass
    # If we didn't find a match, give up.
    raise NoRuleError('No implicit rule to generate {} {} from {} matching {}'
                      .format(target.type.name,
                              target.name,
                              [s.name for s in source],
                              features.essentials()))


def implicit_rule(recipe, target, source):
    """Define an implicit rule to build target type from source type using recipe."""

    fs = recipe._tool.features if recipe._tool else set()
    r = _implicit_rule(recipe, target, source, fs)
    _repository[target].append(r)
    logger.info('irule {}: {} <- {} ({})'
                .format(recipe.qname, target, source, fs))


def rule(target, sources, features=set(), intermediate=False, module=None):
    """Construct a rule using a chain of implicit rules to build target from source."""

    # convert target and source to the proper types...
    sources = aslist(sources)
    sources = [source.instantiate(s, module) for s in sources]
    features = set.instantiate(features)
    target = types.type.typed_name(target) if type(target) is str else target

    logger.info('assembly rule: {} <- {}'.format(target, sources))
    # now look at the source types to see what tools we may need.
    for t in (types.c, types.cxx):
        if any([s.type is t for s in sources]):
            from .tools.compiler import compiler
            compiler.check_instance_for_type(t)

    # now build the chain
    chain = connect(target, sources, features, intermediate, logfile=target.logfile)
    return chain.instantiate(module)
