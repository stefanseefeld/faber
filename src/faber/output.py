#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from . import termcolor
import sys

if sys.platform == 'win32':
    try:
        from colorama import init
        init()
        coloured = termcolor.colored
    except Exception:
        # fall back to undecorated text
        coloured = lambda text, colour=None, on_colour=None, attrs=None: text
else:
    coloured = termcolor.colored

if __name__ == '__main__':

    print(coloured('this is red', 'red'))
    print(coloured('this is green', 'green'))
    print(coloured('this is bold', attrs=['bold']))
