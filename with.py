#!/usr/bin/python -tt
# vim: fileencoding=utf8
#{{{ License header: MIT
# Copyright (c) 2016 Till Maas <opensource@till.name>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#}}}

import glob
import os
import subprocess
import sys


def get_statcheck(attribute, value):
    def check(filename):
        return getattr(os.stat(filename), attribute) == value

    return check


if __name__ == "__main__":
    checks = []
    maxfiles = None
    sort = True

    patterns = []
    while len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if "=" in arg:
            condition, value = arg.split("=")
            if condition == "size":
                value = int(value)
                checks.append(get_statcheck("st_size", value))
            elif condition == "count":
                maxfiles = int(value)
            elif condition == "sort":
                if value == "0":
                    sort = False
                elif value == "1":
                    sort = True

        elif "--" in arg:
            break
        else:
            patterns.append(arg)

    if not patterns:
        patterns = "*"

    runfiles = []
    for pattern in patterns:
        for filename in glob.glob(pattern):
            skip = False
            for check in checks:
                if not check(filename):
                    skip = True
                    break
            if skip:
                continue
            runfiles.append(filename)

    if sort:
        runfiles = sorted(runfiles)
    if maxfiles:
        runfiles = runfiles[:maxfiles]
    if runfiles:
        cmd = sys.argv[1:] + runfiles
        # print("Running: " + repr(cmd))
        subprocess.call(cmd)
