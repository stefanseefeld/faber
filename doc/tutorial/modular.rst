Modular Builds
==============

Once projects become large enough, it becomes useful to modularize the code as
well as the build instructions. Consider a case where we want to build a
library as well as a binary that is using that library. Both live in
separate directories::

  .../project/
              subdir/
	             greet.cpp
		     fabscript
              hello.cpp
	      fabscript


The library subproject
----------------------

The build script we use is very similar to the ones we have seen before. We simply
introduce a new tool to produce the library (which on UNIX uses an `archiver`)::

  from faber.tools.cxx import cxx
  from faber.tools.archiver import archiver

  rule('greet.o', source='greet.cpp', recipe=cxx.compile)
  greet = rule('libgreet.a', source='greet.o', recipe=archiver.ar)

  default = greet

Two little points may be worth noticing:

* The `rule` function actually returns the artefact objects, so in the above case
  we assign that to the `greet` variable.

* Functions that accept a `source` or `artefact` argument typically accept either
  strings (representing file names) or artefact objects. So here we define the
  `default` variable using an artefact object rather than its filename.

The binary project
----------------------

The build script here is again quite similar to previous examples. It
uses however a :term:`module` to refer to the sub-project::

  from faber.tools.cxx import cxx

  subdir = module('subdir')

  rule('hello.o', source='hello.cpp', recipe=cxx.compile)
  hello = rule('hello', source=['hello.o', subdir.greet])
  test('test', hello, attrs=notfile|always)

  default = hello

A few things are worth noticing here:

* The `module` function allows to recurse into subdirectories (or in fact any
  directories) to gather build instructions.

* All the content is available through the returned object, so `subdir.greet`
  refers to the `greet` artefact we defined above inside the :file:`subdir/fabscript`.

* As the `source` argument may contain artefact objects, we can simply pass that
  down to define the `hello` artefact as being built from `libgreet.a`.

