rule
====

.. contents :: Table of Contents

A rule describes when a target must be generated.


synopsis
--------

.. autofunction:: faber.rule.rule
.. autofunction:: faber.rule.alias
.. autofunction:: faber.rule.depend



Examples
--------

::

   # bind target to source using the above rules
   rule('hello.o', 'hello.cpp', recipe=compile)
   rule('hello', 'hello.o', recipe=action('link_with_logging', link_with_logging))
   rule('test', 'hello', recipe=action('run_test', '$(>)'), attrs=notfile|always)

