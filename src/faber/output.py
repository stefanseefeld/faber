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
    except:
        # fall back to undecorated text
        coloured = lambda text, colour=None, on_colour=None, attrs=None: text
else:
    coloured = termcolor.colored

# these values are (for now) bound to the equivalent logging levels
# in the engine, even though the implementation is entirely separate.
summary = 0x01
actions = 0x02
commands = 0x04

level = actions

def _format_count(msg, number):
    if number:
        print(msg.format(number, 's' if number > 1 else ''))

def log_plan(artefacts, temp, updating, cantfind, cantmake):
    if level & summary:
        _format_count('...found {} artefact{}...', artefacts)
        _format_count('...using {} temp artefact{}...', temp)
        _format_count('...updating {} artefact{}...', updating)
        _format_count('...can\'t find {} artefact{}...', cantfind)
        _format_count('...can\'t make {} artefact{}...', cantmake)

def log_summary(failed, skipped, made):
    if level & summary:
        _format_count('...failed updating {} artefact{}...', failed)
        _format_count('...skipped {} artefact{}...', skipped)
        _format_count('...made {} artefact{}...', made)

def log_recipe(name, artefact, status, command, stdout, stderr):
    if level & actions:
        if level > actions:  # if there is more, highlight the actions
            print(coloured('{} {}'.format(name, artefact), attrs=['bold']))
        else:
            print('{} {}'.format(name, artefact))
    if level & commands:
        print(command)
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)

def log_test_status(name, outcome):
    from .test import pass_, fail, xpass, xfail
    if level & actions:
        colour = {pass_: 'green',
                  fail: 'red',
                  xpass: 'yellow',
                  xfail: 'green'}[outcome]
        label =  {pass_: 'PASS',
                  fail: 'FAIL',
                  xpass: 'XPASS',
                  xfail: 'XFAIL'}[outcome]
        print('{}: {}'.format(name, coloured(label, colour)))

def log_test_summary(passes, failures, xfailures, untested):
    if level & summary:
        p = passes and '{} pass'.format(passes) or ''
        if passes > 1: p += 'es'
        f = failures and '{} failure'.format(failures) or ''
        if failures > 1: f += 's'
        x = xfailures and '{} expected failure'.format(xfailures) or ''
        if xfailures > 1: x += 's'
        u = untested and '{} untested' or ''
        line = ', '.join([o for o in [p, f, x, u] if o])
        if level > actions:  # if there is more, highlight the summary
            print(coloured('test summary: ' + line, attrs=['bold']))
        else:
            print('test summary: ' + line)

if __name__ == '__main__':

    print(coloured('this is red', 'red'))
    print(coloured('this is green', 'green'))
    print(coloured('this is bold', attrs=['bold']))
