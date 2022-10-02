#!/bin/mksh
# © 2022 mirabilos Ⓕ CC0

export LC_ALL=C
unset LANGUAGE

set -A ubu -- 0 0 0

curl -s https://udd.debian.org/cgi-bin/ubuntubugs.cgi | \
    grep -E '^(bash|dash|mksh)[|][0-9]+[|]' |&
    while IFS='|' read -pr pkg bugs rest; do
	case $pkg {
	(bash) n=0 ;;
	(dash) n=1 ;;
	(mksh) n=2 ;;
	(*) print -u2 ERR; continue ;;
	}
	ubu[n]=$bugs
done

print -r -- '-- '
print -r -- 'Support mksh as /bin/sh and RoQA dash NOW!'

curl -s https://udd.debian.org/cgi-bin/ddpo-bugs.cgi | \
    grep -E '^(bash|dash|mksh):[0-9]+\([0-9]+\) [0-9]+\([0-9]+\) [0-9]+\([0-9]+\) [0-9]+\([0-9]+\) [0-9]+\([0-9]+\)' | \
    sort | \
    tr ':()' '   ' | \
    while read -r pkg rc rcm in inm mw mwm fp fpm patch patchm; do
	case $pkg {
	(bash) n=0 ;;
	(dash) n=1 ;;
	(mksh) n=2 ;;
	(*) print -u2 ERR; continue ;;
	}
	((# a = fp + mw + in + rc ))
	((# am = fpm + mwm + inm + rcm ))
	s="‣ src:$pkg ($a"
	[[ $a = $am ]] || s+=" ($am)"
	if (( a == 1 )); then
		s+=' bug: '
	else
		s+=' bugs: '
	fi
	s+=$rc
	[[ $rc = $rcm ]] || s+=" ($rcm)"
	s+=" RC, $in"
	[[ $in = $inm ]] || s+=" ($inm)"
	s+=" I&N, $mw"
	[[ $mw = $mwm ]] || s+=" ($mwm)"
	s+=" M&W, $fp"
	[[ $fp = $fpm ]] || s+=" ($fpm)"
	s+=" F&P)"
	if [[ ${ubu[n]} != 0 ]]; then
		s+=" + ${ubu[n]}"
		(( n == 0 )) || s+=" ubu"
	fi
	print -r -- "$s"
done

print -r -- 'dash has two RC bugs they just closed because they don’t care about quality…'
