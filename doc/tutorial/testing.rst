Running Tests
=============

An important part of building software is testing. Code that has not been tested
adequately generally does not work. As test execution is often intimately tied to
the construction of the tested code, it is natural to integrate the relevant logic
into the construction tool itself.

Defining tests
--------------

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

Running tests and producing a test report
-----------------------------------------

While it is of course possible to run the tests explicitly from the command line
(using `faber ... test1 test2 test3`), it is much more useful to run them using
the built-in report mechanism. In addition to executing the selected tests this
may produce a test summary, or even a more elaborate test report::

  report(test1, test2, test3)

Invoking `faber report` will now generate output such as

.. code-block:: none

  test1: PASS
  test2: FAIL
  test3: XFAIL
  test summary: 1 pass, 1 failure, 1 expected failure

