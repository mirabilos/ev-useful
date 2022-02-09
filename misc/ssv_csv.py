#!/usr/bin/env python3
# coding: utf-8
#-
# Copyright © 2015, 2017, 2020, 2022
#   Thorsten Glaser <t.glaser@tarent.de>
#
# Provided that these terms and disclaimer and all copyright notices
# are retained or reproduced in an accompanying document, permission
# is granted to deal in this work without restriction, including un‐
# limited rights to use, publicly perform, distribute, sell, modify,
# merge, give away, or sublicence.
#
# This work is provided “AS IS” and WITHOUT WARRANTY of any kind, to
# the utmost extent permitted by applicable law, neither express nor
# implied; without malicious intent or gross negligence. In no event
# may a licensor, author or contributor be held liable for indirect,
# direct, other damage, loss, or other issues arising in any way out
# of dealing in the work, even if advised of the possibility of such
# damage or existence of a defect, except proven that it results out
# of said person’s immediate fault when using the work as intended.

""" SSV reader/writer and CSV writer library """

__all__ = [
    "CSVInvalidCharacterError",
    "CSVShapeError",
    "CSVWriter",
    "SSVReader",
    "SSVWriter",
]

import re

class CSVShapeError(Exception):
    """ Data to write did not have a consistent amount of columns """
    def __init__(self, want, got):
        Exception.__init__(self, 'got %d field%s but wanted %d' % \
          (got, got != 1 and 's' or '', want))
        self.want = want
        self.got = got

class CSVInvalidCharacterError(Exception):
    """ Disallowed characters in field or row """
    pass

class CSVWriter(object):
    """ CSV writer library, configurable

    Separators, fields, etc. must be str; bytes is not supported.
    """

    # never allow embedded NUL
    invfind = re.compile('[\x00]')
    # to normalise embedded newlines
    nlfind = re.compile('(?:\r\n?|(?<!\r)\n)')
    # to ensure rectangular shape of output
    ncols = -1

    # default line ending is ASCII (“DOS”)
    def __init__(self, sep=',', quot='"', eol='\r\n', qnl='\r\n'):
        """ Configure a new CSV writer instance

        The defaults are suitable for use with most environments;
        changing just the separator to ';' is probably the one
        thing needed for almost every other environment.

         sep - output field separator: ',' or ';' or '\\t'
         quot - output field quote, will be doubled to escape
         eol - output line terminator: '\\r\\n' or (Unix) '\\n'
         qnl - embedded newlines are normalised to this, None disables
        """

        if quot is None:
            self.quots = ''
            self.quotd = ''
            # forbid newlines if we cannot quote them
            self.invfind = re.compile('[\x00\r\n]')
        else:
            self.quots = quot
            self.quotd = quot + quot
        self.quot = quot
        self.sep = self.quots + sep + self.quots
        self.nlrepl = qnl
        self.eol = eol

    def _mapfield(self, field):
        if not isinstance(field, str):
            field = str(field)
        if self.invfind.search(field) is not None:
            raise CSVInvalidCharacterError(field)
        if self.nlrepl is not None:
            field = self.nlfind.sub(self.nlrepl, field)
        if self.quot is not None:
            field = field.replace(self.quots, self.quotd)
        return field

    def write(self, *args):
        """ Print a CSV line (row) to standard output

         *args - list of fields
        """

        print(self.format(*args), end='')

    def format(self, *args):
        """ Produce a CSV row from fields

        The result contains the trailing newline needed.

         *args - list of fields

        Returns the CSV row as a string
        """

        if self.ncols == -1:
            self.ncols = len(args)
        elif self.ncols != len(args):
            raise CSVShapeError(self.ncols, len(args))
        return self.quots + self.sep.join(map(self._mapfield, args)) + \
          self.quots + self.eol

class SSVWriter(CSVWriter):
    """ SSV writer library

    shell-parseable separated values (or separator-separated values)
    is an idea to make CSV into something usable:

    • newline (\\x0A) is row separator
    • unit separator (\\x1F) is column separator
    • n̲o̲ quotes or escape characters
    • carriage return (\\x0D) represents embedded newlines in cells

    Cell content is, in theory, arbitrary binary except NUL and
    the separators (\\x1F and \\x0A). In practice it should be UTF-8.
    This library supports str on the Python3 side only, not bytes.

    SSV can be easily read from shell scripts:

        while IFS=$'\\x1F' read -r field1 field2…; do
            # do something
        done
    """

    def __init__(self):
        """ Initialise a new CSV writer instance to SSV """

        CSVWriter.__init__(self, '\x1F', None, '\n', '\r')
        # not permitted in SSV fields
        self.invfind = re.compile('[\x00\x1F]')

class SSVReader(object):
    """ SSV reader library

    See SSVWriter about the SSV format.
    """

    _codes = (
        ('\n', '\r', '\x1F', '\r\n', '\x00'),
        (b'\n', b'\r', b'\x1F', b'\r\n', b'\x00'),
    )

    def __init__(self, f):
        """ Initialise a new SSV reader

        The passed files-like object must support .readline() and
        must not use newline conversion (or support .reconfigure()
        as in _io.TextIOWrapper, which is called with newline='\\n'
        for the f object if hasattr).

         f - files-like object read from
        """

        if hasattr(f, 'reconfigure'):
            # see https://bugs.python.org/issue46695 though
            f.reconfigure(newline='\n')
        self.f = f

    def read(self):
        """ Read and decode one SSV line

        Returns a list of fields, or None on EOF
        """

        s = self.f.readline()
        if not s:
            return None

        if isinstance(s, bytes):
            codes = self._codes[1]
        elif isinstance(s, str):
            codes = self._codes[0]
        else:
            raise TypeError()
        lf, cr, us, nl, nul = codes
        if s.find(nul) != -1:
            raise CSVInvalidCharacterError(s)

        s = s.rstrip(lf)
        if s.find(lf) != -1:
            raise CSVInvalidCharacterError(s)
        return s.replace(cr, nl).split(us)

# mostly example of how to use this
if __name__ == "__main__":
    newline_ways = {
        'ascii': '\r\n',
        'unix': '\n',
        'mac': '\r',
    }
    import argparse
    p = argparse.ArgumentParser(description='Converts SSV to CSV.', add_help=False)
    g = p.add_argument_group('Options')
    g.add_argument('-h', action='help', help='show this help message and exit')
    g.add_argument('-s', metavar='sep', help='field separator, e.g. \x27,\x27 (default: tab)', default='\t')
    g.add_argument('-q', metavar='qch', help='quote character, e.g. \x27\x22\x27 (default: none)', default=None)
    g.add_argument('-n', metavar='eoltype', choices=list(newline_ways.keys()), help='line endings (ascii (default), unix, mac)', default='ascii')
    g.add_argument('-P', metavar='preset', choices=['std', 'sep', 'ssv'], help='predefined config (std=RFC 4180, sep=Excel header, ssv=SSV)')
    g = p.add_argument_group('Arguments')
    g.add_argument('file', help='SSV file to read, "-" for stdin (default)', nargs='?', default='-')
    args = p.parse_args()
    if args.P in ('std', 'sep'):
        args.s = ','
        args.q = '"'
        args.n = 'ascii'
    nl = newline_ways[args.n]
    if args.P == 'sep':
        print('sep=%s' % args.s, end=nl)
    if args.P == 'ssv':
        w = SSVWriter()
    else:
        w = CSVWriter(args.s, args.q, nl, nl)
    def _convert(f):
        r = SSVReader(f)
        while (l := r.read()) is not None:
            w.write(*l)
    if args.file == '-':
        import sys
        _convert(sys.stdin)
    else:
        with open(args.file, 'r') as f:
            _convert(f)
