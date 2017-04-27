tool
====

.. contents :: Table of Contents

A tool provides an (object-oriented) abstraction that encapsulates (certain) actions. In the context of a tool, actions become methods, with all the associated benefits.

Examples
--------

Given a simple conscript such as::

   from faber.tools.cxx import cxx
   
   rule('hello.o', source='hello.cpp', recipe=cxx.compile)

it becomes possible to configure your build environment by instantiating
different compilers::

  from faber.tools.gxx import gxx

  gxx = gxx()
  gxx11 = gxx(name='g++11', features=cxxflags('--std=c++11'))
  gxx03 = gxx(name='g++03', features=cxxflags('--std=c++03'))
  mingwxx = gxx(name='mingw++', command='/usr/bin/x86_64-w64-mingw32-g++')
  
Now you can invoke a build by selecting either of these to compile `hello.o`:

.. code-block :: none

  $ construct cxx.name=gxx

will invoke :code:`g++ ...`,

.. code-block :: none

  $ construct cxx.name=g++11

will invoke :code:`g++ --std=c++11 ...`,

.. code-block :: none

  $ construct cxx.name=mingw++

will invoke :code:`/usr/bin/x86_64-w64-mingw32-g++ ...`

