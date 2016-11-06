#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..artefact import artefact
from ..tool import tool
from ..feature import feature, multi, path
from os.path import basename

cppflags = feature('cppflags', attributes=multi)
define = feature('define', attributes=multi)
include = feature('include', attributes=multi|path)
cflags = feature('cflags', attributes=multi)
cxxflags = feature('cxxflags', attributes=multi)
ldflags = feature('ldflags', attributes=multi)
link = feature('link', ['static', 'shared'])
linkpath = feature('linkpath', attributes=multi)
libs = feature('libs', attributes=multi)

class compiler(tool):

    path_spec = '{compiler.name}-{compiler.version}/{link}/'
