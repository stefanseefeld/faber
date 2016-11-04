#
# Copyright (c) 2017 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from ..action import action
from ..platform import os

if os == 'Windows':

    touch = action('touch', """
@echo off
    setlocal enableextensions disabledelayedexpansion

    (for %%a in ($(<)) do if exist "%%~a" (
        pushd "%%~dpa" && ( copy /b "%%~nxa"+,, & popd )
    ) else (
        type nul > "%%~fa"
    )) >nul 2>&1""")

    copy = action('copy', 'copy /b $(>) $(<)')
    remove = action('remove', 'del $(>)')

else:
    touch = action('touch', 'touch $(<)')
    copy = action('copy', 'cp -r $(>) $(<)')
    remove = action('remove', 'rm -rf $(>)')
