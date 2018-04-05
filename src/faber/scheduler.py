#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
from . import bjam
from .bjam import DependencyError  # noqa F401
from .utils import capture_output
from .artefact import notfile, intermediate
from .cache import filecache
from .utils import aslist
from types import FunctionType, MethodType
from os import makedirs, remove, rmdir
from os.path import dirname, lexists
from collections import defaultdict
import logging

logger = logging.getLogger('scheduler')
summary_logger = logging.getLogger('summary')

#
# The bjam backend only operates on strings (action names,
# target names, filenames), so this module translates between
# action and artefact instances and their corresponding ids.
#

artefacts = {}   # map ids to instances
boundnames = {}  # map bound names (filenames) to instances
actions = {}     # map ids to instances
recipes = []     # register (action, targets)

files = None
intermediates = []
keep_intermediates = False
noexec = False

summary = defaultdict(int)


def _format_count(msg, what):
    number = summary[what]
    if number:
        summary_logger.info(msg.format(number, 's' if number > 1 else ''))


def _report_recipe(name, target, status, cmd, time, stdout, stderr):
    a = actions.get(name)
    if a:
        if isinstance(target, list):
            target = [artefacts[t] for t in target]
        else:
            target = [artefacts[target]]
        if status == 0:
            intermediates.extend([t._filename for t in target
                                  if t.attrs & intermediate])
            files.extend([t._filename for t in target if not t.attrs & notfile])

        a.__status__(target, status == 0, cmd, time, stdout, stderr)


def _report_artefact(name, status, failed):
    a = artefacts[name]
    if failed:
        failed = artefacts[failed]
        msg = '...skipped {} for lack of {}...'.format(a.boundname, failed.boundname)
        if a.logfile:
            a.logfile.write(msg + '\n')
        else:
            summary_logger.info(msg)
    a.__status__(status == 0)


def _report(what, *args):
    if what == '__summary__':
        failed, skipped, made = args
        summary['failed'] += failed
        summary['skipped'] += skipped
        summary['made'] += made
    elif what == '__recipe__':
        _report_recipe(*args)
    elif what == '__artefact__':
        _report_artefact(*args)
    else:
        raise ValueError('invalid report')


def _prepare(recipe, target):
    """Prepare target variables and filename before running recipe."""

    r = actions[recipe]
    t = artefacts[target]
    t.features.eval()
    if not t.attrs & notfile:
        bind_filename(t)
        d = dirname(t._filename) or '.'
        if not lexists(d):
            makedirs(d)
    vars = r.map(t.features)
    if vars:
        logger.info('setting variables for {}: {}'.format(t.id, vars))
    return vars


def _pyaction(name, func):
    """command actions report their execution back.
    Python callables are executed differently, so we wrap them here
    to be able to capture and report their status."""

    from .action import action, CallError

    def wrapper(target, source, **kwds):
        tt = [boundnames[t] for t in target]
        ss = [boundnames.get(s, s) for s in source]
        with capture_output() as (out, err):
            status = True
            cmd = None
            # This little hack allows us to instruct the scheduler
            # to run certain (python) functions even in 'noexec'
            # mode, such as the ones to assemble compound artefacts.
            if not noexec or hasattr(func, '__noexec__'):
                try:
                    status = func(tt, ss, **kwds)
                    # let users indicate failure by explicitly returning 'False'
                    if status is not False:
                        status = True
                except bjam.DependencyError:
                    # dependency errors are fatal - there is no point
                    # in carrying on...
                    raise
                except CallError as e:
                    status = False
                    cmd = e.cmd
                except Exception as e:
                    # while normal exceptions simply result in update
                    # failures.
                    print(e)
                    import traceback as tb
                    tb.print_exc()
                    status = False
        if not cmd:
            cmd = action.command_string(func, target, source, kwds)
        target = [t.id for t in tt]
        _report_recipe(name, target, 0 if status else 1, cmd, -1.,
                       out.getvalue(), err.getvalue())
        return status
    return wrapper


def init(params, builddir, readonly=False, **options):
    global noexec, files, keep_intermediates
    # enable DEBUG_MAKEPROG and DEBUG_FATE if 'process' flag is set.
    log = (1 << 3) + (1 << 13) if options.get('log', 0) else 0
    noexec = options.get('noexec', False)
    files = filecache(builddir, params) if not readonly else ()
    keep_intermediates = options.get('intermediates', False)
    bjam.init(_prepare, _report,
              log,
              noexec,
              options.get('jobs', 1),
              options.get('timeout', 0),
              options.get('force', False))


def clean(level=1):
    dirs = []
    # remove file artefacts...
    for f in files:
        # We may encounter symbolic links during the cleanup
        # which no longer refer to existing files. To be able
        # to detect them we need to use `lexists`...
        if lexists(f):
            dirs.append(dirname(f))
            remove(f)
    if files:
        files.clear()
    # ...then clean up empty build directories
    dirs = sorted(set(dirs), reverse=True)
    root = '' if files.root == '.' else files.root
    for d in dirs:
        try:
            while d != root:
                rmdir(d)
                d = dirname(d)
        except OSError:  # directory wasn't empty, move on
            continue


def finish():
    global files
    # Remove intermediate files
    if not keep_intermediates:
        for i in intermediates:
            if lexists(i):
                remove(i)

    # print cumulative summary
    _format_count('...failed updating {} artefact{}...', 'failed')
    _format_count('...skipped {} artefact{}...', 'skipped')
    _format_count('...made {} artefact{}...', 'made')

    artefacts.clear()
    boundnames.clear()
    actions.clear()
    del files
    del recipes[:]
    bjam.finish()


def variables(a):
    logger.info('getting variables for {}'.format(a.id))
    return bjam.get_target_variables(a.id)


def define_action(a):
    if a.id not in actions:
        logger.info('define action {} = {}'.format(a.id, a.command))
        actions[a.id] = a
        func = a.command
        if type(func) in (FunctionType, MethodType):
            func = _pyaction(a.id, func)
        bjam.define_action(a.id, func, [])


def define_target(a):
    logger.info('define target {}'.format(a.id))
    artefacts[a.id] = a
    if a.attrs & notfile:
        boundnames[a.id] = a
    bjam.define_target(a.id, a.attrs)


def bind_filename(a):
    logger.info('bind filename {} {}'.format(a.id, a._filename))
    boundnames[a._filename] = a
    return bjam.bind_filename(a.id, a._filename, lexists(a._filename))


def add_dependency(a, deps):
    deps = [d.id for d in aslist(deps)]
    logger.info('declare dependencies {} -> {}'
                .format(a.id, deps))
    return bjam.add_dependency(a.id, deps)


def define_recipe(a, targets, sources=[]):
    targets = [t.id for t in targets]
    if (a.id, tuple(targets)) not in recipes:
        recipes.append((a.id, tuple(targets)))
        sources = [s.id for s in sources]
        logger.info('define recipe {}({}, {})'
                    .format(a.id, targets, sources))
        return bjam.define_recipe(a.id, targets, sources)


def run(command):
    logger.info('run {}'.format(command))
    status, stdout, stderr = bjam.run(command)
    return status == 0, stdout, stderr


def update(artefacts=[]):
    return bjam.update([a.id for a in aslist(artefacts)]) == 0


def print_dependency_graph(artefacts=[]):
    return bjam.print_dependency_graph([a.id for a in aslist(artefacts)])
