Artefacts
=========

Rationale
---------

In previous sections we dealt with artefacts that mostly correspond directly to
files, built by specific commands. While this model appeals through its simplicity,
it is not very portable: Most actions depend heavily on the platforms they are to be
executed on. Furthermore, depending on the platform / tools, different intermediate
artefacts may need to be built.

Example
-------

Let's consider again the case of a binary using a library. But instead of
referring explicitly to the library's file name (which may differ depending on the
platform, as well as whether or not it is compiled as a shared or a static library),
we use a composite artefact to encapsulate those details.
We use a new `library` rule to define it::

  from faber.artefacts.library import *
  greet = library('greet', 'greet.cpp')

As with the `rule()` invocation encountered earlier, the `library()` call takes an
`artefact` and a `sources` argument, and returns the artefact instance.
However, the artefact's name (`greet.name`) doesn't necessarily correspond
to the filename.
The precise build instructions are fully encapsulated inside the artefact,
and will take into account both the (target) platform as well as the tool and
features selected when the build was started.

Similarly, to use the library, you can pass `greet` as source to any dependent
rule or artefact, and the build logic will determine the precise action sequence
to use it::

  from faber.artefacts.binary import *
  hello = binary('hello', ['hello.cpp', greet])

Then, to build this with `greet` as shared library (`.so` on UNIX, `.dll` on
Windows), call `faber link=shared`. To build this as a static library
(`.a` on UNIX, `.lib` on Windows), use `faber link=static`.

