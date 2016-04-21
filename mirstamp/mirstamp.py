#!/usr/bin/env python
# coding: utf-8
#-
# Copyright © 2016
#	mirabilos <m@mirbsd.org>
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
#-
# GIMP plugin to add a text to an image’s corner

from array import array
from datetime import datetime
from gimpfu import *

default_text = '© %d mirabilos' % datetime.now().year

def do_mirstamp(timg, tdrawable, text, colour):
    # ╱╲╱╲╱╲ 96x16px R,G,B – for now…
    w = 96
    h = 16
    tl = gimp.Layer(timg, "tmp", w, h, RGBA_IMAGE, 100, NORMAL_MODE)
    tl.fill(TRANSPARENT_FILL)
    pr = tl.get_pixel_rgn(0, 0, w, h)
    if len(pr[0, 0]) != 4:
        raise Exception("number of channels (%d) unexpectedly not 4" % len(pr[0, 0]))
    fb = array("B", pr[0:w, 0:h])
    for (ofs, col) in ((0,(255,0,0)), (32,(0,255,0)), (64,(0,0,255))):
        bcol = array("B", col)
        bcol.append(0xFF)
        def draw(x, y):
            ptr = (y * w + x + ofs) * 4
            fb[ptr:ptr+4] = bcol
        draw(0, 15 - 0)
        draw(0, 15 - 1)
        draw(1, 15 - 2)
        draw(2, 15 - 2)
        draw(3, 15 - 3)
        draw(4, 15 - 4)
        draw(5, 15 - 5)
        draw(6, 15 - 6)
        draw(7, 15 - 7)
        draw(8, 15 - 8)
        draw(9, 15 - 9)
        draw(10, 15 - 10)
        draw(11, 15 - 11)
        draw(12, 15 - 12)
        draw(13, 15 - 13)
        draw(14, 15 - 14)
        draw(15, 15 - 15)
        draw(16, 15 - 15)
        draw(17, 15 - 14)
        draw(18, 15 - 13)
        draw(19, 15 - 12)
        draw(20, 15 - 11)
        draw(21, 15 - 10)
        draw(22, 15 - 9)
        draw(23, 15 - 8)
        draw(24, 15 - 7)
        draw(25, 15 - 6)
        draw(26, 15 - 5)
        draw(27, 15 - 4)
        draw(28, 15 - 3)
        draw(29, 15 - 2)
        draw(30, 15 - 1)
        draw(31, 15 - 0)
    pr[0:w, 0:h] = fb.tostring()
    tl.set_offsets(0, timg.height - h)
    timg.add_layer(tl, -1)
    timg.flatten()

register("mirstamp",
  "Add copyright overlay text",
  "Add copyright overlay to (for now) bottom-left corner",
  "mirabilos",
  "(c) 2016 mirabilos; published under The MirOS Licence",
  "2016",
  "<Image>/Filters/_MirStamp...",
  "RGB*",
  [
    (PF_STRING, "text", "Text", default_text),
    (PF_COLOUR, "colour", "Text color", (0xAA, 0xAA, 0xAA)),
    # add corner? t/m/b l/c/r
    # (PF_OPTION,"p1",   "OPTION:", 0, ["0th","1st","2nd"]), # initially 0th is choice
    # (PF_RADIO, "p16", "RADIO:", 0, (("0th", 1),("1st",0))), # note bool indicates initial setting of buttons
  ],
  [],
  do_mirstamp)
main()
