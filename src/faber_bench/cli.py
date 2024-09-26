#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import faber_bench
import faber
import argparse


def make_parser():

    parser = argparse.ArgumentParser(description='faber-bench is a construction tool.')
    parser.add_argument('builddir', nargs='?',
                        help='the location of the build directory')
    parser.add_argument('-s', '--srcdir',
                        help='the location of the source directory')
    parser.add_argument('--rc', default=None,
                        help='the location of the rc file')
    parser.add_argument('-v', '--version', action='version', version=faber_bench.__version__)
    parser.add_argument('--debug', action='store_true',
                        help='do not suppress traceback on error')
    return parser


def main():

    parser = make_parser()
    try:
        args = parser.parse_args()
        if args.debug:
            faber.debug = True
        return faber_bench.run(args.builddir, args.srcdir, args.rc)
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
