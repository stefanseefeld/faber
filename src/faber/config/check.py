#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..feature import feature, set
from ..artefact import artefact, notfile
from ..module import module
import sqlite3
import os.path
import os

class cache(object):

    def __init__(self):
        if not os.path.exists(module.current.builddir):
            os.makedirs(module.current.builddir)
        self.filename = os.path.join(module.current.builddir, 'config.cache')
        self.conn = sqlite3.connect(self.filename)
        if not next(self.conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="checks"'), None):
            self.conn.execute('CREATE TABLE checks (name TEXT, features TEXT, value INTEGER)')

    def __del__(self):
        pass

    def __contains__(self, key):
        name, features = key[0], str(key[1])
        with self.conn:
            a = self.conn.execute('SELECT name FROM checks WHERE name=? AND features=?', (name, str(features)))
        value = next(a, None)
        return value
    
    def __setitem__(self, key, value):
        name, features = key[0], str(key[1])
        with self.conn:
            a = self.conn.execute('INSERT INTO checks VALUES(?,?,?)', (name, str(features), value))

    def __getitem__(self, key):
        name, features = key[0], str(key[1])
        with self.conn:
            a = self.conn.execute('SELECT value FROM checks WHERE name=? AND features=?', (name, str(features)))
        value = next(a, None)
        return bool(value[0])

    def get(self, key, default):
        return self[key] if key in self else default
        

class check(artefact):
    """A check is an artefact that performs some tests (typically involving compilation),
    then stores the result in a cache, so it doesn't need to be performed again, until the cache
    is explicitly cleared."""

    cache = cache()

    def __init__(self, name, features=(), if_=(), ifnot=()):

        artefact.__init__(self, name, attrs=notfile, features=features)
        self.if_ = set(if_)
        self.ifnot = set(ifnot)

    def expand(self):
        self.cached = (self.name, self.features) in check.cache

    @property
    def result(self):
        return check.cache.get((self.name, self.features), None)

    @result.setter
    def result(self, value):
        check.cache[(self.name, self.features)] = value
