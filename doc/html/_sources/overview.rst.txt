Overview
========

Basic usage
-----------

A `Faber` build process is encoded in one or more `fabscripts` that describe a set
of `artefacts` that may be constructed using `recipes` from other artefacts
(including existing input or source files). `Faber` will read those fabscripts to
assemble a dependency graph and perform the actions necessary to construct either
goals expressed as command-line arguments, or any default artefacts if no goals were
specified. features may be specified on the command-line as options to influence
the exact properties of the build process (e.g., `cxx.name=g++` may be used to
select a particular compiler, or `target.arch=x86` to select a specific target
architecture.

Hello World !
-------------

Consider this ubiquitous C++ file:

.. code-block:: C++

  #include <iostream>

  int main(int, char **)
  {
    std::cout << "Hello World !" << std::endl;
  }

which we want to compile into a `hello` binary. Here is the associated `fabscript`::

  from faber.artefacts.binary import binary
  from faber.test import test
  
  hello = binary('hello', 'hello.cpp')
  test_hello = test('test', hello, run=True)

  default = hello

The above defines two :term:`artefact`\ s `hello`, and `test`, then identifies 'hello'
to be built by default.

Building it
-----------

To build the `hello` binary, simply run :command:`faber` from within the
directory containing the `hello.cpp` source file and the `fabscript`.
This may produce output such as:

.. code-block:: none

  gxx.compile hello.o
  gxx.link hello

You may also want to perform the test (which in the above example simply consists
in running the binary), by running :command:`faber test`, which should produce output
such as:

.. code-block:: none

   run test
   Hello World !

   test: PASS

Finally, you can clean up all the generated files by executing :command:`faber -c`.

To use a separate build directory you can use the `--builddir` option. Likewise,
you may use `--srcdir` if the source tree isn't in the current location.

The above is a very simple example of how to use `faber` to build and test a binary
from C++ source code. Notice that the build logic is fully portable, i.e. does not
depend on any platform-specific compiler toolchain. End-users however typically
want to control what compiler is used in the build process.
So while `faber` tries to find appropriate tools able to perform the requested
task, it also provides user control over what toolchain to use, or what flags
to pass.
So with the appropriate toolchains installed on the build machine, it is possible
to use

.. code-block:: none
		
  faber cxx.name=g++

or

.. code-block:: none
		
   faber cxx.name=clang++

to pick a named compiler,
or

.. code-block:: none
		
   faber target.arch=w64

to pick the target architecture if you want to cross-compile a project.

