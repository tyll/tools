#!/usr/bin/python -tt
# vim: fileencoding=utf8
#{{{ License header: MIT
# Copyright (c) 2014 Till Maas <opensource@till.name>
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
from contextlib import contextmanager
import signal
import ssl

import OpenSSL


class TimeoutException(Exception):
    pass


@contextmanager
def timelimit(seconds):
    def signalhandler(signum, frame):
        raise TimeoutException("timed out after {} seconds".format(seconds))

    signal.signal(signal.SIGALRM, signalhandler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def get_certnames(target, port=443, timeout=3):
    pem_cert = None
    exceptions = []
    for version in [ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_SSLv23]:
        try:
            with timelimit(timeout):
                pem_cert = ssl.get_server_certificate((target, port),
                                                      ssl_version=version)
            break
        except Exception as e:
            exceptions.append(str(e))

    if pem_cert is None:
        return "EXCEPTION: " + " ".join(exceptions)
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                           pem_cert)
    subject = cert.get_subject()
    cn = dict(subject.get_components())["CN"]

    subjectAltName = None
    for i in range(0, cert.get_extension_count()):
        e = cert.get_extension(i)
        if e.get_short_name() == "subjectAltName":
            subjectAltName = str(e).replace(",", "")
            break

    certnames = cn
    if subjectAltName is not None:
        certnames += " "
        certnames += subjectAltName
    return certnames

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=443)
    parser.add_argument("--timeout", default=3)
    parser.add_argument("target", nargs="+")
    args = parser.parse_args()
    for target in args.target:
        if ":" in target:
            target, port = target.split(":")
            port = int(port)
        else:
            port = args.port
        certnames = get_certnames(target, port, timeout=args.timeout)
        print("{} {}".format(target, certnames))
