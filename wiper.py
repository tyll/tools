#!/usr/bin/python3 -tt
# vim: fileencoding=utf8
# {{{ License header: MIT
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
# }}}

import argparse
import os
import sys
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    args = parser.parse_args()

    fd = os.open(args.target, os.O_WRONLY)
    # POSIX_FADV_NOREUSE is a no-op
    # os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_NOREUSE)
    os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
    filesize = os.lseek(fd, 0, os.SEEK_END)
    os.lseek(fd, 0, os.SEEK_SET)

    bufsize = 512 * 4 * 1024
    buf = bytearray([0] * bufsize)
    allwritten = 0
    remainingdata = filesize
    filesize_mib = int(filesize / 2**20)

    start = time.time()
    laststatus = start
    buffered = 0
    try:
        while remainingdata != 0:
            remainingdata = filesize - allwritten
            if remainingdata < bufsize:
                bufsize = remainingdata
                buf = bytearray([0] * bufsize)
            written = os.write(fd, buf)
            allwritten += written
            buffered += written
            now = time.time()
            if now - laststatus > 1:
                allwritten_mib = int(allwritten / 2**20)
                elapsed = now - start
                writespeed = allwritten / elapsed
                progress = int(allwritten / filesize * 100)
                remainingtime = int(remainingdata / writespeed)
                sys.stderr.write("\r\x1b[KSpeed: {} KiB/s, progress: {}%, "
                                 "remaining: {}s, elapsed: {}s, "
                                 "written: {}/{} MiB".format(
                                    int(writespeed / 1024), progress,
                                    remainingtime, int(elapsed),
                                    allwritten_mib, filesize_mib)
                                 )
                laststatus = now

            if buffered > 30 * 2 ** 20:
                os.fdatasync(fd)
                buffered = 0
            if written != bufsize:
                sys.stderr.write(
                    "\nAborted, only wrote {} bytes, total written: {}".format(
                        written, allwritten))
                break
    except KeyboardInterrupt:
        sys.stderr.write(
            "\nAborted, only wrote {} bytes, total written: {}".format(
                written, allwritten))
    elapsed = now - start
    writespeed = allwritten / elapsed
    remainingdata = filesize - allwritten
    sys.stderr.write("\n{} bytes remaining. writespeed: {} KiB/s\n".format(
        remainingdata, int(writespeed / 1024)))
