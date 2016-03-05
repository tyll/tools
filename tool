#!/usr/bin/python3 -tt
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
import stat
import os
import os.path

import yaml


DEFAULT_YAML = """
bindir: ~/bin
tooldirs: {}
"""


class Config(object):
    def __init__(self, filepath):
        self.filepath = os.path.expanduser(filepath)
        try:
            with open(self.filepath, "r") as ifile:
                self.config = yaml.safe_load(ifile)
        except FileNotFoundError:
            self.config = yaml.safe_load(DEFAULT_YAML)
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            self.save()

    def save(self):
        with open(self.filepath, "w") as ofile:
            ofile.write(yaml.safe_dump(self.config, indent=4,
                                       default_flow_style=False))

    def __getitem__(self, key):
        return self.config.__getitem__(key)

    def __missing__(self, key):
        return self.config.__missing__(key)

    def __setitem__(self, key, value):
        return self.config.__setitem__(key, value)

    def __delitem__(self, key):
        return self.config.__delitem__(key)

    def __iter__(self):
        return self.config.__iter__()

    def __reversed__(self):
        return self.config.__reversed__()

    def __contains__(self, item):
        return self.config.__contains__(item)


def get_tools(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            fullpath = os.path.join(root, f)
            filestat = os.stat(fullpath)
            if "x" in stat.filemode(filestat.st_mode):
                yield fullpath, filestat
        for ignore in (".git", ".svn", ".hg"):
            if ignore in dirs:
                dirs.remove(ignore)


class Tooler(object):
    def main(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        parser_add = subparsers.add_parser("add", help="Add tooldirs")
        parser_add.set_defaults(cmd="add")
        parser_add.add_argument("tooldir", nargs="*",
                                help="tooldirs to add, default: %(default)s",
                                default=["."])
        parser_check = subparsers.add_parser("check",
                                             help="Check for bad links")
        parser_check.set_defaults(cmd="check")
        args = parser.parse_args()

        config = Config("~/.config/tooler/tooler.yml")
        self.config = config
        self.bindir = os.path.expanduser(config["bindir"])
        self.homedir = os.path.expanduser("~")

        if args.cmd == "add":
            self.add(args.tooldir)
        elif args.cmd == "check":
            self.check(None)

    def add(self, dirs):

        for dir_ in dirs:
            tooldir = os.path.relpath(dir_, self.homedir)
            if not tooldir in self.config:
                self.config["tooldirs"][tooldir] = {}
                self.config.save()
            for tool, toolstat in get_tools(dir_):
                toolname = os.path.basename(tool)
                binpath = os.path.join(self.bindir, toolname)
                relpath = os.path.relpath(tool, self.bindir)
                linkinfo = "{} -> {}".format(binpath, relpath)
                if not os.path.isfile(binpath):
                    os.symlink(relpath, binpath)
                    print("Added " + linkinfo)
                else:
                    filestat = os.stat(binpath)
                    if os.path.samestat(filestat, toolstat):
                        print("Already linked: " + linkinfo)
                    else:
                        print("Conflict: " + linkinfo)

    def check(self, dirs):
        if dirs is None:
            dirs = list(self.config["tooldirs"])
        dirs = [os.path.relpath(os.path.join(self.homedir, dir_),
                                self.bindir) for
                dir_ in dirs]

        def isknown(target):
            for dir_ in dirs:
                dir_ += os.sep
                if target.startswith(dir_):
                    return True
            return False

        for entry in os.listdir(self.bindir):
            entry = os.path.join(self.bindir, entry)
            if os.path.islink(entry):
                linktarget = os.readlink(entry)
                if not os.path.isfile(os.path.join(self.bindir, linktarget)):
                    linkinfo = "{} -> {}".format(entry, linktarget)
                    if isknown(linktarget):
                        print("rm ", entry, "# ", linkinfo)
                    else:
                        print(linkinfo)
                else:
                    if isknown(linktarget):
                        print("GOOD", entry)
                    else:
                        print("UNKNOWN link", entry)
            else:
                print("UNKNOWN", entry)


if __name__ == "__main__":
    tooler = Tooler()
    tooler.main()
