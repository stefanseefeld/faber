The `config` module
===================

.. py:currentmodule:: faber.config

.. contents :: Table of Contents

The config mechanism can be used to perform a set of checks prior to defining
the build logic. Config check results are typically captured as features that can
subsequently be used, either to fine-tune the build actions (e.g., by defining a
macro or adding an include path), to select what source files to include in a build,
etc.


synopsis
--------

.. autoclass:: faber.config.check.check

.. autoclass:: faber.config.try_compile.try_compile

.. autoclass:: faber.config.try_link.try_link
	       
.. autoclass:: faber.config.cxx_checks.has_cxx11
.. autoclass:: faber.config.cxx_checks.has_cxx14
.. autoclass:: faber.config.cxx_checks.has_cxx17
.. autoclass:: faber.config.c_checks.sizeof
	       

Examples
--------

::

   checks = [c_checks.sizeof('char', cxx, features=features),
             c_checks.sizeof('long', cxx, features=features),
             cxx_checks.has_cxx11(features, define('HAS_CXX11')),
             cxx_checks.has_cxx14(features, define('HAS_CXX14')),
             cxx_checks.has_cxx17(features, define('HAS_CXX17'))]

   config = report('config', checks)

Running `faber config` will perform the above checks, and print out a little report, such as:

.. code-block:: none

  configuration check results:
  sizeof_char : 1 
  sizeof_long : 8 
  pytest      : False 
  has_cxx11   : True 
  has_cxx14   : True 
  has_cxx17   : False 

(Note that the check base class implements some caching, so the actual checks are only
performed if the cache is not present or invalidated.)
