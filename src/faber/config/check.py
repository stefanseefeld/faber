#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..feature import conditional
from ..artefact import artefact, notfile, nocare
from ..module import module
import sqlite3
import hashlib
import os
import os.path
import logging

logger = logging.getLogger('config')


class cache(object):

    def __init__(self):
        if not os.path.exists(module.current.builddir):
            os.makedirs(module.current.builddir)
        self.filename = os.path.join(module.current.builddir, '.configcache')
        self.conn = sqlite3.connect(self.filename)
        # Create table if it doesn't exist yet.
        if not next(self.conn.execute('SELECT name FROM sqlite_master '
                                      'WHERE type="table" AND name="checks"'), None):
            self.conn.execute('CREATE TABLE checks '
                              '(key TEXT, status INTEGER, type TEXT, value TEXT)')

    def __del__(self):
        self.conn.commit()

    def clean(self):
        self.conn.close()
        os.remove(self.filename)
        del self

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


class check(artefact):
    """A check is an artefact that performs some tests (typically involving compilation),
    then stores the result in a cache, so it doesn't need to be performed again,
    until the cache is explicitly cleared."""

    cache = cache() if module.current else None  # to support sphinx' autoclass

    def __init__(self, name, features=(), if_=(), ifnot=()):

        self.result = None
        artefact.__init__(self, name, attrs=notfile|nocare, features=features)
        # The 'condition' here is simply the value of the check's status member.
        self.use = conditional(lambda ctx: self.status, self, if_, ifnot)
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
