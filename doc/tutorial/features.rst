Features
========

A feature is a variable type that can be used to configure a build process. Features
are defined once, but can be instantiated multiple times, can be combined into
`feature sets`, can be used to filter and select other objects (such as tools), or
parametrize `artefacts`.

Defining vs. instantiating features
-----------------------------------

Features are defined with a name, an optional `attributes` argument, as well as an
optional `values` argument. `values`, if provided, defines a set of valid values
the feature may take. Without it, it may take arbitrary values.
For example, the `faber.tools.compiler` module defines a set of features that
are used to parametrize the various compiler-related actions that may be performed::

  from faber.feature import *

  include = feature('include', attributes=multi)
  link = feature('link', values=('shared', 'static'))
  ...
  

Feature values may then be instantiated from the above features::

  i1 = include('path1', 'path2')
  i2 = include('path3')
  l1 = link('shared')
  l2 = link('static')

While `include` values may be freely combined::

  i3 = i1 + i2

`link` values can't. (`l1 + l2` results in an error, unless both have the same value,
in which case this is a no-op). Typically, feature values are combined into feature-sets::

  fs = set(include('path1', 'path2'), link('shared'))

and feature values are accessible as::

  i = fs.include

Likewise, feature-sets can be combined using `+` or `+=`. In addition, feature values
from one feature-set may override feature values from another (for example, a default
feature-set may be overridden by a artefact-specific feature-set)::

  fs = default_fs
  fs.update(artefact_specific_fs)




Instances of these features can then be created either explicitly in the fabscripts,
or be defined globally via command-line options, and can be set when creating
artefacts. Compilers will then inspect these values and translate them into
compiler-specific flags.

For example, to add include paths to a rule by which an object file is compiled from
a source file, you may write::

  obj = rule('hello.o', 'hello.cpp', features=(include('path1', 'path2'),))

To define an include search path globally as a command line option, you may run:

.. code-block:: bash

  $ faber include=path1 include=path2

Features can also be composed::

  tool = feature('tool', name=feature(), version=feature())
  t1 = tool(name='gxx', version='6.3.2')
  t2 = tool(name='msvc') # leave version undefined

(Note how nested features don't require a `name` argument, as that can be deduced
from the name of the keyword argument.)
As all tools define such a composite feature (whose name is the name of the
associated tool class), it becomes possible to select tools by name using
command-line arguments (more on that in the section on tools):

.. code-block:: none

  $ faber cxx.name=gxx


