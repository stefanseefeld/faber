#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .utils import add_metaclass
from .action import action
from collections import defaultdict
from copy import copy
import logging

logger = logging.getLogger(__name__)


class tool_type(type):
    def __init__(cls, name, bases, dict):
        """For any attribute of type 'action', set the action's name
        to the attribute name."""

        for k,v in dict.iteritems():
            if isinstance(v, action):
                v._cls = cls
                v.name = k


@add_metaclass(tool_type)
class tool(object):

    def __init__(self, name='', version=''):
        pass

