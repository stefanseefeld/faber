Basic concepts
==============

In the previous section we have seen a compact way to define a simple build logic to
compile a binary from C++ source code, and test it. A `binary` is an example of a
`composite artefact`. In order to understand that, we first need to take a step back
and look at a few more basic building blocks out of which such higher-level constructs
are composed.
The central concepts in `faber` are *artefacts*, which are generated using *actions*.
In the simplest case, artefacts are declared using *rules*, which instruct faber how
to generate artefacts, possibly from other ("source") artefacts.

So to appreciate this mechanism, let's rebuild the previous example from these
foundational building blocks. Consider this `fabscript`::

  
  # define some actions
  compile = action('c++.compile', 'c++ -c -o $(<) $(>)')
  link = action('c++.link', 'c++ -o $(<) $(>)')

  # bind artefacts to sources using the above recipes
  obj = rule(compile, 'hello.o', 'hello.cpp')
  bin = rule(link, 'hello', obj)
  test = rule(action('run_test', './$(>)'), 'test', bin, attrs=notfile|always)

  default = bin

In the following sections we will dissect this build logic to understand the individual
items, before we then move on to higher level abstractions.

Actions and recipes
-------------------

The following line defines a very simple action called `c++.compile`::

   compile = action('c++.compile', 'c++ -c -o $(<) $(>)')

It can be used as a recipe in a rule to compile an object::

  obj = rule(compile, 'hello.o', 'hello.cpp')

The action has a name, which will be reported as the build process progresses, as well
as a command, which will be executed in a platform-specific shell. Such commands may
use variables (`$(...)`) which are substituted when the action is bound to specific
targets and sources, that is, when it is instantiated into a `recipe`.
In the above case the two variables `<` and `>` are being substituted
for target and source respectively, so the command will actually be:

.. code-block:: none

  c++ -c -o hello.o hello.cpp

It is also possible to use Python functions as actions, with the following calling convention::

  def do_something(targets, sources=[]):
      ...

that is, the function should take one or two arguments, the first being a list of target
artefacts (which this function should generate or update), as well as an optional list
of source artefacts, serving as input.

Actions may also be called explicitly from inside functions. Consider the example from the
previous chapter where we defined a `run_test` action to update a `test` artefact::

  test = rule(action('run_test', './$(>)'), 'test', bin, attrs=notfile|always)

We could adorn this action with some output to indicate whether the test passed or failed::

  run = action('run', './$(>)')

  # python functions may be actions, too
  def run_test(target, source):
      print('performing {}...'.format(target[0].name))
      # actions may also be called explicitly
      if run(target, source):
          print('...success.')
      else:
          print('...failed.')

  test = rule(run_test, 'test', bin, attrs=notfile|always)

Note that the new `run_test` recipe has become a (Python) function, still using the same
name as before, but instead of using a (shell) command, now being executed in-process.
The function itself explicitly calls the action `run`, but performs additional work before
and after that. While in this case this is a trivial print, this can be arbitrarily complex
logic, using the full power of Python.
In the above, we print out the name of the first target (in our fabscript there will only be
one). We will cover the :term:`artefact` API including the `name` property a little later.

Rules, dependencies, aliases
----------------------------

As mentioned before, :term:`rule`\ s are used to declare how to make (or update) target
artefacts from sources. In the simplest case a rule is called with two arguments: the action
to perform, and the target to generate or update. It will return an `artefact` instance::

  output = rule(build, 'output')

As we have already seen, the action argument may either be an action instance, or a Python
function (or more generally: `callable`). The target argument may be one or more strings
(target names), or artefact instances. (While most actions generate an individual target,
some generate more than one.)
The most common case, though, includes also a `sources` argument, which has the same type
as the `target` argument: one or more names or artefact instances.

In addition, there are additional (optional) arguments. For the full list please refer
to the reference manual. Here we describe the most common ones:

* dependencies: a list of artefacts that need to be up-to-date before this rule may be invoked
* attrs: attributes to be set for this artefact:
  
  - notfile: the artefact is not a file
  - always: never consider this artefact up-to-date
  - nocare: allow the update of this artefact to fail
* features: a set of features to be associated with this artefact

In addition to the `rule` function that declares how to update a target artefact
using a recipe, it may be desirable to merely declare a dependency::

  depend(a, b)  # make sure b is up to date before a is updated

or to define an 'alias' for one or more other artefacts::

  alias('all', [a, b, c])  # update a, b, and c whenever `faber all` is called


Features
--------

Features allow a build process to be parametrized by injecting variables into
actions, as well as into the logic that is used to decide which artefacts to
generate or update.

Values may be defined globally, for example as command-line options:

.. code-block:: none

  $ faber variant=release target.os=w64

or per artefact::

  lib=library('greet', sources='greet.cpp', features=link('shared'))

An individual feature corresponds to a variable (e.g. 'variant', 'target.os',
or 'link', in the above examples), which may hold different values (e.g.
'release', 'w64', 'shared').
Features are typically defined in a domain-specific context. "define", "include",
and "link" are features defined in the context of C/C++ compilation, while
"target.os" is a feature more generally useful to describe the system binary
artefacts will run on).

As different commands will use different flags based on their values, these
values are `mapped` to command-specific variables as recipes are instantiated
for a given target artefact. Consider the `compile` action we already encountered,
now augmented by a flag to set an include path. A somewhat more advanced version
suitable to be used with `g++` on Linux may look somewhat like::

  class compile(action):

      command = 'g++ $(cppflags) -c -o $(<) $(>)'
      cppflags = map(compiler.include, translate, prefix='-I')
  
i.e. a `cppflags` variable (referenced in the action command) is generated from
a platform-agnostic `compiler.include` feature by prefixing all values with '-I'.

This powerful mechanism allows complex build logic to be separated into a generic
part that maps platform-agnostic features to platform-specific tools and commands,
and an application-specific part that is focused on the semantics of their build
system, without having to think about (or in fact know) all platforms they want
to support.

While in the simplest case feature values are defined statically, they may also
be computed dynamically as an artefact is updated. We will look more into the
resulting complexities of such data flows in a later chapter.

Artefacts
---------

An :term:`artefact` is the central concept at the heart of `faber`. Typically,
artefacts are declared using `rules` as described in earlier sections, or as
`aliases` to other artefacts. While we leave the full description of the
associated API to the reference manual, here are a few frequently used properties:

* name: the (unqualified) name of the artefact. In a simple case, this also corresponds
        to the name by which it can be invoked via `faber <name>`
* features: the feature set used to update the artefact
* boundname: the filename if this artefact corresponds to a file, a simple name otherwise.

Domain-specific artefacts may be constructed directly, rather than by virtue of a `rule` call.
Examples include configure checks, test execution and reporting, or composite artefacts
to build libraries or binaries from sources.
All of those will be discussed in detail in later chapters.
