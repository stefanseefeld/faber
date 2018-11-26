Special Topics
==============

Configuring Builds
------------------

The build logic of a project may depend on features of the build platform that
isn't known in advance. The user (who does the build) may wish to provide some
parameters (such as prerequisite library paths), or check whether the compiler
supports the latest language features.

The `faber.config` subpackage provides facilities to perform such checks (akin
to those in the `GNU autoconf tool`). They define conditional features that
can be set either globally or for specific artefacts. For example::

  from faber.config import cxx_checks, report

  checks = [cxx_checks.has_cxx11(c.features, define('HAS_CXX11')),
            cxx_checks.has_cxx14(c.features, define('HAS_CXX14')),
            cxx_checks.has_cxx17(c.features, define('HAS_CXX17'))]

  config = report('config', checks)
  check = binary('check', 'main.cpp', features=config.use)
  ...

The `check` binary gets its features from the `config` report, which performs
a set of checks, and then defines macros corresponding to the compiler features
that are detected. Injecting these features implies a dependency, so whenever
`check` needs to be built, the associated config checks will be done first.
(Faber provides some caching mechanism so these checks don't have to be re-run
if their values are already known.)

Running Tests
-------------

An important part of building software is testing. Code that has not been tested
adequately generally does not work. As test execution is often intimately tied to
the construction of the tested code, it is natural to integrate the relevant logic
into the construction tool itself.

Consider this fabscript snippet::

  from faber.artefacts.binary import binary
  from faber.test import test, report, fail

  passing = binary('passing', 'passing.cpp')
  failing = binary('failing', 'failing.cpp')

  test1 = test('test1', passing, run=True)
  test2 = test('test2', failing, run=True)
  test3 = test('test3', failing, run=True, expected=fail)

  ...

The above defines three tests consisting in running test binaries. For the sake
of example, let us assume that one of the binaries is passing and one is failing.
the `test3` above takes an optional argument to indicate that the test is expected
to fail.

While it is of course possible to run the tests explicitly from the command line
(using `faber ... test1 test2 test3`), it is much more useful to run them using
the built-in report mechanism. In addition to executing the selected tests this
may produce a test summary, or even a more elaborate test report::

  report('test-report', [test1, test2, test3])

Invoking `faber test-report` will now generate output such as

.. code-block:: none

  test1: PASS
  test2: FAIL
  test3: XFAIL
  test summary: 1 pass, 1 failure, 1 expected failure

