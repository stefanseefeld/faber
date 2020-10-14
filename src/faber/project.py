#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from . import scheduler
from .feature import lazy_set
from .feature.condition import expr as fexpr
from .artefact import artefact, init as artefact_init
from .assembly import init as assembly_init
from .module import module
from .error import error_reporter
from .utils import aslist
from . import config as C
import logging
from configparser import ConfigParser
import warnings
from os.path import exists, join, abspath
import shutil
import os

builtin_formatwarning = warnings.formatwarning


def formatwarning(message, category, *args, **kwds):
    if category is UserWarning:
        # ignore everything except the message
        return 'Warning: {}\n'.format(message)
    else:
        return builtin_formatwarning(message, category, *args, **kwds)


warnings.formatwarning = formatwarning
logger = logging.getLogger(__name__)


def init():
    assembly_init()


def config(script):
    """Read in a config file and return its content."""

    logger.debug('reading config file {}'.format(script))
    if not exists(script):
        raise RuntimeError('config file "{}" not found'.format(script))
    env = {}
    with error_reporter(script), open(script) as f:
        exec(f.read(), env)
    return env


class buildinfo(object):
    """The collection of build-related information, initially provided
    via command-line arguments, stored in the build directory and later
    retrieved from there."""

    def __init__(self, builddir, srcdir=None):
        filename = join(builddir, '.faber', 'info') if builddir else None
        if filename and exists(filename):  # this is an existing build directory
            self.builddir = builddir
            c = ConfigParser(allow_no_value=True)
            c.read(filename)
            self.srcdir = c['general']['srcdir']
            if srcdir and abspath(srcdir) != abspath(self.srcdir):
                raise Exception('incompatible source directory')
            self.options = dict(c.items('options'))
            self.parameters = dict(c.items('parameters'))
        elif builddir and exists(join(builddir, 'fabscript')):  # it's a source directory
            self.builddir = builddir
            if srcdir and abspath(self.builddir) != abspath(srcdir):
                raise Exception('incompatible source directory')
            else:
                self.srcdir = srcdir or self.builddir
                self.options = {}
                self.parameters = {}
        else:  # it's a new builddir
            self.builddir = builddir
            self.srcdir = srcdir
            self.options = {}
            self.parameters = {}

    def store(self):
        if not exists(join(self.builddir, '.faber')):
            os.makedirs(join(self.builddir, '.faber'))
        filename = join(self.builddir, '.faber', 'info')
        config = ConfigParser(allow_no_value=True)
        config['general'] = dict(srcdir=self.srcdir)
        config['options'] = self.options
        config['parameters'] = self.parameters
        with open(filename, 'w') as info:
            config.write(info)

    def valid(self): return self.srcdir is not None


class options(dict):
    def __readonly__(self, *args, **kwargs):
        raise RuntimeError('options is immutable')
    __setitem__ = __readonly__
    __delitem__ = __readonly__
    pop = __readonly__
    popitem = __readonly__
    clear = __readonly__
    update = __readonly__
    setdefault = __readonly__
    del __readonly__

    def get_with(self, value):
        return self.get('with-' + value)

    def get_without(self, value):
        return self.get('without-' + value)


class project(object):

    def __init__(self, info, **kwds):
        """Construct a project. Parameters:

        * srcdir: the source directory
        * builddir: the build directory
        * options: any config options being passed (--with=, --without=)
        * parameters: dictionary of pre-defined parameters"""

        self.srcdir = info.srcdir
        self.builddir = info.builddir
        self.options = options(info.options)
        self.parameters = dict(info.parameters.items())
        info.store()
        self.sched_opts = kwds

    def __enter__(self):
        artefact_init()
        scheduler.init(self.parameters, self.builddir, **self.sched_opts)
        module.init(self.options, self.parameters)
        C.init(self.builddir)
        return self

    def __exit__(self, type, value, traceback):
        C.finish()
        module.finish()
        scheduler.finish()

    def build(self, goals):
        """build the project, updating the given goals or any defaults if None."""

        with self:
            m = module('', self.srcdir, self.builddir)
            if goals:
                try:
                    goals = [a for g in goals for a in artefact.lookup(g)]
                except KeyError as e:
                    print('don\'t know how to make {}'.format(e))
                    goals = []
                    result = False
            else:
                goals = aslist(m.default)
                # if we pick up default goals, check their conditions first
                deps = set([d for g in goals for d in g.features.dependencies()])
                # (allow dependencies to fail)
                scheduler.update(list(deps))

                def check(a):
                    if a.condition is None:
                        return True
                    elif isinstance(a.condition, fexpr):
                        return a.condition(a.features.eval())
                    else:
                        return a.condition

                # now filter by condition
                goals = [g for g in goals if check(g)]
                result = True
            if goals:
                result = scheduler.update(goals)
            elif result:
                print('no goals given and no "default" artefact defined - nothing to do.')
                result = True
        return result

    def clean(self, level):
        """Clean up file artefacts."""

        with self:
            m = module('', self.srcdir, self.builddir)  # noqa F841
            scheduler.clean(level)
            C.clean(level)
        if level > 1:
            shutil.rmtree(join(self.builddir, '.faber'))
        return True

    def info(self, what, items):
        """print project information, rather than performing a build.
        Parameters are the same as for the `build` function."""

        with self:
            result = True
            if what == 'goals':
                m = module('', self.srcdir, self.builddir)
                print('known artefacts:')
                for a in sorted(artefact.iter(), key=lambda a: a.qname):
                    print('  {}'.format(a.qname))
                if items:
                    try:
                        goals = [a for i in items for a in artefact.lookup(i)]
                    except KeyError as e:
                        print('don\'t know how to make {}'.format(e))
                        goals = []
                        result = False
                else:
                    goals = aslist(m.default)
                if goals:
                    scheduler.print_dependency_graph(goals)
            elif what == 'tools':
                from . import tool
                features = lazy_set(module.params.copy())
                for i in items:
                    tool.info(i, features)
        return result

    def shell(self):
        """load module in srcdir but rather than updating any goals,
        simply drop into an interactive shell."""

        import pydoc

        class Helper(pydoc.Helper):
            def __init__(self, env):
                self._env = env
                super(Helper, self).__init__()

            def intro(self):
                self.output.write("""
Welcome the Faber shell's help utility!

To get a list of available artefacts or features, type
"artefacts" or "features".""")

            def help(self, request):
                if isinstance(request, str):
                    request = request.strip()
                    if request == 'artefacts': self.listartefacts()
                    elif request == 'features': self.listfeatures()
                    else:
                        return super(Helper, self).help(request)
                else:
                    return super(Helper, self).help(request)
                self.output.write('\n')

            def listartefacts(self):
                self.list([k for k, v in self._env.items()
                           if isinstance(v, artefact)])

            def listfeatures(self):
                from .feature import feature
                self.list(feature._registry.keys())

        with self:
            m = module('', self.srcdir, self.builddir)
            # Use the module's environment, but inject a few helper functions
            env = m._env.copy()
            env['artefacts'] = list(artefact.iter())
            pydoc.help = Helper(env)
            history = None
            import code
            try:
                import readline
            except ImportError:
                pass
            else:
                import rlcompleter
                readline.set_completer(rlcompleter.Completer(env).complete)
                readline.parse_and_bind('tab: complete')
                fdir = join(self.builddir, '.faber')
                if not exists(fdir):
                    os.makedirs(fdir)
                history = join(fdir, 'history')
                try:
                    readline.read_history_file(history)
                except IOError:
                    pass

            code.interact('Faber interactive shell', local=env)
            if history:
                readline.write_history_file(history)
        return True
