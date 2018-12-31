#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from PyQt5 import QtCore, QtGui, QtWidgets


class Feature(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setWindowIcon(QtGui.QIcon(':images/logo_small.ico'))

    def setupUi(self):
        self.setObjectName("add_feature")
        self.setModal(True)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        self.feature = QtWidgets.QTableWidget(self)

        self.feature.setRowCount(1)
        self.feature.setColumnCount(2)
        self.feature.setObjectName("feature")
        self.feature.horizontalHeader().setStretchLastSection(True)
        self.feature.verticalHeader().setVisible(False)
        self.feature.setHorizontalHeaderLabels(['feature', 'value'])

        self.feature.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.feature.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.feature.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.feature.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.feature.resizeColumnsToContents()

        self.layout.addWidget(self.feature)
        self.buttons = QtWidgets.QDialogButtonBox(self)
        self.buttons.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttons.setFocusPolicy(QtCore.Qt.TabFocus)
        self.buttons.setOrientation(QtCore.Qt.Horizontal)
        self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttons.setObjectName("buttons")
        self.layout.addWidget(self.buttons)

        self.retranslateUi()
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("add_feature", "Add feature"))

    def get_feature(self):
        return (self.feature.item(0, 0).data(QtCore.Qt.DisplayRole),
                self.feature.item(0, 1).data(QtCore.Qt.DisplayRole))


if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication
    app = QApplication(['faber-bench'])
    view = Feature()
    view.exec_()
