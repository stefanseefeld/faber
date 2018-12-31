#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .module_ui import Ui_editor
from PyQt5.QtWidgets import QDialog


def inspect_module(m):
    win = QDialog()
    win.setWindowTitle('Module viewer : {}'.format(m.srcdir))
    win.ui = Ui_editor()
    win.ui.setupUi(win)
    win.ui.edit.load(m)
    win.exec_()
