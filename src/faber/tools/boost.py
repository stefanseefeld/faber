#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import Action
from ..feature import Set
from ..tool import Tool
from .xslt import Process
import os
from os.path import join


class QuickBook(Tool):

    process = Action('quickbook --input-file=$(>) --output-file=$(<)')

    def __init__(self, name='quickbook', command=None, version='', features=()):
        Tool.__init__(self, name=name, version=version)
        self.features |= features
        if command:
            self.process.subst('quickbook', command)


class BoostBook(Tool):

    db = Process()  # bb -> db
    html = Process()  # db -> html

    def __init__(self, name='boostbook', command=None, version='', prefix='', features=()):
        Tool.__init__(self, name=name, version=version)
        self.features |= Set.instantiate(features)
        if command:
            self.db.subst('xsltproc', command)
            self.html.subst('xsltproc', command)
        if not prefix and 'BOOST_ROOT' in os.environ:
            prefix = join(os.environ['BOOST_ROOT'], 'tools/boostbook')
        if prefix:
            db_xsl = prefix + '/xsl/docbook.xsl'
            self.db.subst('$(stylesheet)', db_xsl)
            html_xsl = prefix + '/xsl/html.xsl'
            self.html.subst('$(stylesheet)', html_xsl)
        else:
            raise ValueError('no prefix set and $BOOST_ROOT undefined')
