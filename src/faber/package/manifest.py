#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from os.path import join, normcase, basename
from os import walk
import fnmatch
from glob import glob


class manifest(set):

    def __init__(self, base, source):

        self.base = base
        # TODO: need to sort entries to handle excludes last
        for s in source:
            cmd = s.split(' ')
            args = map(normcase, cmd[1:])
            if cmd[0] == 'include':
                self._include(args)
            elif cmd[0] == 'recursive-include':
                self._recursive_include(args[0], args[1:])
            elif cmd[0] == 'exclude':
                self._exclude(args)
            elif cmd[0] == 'recursive-exclude':
                self._recursive_exclude(args[0], args[1:])
            else:
                raise ValueError('unrecognized command "{}"'
                                 .format(cmd[0]))

    def _include(self, patterns):
        for pattern in patterns:
            pattern = join(self.base, pattern)
            files = glob(pattern)
            self |= set(files)

    def _recursive_include(self, dir, patterns):
        base = join(self.base, dir)
        files = []
        for pattern in patterns:
            for root, _, filenames in walk(base):
                for filename in fnmatch.filter(filenames, pattern):
                    files.append(join(root, filename))
        self |= set(files)

    def _exclude(self, patterns):
        files = []
        for pattern in patterns:
            for filename in fnmatch.filter(self, pattern):
                files.append(filename)
        self -= set(files)

    def _recursive_exclude(self, dir, patterns):
        files = []
        if dir == '.':
            dir = ''
        for pattern in patterns:
            for filename in self:
                if (filename.startswith(dir) and
                    fnmatch.filter(basename(filename), pattern)):  # noqa E129
                    files.append(filename)
        self -= set(files)
