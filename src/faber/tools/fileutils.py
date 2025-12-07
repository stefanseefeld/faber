#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import Action
from ..platform import os

if os == 'Windows':

    touch = Action('touch', """
@echo off
    setlocal enableextensions disabledelayedexpansion

    (for %%a in ($(<)) do if exist "%%~a" (
        pushd "%%~dpa" && ( copy /b "%%~nxa"+,, & popd )
    ) else (
        type nul > "%%~fa"
    )) >nul 2>&1""")

    copy = Action('copy', 'copy /b $(>) $(<)')
    remove = Action('remove', 'del $(>)')

else:
    touch = Action('touch', 'touch $(<)')
    copy = Action('copy', 'cp -r $(>) $(<)')
    remove = Action('remove', 'rm -rf $(>)')
