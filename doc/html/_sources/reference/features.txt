Builtin features
================

The following features are provided by Faber and its built-in tools.

.. fab:feature:: cppflags
   :attributes: multi, incidental
   :module: faber.tools.compiler
	    
   Generic preprocessing flags.

.. fab:feature:: cflags
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Generic C compiler flags.

.. fab:feature:: cxxflags
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Generic C++ compiler flags.

.. fab:feature:: ldflags
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Generic linker flags.

.. fab:feature:: define
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Macro definitions.

.. fab:feature:: linkpath
   :attributes: multi, path, incidental
   :module: faber.tools.compiler

   Library search paths.

.. fab:feature:: include
   :attributes: multi, path, incidental
   :module: faber.tools.compiler

   Header search paths.

.. fab:feature:: libs
   :attributes: multi, incidental
   :module: faber.tools.compiler

   Libraries to be linked to.

.. fab:feature:: link
   :module: faber.tools.compiler
   :values: 'static', 'shared'

   Link type for libraries.

.. fab:feature:: target.os
   :module: faber.tools.compiler

   The target OS of the compiler.

.. fab:feature:: target.arch
   :module: faber.tools.compiler

   The target architecture of the compiler.

.. fab:feature:: runpath
   :attributes: multi, path, incidental
   :module: faber.tools.compiler

   The library search path used during application execution.

.. fab:feature:: pythonpath
   :attributes: multi, path, incidental
   :module: faber.tools.python

   The Python module search path used during application execution.

