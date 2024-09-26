#
# Copyright (c) 2021 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop
import asyncio


def submit(task):
    asyncio.ensure_future(task)


def wait_for(task):
    task()


def exit():
    asyncio.get_event_loop().stop()


class Application:

    def __init__(self, argv):
        self.app = QApplication(argv)
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)

    def exec_(self):
        with self.loop:
            print('running loop...')
            self.loop.run_forever()
