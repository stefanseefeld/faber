#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..feature import set
from ..artefact import artefact, notfile, nocare
from ..delayed import delayed
import sqlite3
import hashlib
import os
from os.path import exists, join
import logging

logger = logging.getLogger('config')


class cache(object):

    def __init__(self, builddir):
        fdir = join(builddir, '.faber')
        if not exists(fdir):
            os.makedirs(fdir)
        self.filename = join(fdir, 'configcache')
        self.conn = sqlite3.connect(self.filename)
        # Create table if it doesn't exist yet.
        if not next(self.conn.execute('SELECT name FROM sqlite_master '
                                      'WHERE type="table" AND name="checks"'), None):
            self.conn.execute('CREATE TABLE checks '
                              '(key TEXT, status INTEGER, type TEXT, value TEXT)')

    def finish(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def reset(self, level):
        self.conn.commit()
        if level > 1:
            self.conn.execute('DELETE FROM checks')

    def clean(self):
        self.conn.close()
        self.conn = None
        logger.info('cleaning config cache')
        os.remove(self.filename)
        self.conn = sqlite3.connect(self.filename)

    def __contains__(self, key):
        with self.conn:
            a = self.conn.execute('SELECT key FROM checks WHERE key=?', (key,))
        value = next(a, None)
        return bool(value)

    def __setitem__(self, key, value):
        status, result = value[0], value[1]
        with self.conn:
            self.conn.execute('INSERT INTO checks VALUES(?,?,?,?)',
                              (key, status, type(result).__name__, str(result)))

    def __getitem__(self, key):
        with self.conn:
            a = self.conn.execute('SELECT status, type, value FROM checks WHERE key=?',
                                  (key,))
        status, type, value = next(a, (None, None, None))
        value = {'str': lambda x: x,
                 'unicode': lambda x: x,
                 'bool': lambda x: eval(x),
                 'int': lambda x: int(x)}[type](value)
        return status, value


class logfiles(dict):

    def __getitem__(self, m):
        if m not in self:
            self[m] = open(join(m.builddir, 'config.log'), 'a')
        return dict.__getitem__(self, m)

    def clear(self):
        for f in self.values():
            f.close()
        dict.clear(self)

    def clean(self):
        for f in self.values():
            f.close()
            os.remove(f.name)

    def reset(self):
        for f in self.values():
            f.seek(0)
            f.truncate(0)


class check(artefact):
    """A check is an artefact that performs some tests (typically involving compilation),
    then stores the result in a cache, so it doesn't need to be performed again,
    until the cache is explicitly cleared."""

    cache = None
    logfiles = None

    def __init__(self, name, features=(), if_=(), ifnot=()):

        self.result = None
        artefact.__init__(self, name, attrs=notfile|nocare, features=features)
        self.logfile = check.logfiles[self.module]
        # The 'condition' here is simply the value of the check's status member.
        self.use = delayed(lambda: set.instantiate(if_) if self.status else set.instantiate(ifnot), self)
        self.reset()

    def reset(self):
        key = str((self.name, str(self.features))).encode('utf-8')
        self._cache_key = hashlib.md5(key).hexdigest()
        self.cached = self._cache_key in check.cache
        if self.cached:
            self.status, self.result = check.cache[self._cache_key]

    def __status__(self, status):
        logger.debug('check.__status__({})'.format(status))
        if self.cached:
            return  # the cached value takes precedence
        artefact.__status__(self, status)
        if not self.status or self.result is None:
            self.result = self.status
        check.cache[self._cache_key] = (self.status, self.result)
