#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import sqlite3
import hashlib
import os
import os.path


class filecache(object):
    """Record all file artefacts to facilitate their cleanup."""

    def __init__(self, builddir, params):
        self.root = builddir
        fdir = os.path.join(builddir, '.faber')
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        self.filename = os.path.join(fdir, 'filecache')
        variant = str(params).encode('utf-8')
        self.variant = hashlib.md5(variant).hexdigest()
        self.conn = sqlite3.connect(self.filename)
        # Create table if it doesn't exist yet.
        if not next(self.conn.execute('SELECT name FROM sqlite_master '
                                      'WHERE type="table" AND name="files"'), None):
            self.conn.execute('CREATE TABLE files (variant TEXT, filename TEXT)')

    def __del__(self):
        self.conn.commit()

    def append(self, filename):
        with self.conn:
            self.conn.execute('INSERT INTO files VALUES(?,?)',
                              (self.variant, filename))

    def extend(self, filenames):
        with self.conn:
            self.conn.executemany('INSERT INTO files VALUES(?,?)',
                                  [(self.variant, f) for f in filenames])

    def clear(self):
        with self.conn:
            self.conn.execute('DELETE FROM files')

    def __iter__(self):
        with self.conn:
            for i in self.conn.execute('SELECT filename FROM files WHERE variant=?',
                                       (self.variant,)):
                yield i[0]
