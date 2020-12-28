#
# Copyright (c) 2020 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import source, artefact


def make_source(name, content):
    """Create and return a source artefact with the specified content."""
    src = source(name)
    with open(src._filename, 'w') as out:
        out.write(content)
    return src


def check_makedep(compiler, src, num_deps):
    """Generic makedep test. Call with a specific compiler instance."""

    dependencies = artefact('dependencies.d')
    targets, sources = [dependencies], [src]
    compiler.makedep(targets, sources)
    with open(dependencies._filename, 'r') as d:
        assert sum(1 for line in d if line) == num_deps


def check_compile(compiler, src):
    """Generic compile test. Call with a specific compiler instance."""

    obj = artefact('out.o')
    targets, sources = [obj], [src]
    compiler.compile(targets, sources)
