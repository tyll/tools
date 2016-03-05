#!/usr/bin/python -tt
# vim: fileencoding=utf8
# {{{ License header: MIT
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
# }}}

import argparse
from collections import OrderedDict
try:
    import simplejson as json
except ImportError:
    import json

import sys
import urllib


class POSTData(object):
    def __init__(self, postdata, encoding="latin1"):
        params = OrderedDict()
        for parampair in postdata.split("&"):
            name, value = parampair.split("=")
            name = urllib.unquote_plus(name).decode(encoding)
            value = urllib.unquote_plus(value).decode(encoding)
            if name in params:
                if isinstance(params[name], list):
                    params[name].append(value)
                else:
                    params[name] = [params[name], value]

            else:
                params[name] = value

        self.params = params

    def javascript(self):
        javascript = "var postdata = {};\n"
        json_var = json.dumps(self.params, indent=4)
        return javascript.format(json_var)

    def latex(self):
        latex = ""
        for name, values in self.params.items():
            name = "\\verb^{}^".format(name.encode("utf-8"))
            if not isinstance(values, list):
                values = [values]

            for value in values:
                if value:
                    value = "\\verb^{}^".format(value.encode("utf-8"))

                latex += "{} & {} \\\\\n".format(name, value)

        return latex


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--utf8", action="store_const", const="utf8",
                        dest="encoding", default="latin1",
                        help="Use UTF-8 encoding")
    parser.add_argument("postdata")
    args = parser.parse_args()

    with open(args.postdata) as ifile:
        raw_postdata = ifile.read()

    if raw_postdata[-1] == "\n":
        raw_postdata = raw_postdata[:-1]

    postdata = POSTData(raw_postdata, args.encoding)
    sys.stdout.write(postdata.javascript())
    sys.stdout.write(postdata.latex())
