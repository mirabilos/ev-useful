#!/bin/mksh
# $Id: report.cgi 4042 2014-05-23 09:30:40Z tglase $
#-
# Copyright © 2009, 2010, 2011, 2012, 2013, 2014
#	Thorsten Glaser <t.glaser@tarent.de>
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

export LC_ALL=C TZ=Europe/Berlin
unset LANG LANGUAGE

cd /var/lib/checktask-server

if [[ $REMOTE_ADDR != +([0-9]).+([0-9]).+([0-9]).+([0-9]) ]]; then
	logger -t checktasks-report "rc=500 IP<$REMOTE_ADDR> QS<$QUERY_STRING>"
	print Status: 500 wrong input
	exit 1
fi

if [[ $REMOTE_ADDR = @(195.71.200.162|172.28.1.14) ]]; then
	print Status: 402 Payment Required
	print Content-type: text/plain
	print
	print FAIL because ... are no longer managed by us.
	exit 0
fi

qs=$QUERY_STRING
tslval=$(date +'%s')
tsval=$tslval
if [[ $qs = 8,+([0-9/.-]),* ]]; then
	qs=${qs#8,}
	tsqs=${qs%%,*}
	qs=7,${qs#*,}
else
	tsqs=
fi
if [[ $qs = 7,?(-)+([0-9]),* ]]; then
	qs=${qs#7,}
	deltat=${qs%%,*}
	qs=${qs#*,}
	(( tsval -= deltat ))
fi
tsval=$(date -d @$tsval +'%Y-%m-%d %H:%M')

if [[ $qs = 1,?([~!])+([a-zA-Z0-9._-]),* || \
    $qs = [23],,?([~!])+([a-zA-Z0-9._-]),* || \
    $qs = 4,+([0-9a-zA-Z:.]),,?([~!])+([a-zA-Z0-9._-]),* ]]; then
	logger -t checktasks-report "rc=NOMAC IP<$REMOTE_ADDR> QS<$QUERY_STRING>"
	typeset -Uui16 -Z5 hexval
	remote_lladdr=ff:ff
	save_IFS=$IFS
	IFS=.
	for i in $REMOTE_ADDR; do
		let hexval=10#$i
		remote_lladdr=$remote_lladdr:${hexval#16#}
	done
	IFS=$save_IFS
elif [[ $qs = 4,+([0-9a-zA-Z:.]),*([0-9a-fA-F:]),?([~!])+([a-zA-Z0-9._-]),* ]]; then
	logger -t checktasks-report "rc=OK IP<$REMOTE_ADDR> QS<$QUERY_STRING>"
	remote_lladdr=${qs#4,+([0-9a-zA-Z:.]),}
	remote_lladdr=${remote_lladdr%%,*}
elif [[ $qs = 2,*([0-9a-fA-F:]),?([~!])+([a-zA-Z0-9._-]),* ]]; then
	logger -t checktasks-report "rc=OLD IP<$REMOTE_ADDR> QS<$QUERY_STRING>"
	remote_lladdr=${qs#2,}
	remote_lladdr=${remote_lladdr%%,*}
elif [[ $qs = 3,*([0-9a-fA-F:]),?([~!])+([a-zA-Z0-9._-]),* ]]; then
	logger -t checktasks-report "rc=DHCP IP<$REMOTE_ADDR> QS<$QUERY_STRING>"
	remote_lladdr=${qs#3,}
	REMOTE_ADDR=${remote_lladdr#*,}
	qs=${REMOTE_ADDR#*,}
	REMOTE_ADDR=${REMOTE_ADDR%%,*}
	remote_lladdr=${remote_lladdr%%,*}
	qs=3,$remote_lladdr,$qs
else
	logger -t checktasks-report "rc=FAIL IP<$REMOTE_ADDR> QS<$QUERY_STRING>"
	rc=FAIL
	print Content-type: text/plain
	print
	print -r -- $rc "$QUERY_STRING"
	exit 0
fi

typeset -u remote_lladdr
rc=OK
outf=cooked.$remote_lladdr
ipdot=$REMOTE_ADDR

print Content-type: text/plain
print
print -r -- $rc "$QUERY_STRING"

# for debugging, append stderr now
exec 2>&1

function iptohex {
	local i h a save_IFS
	typeset -Uui n

	save_IFS=$IFS; IFS=.; set -A a -- $1; IFS=$save_IFS
	h=0x
	for i in 0 1 2 3; do
		(( n = 0x100 + 10#${a[i]} ))
		(( n < 0x100 || n > 0x1FF )) && return 1
		h=$h${n#16#1}
	done
	print $h
}

function fqdnfix {
	local fqdn=$1

	[[ $fqdn = *.tarent.buero ]] && \
	    fqdn=${fqdn%%.tarent.buero}.berlin.tarent.de
	fqdn=${fqdn/.tarent.//}
	fqdn=${fqdn/%.unbelievable-machine.net/\~UM}
	fqdn=${fqdn/%.pool.mediaWays.net/\~Viag}
	fqdn=${fqdn/%.dip0.t-ipconnect.de/\~Tdip}
	print -r -- "$fqdn"
}

function url2html {
	print -n -- $(print -nr -- "$@" | sed -e 's/\\/%5c/g' \
	    -e 's/%\([0-9a-fA-F][0-9a-fA-F]\)/\\x\1/g') | \
	    expand | \
	    sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' \
	    -e 's!\([]\)!	\1</span>!g' \
	    -e 's!</span>	!!g' \
	    -e 's	<span style="background:#000000; color:#FF00FF; margin:1px; padding:1px;">g' \
	    -e 'y//ABCDEFGHKLMNPQRSTUVWXYZ[\\]^_/' | \
	    tr '\n' ''
}

function htmlencode {
	print -nr -- "$@" | sed \
	    -e 's/&/\&amp;/g' \
	    -e 's/</\&lt;/g' \
	    -e 's/>/\&gt;/g'
}

function fqdnencode {
	local short=$1 full=$2 makesmall=$3

	if (( makesmall )) && \
	    [[ $short != +([0-9]).+([0-9]).+([0-9]).+([0-9]) ]]; then
		short=$(htmlencode "$short" | \
		    sed 's!^\([^.]*.\)\(.*\)$!\1<span class="ipdom">\2</span>!')
	else
		short=$(htmlencode "$short")
	fi

	if [[ -n $full ]]; then
		print -r "<span title=\"$(htmlencode "$full")\">$short</span>"
	else
		print -r -- "$short"
	fi
}

typeset -Z11 -Uui16 iphex
typeset -Uui1 c

iphex=$(iptohex $ipdot) || exit 0

ttype=%
ofqdn=
sfqdn=1
if [[ $qs = 1,?([~!])+([a-zA-Z0-9._-]),* || \
    $qs = [23],*([0-9a-fA-F:]),?([~!])+([a-zA-Z0-9._-]),* ||
    $qs = 4,+([0-9a-zA-Z:.]),*([0-9a-fA-F:]),?([~!])+([a-zA-Z0-9._-]),* ]]; then
	if [[ $qs = 4,* ]]; then
		lladdr=${qs#4,}
		ttype=${lladdr%%,*}
		lladdr=${lladdr#+([0-9a-zA-Z:.]),}
		fqdn=${lladdr#*([0-9a-fA-F:]),}
		lladdr=${lladdr%%,*}
	elif [[ $qs = 1,* ]]; then
		fqdn=${qs#1,}
		lladdr=
	elif [[ $qs = [23],* ]]; then
		[[ $qs = 3* ]] && ttype=DHCP
		lladdr=${qs#[23],}
		fqdn=${lladdr#*([0-9a-fA-F:]),}
		lladdr=${lladdr%%,*}
	fi
	text=${fqdn#*,}
	fqdn=${fqdn%%,*}
	if [[ $qs = 1,* || $qs = [23],,* || $qs = 4,+([0-9a-zA-Z:.]),,* ]]; then
		c=1	# red
		fqdn=${fqdn#[~!]}
	elif [[ $qs = 3,* ]]; then
		c=8	# grey
	elif [[ $fqdn = !* ]]; then
		c=4	# blue
		fqdn=${fqdn#!}
	elif [[ $fqdn = ~* ]]; then
		c=1	# red
		fqdn=${fqdn#~}
	else
		c=3	# green
	fi
	lladdr=$remote_lladdr

	if [[ $fqdn = *.X ]]; then
		sfqdn=0
		fqdn=${fqdn%.X}
	fi
	ofqdn=$fqdn
	fqdn=$(fqdnfix "$ofqdn")
	[[ $ofqdn = "$fqdn" ]] && ofqdn=

	if [[ $text = *'%0'[Aa]* ]]; then
		body=$(url2html "${text#*'%0'[Aa]}")
		text=${text%%'%0'[Aa]*}
	else
		body=
	fi
	text=$(url2html "$text")
else
	fqdn=0x${iphex#16#}
	lladdr=
	c=1	# red
	text="invalid QUERY_STRING received"
	body=$(htmlencode "$qs")
fi

revdns=$(host $ipdot 2>&1 | fgrep -v 'is an alias for' | tr '\n' '')
if [[ $revdns = *'domain name pointer'*''* ]]; then
	revdns=${revdns%%.*}
	orevdns=${revdns##*domain name pointer }
	revdns=$(fqdnfix "$orevdns")
	[[ $orevdns = "$revdns" ]] && orevdns=
else
	revdns="no PTR RR"
	orevdns=
fi

if [[ $tsqs = +([0-9])/* ]]; then
	tsqtv=10#${tsqs%%/*}
	tsqs=${tsqs#*/}
else
	tsqtv=
	tsqs=
fi
if [[ $tsqs = ?(-)+([0-9]).+([0-9])/+([0-9]).+([0-9]).+([0-9]).+([0-9]) ]]; then
	tsqd=${tsqs%%/*}
	tsqr=${tsqs#*/}
	tsqms=${tsqd#-}
	tsqs=${tsqms%.*}
	tsqms=${tsqms#*.}000
	tsqms=$tsqs${tsqms::3}
	tsqd="$tsqd s to"
	tsqms=10#$tsqms		# interpret as decimal
	if [[ $tsqs = @([0-9][0-9][0-9][0-9][0-9][0-9])* && -n $tsqtv ]]; then
		# much more than a day
		tsqs=$((tslval - tsqtv))
		(( tsqs >= 0 )) || (( tsqs = -tsqs ))
		tsqd="$tsqs s off(${tsqd%%[ .]*})"
		tsqr=
		tsfarbe=grey
		(( tsqs > 30 )) && tsfarbe=bwinverse
		(( tsqs > 86400 )) && tsfarbe=red
	elif (( tsqms < 128 )); then
		tsfarbe=bwnormal
	elif (( tsqms < 500 )); then
		tsfarbe=green
	elif (( tsqms < 1000 )); then
		tsfarbe=yellow
	elif (( tsqms < 5000 )); then
		tsfarbe=blue
	elif (( tsqms < 60000 )); then
		tsfarbe=orange
	else
		tsfarbe=red
	fi
elif [[ -n $tsqtv ]]; then
	tsqs=$((tslval - tsqtv))
	(( tsqs >= 0 )) || (( tsqs = -tsqs ))
	tsqd="$tsqs s off"
	tsqr=127.0.0.1
	tsfarbe=grey
	(( tsqs > 30 )) && tsfarbe=bwinverse
else
	tsqd=
	tsqr=
	tsqms=
fi
if [[ -n $tsqd ]]; then
	tslinepart="${tsfarbe}$(htmlencode $tsval)${tsqd}${tsqr}</pre></td><td>"
else
	tslinepart="<td class=\"tsval greyed\">$(htmlencode $tsval)</td><td>"
fi

line="$tsval ${iphex#16#} $fqdn ${lladdr:-~} $ttype "
line="$line <tr><td style=\"background-color:${c#1#};\" "
line="$line<td style=\"background-color:${c#1#};\""
line="$line class=\"ip\">$(htmlencode $ipdot)"
line="$line$(fqdnencode "$revdns" "$orevdns" 0)"
line="$line${lladdr:+<br />$lladdr}</td>"
line="$line<td class=\"ttype\">$(htmlencode "$ttype")</td>"
if [[ $fqdn = +([0-9]).+([0-9]).+([0-9]).+([0-9]) ]]; then
	fqdnclass=grey
elif [[ $fqdn = *localhost* || $fqdn = *.local* ]]; then
	fqdnclass=red
elif [[ $fqdn = *.invalid.fqdn || $fqdn = dhcp-* || $fqdn = *.dynamic* ]]; then
	fqdnclass=orange
	fqdn=${fqdn%.invalid.fqdn}
elif [[ $fqdn = *.no.fqdn ]]; then
	fqdnclass=orange
	fqdn=${fqdn%.no.fqdn}.--
elif [[ $fqdn = +([!.]).lan/de ]]; then
	fqdnclass=fqdn
elif [[ $fqdn = +([!.]).lan.osiam.net ]]; then
	fqdnclass=fqdn
elif [[ $fqdn = *.lan* ]]; then
	fqdnclass=red
else
	fqdnclass=fqdn
fi
[[ $sfqdn$fqdnclass = 0fqdn ]] && fqdnclass=yellow
line="$line<td class=\"$fqdnclass\">$(fqdnencode \
    "$fqdn" "$ofqdn" 1)</td>$tslinepart"
[[ -n $body ]] && line="${line}"
line="$line<tt>$text</tt>"
[[ -n $body ]] && line="${line}$body"
line="$line</td></tr>"

print -r -- "$line" >$outf
exit 0
