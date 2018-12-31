#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .init_ui import Ui_init
from . import feature
from faber.project import buildinfo as infobase
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog


class buildinfo(infobase):
    def __init__(self, builddir, srcdir=None):
        super().__init__(builddir, srcdir)
        # if this is a new info, populate configuration
        if not self._config.has_section('bench'):
            self._config.add_section('bench')


class Init(QDialog):
    """Initialize the configuration of a build directory.

    The creation of the info object will already have taken care of some basic
    validation (srcdir and builddir are valid, if provided).

    A few remaining use-cases are worth calling out:

    1) srcdir is given, builddir not

       Any new builddir pick needs to refer either to a new (empty or nonexistent)
       directory, or one that is compatible with the srcdir.

    2) builddir is given, srcdir not

       If builddir exists and is valid, its info contains a reference to the srcdir,
       otherwise it must be an empty or non-existent directory

    3) neither srcdir nor builddir are given

       Whenever srcdir changes, validate the builddir
       - if builddir is not valid, ask to change it (or reset it ?)

       Whenever builddir changes, validate the srcdir
       - if srcdir is not valid, as to change it
       - re-generate the options and parameters listing
    """

    def __init__(self, info):
        super().__init__()
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.info = info
        self.ui = Ui_init()
        self.ui.setupUi(self)
        self.ui.srcdir_value.setCurrentText(self.info.srcdir)
        self.ui.browse_srcdir.clicked.connect(self.select_srcdir)
        self.ui.builddir_value.setCurrentText(self.info.builddir)
        self.ui.browse_builddir.clicked.connect(self.select_builddir)
        self.ui.srcdir_value.currentTextChanged.connect(self.set_srcdir)
        self.ui.builddir_value.currentTextChanged.connect(self.set_builddir)
        self.ui.parameters.itemSelectionChanged.connect(self.enable_remove_parameter_button)
        self.ui.add_parameter.clicked.connect(self.add_parameter)
        self.ui.remove_parameter.setEnabled(False)
        self.ui.remove_parameter.clicked.connect(self.remove_parameter)
        self.ui.parameters.set(dict(self.info.parameters.items()))
        self.ui.enable_parameters.stateChanged.connect(self.enable_parameters)
        if len(self.info.parameters.items()):
            self.ui.enable_parameters.setChecked(True)
        self.ui.options.itemSelectionChanged.connect(self.enable_remove_option_button)
        self.ui.add_option.clicked.connect(self.add_option)
        self.ui.remove_option.setEnabled(False)
        self.ui.remove_option.clicked.connect(self.remove_option)
        self.ui.options.set(dict(self.info.options.items()))
        self.ui.enable_options.stateChanged.connect(self.enable_options)
        if len(self.info.options.items()):
            self.ui.enable_options.setChecked(True)
        self.ui.run.setEnabled(bool(self.info.srcdir and self.info.builddir))
        self.ui.cancel.clicked.connect(self.cancel)
        self.ui.run.clicked.connect(self.run)
        if self.info.srcdir:
            self.ui.builddir_value.setFocus()
        else:
            self.ui.srcdir_value.setFocus()

    def enable_parameters(self, enabled):
        if enabled:
            self.ui.parameters.show()
            self.ui.add_parameter.show()
            self.ui.remove_parameter.show()
        else:
            self.ui.parameters.hide()
            self.ui.add_parameter.hide()
            self.ui.remove_parameter.hide()

    def enable_options(self, enabled):
        if enabled:
            self.ui.options.show()
            self.ui.add_option.show()
            self.ui.remove_option.show()
        else:
            self.ui.options.hide()
            self.ui.add_option.hide()
            self.ui.remove_option.hide()

    def enable_remove_parameter_button(self):
        enabled = self.ui.parameters.get_selection() is not None
        self.ui.remove_parameter.setEnabled(enabled)

    def enable_remove_option_button(self):
        enabled = self.ui.options.get_selection() is not None
        self.ui.remove_option.setEnabled(enabled)

    def add_parameter(self):
        f = feature.Feature()
        if f.exec_():
            self.ui.parameters.append(*f.get_feature())

    def remove_parameter(self):
        row = self.ui.parameters.get_selection()
        self.ui.parameters.remove(row)

    def add_option(self):
        f = feature.Feature()
        if f.exec_():
            self.ui.options.append(*f.get_feature())

    def remove_option(self):
        row = self.ui.options.get_selection()
        self.ui.options.remove(row)

    def cancel(self):
        self.done(0)

    def run(self):
        self.info.parameters = self.ui.parameters.data()
        self.info.options = self.ui.options.data()
        self.done(1)

    def select_srcdir(self):
        """Start a dialog to select a srcdir."""
        options = QFileDialog.Options(QFileDialog.ShowDirsOnly)
        options |= QFileDialog.ExistingFile
        srcdir = QFileDialog.getExistingDirectory(None,
                                                  'Select source directory',
                                                  self.info.srcdir,
                                                  options=options)
        self.ui.srcdir_value.setCurrentText(srcdir)
        if not self.info.builddir:
            # as a convenience, initialize the builddir to be the same
            self.ui.builddir_value.setCurrentText(srcdir)

    def set_srcdir(self, srcdir):
        self.info = buildinfo(self.info.builddir, srcdir)
        self.ui.run.setEnabled(bool(self.info.srcdir and self.info.builddir))

    def select_builddir(self):
        """Start a dialog to select a builddir."""
        options = QFileDialog.Options(QFileDialog.ShowDirsOnly)
        builddir = QFileDialog.getExistingDirectory(None,
                                                    'Select build directory',
                                                    self.info.builddir,
                                                    options=options)
        self.ui.builddir_value.setCurrentText(builddir)

    def set_builddir(self, builddir):
        self.info = buildinfo(builddir, self.info.srcdir)
        # once we know the build directory we can try to
        # recover srcdir as well as build configurations,
        # then we are ready to go.
        if self.info.srcdir:
            self.ui.srcdir_value.setCurrentText(self.info.srcdir)
        self.ui.parameters.set(self.info.parameters)
        if len(self.info.parameters.items()):
            self.ui.enable_parameters.setChecked(True)
        self.ui.options.set(self.info.options)
        if len(self.info.options.items()):
            self.ui.enable_options.setChecked(True)
        self.ui.run.setEnabled(bool(self.info.srcdir and self.info.builddir))

    def parameters(self):
        return {f[0]: f[1] for f in self.ui.parameters.data()}

    def options(self):
        return {f[0]: f[1] for f in self.ui.options.data()}
