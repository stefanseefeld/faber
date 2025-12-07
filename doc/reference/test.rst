The `test` module
=================

.. py:currentmodule:: faber.test

The test classes can be used to define and run tests, and generate test reports.


synopsis
--------

.. autoclass:: faber.test.Test
   :members: __init__

.. autoclass:: faber.test.Report
   :members: __init__, print_summary

Examples
--------

::

  from faber.artefacts.binary import Binary
  from faber.test import Test, Report, fail

  passing = Binary('passing', 'passing.cpp')
  failing = Binary('failing', 'failing.cpp')

  test1 = Test('test1', passing, run=True)
  test2 = Test('test2', failing, run=True)
  test3 = Test('test3', failing, run=True, expected=fail)
  test4 = Test('test4', failing, condition=False)

  r = Report('test-report', [test1, test2, test3, test4])

Running `faber test-report` will perform the tests, print
out individual results (e.g., 'PASS', 'FAIL', etc.), then print
out a summary, such as:

.. code-block:: none

  test summary: 1 pass, 1 failure, 1 expected failure, 1 skipped
