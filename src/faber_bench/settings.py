#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.scheduler import recipe
from .settings_ui import Ui_settings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog


class Settings(QDialog):

    def __init__(self, config):

        super().__init__()
        self.config = config
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.ui = Ui_settings()
        self.ui.setupUi(self)
        self.ui.parallelism.setValue(int(self.config.get('parallelism', 1)))

    def accept(self):
        print('accepting setting changes')
        self.config['parallelism'] = str(self.ui.parallelism.value())
        super().accept()

    def update(self):
        recipe.recipe.init(int(self.config['parallelism']))
