#! /usr/bin/python -tt
# vim: fileencoding=utf8
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
import os

import sys


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def sharfile(filepath, ofile):
    quotedfile = shellquote(filepath)
    with open(filepath, "r", encoding="latin1") as ifile:
        filedata = ifile.read()
    ofile.write("cat > {} <<EOF\n".format(quotedfile))
    ofile.write(filedata)
    ofile.write("EOF\n")


if __name__ == "__main__":
    # Shell Archive tool
    ofile = sys.stdout
    if len(sys.argv) > 1:
        startdir = sys.argv[1]
    else:
        startdir = "."

    if os.path.isfile(startdir):
        sharfile(startdir, ofile)
    else:
        for root, dirs, files in os.walk(startdir):
            for d in dirs:
                quoteddir = shellquote(os.path.join(root, d))
                ofile.write("mkdir {}\n".format(quoteddir))

            for f in files:
                filepath = os.path.join(root, f)
                sharfile(filepath, ofile)
