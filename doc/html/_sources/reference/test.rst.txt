The `test` module
=================

.. py:currentmodule:: faber.test

The test classes can be used to define and run tests, and generate test reports.


synopsis
--------

.. autoclass:: faber.test.test
   :members: __init__

.. autoclass:: faber.test.report
   :members: __init__, print_summary

Examples
--------

::

  from faber.artefacts.binary import binary
  from faber.test import test, report, fail

  passing = binary('passing', 'passing.cpp')
  failing = binary('failing', 'failing.cpp')

  test1 = test('test1', passing, run=True)
  test2 = test('test2', failing, run=True)
  test3 = test('test3', failing, run=True, expected=fail)
  test4 = test('test4', failing, condition=False)

  r = report('test-report', [test1, test2, test3, test4])

Running `faber test-report` will perform the tests, print
out individual results (e.g., 'PASS', 'FAIL', etc.), then print
out a summary, such as:

.. code-block:: none

  test summary: 1 pass, 1 failure, 1 expected failure, 1 skipped
