#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.tool import *
from faber.feature import *
import pytest


def test_tool():

    class A(tool):
        def __init__(self, name=None, features=()):
            tool.__init__(self, name=name, features=features)

    class B(A):
        pass

    class C(B):
        def __init__(self, name='CC', features=()):
            B.__init__(self, name=name, features=features)

    # just generate an A
    assert isinstance(A.instance(), A)
    # make sure A instances have a feature 'A' with A.name='A'
    assert isinstance(A.instance(set(A.tool(name='A'))), A)

    # test simple inheritance
    assert isinstance(B.instance(), A)
    assert isinstance(B.instance(), B)
    assert isinstance(B.instance(set(A.tool(name='B'))), B)
    assert isinstance(B.instance(set(B.tool(name='B'))), B)

    # test tools with explicit name
    assert isinstance(C.instance(), C)
    assert isinstance(C.instance(set(A.tool(name='CC'))), C)

    c1 = C('C1')  # noqa F841
    c2 = C('C2')  # noqa F841
    cc1 = C.instance(set(A.tool(name='C1')))
    cc2 = C.instance(set(A.tool(name='C2')))
    assert cc1.features.A.name == 'C1'
    assert cc2.features.A.name == 'C2'
    cc3 = C.instance(set(A.tool(name='CC')))  # noqa F841
    with pytest.raises(ValueError):
        cc = C.instance(set(A.tool(name='CCCC')))  # noqa F841


def test_action():

    class A(tool):

        a = action('some command')

    class B(A): pass

    assert A.a._cls is A
    assert B.a._cls is B
    assert A.a is not B.a

    a = A()
    b = B()

    assert a.a._cls is A
    assert a.a._tool is a
    assert b.a._cls is B
    assert b.a._tool is b
