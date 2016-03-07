#!/usr/bin/python2 -tt
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

# generic hash checking tool

from binascii import hexlify, unhexlify
import hashlib
import sys


BUFFERSIZE = 2 ** 21  # 2 MiB


def get_lengthmap():
    lengthmap = {}
    for algorithm in hashlib.algorithms:
        hashlength = hashlib.new(algorithm).digest_size
        lengthmap.setdefault(hashlength, []).append(algorithm)
    return lengthmap


lengthmap = get_lengthmap()


def checkfile(checksum, filename):
    """
    ascii checksum

    filename: Filename with binary indicator
    leading asterisks means binary, leading space means text
    """

    try:
        binary_checksum = unhexlify(checksum)
    except TypeError:
        return False

    hashers = {}
    for algorithm in lengthmap.get(len(binary_checksum), []):
        hasher = hashlib.new(algorithm)
        hashers[hasher] = algorithm

    if filename[0] == "*":
        mode = "rb"
    else:
        mode = "r"
    filename = filename[1:]  # remove binary indicator

    try:
        with open(filename, mode) as ifile:
            while True:
                data = ifile.read(BUFFERSIZE)
                if not data:
                    break
                for hasher in hashers:
                    hasher.update(data)
    except IOError:
        return False
    result = []
    for hasher, algorithm in hashers.items():
        calculated = hasher.digest()
        if calculated == binary_checksum:
            check = "GOOD"
            extra = ""
        else:
            check = "BAD"
            extra = " {} != {}".format(hexlify(calculated),
                                       hexlify(binary_checksum))
        result.append("{} {}: {}{}".format(check, algorithm, filename,
                                           extra)
                      )
    return result


if __name__ == "__main__":
    bad_lines = 0
    with open(sys.argv[1], "r") as ifile:
        for line in ifile:
            if "  " or " *" in line:
                line = line.rstrip("\n")
                checksum, filename = line.split(" ", 1)
                result = checkfile(checksum, filename)
                if result:
                    print("\n".join(result))
                    continue
            bad_lines += 1
    if bad_lines > 1:
        print("{} lines ignored".format(bad_lines))
