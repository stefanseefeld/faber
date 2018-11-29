rule, alias, depend
===================

.. py:currentmodule:: faber.rule

A rule describes how to update an artefact using a recipe.
An alias defines a means to reference one or more artefacts
with a single name / object.
Depend allows to make an artefact explicitly dependent one
or more other artefacts.


synopsis
--------

.. autofunction:: faber.rule.rule
.. autofunction:: faber.rule.alias
.. autofunction:: faber.rule.depend


Examples
--------

::

   # bind target to source using the above rules
   obj = rule(compile, 'hello.o', 'hello.cpp')
   bin = rule(link, 'hello', obj)
   # force obj to be updated whenever header.h is newer.
   depend(obj, 'header.h')
   # make 'all' an alias for 'hello'
   alias('all', bin)

With the above, `faber all` will update the `hello` binary.
