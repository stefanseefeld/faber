# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/faber_bench/settings.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.setWindowModality(QtCore.Qt.ApplicationModal)
        Settings.resize(192, 124)
        self.formLayout_2 = QtWidgets.QFormLayout(Settings)
        self.formLayout_2.setObjectName("formLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.parallelismLabel = QtWidgets.QLabel(Settings)
        self.parallelismLabel.setObjectName("parallelismLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.parallelismLabel)
        self.parallelism = QtWidgets.QSpinBox(Settings)
        self.parallelism.setDisplayIntegerBase(10)
        self.parallelism.setObjectName("parallelism")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.parallelism)
        self.timeoutLabel = QtWidgets.QLabel(Settings)
        self.timeoutLabel.setObjectName("timeoutLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.timeoutLabel)
        self.timeout = QtWidgets.QSpinBox(Settings)
        self.timeout.setToolTip("")
        self.timeout.setObjectName("timeout")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.timeout)
        self.saveIntermediatesLabel = QtWidgets.QLabel(Settings)
        self.saveIntermediatesLabel.setObjectName("saveIntermediatesLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.saveIntermediatesLabel)
        self.intermediates = QtWidgets.QCheckBox(Settings)
        self.intermediates.setObjectName("intermediates")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.intermediates)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.buttonBox)

        self.retranslateUi(Settings)
        self.buttonBox.accepted.connect(Settings.accept)
        self.buttonBox.rejected.connect(Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Scheduler settings"))
        self.parallelismLabel.setText(_translate("Settings", "parallelism"))
        self.timeoutLabel.setText(_translate("Settings", "timeout"))
        self.saveIntermediatesLabel.setText(_translate("Settings", "save intermediates"))

