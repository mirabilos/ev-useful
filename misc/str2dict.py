#!/usr/bin/env python
# coding: utf-8
# $Id: tools.py 660 2009-10-01 09:17:51Z tglase $
#-
# Copyright © 2009
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
