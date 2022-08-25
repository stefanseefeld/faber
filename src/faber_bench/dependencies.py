#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .artefact import inspect_artefact
from faber.scheduler.graph import walk, collect
from PyQt5.QtCore import Qt, QRectF, QLineF
from PyQt5.QtGui import QColor, QBrush, QPen, QPainter, QIcon, QLinearGradient
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
from collections import namedtuple
import math
import pydot


Rect = namedtuple('Rect', ['x', 'y', 'w', 'h'])


class Node(QGraphicsRectItem):
    """A Node represents an artefact in a dependency graph. While it may have more than one prerequisite,
    for layout purposes only one is considered the parent."""
    def __init__(self, artefact, parent):
        self.rect = None
        super().__init__()
        self.artefact = artefact
        self._parents = []
        self.name = self.artefact.name
        self.label = self.artefact.name
        gradient = QLinearGradient(0, 0, 1, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        if self.artefact.frontend.isfile:
            self.setPen(QPen(QColor('#496592')))
            gradient.setColorAt(0, QColor('#496592'))
            gradient.setColorAt(1, QColor('#abb7cd'))
        else:
            self.setPen(QPen(QColor('#e5941d')))
            gradient.setColorAt(0, QColor('#e5941d'))
            gradient.setColorAt(1, QColor('#f7cf94'))
        self.setBrush(QBrush(gradient))
        self.text = QGraphicsTextItem(self.label, self)
        self.setToolTip(f'{self.label}')

        self._children = []
        self._edges = {}
        self._hide_parents = False
        self._collapsed = False
        if parent:
            parent.add_child(self)

    def setRect(self, rect):
        self.rect = rect
        self.setPos(0, 0)
        super().setRect(*self.rect)
        self.text.setPos(self.rect.x, self.rect.y)

    def add_child(self, node):
        self._children.append(node)
        node._parents.append(self)
        edge = QGraphicsLineItem()
        self.scene().addItem(edge)
        edge.setZValue(-1000)
        self._edges[node.name] = edge

    def hide_parents(self, keep=None):
        for p in self._parents:
            # hide parents recursively...
            p.hide_parents(keep)
            p.hide()
            # ...as well as siblings
            p.collapse(keep)
            for e in p._edges.values():
                e.hide()
        self._hide_parents = True

    def show_parents(self, keep=None):
        for p in self._parents:
            # show parents recursively...
            p.show_parents(keep)
            p.show()
            # ...as well as siblings
            p.expand(keep)
            for e in p._edges.values():
                e.show()
        self._hide_parents = False

    def collapse(self, keep=None):
        for c in self._children:
            if c is not keep:
                c.collapse(keep)
                c.hide()
                for p in c._parents:
                    p._edges[c.name].hide()
        for e in self._edges.values():
            e.hide()
        self._collapsed = True

    def expand(self, keep=None):
        for c in self._children:
            if c is not keep:
                c.show()
                c.expand(keep)
        for e in self._edges.values():
            e.show()
        self._collapsed = False

    def mousePressEvent(self, event):
        if (event.button() == Qt.RightButton):
            menu = self.scene().main.make_context_menu(self.artefact.frontend)
            menu.exec_(event.screenPos())
        self._moved = False

    def mouseMoveEvent(self, event):
        diff = event.pos() - event.lastPos()
        self._move_subgraph(diff.x(), diff.y())
        self._moved = True

    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.LeftButton and not self._moved):
            if qApp.keyboardModifiers() == Qt.ShiftModifier:
                self.expand_parents(self) if self._hide_parents else self.hide_parents(self)
            else:
                self.expand() if self._collapsed else self.collapse()
        self._moved = False

    def adjust_edges(self):
        nodes, edges = self._collect_subgraph()
        for e in edges:
            e.setPos(0, 0)
        # iterate over all graph-internal edges
        for n in nodes:
            start = n.rect.x + n.rect.w / 2, n.rect.y + n.rect.h / 2
            for c in n._children:
                end = c.rect.x + c.rect.w / 2, c.rect.y + c.rect.h / 2
                line = QLineF(start[0], start[1], end[0], end[1])
                n._edges[c.name].setLine(line)
        # iterate over all outward edges
        for n in nodes:
            end = n.rect.x + n.rect.w / 2, n.rect.y + n.rect.h / 2
            for p in n._parents:
                if p not in nodes:
                    start = p.rect.x + p.rect.w / 2, p.rect.y + p.rect.h / 2
                    line = QLineF(start[0], start[1], end[0], end[1])
                    p._edges[n.name].setLine(line)

    def _move_subgraph(self, x, y):
        nodes, edges = self._collect_subgraph()
        # move all child nodes...
        for n in nodes:
            n.moveBy(x, y)
        # ...as well as child edges...
        for e in edges:
            e.moveBy(x, y)
        # ... then adjust upward edges
        for n in nodes:
            for p in n._parents:
                if p not in nodes:
                    e = p._edges[n.name]
                    line = QLineF(e.line().x1(), e.line().y1(), e.line().x2() + x, e.line().y2() + y)
                    e.setLine(line)

    def _collect_subgraph(self):
        nodes = set((self,))
        nodes |= set(self._children)
        edges = set(self._edges[e] for e in self._edges)
        for child in self._children:
            sn, se = child._collect_subgraph()
            nodes |= sn
            edges |= se
        return nodes, edges


class Scene(QGraphicsScene):

    def __init__(self, main, a):
        super().__init__()
        self.main = main
        self.nodes = {}
        for n, p in walk(a):
            if n not in self.nodes:
                node = Node(n, self.nodes[p] if p else None)
                self.nodes[n] = node
                self.addItem(node)
            else:
                self.nodes[p].add_child(self.nodes[n])
        self.root = self.nodes[a]
        self.layout()

    def layout(self):
        positions = self._layout(self.root)
        for n in positions:
            n.setRect(positions[n])
        self.root.adjust_edges()
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.mouseGrabberItem() is None:
            if (event.button() == Qt.RightButton):
                menu = QMenu()
                menu.addAction(self.tr('layout'), lambda: self.layout())
                menu.exec_(event.screenPos())
        
    @staticmethod
    def _walk(node, parent=None, visited=None):
        visited = set() if visited is None else visited
        yield node, parent
        for c in node._children:
            if c not in visited:
                visited.add(c)
                yield from Scene._walk(c, node, visited)
            else:
                yield c, node

    def _layout(self, node):

        hash = lambda a: repr(id(a))
        nodes, edges = [], []
        for n, p in Scene._walk(node):
            if n.isVisible():
                if n not in nodes:
                    nodes.append(n)
                if p:
                    edges.append((p, n))

        g = pydot.Dot('', graph_type='digraph', strict=True)

        for n in nodes:
            g.add_node(pydot.Node(hash(n), label=f'"{n.name}"', shape='box'))
        for e in edges:
            g.add_edge(pydot.Edge(hash(e[0]), hash(e[1])))

        dot = str(g.create_dot(prog='dot'), encoding='utf-8')
        if not dot:
            raise RuntimeError('error running "dot"')
        graph = pydot.graph_from_dot_data(dot)[0]

        layout = {}
        for n, _ in Scene._walk(node):
            if not n.isVisible():
                continue
            gn = graph.get_node(hash(n))[0]
            x, y = gn.get_pos()[1:-1].split(',')
            # convert from inches to points (72 dpi)
            w, h = float(gn.get_width()) * 72, float(gn.get_height()) * 72
            x, y = float(x) - w / 2, h / 2 - float(y)
            layout[n] = Rect(x, y, w, h)
        return layout


class Dependencies(QMainWindow):

    def __init__(self, main, artefact):
        super().__init__()
        self.main = main
        self.target_process = None
        self.scene = Scene(self.main, artefact)
        self.view = QGraphicsView(self.scene)
        self.view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.view)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.setWindowTitle('Faber dependency viewer')
        self.show()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Plus:
            self.scale(1.2)
        elif key == Qt.Key_Minus:
            self.scale(1 / 1.2)

    def wheelEvent(self, event):
        if qApp.keyboardModifiers() == Qt.ShiftModifier:
            self.scale(math.pow(2.0, -event.angleDelta().y() / 240.0))
        else:
            super().wheelEvent(event)

    def scale(self, s):
        factor = self.view.transform().scale(s, s).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.view.scale(s, s)
