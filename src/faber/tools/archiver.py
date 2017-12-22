#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..tool import tool
import shutil


class archive(action):

    def __init__(self, format=None):
        action.__init__(self)
        if format:
            self.format = format
        elif shutil._BZ2_SUPPORTED:
            self.format = 'bztar'
        elif shutil._ZLIB_SUPPORTED:
            self.format = 'gztar'
        else:
            self.format = 'tar'

    def command(self, targets, sources):
        archive = targets[0]
        installation = sources[0]
        stage = str(installation.features.stage)
        shutil.make_archive(archive.name, self.format, stage)


class archiver(tool):

    @staticmethod
    def extension(format):
        if format == 'bztar':
            return '.tar.bz2'
        elif format == 'gztar':
            return '.tar.gz'
        elif format == 'tar':
            return '.tar'
        elif format == 'zip':
            return '.zip'
        else:
            raise ValueError('unsupported archive format {}'.format(format))

    archive = archive
