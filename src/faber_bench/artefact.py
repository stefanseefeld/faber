#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .artefact_ui import Ui_artefact
from PyQt5.QtWidgets import QDialog


def inspect_artefact(a):
    win = QDialog()
    win.setWindowTitle('Artefact viewer')
    win.ui = Ui_artefact()
    win.ui.setupUi(win)
    win.ui.name.setText(a.name)
    win.ui.type.setText(a.__class__.__name__)
    for k, v in a.features._serialize().items():
        # FIXME: why is the feature value sometimes a list, sometimes a string ?
        win.ui.features.append(k, v if type(v) is str else ','.join(v))
    win.exec_()
