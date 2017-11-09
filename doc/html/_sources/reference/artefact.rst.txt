artefact
========

.. contents :: Table of Contents

An artefact represents the outcome of an action. In fabscripts they are typically
created by invoking a `rule`. Higher-level artefacts (typically those that are built
using `implicit rules`, such as `library` or `binary` instances), can be instantiated
explicitly.


synopsis
--------

.. autoclass:: faber.artefact.artefact
   :members: __init__, qname, id, filename, boundname, __call__



Examples
--------

::

   # define some actions
