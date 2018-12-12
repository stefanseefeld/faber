#
# Copyright (c) 2018 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .artefact import flag
import os
import graphviz


def walk(a, d=None):
    """Traverse the prerequisites of `a`."""

    # This of course assumes the graph not to have any cycles.
    yield a, d
    for p in a.prerequisites:
        yield from walk(p, a)


def visualize(*args, filename='dependencies', format=None):
    """Visualize the dependency graph for artefacts in `args`."""

    g = graphviz.Digraph(graph_attr={'rankdir': 'TB'})

    nodes = set()
    edges = set()
    for arg in args:
        for t, s in walk(arg):
            if t not in nodes:
                fillcolor='bisque1:bisque3' if t.flags & flag.NOTFILE else 'darkolivegreen1:darkolivegreen3'
                g.node(str(t), label=t.name, shape='rectangle', style='filled', fillcolor=fillcolor)
                nodes.add(t)
            # Avoid circular references
            if s and s != t and (s, t) not in edges:
                g.edge(str(s), str(t))
                edges.add((s, t))

    fmts = ['.png', '.pdf', '.dot', '.svg', '.jpeg', '.jpg']
    if format is None and any(filename.lower().endswith(fmt) for fmt in fmts):
        filename, format = os.path.splitext(filename)
        format = format[1:].lower()

    if format is None:
        format = 'png'

    data = g.pipe(format=format)
    if not data:
        raise RuntimeError('Graphviz failed to properly produce an image.')

    full_filename = '.'.join([filename, format])
    with open(full_filename, 'wb') as f:
        f.write(data)
    print('output written to {}'.format(full_filename))
