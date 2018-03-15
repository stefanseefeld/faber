#
# Copyright (c) 2016 Stefan Seefeld
# All rights reserved.
#
# This file is part of Faber. It is made available under the
# Boost Software License, Version 1.0.
# (Consult LICENSE or http://www.boost.org/LICENSE_1_0.txt)

from .check import check
from ..artefact import intermediate, always
from ..tools.compiler import compiler
from ..rule import rule
from ..action import action
from ..artefacts.binary import binary
import subprocess


class try_run(check):
    """Try to compile and run a chunk of source code."""

    run = action('run', '$(>)')

    def __init__(self, name, source, type, features=(), if_=(), ifnot=()):

        check.__init__(self, name, features, if_, ifnot)
        compiler.check_instance_for_type(type, self.features)
        if not self.cached:
            # create source file
            src = type.synthesize_name(self.name)

            def generate(targets, _):
                with open(targets[0]._filename, 'w') as os:
                    os.write(source)
            src = rule(generate, src, attrs=intermediate|always,
                       logfile=self.logfile)
            bin = binary(self.name, src, features=self.features,
                         attrs=intermediate, logfile=self.logfile)
            rule(self.run, self, bin, logfile=self.logfile)


class check_output(try_run):
    """Compile and run a chunk of source code and check the generated output."""

    def post_process(self, output):
        self.result = output

    def run(self, _, source):
        """run the binary in a subprocess, then post-process the output."""
        output = subprocess.check_output([source[0].filename.result()]).decode().strip()
        self.post_process(output)
