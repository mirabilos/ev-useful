#!/bin/mksh
#-
# Copyright © 2023
#	mirabilos <m@mirbsd.org>
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
# BSD calendar(1) to iCalendar converter.

export LC_ALL=C
unset LANGUAGE
me=$(realpath "$0/..")
T=
set -o noglob

die() {
	print -ru2 "E: $*"
	cd /
	[[ -z $T ]] || rm -rf "$T"
	exit 1
}

usage() {
	print -ru2 "Usage: $0 [-l localtimezone] [-n name] calendarfile >converted.ics"
	exit ${1:-1}
}

command -v md5sum >/dev/null 2>&1 || alias md5sum=md5
function hsh {
	local x

	x=$(md5sum <<<"$1") || die md5sum failed
	set -- $x
	REPLY=${1::16}
}

localtime=-
calname=
defdur=PT42M
ca=$'\x01'
cr=$'\r'
set -A cal_cmd -- calendar -PP
while getopts 'D:hl:n:' ch; do
	case $ch {
	(D) cal_cmd+=("-D$OPTARG") ;;
	(h) usage 0 ;;
	(l) localtime=$OPTARG ;;
	(n) calname=$OPTARG ;;
	(*) usage ;;
	}
done
shift $((OPTIND - 1))
[[ $# = 1 ]] || usage

if [[ $localtime = - ]]; then
	localtime=$(readlink /etc/localtime) || \
	    die cannot readlink /etc/localtime
	[[ $localtime = /usr/share/zoneinfo/* ]] || \
	    die "not a timezone: ${localtime@Q}"
	localtime=${localtime#/usr/share/zoneinfo/}
fi
if [[ $localtime = */..?(/*) ]]; then
	die "invalid timezone ${localtime@Q}"
fi
[[ -s $me/tzdata.ics/$localtime ]] || die "unknown timezone ${localtime@Q}"
set -A tzs -- "$localtime"
F=$1
[[ $F = /* ]] || F=$PWD/$F
[[ -f $F && -r $F ]] || die "no calendar file: ${F@Q}"
FH=${|hsh "$F";}
H=$(hostname -f 2>/dev/null) || H=$(hostname) || die hostname failed
[[ -n $H ]] || die hostname empty
dtstamp=$(date -u +'%Y%m%dT%H%M%SZ')

function oo {
	print -r -- "$1$cr" || die cannot output
}

function ow {
	local l=$1 c n

	while [[ -n $l ]]; do
		set +U
		n=${#l}
		if (( n <= 75 )); then
			oo "$l"
			return
		fi
		set -U
		c=${l::72}
		set +U
		n=${#c}
		if (( n <= 75 )); then
			oo "$c"
			set -U
			l=" ${l:72}"
			continue
		fi
		set -U
		c=${l::60}
		set +U
		n=${#c}
		if (( n <= 75 )); then
			oo "$c"
			set -U
			l=" ${l:60}"
			continue
		fi
		set -U
		oo "${l::18}"	# 75/4, 4=MB_LEN_MAX in UTF-8
		l=" ${l:18}"
	done
}

function ot {
	local s

	s=${2@/[,;\\]/\\$KSH_MATCH}
	ow "$1:${s//$'\n'/\\n}"
}

function cvwd {
	case $1 {
	(Sun) REPLY=SU ;;
	(Mon) REPLY=MO ;;
	(Tue) REPLY=TU ;;
	(Wed) REPLY=WE ;;
	(Thu) REPLY=TH ;;
	(Fri) REPLY=FR ;;
	(Sat) REPLY=SA ;;
	(*)
		die "invalid weekday ${1@Q} in ${o@Q}" ;;
	}
}

function emit {
	local xuntil

	oo 'BEGIN:VEVENT'
	oo "DTSTAMP:$dtstamp"
	ow "UID:cal2ics.$FH.${|hsh "$o";}@$H"
	if [[ $start = whole-day ]]; then
		oo "DTSTART;VALUE=DATE:${date//-}"
	elif [[ $tz = UTC ]]; then
		oo "DTSTART:${date//-}T${start/:}00Z"
	else
		ow "DTSTART;TZID=$tz:${date//-}T${start/:}00"
	fi
	if [[ $recurmode = special && $year != '*' ]]; then
		summary="$year, $summary"
	fi
	ot SUMMARY "$asterisk$summary"
	[[ $recurmode = @(monthly|weekly) && $year != '*' ]] && \
	    if [[ $start = whole-day ]]; then
		xuntil=";UNTIL=${year}1231"
	elif [[ $tz = UTC ]]; then
		xuntil=";UNTIL=${year}1231T235959Z"
	else
		xuntil=";UNTIL=${year}1231T235959"
	fi
	if [[ $recurmode = yearly && $recurfreq = *,* ]]; then
		# yearly -05,Sun+2
		ow "RRULE:FREQ=YEARLY;BYMONTH=${recurfreq:1:2};BYDAY=${recurfreq:7}${|cvwd ${recurfreq:4:3};}"
	elif [[ $recurmode = yearly ]]; then
		# yearly -06-01
		oo "RRULE:FREQ=YEARLY;BYMONTH=${recurfreq:1:2};BYMONTHDAY=${recurfreq:4}"
	elif [[ $recurmode = monthly && $recurfreq = +([0-9]) ]]; then
		# monthly 15
		ow "RRULE:FREQ=MONTHLY;BYMONTHDAY=$recurfreq$xuntil"
	elif [[ $recurmode = monthly ]]; then
		# monthly Wed+3
		ow "RRULE:FREQ=MONTHLY;BYDAY=${recurfreq:3}${|cvwd ${recurfreq::3};}$xuntil"
	elif [[ $recurmode = weekly ]]; then
		# weekly Wed
		ow "RRULE:FREQ=WEEKLY;BYDAY=${|cvwd $recurfreq;}$xuntil"
	fi
	if [[ $start = whole-day ]]; then
		: default duration of 1 day is okay
	elif [[ $end = ?('@') ]]; then
		oo "DURATION:$defdur"
	elif [[ $tz = UTC ]]; then
		oo "DTEND:${date//-}T${end/:}00Z"
	else
		ow "DTEND;TZID=$tz:${date//-}T${end/:}00"
	fi
	ot COMMENT "$o"
	oo 'END:VEVENT'
}

T=$(mktemp -d /tmp/cal2ics.XXXXXXXXXX) || die cannot create temporary directory
"${cal_cmd[@]}" -f "$F" >"$T/p" || die cannot parse "${F@Q}" as calendar file
print '>' >>"$T/p" || die huh?
cd "$T" || die cannot change to temporary directory
s=0
while IFS= read -r line; do
	# any UTF-8 in the input is presumed valid
	[[ $line = *[$'\x01'-$'\x08\x0A'-$'\x1F\x7F']* ]] && \
	    die "invalid control characters in ${line@Q}"
	if [[ $line = '>'* ]]; then
		(( s == 0 )) || emit
		o=${line#'>'}
		s=1
		continue
	fi
	if [[ $s$line = 1@(=|'*')* ]]; then
		asterisk=
		[[ $line = '*'* ]] && asterisk='*'
		set -- ${line#?}
		date=$1
		recurmode=$2
		recurfreq=$3
		year=$4
		start=$5
		end=$6
		tz=$7
		summary=
		t="${asterisk:-=}$date $recurmode $recurfreq $year $start"
		(( $# > 5 )) && t+=" $end"
		(( $# > 6 )) && t+=" $tz"
		if [[ $line != "$t" ]]; then
			print -ru2 "N: got: $line"
			print -ru2 "N: want $t"
			print -ru2 "N: orig $o"
			die invalid input line for calendaric entry
		fi
		if [[ -n $tz ]]; then
			if [[ $tz != +([ !#-+.-9<-~-]) ]]; then
				print -ru2 "N: orig $o"
				die "invalid timezone ${tz@Q}"
			fi
			found=0
			for x in "${tzs[@]}"; do
				[[ $tz = "$x" ]] || continue
				found=1
				break
			done
			if (( !found )); then
				[[ -s $me/tzdata.ics/$tz ]] || \
				    die "unknown timezone ${tz@Q}"
				tzs+=("$tz")
			fi
		else
			tz=$localtime
		fi
		s=2
		continue
	fi
	if [[ $s$line = 2$'\t'* ]]; then
		t=${line#?}
		if [[ -n $summary ]]; then
			o+=$'\n'$t
			summary+=$'\n'$t
		else
			summary=$t
		fi
		continue
	fi
	print -ru2 "N: orig $o"
	print -ru2 "N: this ${line@Q}"
	die invalid continuation line
done <p >e
set -sA tzs -- "${tzs[@]}"
oo 'BEGIN:VCALENDAR'
oo 'VERSION:2.0'
ow 'PRODID:https://evolvis.org/plugins/scmgit/cgi-bin/gitweb.cgi?p=useful-scripts/useful-scripts.git\;a=tree\;f=cal2ics\;hb=HEAD'
if [[ -n $calname ]]; then
	# RFC 7986
	ot NAME "$calname"
	# https://stackoverflow.com/a/17187346/2171120
	ot X-WR-CALNAME "$calname"
fi
for tz in "${tzs[@]}"; do
	[[ $tz = UTC ]] && continue
	sed -n '/^BEGIN:VTIMEZONE/,/^END:VTIMEZONE/p' \
	    <"$me/tzdata.ics/$tz" || die "cannot add timezone ${tz@Q}"
done
cat e || die cannot add VEVENT stream
oo 'END:VCALENDAR'
cd /
rm -rf "$T"
