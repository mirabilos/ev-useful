#!/usr/bin/env python3
#-
# Copyright © 2024 mirabilos
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

import bs4
import re
import sys

us = '\x1F'
ls = '\x0D'
cellre = re.compile("^t[dh]$")

def escape(s):
    s = ''+s
    if s.find(us) != -1:
        raise ValueError("unit separator in cell: " + s)
    if s.find(ls) != -1:
        raise ValueError("line separator in cell: " + s)
    s = s.replace('\n', ls)
    return s

for name in sys.argv[1:]:
    tblno = 0
    print("I: working on", name)
    with open(name, encoding='UTF-8', errors='strict', newline='\n') as fp:
        text = fp.read()
    text = re.sub('\r+\n?', '\n', text)
    html = bs4.BeautifulSoup(text, 'html.parser', multi_valued_attributes=None)
    for e in html.find_all('table'):
        tblno += 1
        rowspans = {}
        with open("%s.%d.ssv" % (name, tblno), "w", encoding='UTF-8', newline='\n') as fp:
            for row in e.find_all('tr'):
                rowstr = ''
                colsep = ''
                curcol = 0
                for cell in row.find_all(cellre):
                    curcol += 1
                    while curcol in rowspans:
                        rowsp = rowspans.pop(curcol)
                        if rowsp > 1:
                            rowstr += colsep
                            colsep = us
                            if rowsp > 2:
                                rowspans[curcol] = rowsp - 1
                            curcol += 1
                    rowstr += colsep + escape(cell.get_text())
                    colsep = us
                    if cell.has_attr('colspan'):
                        nspan = int(cell['colspan'])
                        while nspan > 1:
                            rowstr += colsep
                            nspan -= 1
                    if cell.has_attr('rowspan'):
                        rowspans[curcol] = int(cell['rowspan'])
                fp.write(rowstr + '\n')
        print("I: processed table", tblno)
