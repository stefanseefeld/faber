The `tool` class
================

.. py:currentmodule:: faber.tool

A tool provides an (object-oriented) abstraction that encapsulates actions. In the context of a tool,
actions become methods, with all the associated benefits.
Following idiomatic object-oriented design, abstract tools provide an interface by defining abstract
action methods, while subclasses implement them.
Each derived tool class registers a new `feature` of the same name as the tool class with two subfeatures:
name and version. For example, consider this simple tool hierarchy:

.. graphviz::
   
   digraph T {
     rankdir="LR"
     node [ fontname="Bitstream Vera Sans", fontsize=8, shape=record, style=filled, fillcolor="khaki3:khaki1"]
     edge [ arrowtail="empty" arrowhead="none" dir="back"]
     cxx [ label="{ {cxx|cxx.name : feature\lcxx.version : feature\lcompile : action\l}}"]
     gxx [ label="{ {gxx|gxx.name : feature\lgxx.version : feature\lcompile : action\l}}"]
     "tool" -> "cxx" -> "gxx";
   }


The *value* of these these feature variables will be determined by the actual instances of these classes,
i.e. an instance of `gxx` will have cxx.name=gxx.name='gxx'.
This mechanism allows for references to abstract actions such as `cxx.compile` to be resolved to concrete
actions.


Constructor
-----------

.. method:: tool(name='', version='')

   The tool name defaults to its class name.

Attributes
----------
   
.. attribute:: name

   Return the tool's name

.. attribute:: version

   Return the tool's version string (defaults to '' if no version is known).

.. attribute:: id

   Return the tool's id (a string combining name and version).

.. attribute:: features

   Any features defined for this tool.

Methods
-------
   
.. classmethod:: instance(cls, features=None)

   Find an instance of `cls` that meets the feature requirements. Tools can be found by their (class) name,
   as well as the names of their base class(es).


Examples
--------

Given a simple fabscript such as::

   from faber.tools.cxx import cxx
   
   rule(cxx.compile, 'hello.o', source='hello.cpp')

it becomes possible to configure your build environment by instantiating
different compilers::

  from faber.tools.gxx import gxx

  gxx = gxx()
  gxx11 = gxx(name='g++11', features=cxxflags('--std=c++11'))
  gxx03 = gxx(name='g++03', features=cxxflags('--std=c++03'))
  mingwxx = gxx(name='mingw++', command='/usr/bin/x86_64-w64-mingw32-g++')
  
Now you can invoke a build by selecting either of these to compile `hello.o`:

.. code-block :: none

  $ faber cxx.name=gxx

will invoke :code:`g++ ...`,

.. code-block :: none

  $ faber cxx.name=g++11

will invoke :code:`g++ --std=c++11 ...`,

.. code-block :: none

  $ faber cxx.name=mingw++

will invoke :code:`/usr/bin/x86_64-w64-mingw32-g++ ...`
