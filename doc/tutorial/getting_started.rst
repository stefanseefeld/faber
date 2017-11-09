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
step to produce the final executable. Here is the associated `fabscript`::

  # define some actions
  compile = action('c++.compile', 'c++ -c -o $(<) $(>)')
  link = action('c++.link', 'c++ -o $(<) $(>)')

  # bind artefacts to sources using the above recipes
  obj = rule(compile, 'hello.o', 'hello.cpp')
  bin = rule(link, 'hello', obj)
  test = rule(action('run_test', './$(>)'), 'test', bin, attrs=notfile|always)

  default = bin

The above defines the two :term:`action`\ s `compile` and `link` and three
:term:`artefact`\ s `obj`, `bin`, and `test`, then identifies one of the artefacts
(`bin`) to be built by default (i.e. if no artefact is explicitly requested).

Building it
-----------

To build the `hello` binary, simply run :command:`faber` from within the
directory containing the `hello.cpp` source file and the `fabscript`.
This may produce output such as:

.. code-block:: none

  c++.compile ./hello.o
  c++.link ./hello

You may also want to perform the test (which in the above example simply consists
in running the binary), by running :command:`faber test`.

Finally, you can clean up all the generated files by executing :command:`faber -c`.

To use a separate build directory you can use the `--builddir` option. Likewise,
you may use `--srcdir` if the source tree isn't in the current location.

The above is a very simple example of how to use `faber` to build and test a binary
from C++ source code. This example assumes that you are running in an environment
with a C++ compiler that can be executed as `c++ ...`. In the next couple of chapters
we will explore how to generalize this basic idea to a portable workflow that works
on many platforms with different compilers. We will also see how to customize the
build process to generate different `build variants`, how to scale the build logic
by making it `modular`, as well as adding other common features, such as configure checks,
tests and test report generation, and much more.
