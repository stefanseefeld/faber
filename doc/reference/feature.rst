feature
=======

.. contents :: Table of Contents

A feature is a typed variable that can be used to parametrize the build process.

synopsis
--------

.. autoclass:: faber.feature.feature
   :members: __init__, lookup, __call__

.. autoclass:: faber.feature.value
   :members: __init__, __iadd__, __ior__, __eq__

.. autoclass:: faber.feature.set
   :members: __init__

Examples
--------

::
   
  from faber.feature import *
   
  include = feature('include', multi)
  link = feature('link', values=('shared', 'static'))

  i1 = include('search', 'path')
  l1 = link('shared')

  fs = set(i1, l1)
  assert fs.include == ('search', 'path')
