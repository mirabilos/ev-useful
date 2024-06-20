#!/usr/bin/env python3
# Testsuite for dversion.py cribbed from:
# libdpkg - Debian packaging suite library routines
# t-version.c - test version handling
#
# Copyright © 2009-2014 Guillem Jover <guillem@debian.org>
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from dversion import Version

def p(v):
    if not v:
        raise Exception('v: ' + repr(v))

def f(v):
    if v:
        raise Exception('v: ' + repr(v))

a = Version(b"1:0")
b = Version(b"1:0")
p(a == b)
b = Version(b"2:0")
f(a == b)

a = Version((0, b"1", b"1"), True)
b = Version((0, b"2", b"1"), True)
f(a == b);

a = Version((0, b"1", b"1"), True)
b = Version((0, b"1", b"2"), True)
f(a == b);

# Test for version equality
a = b = Version((0, b"0", b"0"), True)
p(a == b);

a = Version((0, b"0", b"00"), True)
b = Version((0, b"00", b"0"), True)
p(a == b);

a = b = Version((1, b"2", b"3"), True)
p(a == b);

# Test for epoch difference
a = Version((0, b"0", b"0"), True)
b = Version((1, b"0", b"0"), True)
p(a < b);
p(b > a);

# Test for version component difference
a = Version((0, b"a", b"0"), True)
b = Version((0, b"b", b"0"), True)
p(a < b);
p(b > a);

# Test for revision component difference
a = Version((0, b"0", b"a"), True)
b = Version((0, b"0", b"b"), True)
p(a < b);
p(b > a);

a = Version((0, b"1", b"1"), True)
b = Version((0, b"1", b"1"), True)
p(a == b);
f(a < b);
p(a <= b);
f(a > b);
p(a >= b);

a = Version((0, b"1", b"1"), True)
b = Version((0, b"2", b"1"), True)
f(a == b);
p(a < b);
p(a <= b);
f(a > b);
f(a >= b);

a = Version((0, b"2", b"1"), True)
b = Version((0, b"1", b"1"), True)
f(a == b);
f(a < b);
f(a <= b);
p(a > b);
p(a >= b);

b = Version((0, b"0", None), True)
a = Version(b"0:0")
p(a.isDebianVersion() != False)
p(a == b);

b = Version((0, b"0", b"0"), True)
a = Version(b"0:0-0")
p(a.isDebianVersion() != False)
p(a == b);

b = Version((0, b"0.0", b"0.0"), True)
a = Version(b"0:0.0-0.0")
p(a.isDebianVersion() != False)
p(a == b);

# Test epoched versions
b = Version((1, b"0", None), True)
a = Version(b"1:0")
p(a.isDebianVersion() != False)
p(a == b);

b = Version((5, b"1", None), True)
a = Version(b"5:1")
p(a.isDebianVersion() != False)
p(a == b);

# Test multiple hyphens
b = Version((0, b"0-0", b"0"), True)
a = Version(b"0:0-0-0")
p(a.isDebianVersion() != False)
p(a == b);

b = Version((0, b"0-0-0", b"0"), True)
a = Version(b"0:0-0-0-0")
p(a.isDebianVersion() != False)
p(a == b);

# Test multiple colons
b = Version((0, b"0:0", b"0"), True)
a = Version(b"0:0:0-0")
p(a.isDebianVersion() == False)

b = Version((0, b"0:0:0", b"0"), True)
a = Version(b"0:0:0:0-0")
p(a.isDebianVersion() == False)

# Test multiple hyphens and colons
b = Version((0, b"0:0-0", b"0"), True)
a = Version(b"0:0:0-0-0")
p(a.isDebianVersion() == False)

b = Version((0, b"0-0:0", b"0"), True)
a = Version(b"0:0-0:0-0")
p(a.isDebianVersion() == False)

# Test valid characters in upstream version
a = Version(b"0:09azAZ.-+~:-0")
p(a.isDebianVersion() == False)
b = Version((0, b"09azAZ.-+~", b"0"), True)
a = Version(b"0:09azAZ.-+~-0")
p(a.isDebianVersion() != False)
p(a == b);

# Test valid characters in revision
b = Version((0, b"0", b"azAZ09.+~"), True)
a = Version(b"0:0-azAZ09.+~")
p(a.isDebianVersion() != False)
p(a == b);

# Test empty version
exc = 0
try:
	a = Version(b"")
except:
	exc += 1
try:
	a = Version(b"  ")
except:
	exc += 2
p(exc == 1) # we accept basically any string

# Test empty upstream version after epoch
a = Version(b"0:")
p(a.isDebianVersion() == False)

# Test empty epoch in version
a = Version(b":1.0")
p(a.isDebianVersion() == False)

# Test empty revision in version
a = Version(b"1.0-")
p(a.isDebianVersion() == False)

# Test version with embedded spaces
a = Version(b"0:0 0-1")
p(a.isDebianVersion() == False)

# Test version with negative epoch
a = Version(b"-1:0-1")
p(a.isDebianVersion() == False)

# Test version with huge epoch
a = Version(b"999999999999999999999999:0-1")
p(a.isDebianVersion() == False)

# Test invalid characters in epoch
a = Version(b"a:0-0")
p(a.isDebianVersion() == False)
a = Version(b"A:0-0")
p(a.isDebianVersion() == False)

# Test invalid empty upstream version
a = Version(b"-0")
p(a.isDebianVersion() == False)
a = Version(b"0:-0")
p(a.isDebianVersion() == False)

# Test upstream version not starting with a digit
a = Version(b"0:abc3-0")
p(a.isDebianVersion() != False)

# Test invalid characters in upstream version
a = Version(b"0:0%s-0" % b"a")
p(a.isDebianVersion() != False)
a = Version(b"0:0%s-0" % b"!")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"#")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"@")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"$")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"%")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"&")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"/")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"|")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"\\")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"<")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b">")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"(")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b")")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"[")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"]")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"{")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"}")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b";")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b",")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"_")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"=")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"*")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"^")
p(a.isDebianVersion() == False)
a = Version(b"0:0%s-0" % b"'")
p(a.isDebianVersion() == False)

# Test invalid characters in revision
a = Version(b"0:0-0%s0" % b":")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"a")
p(a.isDebianVersion() != False)
a = Version(b"0:0-0%s0" % b"!")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"#")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"@")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"$")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"%")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"&")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"/")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"|")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"\\")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"<")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b">")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"(")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b")")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"[")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"]")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"{")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"}")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b";")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b",")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"_")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"=")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"*")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"^")
p(a.isDebianVersion() == False)
a = Version(b"0:0-0%s0" % b"'")
p(a.isDebianVersion() == False)

# and from me
a = Version(b'1.23.')
b = Version(b'1.23.0')
p(a == b)

print("ok")
