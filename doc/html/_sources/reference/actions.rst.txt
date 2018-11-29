Builtin actions
===============

The following actions are provided by Faber and its built-in tools.

.. fab:action:: touch
   :module: faber.tools.fileutils

   Touch a file, i.e. either create it if it doesn't exist,
   or update its modification time.

.. fab:action:: copy
   :module: faber.tools.fileutils

   Copy a file.

.. fab:action:: remove
   :module: faber.tools.fileutils

   Remove a file.

.. fab:action:: cc.makedep
   :module: faber.tools.cc
   :abstract:

.. fab:action:: cc.compile
   :module: faber.tools.cc
   :abstract:

.. fab:action:: cc.archive
   :module: faber.tools.cc
   :abstract:

.. fab:action:: cc.link
   :module: faber.tools.cc
   :abstract:

.. fab:action:: cxx.makedep
   :module: faber.tools.cxx
   :abstract:

.. fab:action:: cxx.compile
   :module: faber.tools.cxx
   :abstract:

.. fab:action:: cxx.archive
   :module: faber.tools.cxx
   :abstract:

.. fab:action:: cxx.link
   :module: faber.tools.cxx
   :abstract:

.. fab:action:: gcc.makedep
   :module: faber.tools.gcc

.. fab:action:: gcc.compile
   :module: faber.tools.gcc

.. fab:action:: gcc.archive
   :module: faber.tools.gcc

.. fab:action:: gcc.link
   :module: faber.tools.gcc

.. fab:action:: gxx.makedep
   :module: faber.tools.gxx

.. fab:action:: gxx.compile
   :module: faber.tools.gxx

.. fab:action:: gxx.archive
   :module: faber.tools.gxx

.. fab:action:: gxx.link
   :module: faber.tools.gxx

.. fab:action:: clang.makedep
   :module: faber.tools.clang

.. fab:action:: clang.compile
   :module: faber.tools.clang

.. fab:action:: clang.archive
   :module: faber.tools.clang

.. fab:action:: clang.link
   :module: faber.tools.clang

.. fab:action:: clangxx.makedep
   :module: faber.tools.clangxx

.. fab:action:: clangxx.compile
   :module: faber.tools.clangxx

.. fab:action:: clangxx.archive
   :module: faber.tools.clangxx

.. fab:action:: clangxx.link
   :module: faber.tools.clangxx

.. fab:action:: msvc.makedep
   :module: faber.tools.msvc

.. fab:action:: msvc.compile
   :module: faber.tools.msvc

.. fab:action:: msvc.archive
   :module: faber.tools.msvc

.. fab:action:: msvc.link
   :module: faber.tools.msvc

.. fab:action:: python.run
   :module: faber.tools.python
