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
        l3 = link('invalid')
    with pytest.raises(ValueError):
        l1 += l2
    assert l1 in l1
    assert l1 not in l2
    assert l2 not in l1

def test_include():
    
    include = feature('include', attributes=multi|incidental)
    i1 = include('a', 'b')
    i2 = include('c')
    i1 += i2
    assert i1 == ('a', 'b', 'c')
    assert i1 in i2
    assert i2 in i1

def test_composite():
    
    tool = feature('tool', name=feature(), version=feature())
    t1 = tool(name='g++')
    t2 = tool(name='g++', version='6.3')
    assert t1 != t2
    assert t1.name == t2.name
    assert t1.version != t2.version
    # t2 "matches" t1 (used as a spec)
    assert t1 not in t2
    assert t2 in t1
    t3 = tool(name='clang++')
    assert t1 != t3
    assert t1.name != t3.name
    assert t1 not in t3

    some = feature('some', include=feature(attributes=multi))
    s1 = some(include=('a', 'b'))
    include = feature('include', attributes=multi)
    i1 = include('a', 'b')
    assert s1.include.value == i1.value # values are equal
    assert s1.include != i1             # but their types are not 
    
    s2 = some(include=('a', 'c'))
    s1 += s2
    assert s1.include == ('a', 'b', 'a', 'c')


def test_lazy_set():

    tool = feature('tool', name=feature(), version=feature())
    include = feature('include', attributes=multi)
    define = feature('define', attributes=multi)
    gxx = tool(name='g++', version='6.3')
    clangxx = tool(name='clang++', version='3.9')
    variant = feature('variant', ('release', 'debug'))
    
    o1 = {'tool.name':'g++', 'variant':'release'}
    o2 = {'tool.name':'clang++', 'tool.version':'3.9', 'variant':'release'}
    fs = lazy_set(o1)
    t1 = fs.tool
    v1 = fs.variant
    fs = lazy_set(o2)
    t2 = fs.tool
    v2 = fs.variant
    assert gxx in t1
    assert v1 == 'release'
    assert clangxx not in t1
    assert gxx not in t2
    assert clangxx in t2
    assert v2 == 'release'

    o3 = {'include':'AB'}
    fs = lazy_set(o3)
    assert fs.include == ('AB',)
    o4 = {'include':['A','B']}
    fs = lazy_set(o4)
    assert fs.include == ('A','B')

    o5 = {'define':'C', 'new_tool.name':'g++', 'new_tool.version':'6.3'}
    lazy = lazy_set(o5, define('A', 'B'), include('I'))
    assert 'define' in lazy
    assert lazy.define == ('C', 'A', 'B')
    assert 'new_tool' not in lazy
    tool = feature('new_tool', name=feature(), version=feature())
    assert 'new_tool' in lazy
    assert lazy.new_tool.name == 'g++'

    
def test_serialize():

    o = {'tool.name':'clang++', 'tool.version':'3.9', 'variant':'release'}
    fs = lazy_set(o)
    t = fs.tool
    v = fs.variant
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

    tool = feature('tool', name=feature(), version=feature())
    target = feature('target', arch=feature())
    link = feature('link', ('shared', 'static'))
    include = feature('include', attributes=multi|incidental)
    linkpath = feature('linkpath', attributes=multi|incidental)
    
    fs = set(link('shared'), include('a', 'b'))
    fs += set(include('c'), linkpath('d'))
    fs += tool(name='g++', version='6.3')
    fs += target(arch='A')
    fs += link('shared')

    assert 'link' in fs
    assert 'define' not in fs

    assert fs.tool.name == 'g++'
    assert fs.link == 'shared'
    assert fs.include == ('a', 'b', 'c')
    assert fs.linkpath == ('d',)
    with pytest.raises(ValueError):
        fs += link('static')

    fs.update(set(link('static')))
    assert fs.link == 'static'

    assert len(fs) == 5
    
    fs2 = fs.copy()
    assert fs2 in fs
    del fs2.link
    assert fs2 in fs
    assert fs in fs2
    fs2.include += include('d')
    assert fs2 in fs
    assert fs in fs2

    del fs2.target
    assert fs2 in fs
    assert fs in fs2



def test_fs_clone():

    include = feature('include', attributes=multi)
    link = feature('link', ['shared', 'static'])
    fs = set(include('a', 'b'), link('shared'))
    assert fs.include == ('a', 'b')
    fs2 = fs.copy()
    fs2 += include('c')
    assert fs.include == ('a', 'b')
    assert fs2.include == ('a', 'b', 'c')



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


def test_conditional():

    tool = feature('tool', name=feature(), version=feature())
    define = feature('define', attributes=multi)
    include = feature('include', attributes=multi)
    link = feature('link', ['shared', 'static'])
    fs = set(define('MACRO'), include('a', 'b'), link('shared'),
                     tool(name='g++', version='6.3'))
    c1 = set.link == 'shared'
    c2 = set.link == 'static'
    c3 = set.tool.name == 'g++'
    c4 = set.tool.name == 'clang++'
    with pytest.raises(ValueError):
        c5 = c3 or c4
    with pytest.raises(ValueError):
        c6 = c3 and c4
    c5 = c3 | c4
    c6 = c3 & c4
    assert c1(fs) == True
    assert c2(fs) == False
    assert c3(fs) == True
    assert c5(fs) == True
    assert c6(fs) == False

    cc1 = c1 | c2
    cc2 = c1 & c2
    assert cc1(fs) == True
    assert cc2(fs) == False

    c3 = set.foo == 'bar'
    assert c3(fs) == False

    fs += define('SHARED', condition=set.link == 'shared')
    fs += define('GXX', condition=set.tool.name == 'g++')
    fs += define('CLANGXX', condition=set.tool.name == 'clang++')
    fs += define('CXX', condition=((set.tool.name == 'clang++') | \
                                   (set.tool.name == 'g++')))
    assert fs.define == ('MACRO',)
    fs.eval()
    assert fs.define == ('MACRO', 'CXX', 'GXX', 'SHARED')
