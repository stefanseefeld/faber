Tools
=====

Tools provide an object-oriented model around actions. For example, a `compiler`
tool may provide different methods to compile and link code. Using class hierarchies
for tools provides polymorphism, so a build script may refer to a `cxx` compiler,
which for a given build gets replaced by an actual compiler instance that's
available on the platform on which the build is performed.

Types vs. instances
-------------------

Tools provide an abstraction mechanism for actions. For example, the `cxx` tool
defines the interface for compiling C++ code::

  class cxx(tool):

    compile = action()
    link = action()

which allows fabscripts to use to reference `cxx.compile` when defining rules::

  obj = rule('hello.o', 'hello.cpp', recipe=cxx.compile)

`faber` includes a range of C++ compilers that implement the above interface.
All these classes are registered with their respective base-classes, so a suitable
implementation can be instantiated on-demand. For example, `gxx` derives from `cxx`::

  class gxx(cxx):

    compile = action('g++ -c -o $(<) $(>)')
    ...

allowing the build system to later substitute `gxx.compile` where `cxx.compile` was
requested. This substitution may be automatic, unless a specific compiler is
requested as a feature, for example as a command-line option:

.. code-block:: none

  $ faber cxx.name=gxx

Tools may also be instantiated explicitly in a config file, allowing for additional
configuration (such as specific paths or flags)::

  gxx11 = gxx(name='g++11', features=cxxflags('--std=c++11'))

Here, we defined a new `gxx` instance using an additional flag `==std=c++11`, and
gave it the name `g++11`. To select that from the command line, we would invoke:

.. code-block:: none

  $ faber cxx.name=g++11

You may also want to set up a `gxx` instance to configure a cross-compiler::

  mingwxx = gxx(name='mingw++', command=`/usr/bin/x86_64-w64-mingw32-g++`)
  
and then cross-compile by invoking:

.. code-block:: none

  $ faber cxx.name=mingw++
  
Implicit rules
--------------

While simple build pipelines may be declared using `rules`, this leads to a lot
of repitition as very similar rules would need to be declared to compile all source
files into object files, for example. To simplify this, `implicit rules` can be provided
by tools, which don't declare how to make a specific artefact from a source (or prerequisite
artefact), but rather how a certain artefact *type* (e.g., an object file) can be generated
from a source (or artefact) type (such as a C or C++ source file).
Higher-order artefacts such as `library` or `binary` can then request that the appropriate
implicit rules are instantiated into ordinary rules to make a library or a binary without
the user having to spell out all the intermediate artefacts.

This is done in a tool's constructor. For example, the `gxx` constructor calls::
  
  assembly.irule(types.obj, types.cxx, self.compile)
  assembly.irule(types.lib, types.obj, self.archive)
  assembly.irule(types.bin, (types.obj, types.dso, types.lib), self.link)
  assembly.irule(types.dso, (types.obj, types.dso, types.lib), self.link)

to register four implicit rules:

* one to build an object file from a C++ source file using a `compile` action
* one to build a static library from one or more object files using an `archive` action
* one to build a binary from object files, as well as shared and static libs using a `link` action
* one to build a shared library from object files, as well as shared and static libs using a `link` action

