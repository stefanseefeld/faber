Getting Started
===============

Hello World !
-------------

Consider this ubiquitous C++ file:

.. code-block:: C++

  #include <iostream>

  int main(int, char **)
  {
    std::cout << "Hello World !" << std::endl;
  }

which for the sake of the example we want to compile into a `hello` binary
using two steps: a `compile` step to produce an object file, followed by a `link`
step to produce the final executable. Here is the associated build script::

  # define some actions
  compile = action('c++.compile', 'c++ -c -o $(<) $(>)')
  link = action('c++.link', 'c++ -o $(<) $(>)')

  # bind artefacts to sources using the above recipes
  obj = rule('hello.o', 'hello.cpp', recipe=compile)
  bin = rule('hello', obj, recipe=link)
  test = rule('test', bin, recipe=action('run_test', '$(>)'), attrs=notfile|always)

  default = bin

The above defines the two :term:`action`\ s `compile` and `link` and three
:term:`artefact`\ s `obj`, `bin`, and `test`, then identifies one of the artefacts
(`bin`) to be built by default (i.e. if no artefact is explicitly requested).

Building it
-----------

To build the `hello` binary, simply run :command:`faber` from within the
directory containing the `hello.cpp` source file and the `faber`.
This may produce output such as:

.. code-block:: none

  ...found 3 artefacts...
  ...updating 2 artefacts...
  c++.compile ./hello.o
  c++.link ./hello
  ...updated 2 artefacts...

You may also want to perform the test (which in the above example simply consists
in running the binary), by running :command:`faber test`.

Finally, you can clean up all the generated files by :command:`faber clean`.

To use a separate build directory you can use the `--builddir` option. Likewise,
you may use `--srcdir` if the source tree isn't in the current location.

Actions
-------

The above build script defines two actions, each with a name and a command. The
name is used to report the action when it is performed, while the command is being
executed in a platform-specific shell.

It is also possible to use a Python callable (such as an ordinary function)
instead of a command (string). We could modify the above build script by
introducing a function and then bind that to the appropriate artefact::

  def verbose_link(artefact, source):
    print('calling linker...')
    link(artefact, source)

  rule('hello', obj, recipe=action('verbose_link', verbose_link))

Notice how we can call actions directly from within Python code, allowing
actions to be composed.

Artefacts
---------

The above build script uses rules to define three artefacts. Typically, an artefact
depends on one or more sources, and is only rebuilt if at least one of its
sources is newer than itself. Thus, if you perform :command:`faber` a second
time, you will simply see

.. code-block:: none
		
  ...found 3 artefacts...

However, if you run :command:`faber test` multiple times, the test will be
executed each time, even if the executable being tested hasn't changed.
This is achieved using the `always` attribute. (In addition, the test artefact
doesn't correspond to a file on the file system, so the `notfile` attribute is
used to express that.

Tools
-----

Tools provide an object-oriented model around actions. For example, a `compiler`
tool may provide different methods to compile and link code. Using class hierarchies
for tools provides polymorphism, so a buid script may refer to a `cxx` compiler,
which for a given build gets replaced by an actual compiler instance that is
available on the platform on which the build is performed.

Let's modify the above build logic to use the pre-defined `cxx` tool::

  from faber.tools.cxx import cxx

  # make artefacts from source using a pre-defined C++ compiler tool
  obj = rule('hello.o', 'hello.cpp', recipe=cxx.compile)
  bin = rule('hello', obj, recipe=cxx.link)

Note that the `cxx` tool is abstract. It defines an interface (the two `compile`
and `link` methods), but doesn't implement them. Let us assume that we are running
on a platform with a `g++` compiler installed, so we can create a few instances
in the `config file` ("~/faber.rc")::

  from faber.tools.gxx import gxx

  gxx11 = gxx(name='g++11', features=cxxflags('--std=c++11'))
  gxx03 = cxx(name='g++03', features=cxxflags('--std=c++03'))
  gxx98 = gxx(name='g++98', features=cxxflags('--std=c++98'))

(On Windows, with at least one MSVC installation, we could similarly use::

  from faber.tools.msvc import msvc

  vc = msvc()

)

  
The above creates three `gxx` instances, named 'g++11', 'g++03', and 'g++93'
respectively. As `gxx` is a subclass of `cxx`, it's possible to use either of
them where the above build logic requests `cxx.compile` and `cxx.link`.

To do that run :command:`faber cxx.name=g++11` for example to select the `gxx11`
instance above.

Features
--------

In the previous section we have used three instances of a C++ compiler that used
certain `feature values` to customize the compilation step. Furthermore, a feature
was used on the command-line to select which of these compilers to use.

Features are typed values. Some may take on arbitrary values (names, compiler flags,
...), others may only assume values from a pre-defined set (link type, threading,
...). Features are used to provide a platform-agnostic way to customize tools and
how they build artefacts.

Artefacts
---------

In the above example, we were building a `hello` binary from a `hello.cpp` source
file. Let us now expand that example by separating the code into a library and a
main binary. We are facing the choice of building a shared or a static library.
Depending on that, the sequence of actions as well as the tools needed to perform
them, vary.
For that reason, `faber` offers "composite artefacts", which allow to abstract
the details::

  from faber.artefacts.binary import binary
  from faber.artefacts.library import library

  greet = library('greet', 'greet.cpp')
  hello = binary('hello', ['hello.cpp', greet])

Here, the `hello` artefact is defined to be a `binary` to be built from a `hello.cpp`
source file as well as a `greet` library. The latter is itself defined as a
`library`, to be built from a `greet.cpp` source file.

Both of these artefacts (`greet` and `hello`) are examples of "composite artefacts",
as the build process involves intermediate artefacts that the author of this
fabscript doesn't need to think about, to make the declaration portable.
For example, while on GNU/Linux the `greet` library might actually be a file named
`libgreet.a` (or `libgreet.so`, if it is built as a shared library), on Windows the
equivalent file may be called `libgreet.lib` or `libgreet.dll`, respectively.

Here, features really become useful, as we can specify whether to build a shared or
a static library using the `compiler.link` feature::

  from faber.tools.compiler import link

  ...
  greet = library('greet', 'greet.cpp', features=link('shared'))
  static_greet = greet(features=link('static'))

Now, `greet` is being defined to be a shared library named "greet", while
`static_greet` becomes a variant of it, built as a static library. `hello` can
now be defined with either of the two::

  hello = binary('hello', ['hello.cpp', greet])
  static_hello = binary('hello', ['hello.cpp', static_greet])
  
Modules
-------

To scale this example up even further, it might be desirable to separate the `greet`
library and `hello` binary into separate directories, each with its own fabscript.
Let's assume this source directory layout:

.. code-block:: none
  
  .../project/
              greet/
                    greet.hpp
                    greet.cpp
                    fabscript
              hello.cpp
              fabscript

The `greet` module now contains its own fabscript::

  from faber.artefacts.library import library

  greet = library('greet', 'greet.cpp')
  alias('clean', clean)

  default = greet

and will build nothing but the `greet` library. The root fabscript can include it
simply via::

  from faber.artefacts.binary import binary

  greet = module('greet')
  hello = binary('hello', ['hello.cpp', greet.greet])
  test = rule('test', hello, recipe=action('test', '$(>)'), attrs=notfile|always)
  alias('clean', clean)

  default = hello

Notice how the `greet` artefact from the `greet` module is now available as
`greet.greet`.
