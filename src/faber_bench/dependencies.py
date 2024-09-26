#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .artefact import inspect_artefact
from faber.scheduler.graph import walk
from PyQt5.QtCore import Qt, QRectF, QLineF
from PyQt5.QtGui import QColor, QBrush, QPen, QPainter, QIcon, QLinearGradient
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
from collections import namedtuple
import math
import pydot


Rect = namedtuple('Rect', ['x', 'y', 'w', 'h'])


class Node(QGraphicsRectItem):

    def __init__(self, artefact, parent, rect):
        self.rect = rect
        super().__init__(*self.rect)
        self.artefact = artefact
        self.parent = parent
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
        text = QGraphicsTextItem(self.label, self)
        text.setPos(self.rect.x, self.rect.y)
        self.setToolTip(f'{self.label}')

        self._children = []
        self._edges = {}
        self._collapsed_parents = False
        self._collapsed = False
        if parent:
            parent.add_child(self)

    def add_child(self, node):
        self._children.append(node)
        start = self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2
        end = node.rect.x + node.rect.w / 2, node.rect.y + node.rect.h / 2
        edge = QGraphicsLineItem(start[0], start[1], end[0], end[1])
        self.scene().addItem(edge)
        edge.setZValue(-1000)
        self._edges[node.name] = edge

    def collapse_parents(self, keep=None):
        if self.parent:
            # collapse parents recursively...
            self.parent.collapse_parents(keep)
            self.parent.hide()
            # ...as well as siblings
            self.parent.collapse(keep)
            for e in self.parent._edges.values():
                e.hide()
        self._collapsed_parents = True

    def expand_parents(self, keep=None):
        if self.parent:
            # expand parents recursively...
            self.parent.expand_parents(keep)
            self.parent.show()
            # ...as well as siblings
            self.parent.expand(keep)
            for e in self.parent._edges.values():
                e.show()
        self._collapsed_parents = False

    def collapse(self, keep=None):
        for c in self._children:
            if c is not keep:
                c.collapse(keep)
                c.hide()
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

    def moveBy(self, x, y, child=True):
        super().moveBy(x, y)
        for c in self._children:
            c.moveBy(x, y)
        for e in self._edges:
            self._edges[e].moveBy(x, y)
        if self.parent and not child:
            e = self.parent._edges[self.name]
            line = QLineF(e.line().x1(), e.line().y1(), e.line().x2() + x, e.line().y2() + y)
            e.setLine(line)

    def mousePressEvent(self, event):
        if (event.button() == Qt.RightButton):
            menu = self.scene().main.make_context_menu(self.artefact.frontend)
            menu.exec_(event.screenPos())
        self._moved = False

    def mouseMoveEvent(self, event):
        diff = event.pos() - event.lastPos()
        self.moveBy(diff.x(), diff.y(), child=False)
        self._moved = True

    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.LeftButton and not self._moved):
            if qApp.keyboardModifiers() == Qt.ShiftModifier:
                self.expand_parents(self) if self._collapsed_parents else self.collapse_parents(self)
            else:
                self.expand() if self._collapsed else self.collapse()
        self._moved = False


class Scene(QGraphicsScene):

    def __init__(self, main, a):
        super().__init__()
        self.main = main
        layout = self._layout(a)
        self.nodes = {}
        for n, p in walk(a):
            node = Node(n, self.nodes[p] if p else None, layout[n])
            self.nodes[n] = node
            self.addItem(node)

    def _layout(self, artefact):

        nodes, edges = [], []
        for n, p in walk(artefact):
            nodes.append(n)
            if p:
                edges.append((p, n))

        g = pydot.Dot('', graph_type='digraph', strict=True)

        for n in nodes:
            g.add_node(pydot.Node(str(n), label=n.name, shape='box'))
        for e in edges:
            g.add_edge(pydot.Edge(str(e[0]), str(e[1])))

        dot = str(g.create_dot(prog='dot'), encoding='utf-8')
        if not dot:
            raise RuntimeError('error running "dot"')
        graph = pydot.graph_from_dot_data(dot)[0]

        layout = {}
        for n, _ in walk(artefact):
            node = graph.get_node(str(n))[0]
            x, y = node.get_pos()[1:-1].split(',')
            # convert from inches to points (72 dpi)
            w, h = float(node.get_width()) * 72, float(node.get_height()) * 72
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
