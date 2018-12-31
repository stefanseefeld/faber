#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from faber.artefact import artefact
from faber.logging import getLogger, logging
# reach into the gory details of the asyncio scheduler
from faber.scheduler import asyncio
from faber.scheduler.artefact import artefact as A

from .main_ui import Ui_main
from .artefact import inspect_artefact
from .module import inspect_module
from .logging import Handler
from .models import ArtefactTreeModel
from .widgets import CheckableComboBox
from .settings import Settings
from . import application
from PyQt5.QtWidgets import QMenu, QMainWindow, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class Main(QMainWindow):

    default_loggers = ['summary', 'actions', 'output']

    class adapter:
        """Receive updates from the scheduler and forward them to the Main instance."""
        def __init__(self, main):
            self.main = main

        def add_prerequisite(self, _, p):
            a = p.frontend
            if a not in self.main.current_artefacts:
                self.main.current_artefacts.add(a)
                self.main.ui.tree.model().insert(a)
                self.main.ui.progress.increment_max()

        def status(self, a):
            self.main.update_status(a.frontend)

    def __init__(self, module, config):

        super().__init__()
        self.config = config
        A.callback = Main.adapter(self)
        self.setWindowIcon(QIcon(':images/logo_small.ico'))
        self.root = module
        self.ui = Ui_main()
        self.ui.setupUi(self)
        # Qt designer can't do this, so we are doing it here:
        self.ui.logo.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.sourcedir_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.builddir_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.sourcedir.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.builddir.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ui.sourcedir.setText(self.root.srcdir)
        self.ui.builddir.setText(self.root.builddir)
        # Qt designer still can't insert arbitrary widgets into a toolbar,
        # so we have to do it here. (*sigh*)
        self.ui.view = QComboBox(self.ui.toolbar)
        self.ui.view.setObjectName('view')
        self.ui.view.addItem(QIcon(':images/view.svg'), self.tr('view public'))
        self.ui.view.addItem(QIcon(':images/view.svg'), self.tr('view all'))
        self.ui.toolbar.addWidget(self.ui.view)
        self.ui.log = CheckableComboBox(self.ui.toolbar)
        self.ui.log.setObjectName('log')
        self.ui.toolbar.addWidget(self.ui.log)
        self.ui.clean = QPushButton(QIcon(':images/cleanup.svg'), 'clean', self.ui.toolbar)
        clean = QMenu()
        clean.addAction(self.tr('clean'), lambda: self.clean(0))
        clean.addAction(self.tr('clean all'), lambda: self.clean(1))
        self.ui.clean.setMenu(clean)
        self.ui.toolbar.addWidget(self.ui.clean)
        self.ui.stop = QPushButton(QIcon(':images/stop.svg'), None, self.ui.toolbar)
        self.ui.stop.setEnabled(False)
        self.ui.stop.clicked.connect(self.stop)
        self.ui.toolbar.addWidget(self.ui.stop)

        self.setWindowTitle('Faber Bench: ' + self.root.srcdir)
        self.ui.quit.triggered.connect(self.terminate)
        self.ui.settings.triggered.connect(self.settings)

        model = ArtefactTreeModel()
        self.ui.tree.setModel(model)
        self.ui.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tree.customContextMenuRequested.connect(self.tree_menu)
        self.view_artefacts()  # run default filter
        self.ui.view.activated.connect(self.view_artefacts)
        self.log_handler = Handler(self.ui.output)
        self.ui.log.stateChanged.connect(self.set_logging)
        self.ui.log.model().item(0, 0).setFlags(Qt.NoItemFlags)
        self.loggers = ['actions', 'commands', 'summary', 'output']
        for l in self.loggers:
            self.ui.log.addItem(l, checked=l in Main.default_loggers)
        self.ui.view_public_artefacts.triggered.connect(lambda: self.view_artefacts(0))
        self.ui.view_all_artefacts.triggered.connect(lambda: self.view_artefacts(1))
        self.ui.about.triggered.connect(self.about)
        self.dependencies = None
        self.current_artefacts = None
        self.module_edit = None

    def terminate(self):
        self.log_handler.close()
        application.exit()

    def settings(self):
        view = Settings(self.config)
        view.exec_()

    def view_artefacts(self, index=None):
        from faber.artefact import intermediate, nopropagate, internal, source, conditional
        from faber.artefacts.include_scan import scan

        def is_internal(a):
            return not (a.attrs & internal or
                        a.attrs & intermediate or
                        a.attrs & nopropagate or
                        isinstance(a, conditional) or
                        isinstance(a, scan) or
                        isinstance(a, source))

        all = index == 1
        self.ui.tree.model().set_filter(None if all else is_internal)

    def about(self):
        from . import version
        win = QMessageBox()
        win.setWindowTitle('About Faber Bench')
        win.setTextFormat(Qt.RichText)
        win.setText('<p><b>Faber Bench version {}</b></p>'
                    '<p>Copyright (c) 2021 Stefan Seefeld</p>'.format(version))
        win.exec_()

    def set_logging(self, index):
        level = logging.INFO if self.ui.log.itemChecked(index) else logging.ERROR
        getLogger(self.loggers[index - 1]).setLevel(level=level)

    def clean(self, index):
        from faber import scheduler
        from faber import config

        def _reset():
            level = index + 1
            if level > 1:
                config.reset(level)  # remove config cache then...
            # ...reset artefacts
            scheduler.reset()
            scheduler.clean(level)
        self.wait_for(_reset)
        self.ui.tree.model().update_all()

    def show_dependencies(self, artefact):
        from .dependencies import Dependencies

        a = asyncio.artefacts[artefact]  # fetch backend
        self.view = Dependencies(self, a)
        self.view.show()

    def make_context_menu(self, object, deps=False):
        menu = QMenu()

        async def update(a):
            self.ui.stop.setEnabled(True)
            self.current_artefacts = {a.frontend for a in asyncio.collect(a)}
            self.ui.progress.start(len(self.current_artefacts))
            await asyncio.async_update(a)
            asyncio.reset()
            self.ui.stop.setEnabled(False)

        if isinstance(object, artefact):
            menu.addAction(self.tr('inspect'), lambda: inspect_artefact(object))
            if deps:
                menu.addAction(self.tr('dependencies'), lambda: self.show_dependencies(object))
            menu.addAction(self.tr('update'), lambda: self.submit(update(object)))
        else:
            menu.addAction(self.tr('inspect'), lambda: inspect_module(object))
        return menu

    def tree_menu(self, position):

        selected = self.ui.tree.selectedIndexes()
        if not selected:
            return
        index = selected[0]
        menu = self.make_context_menu(index.data(Qt.UserRole), deps=True)
        menu.exec_(self.ui.tree.viewport().mapToGlobal(position))

    def stop(self):
        pass

    def update_status(self, a):
        self.ui.tree.model().update(a)
        self.ui.progress.increment()
        p = self.ui.progress
        self.ui.statusbar.showMessage(f'{p.value}/{p.max} artefacts updated')

    def submit(self, task):
        application.submit(task)

    def wait_for(self, task):
        application.wait_for(task)
