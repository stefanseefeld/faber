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

   Inject header dependencies for the given target by parsing the source.

.. fab:action:: cc.compile
   :module: faber.tools.cc
   :abstract:

   Compile a C file into an object file.

.. fab:action:: cc.archive
   :module: faber.tools.cc
   :abstract:

   Generate an archive (static library) from the given object file(s).

.. fab:action:: cc.link
   :module: faber.tools.cc
   :abstract:

   Link the given object file(s) into shared library.

.. fab:action:: cxx.makedep
   :module: faber.tools.cxx
   :abstract:

   Inject header dependencies for the given target by parsing the source.
      
.. fab:action:: cxx.compile
   :module: faber.tools.cxx
   :abstract:

   Compile a C++ file into an object file.

.. fab:action:: cxx.archive
   :module: faber.tools.cxx
   :abstract:

   Generate an archive (static library) from the given object file(s).

.. fab:action:: cxx.link
   :module: faber.tools.cxx
   :abstract:

   Link the given object file(s) into shared library.

.. fab:action:: gcc.makedep
   :module: faber.tools.gcc

   Inject header dependencies for the given target by parsing the source.
	    
.. fab:action:: gcc.compile
   :module: faber.tools.gcc

   Compile a C file into an object file.

.. fab:action:: gcc.archive
   :module: faber.tools.gcc

   Generate an archive (static library) from the given object file(s).

.. fab:action:: gcc.link
   :module: faber.tools.gcc

   Link the given object file(s) into shared library.

.. fab:action:: gxx.makedep
   :module: faber.tools.gxx

   Inject header dependencies for the given target by parsing the source.
	    
.. fab:action:: gxx.compile
   :module: faber.tools.gxx

   Compile a C++ file into an object file.

.. fab:action:: gxx.archive
   :module: faber.tools.gxx

   Generate an archive (static library) from the given object file(s).

.. fab:action:: gxx.link
   :module: faber.tools.gxx

   Link the given object file(s) into shared library.

.. fab:action:: clang.makedep
   :module: faber.tools.clang

   Inject header dependencies for the given target by parsing the source.
	    
.. fab:action:: clang.compile
   :module: faber.tools.clang

   Compile a C file into an object file.

.. fab:action:: clang.archive
   :module: faber.tools.clang

   Generate an archive (static library) from the given object file(s).

.. fab:action:: clang.link
   :module: faber.tools.clang

   Link the given object file(s) into shared library.

.. fab:action:: clangxx.makedep
   :module: faber.tools.clangxx

   Inject header dependencies for the given target by parsing the source.
	    
.. fab:action:: clangxx.compile
   :module: faber.tools.clangxx

   Compile a C++ file into an object file.

.. fab:action:: clangxx.archive
   :module: faber.tools.clangxx

   Generate an archive (static library) from the given object file(s).

.. fab:action:: clangxx.link
   :module: faber.tools.clangxx

   Link the given object file(s) into shared library.

.. fab:action:: msvc.makedep
   :module: faber.tools.msvc

   Inject header dependencies for the given target by parsing the source.
	    
.. fab:action:: msvc.compile
   :module: faber.tools.msvc

   Compile a C or C++ file into an object file.

.. fab:action:: msvc.archive
   :module: faber.tools.msvc

   Generate an archive (static library) from the given object file(s).

.. fab:action:: msvc.link
   :module: faber.tools.msvc

   Link the given object file(s) into shared library.

.. fab:action:: python.run
   :module: faber.tools.python

   Run the given Python script.

