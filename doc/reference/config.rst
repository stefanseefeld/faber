config
======

.. contents :: Table of Contents

The config mechanism can be used to perform a set of checks prior to defining
the build logic. Config check results are typically captured as features that can
subsequently be used, either to fine-tune the build actions (e.g., by defining a
macro or adding an include path), to select what source files to include in a build,
etc.


synopsis
--------

.. autoclass:: faber.config.config
   :members: __init__, get_with, get_without, check

.. autoclass:: faber.config.try_compile.try_compile

.. autoclass:: faber.config.try_link.try_link
	       
.. autoclass:: faber.config.cxx_checks.has_cxx11
.. autoclass:: faber.config.cxx_checks.has_cxx14
.. autoclass:: faber.config.cxx_checks.has_cxx17
       

Examples
--------

::

   # define some actions
