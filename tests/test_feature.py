#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.feature import *
import pytest


def test_link():

    link = feature('link', ('shared', 'static'))

    l1 = link('shared')
    l2 = link('static')
    with pytest.raises(ValueError):
        l3 = link('invalid')  # noqa F841
    assert l1.matches(l1)
    assert not l1.matches(l2)
    assert not l2.matches(l1)


def test_include():

    include = feature('include', attributes=multi|incidental)
    i1 = include('a', 'b')
    i2 = include('c')
    i1 += i2
    assert i1 == ('a', 'b', 'c')
    assert i1.matches(i2)
    assert i2.matches(i1)


def test_composite():

    tool = feature('tool', feature('name', sub=True), feature('version', sub=True))
    t1 = tool(name='g++')
    t2 = tool(name='g++', version='6.3')
    assert t1 != t2
    assert t1.name == t2.name
    assert t1.version != t2.version
    assert t1.matches(t2)
    assert t2.matches(t1)
    t3 = tool(name='clang++')
    assert t1 != t3
    assert t1.name != t3.name
    assert not t1.matches(t3)

    some = feature('some', feature('include', sub=True, attributes=multi))
    s1 = some(include=('a', 'b'))
    include = feature('include', attributes=multi)
    i1 = include('a', 'b')
    assert s1.include != i1

    s2 = some(include=('a', 'c'))
    s1 += s2
    assert s1.include == ('a', 'b', 'a', 'c')


def test_parsing():

    tool = feature('tool', feature('name', sub=True), feature('version', sub=True))
    include = feature('include', attributes=multi)
    define = feature('define', attributes=multi)
    gxx = tool(name='g++', version='6.3')
    clangxx = tool(name='clang++', version='3.9')
    variant = feature('variant', ('release', 'debug'))  # noqa F841

    o1 = {'tool.name': 'g++', 'variant': 'release'}
    o2 = {'tool.name': 'clang++', 'tool.version': '3.9', 'variant': 'release'}
    fs = lazy_set(o1)
    t1 = fs.tool
    v1 = fs.variant
    fs = lazy_set(o2)
    t2 = fs.tool
    v2 = fs.variant
    assert gxx.matches(t1)
    assert v1 == 'release'
    assert not clangxx.matches(t1)
    assert not gxx.matches(t2)
    assert clangxx.matches(t2)
    assert v2 == 'release'

    o3 = {'include': 'AB'}
    fs = lazy_set(o3)
    assert fs.include == ('AB',)
    o4 = {'include': ['A', 'B']}
    fs = lazy_set(o4)
    assert fs.include == ('A', 'B')

    o5 = {'define': 'C', 'new_tool.name': 'g++', 'new_tool.version': '6.3'}
    lazy = lazy_set(o5, define('A', 'B'), include('I'))
    assert 'define' in lazy
    assert lazy.define == ('C', 'A', 'B')
    assert 'new_tool' not in lazy
    tool = feature('new_tool', feature('name', sub=True), feature('version', sub=True))
    assert 'new_tool' in lazy
    assert lazy.new_tool.name == 'g++'

    o6 = {'tool': 'g++-7'}
    fs = lazy_set(o6)
    assert fs.tool.name == 'g++' and fs.tool.version == '7'


def test_parsing_conflict():

    tool = feature('tool', feature('name', sub=True), feature('version', sub=True))  # noqa F841

    o1 = {'tool': 'g++-2', 'tool.version': '1'}
    fs = lazy_set(o1)
    with pytest.raises(ValueError):
        # trying to instantiate the values should fail
        fs.tool.name == 'g++' and fs.tool.version == 2


def test_serialize():

    tool = feature('tool', feature('name', sub=True), feature('version', sub=True))  # noqa F841
    variant = feature('variant', ('release', 'debug'))  # noqa F841
    o = {'tool.name': 'clang++', 'tool.version': '3.9', 'variant': 'release'}
    fs = lazy_set(o)
    d = fs._serialize()
    assert d == o


def test_mix():

    link1 = feature('link1', ('shared', 'static'))
    link2 = feature('link2', ('shared', 'static'))
    l1 = link1('shared')
    l2 = link2('shared')
    l3 = link1('shared')
    assert l1 != l2
    assert not l1 == l2
    assert l1 == l3
    assert not l1 != l3
    with pytest.raises(ValueError):
        l1 += l2


def test_feature_set():

    tool = feature('tool', feature('name', sub=True), feature('version', sub=True))
    target = feature('target', feature('arch', sub=True))
    link = feature('link', ('shared', 'static'))
    include = feature('include', attributes=multi|incidental)
    linkpath = feature('linkpath', attributes=multi|incidental)

    fs = set(link('shared'), include('a', 'b'))
    fs += set(include('c'), linkpath('d'))
    fs += tool(name='g++', version='6.3')
    fs += target(arch='A')

    assert 'link' in fs
    assert 'define' not in fs

    assert fs.tool.name == 'g++'
    assert fs.link == 'shared'
    assert fs.include == ('a', 'b', 'c')
    assert fs.linkpath == ('d',)

    fs.update(link('static'))
    assert fs.link == 'static'

    assert len(fs) == 5

    fs2 = fs.copy()
    assert fs2.matches(fs)
    del fs2.link
    assert fs2.matches(fs)
    assert fs.matches(fs2)
    fs2.include += include('d')
    assert fs2.matches(fs)
    assert fs.matches(fs2)

    del fs2.target
    assert fs2.matches(fs)
    assert fs.matches(fs2)


def test_fs_copy():

    include = feature('include', attributes=multi)
    link = feature('link', ['shared', 'static'])
    define = feature('define', attributes=multi)
    fs = set(include('a', 'b'), link('shared'))
    fs += define('SHARED', condition=set.link == 'shared')
    assert fs.include == ('a', 'b')
    fs2 = fs.copy()
    fs2 += include('c')
    assert fs.include == ('a', 'b')
    assert fs2.include == ('a', 'b', 'c')

    i = include('a')
    ls = lazy_set({})
    ls |= i
    ls2 = ls.copy()
    ls |= include('c')
    assert ls.include == ('a', 'c')
    assert ls2.include == 'a'

    i = include('a')
    ls = lazy_set({})
    ls |= i
    ls2 = ls.copy()
    print(id(ls.include._value), id(ls2.include._value))
    ls |= include('c')
    print(id(ls.include._value), id(ls2.include._value))
    assert ls.include == ('a', 'c')
    assert ls2.include == 'a'


def test_mapping():

    define = feature('define', attributes=multi)
    include = feature('include', attributes=multi)
    link = feature('link', ('shared', 'static'))
    linkpath = feature('linkpath', attributes=multi)
    libs = feature('libs', attributes=multi)

    fs = set(link('shared'), include('a', 'b'), linkpath('c'), libs('foo', 'bar'))

    cppflags = map(include, translate, prefix='-I') + map(define, translate, prefix='-D')
    cxxflags = map(link, select_if, 'shared', '-fPIC')
    linkpath = map(linkpath, translate, prefix='-L')
    libs = map(libs, translate, prefix='-l', suffix='.lib')

    assert cppflags(fs) == '-Ia -Ib'
    assert cxxflags(fs) == '-fPIC'
    assert linkpath(fs) == '-Lc'
    assert libs(fs) == '-lfoo.lib -lbar.lib'


def test_delayed():

    tool = feature('tool', feature('name', sub=True), feature('version', sub=True))
    define = feature('define', attributes=multi)
    include = feature('include', attributes=multi)
    link = feature('link', ['shared', 'static'])
    fs = set(define('MACRO'), include('a', 'b'), link('shared'),
             tool(name='g++', version='6.3'))
    c1 = set.link == 'shared'
    c2 = set.link == 'static'
    c3 = set.tool.name == 'g++'
    c4 = set.tool.name == 'clang++'
    # doesn't work due to language restrictions
    # c5 = 'MACRO' in set.define
    c5 = set.define.contains('MACRO')
    c6 = c5.not_()
    c7 = set.nonexistent.contains('nothing')
    with pytest.raises(ValueError):
        r1 = c3 or c4
    with pytest.raises(ValueError):
        r2 = c3 and c4
    r1 = c3 | c4
    r2 = c3 & c4
    assert c1(fs) is True
    assert c2(fs) is False
    assert c3(fs) is True
    assert c5(fs) is True
    assert c6(fs) is False
    assert c7(fs) is False
    assert r1(fs) is True
    assert r2(fs) is False

    cc1 = c1 | c2
    cc2 = c1 & c2
    assert cc1(fs) is True
    assert cc2(fs) is False

    c3 = set.foo == 'bar'
    assert c3(fs) is False

    fs += define('SHARED', condition=set.link == 'shared')
    fs += define('GXX', condition=set.tool.name == 'g++')
    fs += define('CLANGXX', condition=set.tool.name == 'clang++')
    fs += define('CXX', condition=((set.tool.name == 'clang++') |
                                   (set.tool.name == 'g++')))
    fs += include('/some/path', condition=set.tool.name == 'g++')
    assert fs.define == ('MACRO',)
    fs.eval()
    assert fs.define == ('MACRO', 'SHARED', 'GXX', 'CXX')
    assert fs.include == ('a', 'b', '/some/path',)


def test_condition():

    tool = feature('tool', feature('name', sub=True), feature('version', sub=True))
    target = feature('target', feature('os', sub=True), feature('arch', sub=True))
    define = feature('define', attributes=multi)
    fs = set(tool(name='g++', version='6.3'), target(os='gnu-linux', arch='x86_64'))
    fs += define('LINUX', condition=set.target.os.matches('.*-linux'))
    fs.eval()
    assert fs.define == ('LINUX',)
