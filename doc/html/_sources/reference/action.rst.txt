The `action` class
==================

.. py:currentmodule:: faber.action

An action is performed in order to (re-)generate an artefact.
it uses either a command string (executed in a platform-specific shell), or
a Python callable.


Constructor
-----------

.. method:: action()

   Construct an empty (abstract) action. This is useful to define an abstract `tool`.

.. method:: action(command)

   Construct an action from the given command (string).

.. method:: action(name, command)

   Construct an action with the given name, from the given command (string).

Call operator
-------------

.. method:: __call__(target, source)
   
   Call the action explicitely. Returns success.


Examples
--------

::

   # define some actions
   compile = action('c++.compile', 'c++ -c -o $(<) $(>)')
   link = action('c++.link', 'c++ -o $(<) $(>)')
   test = action('run_test', '$(>)')

   # this demonstrates how to compound actions
   def run_test(target, source):
     if test(target, source):
       print('PASS')
     else:
       print('FAIL')

   # bind target to source using the above rules
   obj = rule(compile, 'hello.o', 'hello.cpp')
   bin = rule(link, 'hello', obj)
   t = rule(run_test, 'test', bin, attrs=notfile|always)
