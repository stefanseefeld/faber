#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import *
from faber.module import module
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt


class ArtefactTreeModel(QStandardItemModel):

    red = QColor(255, 192, 192)
    green = QColor(192, 255, 192)

    @staticmethod
    def _attrs(a):
        s = ''
        if not a.attrs & notfile:
            s += 'file | '
        if a.attrs & intermediate:
            s += 'intermediate | '
        if a.attrs & nocare:
            s += 'nocare | '
        return s[:-2] if s else ''

    def __init__(self):
        QStandardItemModel.__init__(self, 0, 2)
        self.setHeaderData(0, Qt.Horizontal, 'name')
        self.setHeaderData(1, Qt.Horizontal, 'filename')
        self._module_items = {}
        self._rows = {}
        self.filter = None

    def reset(self):
        self.setRowCount(0)
        self._rows.clear()
        self._module_items.clear()
        for a in artefact.iter():
            self.insert(a)

    def set_filter(self, filter):
        self.filter = filter
        self.reset()

    def insert(self, a):
        if not self.filter or self.filter(a):
            parent = self._module_item(a.module)
            row = self._make_row(a)
            self._rows[a] = row
            if a.status is not None:
                if a.isfile:
                    row[1].setData(a._filename, Qt.DisplayRole)
                color = self.green if a.status else self.red
                row[0].setData(QBrush(color), Qt.BackgroundRole)
            parent.appendRow(row)

    def update_all(self):
        for a in self._rows:
            self.update(a)

    def update(self, artefact):
        row = self._rows.get(artefact)
        if row:
            if artefact.status is None:  # clear
                row[0].setData(None, Qt.BackgroundRole)
                row[1].setData(None, Qt.DisplayRole)
            else:
                if artefact.isfile:
                    row[1].setData(artefact._filename, Qt.DisplayRole)
                color = self.green if artefact.status else self.red
                row[0].setData(QBrush(color), Qt.BackgroundRole)

    def _module_item(self, module):
        if module in self._module_items:
            return self._module_items[module]
        elif not module._parent:
            return self.invisibleRootItem()
        else:
            parent = self._module_item(module._parent)
            item = self._make_row(module)
            parent.appendRow(item)
            self._module_items[module] = item[0]
            return item[0]

    @staticmethod
    def _make_row(item):
        row = [QStandardItem() for i in range(2)]
        row[0].setIcon(ArtefactTreeModel._make_icon(item))
        row[0].setEditable(False)
        row[0].setData(item.name, Qt.DisplayRole)
        row[0].setData(item, Qt.UserRole)
        row[1].setEditable(False)
        if not isinstance(item, (artefact, module)):
            raise Exception('unknown type "{}"'.format(type(item)))
        return row

    @staticmethod
    def _make_icon(item):
        if isinstance(item, module):
            return QIcon(QPixmap(':/images/package.png'))
        elif isinstance(item, artefact):
            if item.isfile:
                return QIcon(QPixmap(':/images/application.png'))
            else:
                return QIcon(QPixmap(':/images/application2.png'))
        else:
            return QIcon(QPixmap(':/images/diamond.png'))
