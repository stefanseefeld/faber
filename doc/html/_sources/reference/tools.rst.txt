Builtin tools
=============

The following tools are provided by Faber.

.. fab:tool:: cc
   :module: faber.tools.cc
   :actions: makedep, compile, archive, link
	    
   Generic C compiler base class.

.. fab:tool:: cxx
   :module: faber.tools.cxx
   :actions: makedep, compile, archive, link

   Generic C++ compiler base class.

.. fab:tool:: gcc
   :module: faber.tools.gcc
   :bases: cc
   :actions: makedep, compile, archive, link

   GCC C compiler.

.. fab:tool:: gxx
   :module: faber.tools.gxx
   :bases: cxx
   :actions: makedep, compile, archive, link

   GCC C++ compiler.

.. fab:tool:: clang
   :module: faber.tools.clang
   :bases: cc
   :actions: makedep, compile, archive, link

   CLang C compiler.

.. fab:tool:: clangxx
   :module: faber.tools.clangxx
   :bases: cxx
   :actions: makedep, compile, archive, link

   CLang C++ compiler.

.. fab:tool:: msvc
   :module: faber.tools.msvc
   :bases: cc, cxx
   :actions: makedep, compile, archive, link

   MSVC C & C++ compiler.

.. fab:tool:: python
   :module: faber.tools.python
   :actions: run

   A (C)Python interpreter.
