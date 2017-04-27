Configuring Builds
==================

The build logic of a project may depend on features of the build platform that
isn't known in advance. The user (who does the build) may wish to provide some
parameters (such as prerequisite library paths), or check whether the compiler
supports the latest language features.

Providing build parameters
--------------------------

`faber` allows users to set parameters on the command-line using generic
`--with-<parameter>` and `--without-<parameter>` arguments, which are made
available to the build logic. To make this more convenient, these values
may be cached, so they only have to be provided once in the first invocation of
`faber`.
Consider this fabscript snippet::

  from faber.config import config

  c = config('config.py')
  python_inc = c.get_with('python-inc')
  python_linkpath = c.get_with('python-linkpath')
  python_lib = c.get_with('python-lib')
  ...

With `faber --with-python-inc=/usr/include/python2.7 --with-python-lib=python2.7`
this will construct a `config` object which makes the two parameters `python-inc`
and `python-lib` accessible and stores them in the "config.py" file for future use.
(In subsequent calls to `faber` these parameters will still be present, until the
"config.py" file is removed.) For convenience, a similar parameter dictionary is
provided for `--without-` parameters.

Running config checks in order to fine-tune a build
---------------------------------------------------

The `config` object can also be used to run some config checks. Similar to autoconf,
`faber` provides simple checks to detect compiler features, the presence of certain
headers, libraries, etc.
These checks can be used to modify a feature-set (typically by defining specific macros),
or otherwise modify the build process. (It's for example possible to include or exclude
certain source files from a build depending on these checks::

  from faber.config import config, cxx_checks

  c = config('config.py')
  checks = [cxx_checks.has_cxx11(c.features, define('HAS_CXX11')),
            cxx_checks.has_cxx14(c.features, define('HAS_CXX14')),
            cxx_checks.has_cxx17(c.features, define('HAS_CXX17'))]

  c.check(checks)
  # now use `c.features` to define build artefacts
  
Here we define three checks `has_cxx11`, `has_cxx14`, `has_cxx17` that will test whether
the selected compiler supports the given language feature. If so, the associated
`HAS_CXX...` macro will be defined in the associated feature-set.
