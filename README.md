![logo](https://github.com/stefanseefeld/faber/raw/develop/doc/_static/logo.png)


CI: ![Linux](https://github.com/stefanseefeld/faber/workflows/Test%20Ubuntu/badge.svg)
 ![OSX](https://github.com/stefanseefeld/faber/workflows/Test%20OSX/badge.svg)
 ![Windows](https://github.com/stefanseefeld/faber/workflows/Test%20Windows/badge.svg)

Code coverage: [![codecov.io](https://codecov.io/gh/stefanseefeld/faber/branch/develop/graph/badge.svg)](https://codecov.io/gh/stefanseefeld/faber)

This project started as a clone of [Boost.Build](https://github.com/boostorg/build/), to experiment with a new Python frontend.
Meanwhile it has evolved into a new build system, which retains most of the features found in Boost.Build, but with (hopefully !)
much simplified logic, in addition of course to using Python as scripting language, rather than Jam.


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
