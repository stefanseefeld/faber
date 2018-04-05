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
import warnings


class filecache(object):
    """Record all file artefacts to facilitate their cleanup."""

    def __init__(self, builddir, params):
        self.root = builddir
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self.filename = os.path.join(self.root, '.filecache')
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


class optioncache(object):
    """Remember command-line options for convenience."""

    def __init__(self, builddir, options, readonly=False):

        self.filename = os.path.join(builddir, '.optioncache')
        self.options = dict(with_={}, without=[])
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                exec(f.read(), self.options)
        if options['with_'] or options['without']:
            if self.options['with_'] or self.options['without']:
                warnings.warn('Overriding saved options with command-line options')
            self.options.update(options)
        if not readonly:
            with open(self.filename, 'w') as opts:
                opts.write('with_={}\n'.format(repr(self.options['with_'])))
                opts.write('without={}\n'.format(repr(self.options['without'])))

    def clean(self):
        os.remove(self.filename)

    def get_with(self, value):
        return self.options['with_'].get(value)

    def get_without(self, value):
        return value in self.options['without']
