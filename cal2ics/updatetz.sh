#!/bin/mksh
#-
# Copyright © 2021
#	mirabilos <t.glaser@tarent.de>
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
# Update shipped timezones from some master copy’s VTIMEZONE files.

export LC_ALL=C
unset LANGUAGE
set +o inherit-xtrace
set -ex
set -o pipefail
cd "$(dirname "$0")"
wd=$(pwd)
bd=$wd/tzdata.ics
test -d "$bd" || mkdir "$bd"
rm -rf .tmp
mkdir .tmp
cd .tmp
git clone --depth 1 https://github.com/libical/libical
chmod -R u+w libical
cd libical

function cvt {
	local line

	while IFS= read -r line; do
		line=${line%}
		if [[ $line = TZID:* ]]; then
			line=TZID:$name
		fi
		print -r -- "${line}"
	done
}

find zoneinfo/ -type f -a -name \*.ics -print0 | \
    while IFS= read -r -d '' fn; do
	dn=${fn%/*}
	if [[ $dn != zoneinfo ]]; then
		dn=${dn#zoneinfo/}
		test -d "$bd/$dn" || mkdir -p "$bd/$dn"
	fi
	name=${fn%.ics}
	name=${name#zoneinfo/}
	cvt <"$fn" >"$bd/$name"
done
cd "$wd"
rm -r .tmp
: ok
