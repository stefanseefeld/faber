#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

import operator
import re


def contains(op1, op2):
    # allow op1 to be `false`, so `set.nonexistent.contains('x')`
    # becomes a valid expression
    return False if isinstance(op1, false) else operator.contains(op1, op2)


def matches(op1, op2):
    # allow op1 to be `false`, so `set.nonexistent.match('x')`
    # becomes a valid expression
    return False if isinstance(op1, false) else re.match(op2, str(op1))


class expr(object):

    # we can't overload __not__ as that has to return a bool...
    def not_(self): return unary(operator.not_, self)
    def __eq__(self, other): return binary(operator.eq, self, other)
    def __ne__(self, other): return binary(operator.ne, self, other)
    def __gt__(self, other): return binary(operator.gt, self, other)
    def __lt__(self, other): return binary(operator.lt, self, other)
    def __and__(self, other): return binary(operator.and_, self, other)
    def __or__(self, other): return binary(operator.or_, self, other)
    # we can't overload __contains__ as that has to return a bool...
    def contains(self, other): return binary(contains, self, other)
    def __bool__(self): raise ValueError('invalid expression "{}" !'.format(self))
    def __nonzero__(self): return self.__bool__()
    def __call__(self, ctx): return True
    def matches(self, other): return binary(matches, self, other)


class true(expr):

    def __eq__(self, other): return True if bool(other) else False
    def __bool__(self): return True
    def __call__(self, ctx): return True
    def __str__(self): return '<expr True>'


class false(expr):

    def __eq__(self, other): return True if not other else False
    def __bool__(self): return False
    def __call__(self, ctx): return False
    def __str__(self): return '<expr False>'


class unary(expr):

    def __init__(self, op, op1):
        self.op = op
        self.op1 = op1

    def __call__(self, ctx):
        op1 = self.op1(ctx)
        return self.op(op1)

    def __str__(self):
        return '<expr {}({})>'.format(self.op.__name__, self.op1)


class binary(expr):

    def __init__(self, op, op1, op2):
        self.op = op
        self.op1 = op1
        self.op2 = op2

    def __call__(self, ctx):
        op1 = self.op1(ctx) if isinstance(self.op1, expr) else self.op1
        op2 = self.op2(ctx) if isinstance(self.op2, expr) else self.op2
        return self.op(op1, op2)

    def __str__(self):
        return '<expr {}({}, {})>'.format(self.op.__name__, self.op1, self.op2)


class sub(expr):
    # a subfeature
    def __init__(self, op, name):
        self.op = op
        self.name = name

    def __call__(self, ctx):
        op = self.op(ctx)
        return getattr(op, self.name) if hasattr(op, self.name) else false()

    def __str__(self):
        return '<expr attr({}, {})>'.format(self.op, self.name)


class value(expr):
    def __init__(self, name):
        self._name = name

    def __getattr__(self, name):
        return sub(self, name)

    def __call__(self, ctx):
        return ctx[self._name] if self._name in ctx else false()

    def __str__(self):
        return '<expr value({})>'.format(self._name)
