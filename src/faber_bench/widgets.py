#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from os.path import join


class CheckableComboBox(QtWidgets.QComboBox):

    stateChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        super().addItem(QIcon(':images/log.svg'), 'log')

    def addItem(self, item, checked=False):
        super().addItem(item)
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
        self.stateChanged.emit(self.count() - 1)

    def itemChecked(self, index):
        item = self.model().item(index, 0)
        return item and item.checkState() == QtCore.Qt.Checked

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
        self.stateChanged.emit(index.row())


class ProgressBar(QtWidgets.QProgressBar):

    def __init__(self, *args):
        super().__init__(*args)
        self.max = 0
        self.value = 0

    def start(self, max):
        self.max = max
        self.value = 0
        self.setMaximum(self.max)
        self.setValue(self.value)

    def increment_max(self):
        self.max += 1
        self.setMaximum(self.max)

    def increment(self):
        self.value += 1
        self.setValue(self.value)


class DictTable(QtWidgets.QTableWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setColumnCount(2)
        self.setRowCount(0)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(['feature', 'value'])

    def set(self, data):
        self.clearContents()
        for k, v in data.items():
            self.append(k, v)

    def get_selection(self):
        # we always select single entire rows, so only return the first
        s = self.selectedIndexes()
        return s[0].row() if s else None

    def append(self, key, value):
        row = self.rowCount()
        self.insertRow(self.rowCount())
        self.setItem(row, 0, QtWidgets.QTableWidgetItem(key))
        self.setItem(row, 1, QtWidgets.QTableWidgetItem(value))

    def remove(self, row):
        self.removeRow(row)

    def data(self):
        return {self.item(r, 0).data(QtCore.Qt.DisplayRole): self.item(r, 1).data(QtCore.Qt.DisplayRole)
                for r in range(self.rowCount())}


class ModuleEdit(QtWidgets.QTextEdit):

    def load(self, module):
        try:
            from pygments import highlight as _highlight
            from pygments.lexers import PythonLexer
            from pygments.formatters import HtmlFormatter

            def highlight(text):
                return _highlight(text, PythonLexer(), HtmlFormatter(full=True))
        except ImportError:
            def highlight(text):
                return text

        script = join(module.srcdir, 'fabscript')
        with open(script, 'r+') as code:
            html = highlight(code.read())
            self.setHtml(html)
