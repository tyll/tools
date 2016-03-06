#!/usr/bin/python3 -ttu
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
from binascii import hexlify
import hashlib
import os
import sys


INITIAL_BLOCKSIZE = 4096
READ_BLOCKSIZE = 2 ** 21

IGNORE_DIRS = (".git", ".svn", ".hg")


class File(object):
    def __init__(self, path, filedb):
        self.filedb = filedb
        self.path = path
        self._size = None
        self._starthash = None
        self._filehash = None
        self.hashconstructor = hashlib.md5
        self.filedb.filenames[path] = self
        self.getsize()

    @property
    def size(self):
        return self.getsize()

    def getsize(self):
        if self._size is None:
            self._size = os.stat(self.path).st_size
            self.filedb.sizes.setdefault(self._size, []).append(self)
        return self._size

    @property
    def starthash(self):
        if not self._starthash:
            with open(self.path, "rb") as ifile:
                self._starthash = self.hashconstructor(
                    ifile.read(INITIAL_BLOCKSIZE)).digest()
                self.filedb.starthashes.setdefault(
                    self._starthash, []).append(self)
                if self.size <= INITIAL_BLOCKSIZE:
                    self._filehash = self._starthash
                    self.filedb.filehashes.setdefault(
                        self._filehash, []).append(self)
        return self._starthash

    @property
    def filehash(self):
        if not self._filehash:
            with open(self.path, "rb") as ifile:
                hasher = self.hashconstructor()
                while True:
                    data = ifile.read(READ_BLOCKSIZE)
                    if data:
                        hasher.update(data)
                    else:
                        break
                self._filehash = hasher.digest()
                self.filedb.filehashes.setdefault(
                    self._filehash, []).append(self)
        return self._filehash


class FileDB(object):
    def __init__(self):
        self.sizes = {}
        self.starthashes = {}
        self.filehashes = {}
        self.filenames = {}

    def add(self, filename):
        File(filename, self)


def get_files(path, suffix=""):
    for root, dirs, files in os.walk(path):
        for f in sorted(files):
            fullpath = os.path.join(root, f)
            if os.path.isfile(fullpath):
                if fullpath.endswith(suffix):
                    yield fullpath
        for ignore in IGNORE_DIRS:
            if ignore in dirs:
                dirs.remove(ignore)
            dirs.sort()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("directories", nargs="*", default=["."])
    parser.add_argument("--suffix", default="")
    parser.add_argument("--rm", default=False, action="store_true")
    parser.add_argument("-v", "--verbose", default=False, action="store_true")
    args = parser.parse_args()

    filedb = FileDB()
    for dir_ in args.directories:
        dir_ = os.path.expanduser(dir_)
        for filename in get_files(dir_, args.suffix):
            filedb.add(filename)

    for size, files in filedb.sizes.items():
        # FIXME: Ignore empty files for now
        # might be __init__.py files
        if size == 0:
            continue
        if len(files) > 1:
            checked = []
            for index, file_ in enumerate(files):
                if file_ in checked:
                    continue
                dupes = []
                if args.verbose:
                    print("Checking ", file_.path, file=sys.stderr)
                for otherfile in files[index + 1:]:
                    if otherfile.starthash == file_.starthash:
                        if otherfile.filehash == file_.filehash:
                            dupes.append(otherfile)
                            checked.append(otherfile)
                if dupes:
                    dupes.insert(0, file_)
                    print("#", dupes[0].path)
                    for f in dupes[1:]:
                        print("rm {}".format(f.path))
                        if args.rm:
                            os.remove(f.path)
                    print("")
