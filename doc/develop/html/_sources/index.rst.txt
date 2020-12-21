Faber documentation
===================

.. toctree::
   :maxdepth: 2

   Overview <overview>
   Tutorial <tutorial/index>
   Reference <reference/index>
   appendix

Introduction
------------

`Faber` is a construction tool. Its main focus is the construction of *software*,
i.e. the process of building (compiling, linking), testing, and packaging of code,
though it is by no means limited to that usage, as all the fundamental concepts
have been designed with genericity and extensibility in mind.

`Faber` is portable, as it provides process and tool abstractions that operate on
all major platforms. This abstraction supports a common division of labour, as
platform specialists can implement and extend specific tools (e.g. compilers),
while application developers can focus on the higher level build logic needed by
their projects, without having to become an expert in all the platforms they want
to support.

`Faber` can be used as a library. It is possible to embed all of faber into other
code, for example to provide alternative (graphical) frontends. It can also be
extended, for example to support additional output formats (say, to generate
test reports).
