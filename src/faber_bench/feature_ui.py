# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/faber_bench/feature.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_add_feature(object):
    def setupUi(self, add_feature):
        add_feature.setObjectName("add_feature")
        add_feature.resize(314, 127)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(add_feature.sizePolicy().hasHeightForWidth())
        add_feature.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo_small.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        add_feature.setWindowIcon(icon)
        add_feature.setModal(True)
        self.layoutWidget = QtWidgets.QWidget(add_feature)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 311, 126))
        self.layoutWidget.setObjectName("layoutWidget")
        self.layout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        self.feature = QtWidgets.QTableWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.feature.sizePolicy().hasHeightForWidth())
        self.feature.setSizePolicy(sizePolicy)
        self.feature.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.feature.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.feature.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.feature.setShowGrid(True)
        self.feature.setRowCount(1)
        self.feature.setColumnCount(2)
        self.feature.setObjectName("feature")
        self.feature.horizontalHeader().setStretchLastSection(True)
        self.feature.verticalHeader().setVisible(False)
        self.layout.addWidget(self.feature)
        self.buttons = QtWidgets.QDialogButtonBox(self.layoutWidget)
        self.buttons.setFocusPolicy(QtCore.Qt.TabFocus)
        self.buttons.setOrientation(QtCore.Qt.Horizontal)
        self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttons.setObjectName("buttons")
        self.layout.addWidget(self.buttons)

        self.retranslateUi(add_feature)
        self.buttons.accepted.connect(add_feature.accept)
        self.buttons.rejected.connect(add_feature.reject)
        QtCore.QMetaObject.connectSlotsByName(add_feature)

    def retranslateUi(self, add_feature):
        _translate = QtCore.QCoreApplication.translate
        add_feature.setWindowTitle(_translate("add_feature", "Add feature"))

from . import resource_rc
