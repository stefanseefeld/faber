Builtin features
================

The following features are provided by Faber and its built-in tools.

.. fab:feature:: cppflags
   :attributes: multi, incidental
   :module: faber.tools.compiler
	    
   Generic preprocessing flags. They are passed through to the compiler, unmodified.

.. fab:feature:: cflags
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Generic C compiler flags. They are passed through to the compiler, unmodified.

.. fab:feature:: cxxflags
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Generic C++ compiler flags. They are passed through to the compiler, unmodified.

.. fab:feature:: cxxstd
   :attributes: incidental
   :values: 98, 03, 11, 14, 17
   :module: faber.tools.cxx

   C++ standard version to be used.

.. fab:feature:: ldflags
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Generic linker flags. They are passed through to the compiler / linker, unmodified.

.. fab:feature:: define
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Macro definitions. They are passed through to the compiler / preprocessor, unmodified.

.. fab:feature:: linkpath
   :attributes: multi, path, incidental
   :module: faber.tools.compiler

   Library search paths. They are passed through to the compiler / linker, unmodified.

.. fab:feature:: include
   :attributes: multi, path, incidental
   :module: faber.tools.compiler

   Header search paths. They are passed through to the compiler / preprocessor, unmodified.

.. fab:feature:: libs
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Libraries to be linked to. They are passed through to the compiler / linker, unmodified.

.. fab:feature:: link
   :module: faber.tools.compiler
   :values: 'static', 'shared'

   Link type for libraries.

.. fab:feature:: target.os
   :module: faber.tools.compiler

   The target OS of the compiler. Examples: Linux, Windows, Darwin.

.. fab:feature:: target.arch
   :module: faber.tools.compiler

   The target architecture of the compiler. Examples: x86_64, x86, arm, aarm64.

.. fab:feature:: runpath
   :attributes: multi, path, incidental
   :module: faber.tools.compiler

   The library search path used during application execution.

.. fab:feature:: pythonpath
   :attributes: multi, path, incidental
   :module: faber.tools.python

   The Python module search path used during application execution.

