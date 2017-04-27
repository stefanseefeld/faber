#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..module import module
from ..artefact import artefact, notfile, always
from ..action import action
from .. import engine
from ..feature import set
import os, os.path


class config(object):

    def __init__(self, filename=None):
        self.features=set()
        self.logfile = os.path.join(module.current.builddir, 'config.log')
        if filename:
            self.configfile = os.path.join(module.current.builddir, filename)
            if os.path.exists(self.configfile):
                # restore previously saved values
                env = {}
                with open(self.configfile) as f:
                    exec(f.read(), env)
                module.config['with_'] = env['with_']
                module.config['without'] = env['without']
            else:
                if not os.path.exists(module.current.builddir):
                    os.makedirs(module.current.builddir)
                # save current values
                with open(self.configfile, 'w') as conf:
                    conf.write('with_={}\n'.format(repr(module.config['with_'])))
                    conf.write('without={}\n'.format(repr(module.config['without'])))
        else:
            self.configfile = None

        # config cleanup
        self.clean = artefact('.config-clean', attrs=notfile|always)
        crm = action('config.clean', self._clean)
        crm.define(module.current)
        crm.submit([self.clean], [], module.current)

    def get_with(self, value):
        return module.config['with_'].get(value)

    def get_without(self, value):
        return module.config['without'].get(value)

    def check(self, checks):
        """Run a set of checks."""

        cached = [c for c in checks if c.cached]
        with open(self.logfile, 'w+') as log:
            results = engine.update([c.qname for c in checks if not c.cached],
                                    str(log.fileno()))

        for c in checks:
            if not c.cached:
                c.result = results[c.qname]
            self.features += c.if_ if c.result else c.ifnot

    def report(self, checks):
        """Report check results."""

        max_name_length = max(len(c.qname) for c in checks)
        print('configuration check results:')
        for c in checks:
            print('  {:{}} : {} {}'
                  .format(c.qname, max_name_length, c.result, '(cached)' if c.cached else ''))

    def _clean(self, *args):
        if os.path.exists(self.logfile):
            os.remove(self.logfile)
        if os.path.exists(self.configfile):
            os.remove(self.configfile)
        from .check import check
        if os.path.exists(check.cache.filename):
            os.remove(check.cache.filename)
