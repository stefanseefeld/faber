Advanced concepts
=================

Tools
-----

Tools provide an object-oriented model around actions. For example, an abstract `compiler`
tool may provide different methods to compile and link code. Concrete compilers may
then provide implementations of that base class, and run the appropriate command for
the respective platform. That substitution can happen during the build process, while
the build logic encoded in the fabscript is strictly platform-agnostic.

Let's augment the original `Hello World !` example to illustrate this. Faber provides
a few built-in tools, such as C and C++ compilers. The abstract interface may look like::

  class cxx(object):

      compile = action()
      link = action()

which allows fabscripts to reference `cxx.compile` when defining rules::

  obj = rule(cxx.compile, 'hello.o', 'hello.cpp')

`faber` also provides specific compilers implementing the above interface, for example::

  class gxx(cxx):

      compile = action('g++ -c -o $(<) $(>)')
      ...

allowing the build system to later substitute `gxx.compile` where `cxx.compile` was
requested. For each reference to an abstract tool, faber will attempt to instantiate
a suitable concrete tool matching the currently active feature set. Thus it's possible
to request a specific compiler on the command line:

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
  
  implicit_rule(self.compile, types.obj, types.cxx)
  implicit_rule(self.archive, types.lib, types.obj)
  implicit_rule(self.link, types.bin, (types.obj, types.dso, types.lib))
  implicit_rule(self.link, types.dso, (types.obj, types.dso, types.lib))

to register four implicit rules:

* one to build an object file from a C++ source file using a `compile` action
* one to build a static library from one or more object files using an `archive` action
* one to build a binary from object files, as well as shared and static libs using a `link` action
* one to build a shared library from object files, as well as shared and static libs using a `link` action

Composite artefacts
-------------------

In previous sections we dealt with artefacts that mostly correspond directly to
files, built by specific commands. While this model appeals through its simplicity,
it is not very portable: Most actions depend heavily on the platforms they are to be
executed on. Furthermore, depending on the platform / tools, different intermediate
artefacts may need to be built.

Let's consider again the case of a binary using a library. But instead of
referring explicitly to the library's file name (which may differ depending on the
platform, as well as whether or not it is compiled as a shared or a static library),
we use a composite artefact to encapsulate those details.
We use a new `library` rule to define it::

  from faber.artefacts.library import *
  greet = library('greet', 'greet.cpp')

The `library()` call looks similar to the `rule()` call: xxx
`artefact` and a `sources` argument, and returns the artefact instance.
However, the artefact's name (`greet.name`) doesn't necessarily correspond
to the filename.
The precise build instructions are fully encapsulated inside the artefact,
and will take into account both the (target) platform as well as the tool and
features selected when the build was started.

Similarly, to use the library, you can pass `greet` as source to any dependent
rule or artefact, and the build logic will determine the precise action sequence
to use it::

  from faber.artefacts.binary import *
  hello = binary('hello', ['hello.cpp', greet])

Then, to build this with `greet` as shared library (`.so` on UNIX, `.dll` on
Windows), call `faber link=shared`. To build this as a static library
(`.a` on UNIX, `.lib` on Windows), use `faber link=static`.



Modular builds
--------------

Once projects become large enough, it becomes useful to modularize the code as
well as the build instructions. Consider a case where we want to build a
library as well as a binary that is using that library. Both live in
separate directories::

  .../project/
              subdir/
	             greet.cpp
		     fabscript
              hello.cpp
	      fabscript


The fabscript for the subproject is simply a stripped-down version of
our previous version, as it now only builds the `greet` library::

  from faber.artefacts.library import *

  greet = library('greet', 'greet.cpp')

  default = greet

The toplevel fabscript now includes that sub-project by virtue of a :term:`module`::

  from faber.artefacts.binary import binary

  subdir = module('subdir')

  hello = binary('hello', ['hello.cpp', subdir.greet])

  rule(action('test', '$(>)'), 'test', hello, attrs=notfile|always)

  default = hello

Notice how the call to `module('subdir')` returns the module object,
through which we can access nested artefacts (and other variables).
The binary rule can now directly reference the `subdir.greet`
library as one of its sources, and the right thing will happen.

