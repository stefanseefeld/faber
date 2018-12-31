# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/faber_bench/module.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_editor(object):
    def setupUi(self, editor):
        editor.setObjectName("editor")
        editor.resize(546, 424)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo_small.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        editor.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(editor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.edit = ModuleEdit(editor)
        self.edit.setReadOnly(True)
        self.edit.setObjectName("edit")
        self.verticalLayout.addWidget(self.edit)

        self.retranslateUi(editor)
        QtCore.QMetaObject.connectSlotsByName(editor)

    def retranslateUi(self, editor):
        pass

from .widgets import ModuleEdit
from . import resource_rc
