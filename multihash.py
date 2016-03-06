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

import argparse
import hashlib

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--algos", default="md5,sha1,sha256,sha512")
    parser.add_argument("filename", nargs="*")
    args = parser.parse_args()

    algos = args.algos.split(",")
    hashers = {}

    for filename in args.filename:
        for h in algos:
            hashers[h] = getattr(hashlib, h)()

        with open(filename, "rb") as ifile:
            while True:
                buf = ifile.read(2 * 2 ** 10)
                if buf:
                    for algo, hasher in hashers.items():
                        hasher.update(buf)
                else:
                    break

        for algo in algos:
            hasher = hashers[algo]
            print "{} ({}) = {}".format(
                algo.upper(), filename, hasher.hexdigest())
