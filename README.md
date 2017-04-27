Boost.Faber (experimental)
==========================

Linux & OSX: [![TravisCI](https://travis-ci.org/stefanseefeld/faber.svg?branch=develop)](https://travis-ci.org/stefanseefeld/faber)
Windows: [![AppVeyor](https://ci.appveyor.com/api/projects/status/vci9pp0endmqcayp/branch/develop?svg=true)](https://ci.appveyor.com/project/stefanseefeld/faber/branch/develop)


This repository is a clone of https://github.com/boostorg/build/, with the goal to produce a prototype of the next generation
build system. While hopefully this will result in working code, the intent is not to fork Boost.Build, but rather to experiment
and inform the future development of the upstream project.

A stripped-down version of `bjam` is being used to schedule build actions, but it has been rewrapped into a Python extension module.
All the Jam scripting has been replaced by a brand-new Python frontend.


Building
--------

``` bash
python setup.py build
```

Testing
-------

``` bash
py.test tests
```

Examples
--------

Working examples are in `examples/`

Docs
----

Documentation can be found in the `doc/` directory (published frequently in https://stefanseefeld.github.io/faber).

Happy hacking !

  --Stefan
