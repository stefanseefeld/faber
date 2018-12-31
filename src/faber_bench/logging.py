#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from __future__ import absolute_import
import faber
from faber.logging import setup
from PyQt5 import QtCore, QtGui
import logging
import re


class Handler(logging.Handler, QtCore.QObject):

    message = QtCore.pyqtSignal(str)

    colors = {30: 'grey',
              31: 'red',
              32: 'green',
              33: 'yellow',
              34: 'blue',
              35: 'magenta',
              36: 'cyan',
              37: 'white'}
    backgrounds = {40: 'on_grey',
                   41: 'on_red',
                   42: 'on_green',
                   43: 'on_yellow',
                   44: 'on_blue',
                   45: 'on_magenta',
                   46: 'on_cyan',
                   47: 'on_white'}
    effects = {1: 'bold',
               2: 'dark',
               3: '',
               4: 'underline',
               5: 'blink',
               6: '',
               7: 'reverse',
               8: 'concealed'}

    def __init__(self, widget):
        setup(log=[], debug=faber.debug)  # we set up loggers explicitly later
        # no idea why `super().__init__()` wouldn't work here...
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self)
        logging.getLogger().handlers=[]
        logging.getLogger().addHandler(self)
        self.widget = widget
        self.default_format = self.widget.currentCharFormat()
        self.current_format = QtGui.QTextCharFormat(self.default_format)
        self.message.connect(self.log)

    def close(self):
        # unregister self to no longer receive logs
        logging.getLogger().handlers=[]

    def emit(self, record):
        # this may be called from other threads, so route it to the
        # main thread (running the Qt event loop)
        self.message.emit(self.format(record))

    def log(self, msg):
        # split by escape sequences, then adjust style accordingly
        for chunk in re.split(r'(\033\[\d+m)', msg):
            if chunk:
                if chunk.startswith('\033['):
                    self.set_style(int(chunk[2:-1]))
                else:
                    self.widget.setCurrentCharFormat(self.current_format)
                    self.widget.append(chunk)
            else:
                self.widget.setCurrentCharFormat(self.current_format)

    def set_style(self, esc):
        if esc in Handler.colors:
            self.current_format.setForeground(QtGui.QColor(Handler.colors[esc]))
        elif esc in Handler.backgrounds:
            self.current_format.setBackground(QtGui.QColor(Handler.backgrounds[esc]))
        elif esc in Handler.effects:
            if esc == 1:
                self.current_format.setFontWeight(600)
        elif esc == 0:
            # reset
            self.current_format = QtGui.QTextCharFormat(self.default_format)
