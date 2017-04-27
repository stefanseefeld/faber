action
======

.. contents :: Table of Contents

An action is something that is performed in order to (re-)generate a 'target'.
it uses either a command string (executed in a platform-specific shell), or
a Python callable.


synopsis
--------

.. autoclass:: faber.action.action
   :members: __init__



Examples
--------

::

   # define some actions
   compile = action('c++.compile', 'c++ -c -o $(<) $(>)')
   link = action('c++.link', 'c++ -o $(<) $(>)')

   # this demonstrates how to compound actions
   def link_with_logging(target, source):
     print('calling linker...')
     link(target, source)

   # bind target to source using the above rules
   rule('hello.o', 'hello.cpp', recipe=compile)
   rule('hello', 'hello.o', recipe=action('link_with_logging', link_with_logging))
   rule('test', 'hello', recipe=action('run_test', '$(>)'), attrs=notfile|always)

