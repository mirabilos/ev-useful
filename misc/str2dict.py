#!/usr/bin/env python
# coding: utf-8
# $Id: tools.py 660 2009-10-01 09:17:51Z tglase $
#-
# Copyright © 2009
#   Thorsten Glaser <t.glaser@tarent.de>

__version__ = """
    $Id: tools.py 660 2009-10-01 09:17:51Z tglase $
"""

def str2dict(s):
    """Convert a "foo=bar, blah=baz" type string into a dictionary"""

    if type(s) not in (str, unicode):
        s = str(s)
    d = {}
    for kv in [[x.strip() for x in i.split('=', 1)] for i in s.split(',')]:
        if (len(kv[0]) > 0) and (len(kv[1]) > 0):
            d[kv[0]] = kv[1]
    return d
