Boost.Faber documentation
=========================

.. toctree::
   :maxdepth: 2

   Overview <overview>
   Tutorial <tutorial/index>
   Reference <reference/index>
   Glossary <glossary>

Introduction
------------

`Faber` is a construction tool. Its main focus is the construction of *software*,
i.e. the process of building (compiling, linking), testing, and packaging of code,
though it is by no means limited to that usage, as all the fundamental concepts
have been designed with genericity and extensibility in mind.

`Faber` is portable, as it provides process and tool abstractions that operate on
all major platforms.

.. admonition:: Relationship to Boost.Build

   `Faber` started as an effort to replace the Jam-based `b2` *frontend* to bjam by
   a new Python interface, preserving all the major concepts that have been developed
   as part of Boost.Build (including the tool hierarchy, features / property-sets, and
   implicit rule generation).
   At this stage, only the `bjam` engine is being reused to drive the job scheduling.
   Everything else, notably the assembly of the tools and the artefact dependency graph
   is entirely rewritten in pure Python.

