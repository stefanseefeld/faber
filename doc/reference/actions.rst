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
   :abstract:

.. fab:action:: cc.compile
   :abstract:

.. fab:action:: cc.archive
   :abstract:

.. fab:action:: cc.link
   :abstract:

.. fab:action:: cxx.makedep
   :abstract:

.. fab:action:: cxx.compile
   :abstract:

.. fab:action:: cxx.archive
   :abstract:

.. fab:action:: cxx.link
   :abstract:

.. fab:action:: gcc.makedep

.. fab:action:: gcc.compile

.. fab:action:: gcc.archive

.. fab:action:: gcc.link

.. fab:action:: gxx.makedep

.. fab:action:: gxx.compile

.. fab:action:: gxx.archive

.. fab:action:: gxx.link

.. fab:action:: clang.makedep

.. fab:action:: clang.compile

.. fab:action:: clang.archive

.. fab:action:: clang.link

.. fab:action:: clangxx.makedep

.. fab:action:: clangxx.compile

.. fab:action:: clangxx.archive

.. fab:action:: clangxx.link

.. fab:action:: msvc.makedep

.. fab:action:: msvc.compile

.. fab:action:: msvc.archive

.. fab:action:: msvc.link

.. fab:action:: python.run
