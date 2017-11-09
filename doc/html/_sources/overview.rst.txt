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

Command-line interface
----------------------

.. argparse::
   :filename: scripts/faber
   :func: make_parser
   :prog: faber
