Actions
=======

The following line defines a very simple action called `c++.compile`::

   compile = action('c++.compile', 'c++ -c -o $(<) $(>)')

It can be used as a recipe in a rule to compile an object::

  obj = rule('hello.o', 'hello.cpp', recipe=compile)

When the action is executed, its command will be run in a (platform-specific)
shell. In the above case the two variables `<` and `>` are being substituted
for artefact and source respectively, so the command will actually be:

.. code-block:: none

  c++ -c -o hello.o hello.cpp



