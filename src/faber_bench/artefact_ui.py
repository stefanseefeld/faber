# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/faber_bench/artefact.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_artefact(object):
    def setupUi(self, artefact):
        artefact.setObjectName("artefact")
        artefact.resize(489, 374)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo_small.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        artefact.setWindowIcon(icon)
        self.formLayout = QtWidgets.QFormLayout(artefact)
        self.formLayout.setObjectName("formLayout")
        self.name = QtWidgets.QLineEdit(artefact)
        self.name.setReadOnly(True)
        self.name.setObjectName("name")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.name)
        self.nameLabel = QtWidgets.QLabel(artefact)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.typeLabel = QtWidgets.QLabel(artefact)
        self.typeLabel.setObjectName("typeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.typeLabel)
        self.type = QtWidgets.QLineEdit(artefact)
        self.type.setObjectName("type")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.type)
        self.attributesLabel = QtWidgets.QLabel(artefact)
        self.attributesLabel.setObjectName("attributesLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.attributesLabel)
        self.attributes = QtWidgets.QLineEdit(artefact)
        self.attributes.setObjectName("attributes")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.attributes)
        self.featuresLabel = QtWidgets.QLabel(artefact)
        self.featuresLabel.setObjectName("featuresLabel")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.featuresLabel)
        self.features = DictTable(artefact)
        self.features.setColumnCount(2)
        self.features.setObjectName("features")
        self.features.setRowCount(0)
        self.features.horizontalHeader().setDefaultSectionSize(200)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.features)
        self.buttonBox = QtWidgets.QDialogButtonBox(artefact)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(artefact)
        self.buttonBox.accepted.connect(artefact.accept)
        self.buttonBox.rejected.connect(artefact.reject)
        QtCore.QMetaObject.connectSlotsByName(artefact)

    def retranslateUi(self, artefact):
        _translate = QtCore.QCoreApplication.translate
        artefact.setWindowTitle(_translate("artefact", "Artefact"))
        self.nameLabel.setText(_translate("artefact", "Name"))
        self.typeLabel.setText(_translate("artefact", "Type"))
        self.attributesLabel.setText(_translate("artefact", "Attributes"))
        self.featuresLabel.setText(_translate("artefact", "Features"))

from .widgets import DictTable
from . import resource_rc
