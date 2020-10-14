#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import faber
from . import project
from . import logging
import os.path
import argparse


class PosArgsParser(argparse.Action):
    def __init__(self, option_strings, dest, **kwds):
        argparse.Action.__init__(self, option_strings, dest, **kwds)
    # Separates positional arguments into targets and parameters
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.parameters is None:
            namespace.parameters={}
        if not namespace.goals:
            namespace.goals=[]
        for v in values:
            if '=' in v:
                name, value = v.split('=', 1)
                if name in namespace.parameters:
                    if type(namespace.parameters[name]) is not list:
                        namespace.parameters[name] = [namespace.parameters[name]]
                    namespace.parameters[name].append(value)
                else:
                    namespace.parameters[name] = value
            else:
                namespace.goals.append(v)


def make_parser():

    parser = argparse.ArgumentParser(description='Faber is a construction tool.')
    parser.add_argument('goals', metavar='GOAL', nargs='*',
                        action=PosArgsParser,
                        help='a goal to update')
    parser.add_argument('parameters', metavar='PARAMETER=VALUE', nargs='*',
                        action=PosArgsParser,
                        help='a parameter value')
    parser.add_argument('--srcdir', default='.',
                        help='the location of the source directory')
    parser.add_argument('--builddir', default='.',
                        help='the location of the build directory')
    parser.add_argument('--rc', default=None,
                        help='the location of the rc file')
    log_args = parser.add_mutually_exclusive_group()
    log_args.add_argument('--log', action='append',
                          choices=logging.topics.keys(),
                          help='add log topic')
    log_args.add_argument('-l', dest='loglevel', type=int,
                          help='set log level (summary=1, actions=2, commands=4)')
    log_args.add_argument('-s', '--silent', action='store_true',
                          help='suppress all output')
    parser.add_argument('-j', '--parallel', type=int, default=1,
                        help='set concurrency level')
    parser.add_argument('--debug', action='store_true',
                        help='do not suppress traceback on error')
    parser.add_argument('-f', '--force', action='store_true',
                        help='update goals even if they are current')
    parser.add_argument('-n', '--noexec', action='store_true',
                        help='do not actually execute actions')
    parser.add_argument('-i', '--intermediates', action='store_true',
                        help='do not remove intermediate files after build')
    parser.add_argument('-c', '--clean', action='count',
                        help='cleanup')
    parser.add_argument('-t', '--timeout', type=int, default=0,
                        help='set timeout for individual actions')
    parser.add_argument('-p', '--profile', action='store_true',
                        help='log timing info with command')
    parser.add_argument('--info', choices=['goals', 'tools'], nargs='?', metavar='WHAT', const='goals',
                        help='print information about the build logic')
    parser.add_argument('--shell', action='store_true',
                        help='run interactive shell')
    parser.add_argument('-v', '--version', action='version', version=faber.__version__)
    return parser


def main():

    parser = make_parser()
    try:
        args, unknown = parser.parse_known_args()
        if args.silent:
            args.log = []

        def with_gen(w):
            k, v = w.split('=', 1) if '=' in w else (w, None)
            yield k[2:]
            yield v
        args.options = dict(map(with_gen, [w for w in unknown
                                           if w.startswith('--with-')]))
        args.options.update(dict.fromkeys([w[2:] for w in unknown
                                           if w.startswith('--without-')], None))

        unknown = [a for a in unknown
                   if not a.startswith('--with-') and not a.startswith('--without-')]
        # Parse the remainder, as there may be more positional arguments.
        # (See https://bugs.python.org/issue14191 for context)
        args = parser.parse_args(unknown, args)

        logging.setup(args.log, args.loglevel, args.debug, args.profile)
        if args.debug:
            faber.debug = True
        project.init()
        if args.rc:
            project.config(os.path.expanduser(args.rc))
        elif os.path.exists(os.path.expanduser('~/.faber')):
            project.config(os.path.expanduser('~/.faber'))

        if args.srcdir and os.path.exists(os.path.join(args.srcdir, '.faberrc')):
            project.config(os.path.join(args.srcdir, '.faberrc'))
        info = project.buildinfo(args.builddir, args.srcdir)
        if args.parameters and info.parameters and \
           args.parameters != info.parameters and \
           input('override existing parameters ? [y/N]:') != 'y':
            return False
        if args.options and info.options and \
           args.options != info.options and \
           input('override existing options ? [y/N]:') != 'y':
            return False
        info.parameters = args.parameters
        info.options = args.options
        proj = project.project(info,
                               parallel=args.parallel, force=args.force,
                               intermediates=args.intermediates,
                               timeout=args.timeout,
                               noexec=args.noexec)
        if args.info:
            result = proj.info(args.info, args.goals)
        elif args.shell:
            result = proj.shell()
        elif args.clean:
            result = proj.clean(args.clean)
        else:
            result = proj.build(args.goals)
        return result
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if args.debug:
            raise
        else:
            print('Error: {}'.format(e))
        return False
    return True


def cli_main():
    """Convert boolean result to process exit status."""
    return 0 if main() else 1


if __name__ == "__main__":
    main()
