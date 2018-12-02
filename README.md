![logo](https://github.com/stefanseefeld/faber/raw/develop/doc/_static/logo.png)


Linux & OSX: [![travis-ci](https://travis-ci.org/stefanseefeld/faber.svg?branch=develop)](https://travis-ci.org/stefanseefeld/faber)
Windows: [![appveyor](https://ci.appveyor.com/api/projects/status/vci9pp0endmqcayp/branch/develop?svg=true)](https://ci.appveyor.com/project/stefanseefeld/faber/branch/develop)
Code coverage: [![codecov.io](https://codecov.io/gh/stefanseefeld/faber/branch/develop/graph/badge.svg)](https://codecov.io/gh/stefanseefeld/faber)

This project started as a clone of [Boost.Build](https://github.com/boostorg/build/), to experiment with a new Python frontend.
Meanwhile it has evolved into a new build system, which retains most of the features found in Boost.Build, but with (hopefully !)
much simplified logic, in addition of course to using Python as scripting language, rather than Jam.
The original bjam engine is still in use as scheduler, though at this point that is mostly an implementation detail.


Building and Installing
-----------------------

``` bash
python setup.py install
```

(See the [Getting Started: Building Faber](https://github.com/stefanseefeld/faber/wiki/Getting-Started%3A-Building-Faber) for a
detailed discussion of the build process, as well as parameters to customize it.)

Examples
--------

Working examples are in `examples/`

Docs
----

Documentation can be found in the `doc/` directory (published frequently in https://stefanseefeld.github.io/faber).

Happy hacking !

  --Stefan
