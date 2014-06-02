#!/bin/mksh
# $Id: overview.cgi 4043 2014-05-23 09:35:30Z tglase $
#-
# Copyright © 2009, 2010, 2011, 2014
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

function htmlencode {
	print -nr -- "$@" | sed \
	    -e 's/&/\&amp;/g' \
	    -e 's/</\&lt;/g' \
	    -e 's/>/\&gt;/g'
}

set -A files -- cooked.*

if (( ${#files[*]} == 0 )); then
	print Content-type: text/plain
	print
	print Sorry, cannot find any data files.
	exit 0
fi

cat <<-'EOF'
	Content-type: text/html; charset=utf-8

	<?xml version="1.0"?>
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
	 "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
	<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"><head>
	 <meta http-equiv="content-type" content="text/html; charset=utf-8" />
	 <title>Overview of all checktask’d hosts</title>
	 <style type="text/css"><!--/*--><![CDATA[/*><!--*/
	  table {
	   border:1px solid black;
	   border-collapse:collapse;
	   text-align:left;
	   vertical-align:top;
	  }
	  tr {
	   border:1px solid black;
	   text-align:left;
	   vertical-align:top;
	  }
	  td {
	   border:1px solid black;
	   text-align:left;
	   vertical-align:top;
	  }
	  th {
	   background-color:#333333;
	   color:#FFFFFF;
	  }
	  .tha {
	   color:#9999FF;
	  }
	  .pms {
	   border:1px solid grey;
	   margin:1px 7px 1px 1px;
	   padding:3px 3px 3px 3px;
	  }
	  .greyed {
	   color:#666666;
	  }
	  .bwinverse {
	   color:#FFFFFF;
	   background-color:#000000;
	  }
	  .bwnormal {
	   color:#000000;
	   background-color:#FFFFFF;
	  }
	  .grey {
	   color:#000000;
	   background-color:#CCCCCC;
	  }
	  .blue {
	   color:#FFFFFF;
	   background-color:#0000FF;
	  }
	  .green {
	   color:#000000;
	   background-color:#00FF00;
	  }
	  .yellow {
	   color:#000000;
	   background-color:#FFFF00;
	  }
	  .orange {
	   color:#000000;
	   background-color:#F87217;
	  }
	  .red {
	   color:#FFFFFF;
	   background-color:#FF0000;
	  }
	  .ip {
	   font-size:80%;
	  }
	  .ttype {
	   font-size:85%;
	  }
	  .tsval {
	   font-size:80%;
	  }
	  .ipdom {
	   font-size:75%;
	  }
	 /*]]>*/--></style>
	 <script type="text/javascript"><!--//--><![CDATA[//><!--
	  function klappen(nr, shnr, tsnr, wie) {
	   var el = document.getElementById("pms" + nr);
	   var bn = document.getElementById("txt" + nr);

	   if (wie == "0")
	    bn.style.display = "block";
	   else if (wie == "1")
	    bn.style.display = "none";

	   if (bn.style.display == "none") {
	    bn.style.display = "block";
	    el.firstChild.nodeValue = "[-]";
	    wie = '1';
	   } else {
	    bn.style.display = "none";
	    el.firstChild.nodeValue = "[+]";
	    wie = '0';
	   }
	   el.className = "pms";
	   if (shnr != '') {
	    shrev(shnr, wie);
	   }
	   if (tsnr != '') {
	    tsrev(tsnr, wie);
	   }
	  }

	  function shrev(nr, wie) {
	   var el = document.getElementById("rev" + nr);
	   var bn = document.getElementById("dns" + nr);

	   if (wie == "0")
	    bn.style.display = "block";
	   else if (wie == "1")
	    bn.style.display = "none";

	   if (bn.style.display == "none") {
	    bn.style.display = "block";
	    el.firstChild.nodeValue = "[-]";
	    wie = '1';
	   } else {
	    bn.style.display = "none";
	    el.firstChild.nodeValue = "[+]";
	    wie = '0';
	   }
	   el.className = "rev";
	  }

	  function tsrev(nr, wie) {
	   var bn = document.getElementById("tsv" + nr);

	   if (wie == "0")
	    bn.style.display = "block";
	   else if (wie == "1")
	    bn.style.display = "none";

	   if (bn.style.display == "none") {
	    bn.style.display = "block";
	   } else {
	    bn.style.display = "none";
	   }
	  }
	 //--><!]]></script>
	</head><body>
	<h1>Overview of all checktask’d hosts</h1>
EOF
print "<p>This page was generated on: $(htmlencode $(TZ=Europe/Berlin date))</p>"
cat <<-'EOF'
	<p><a href="#" onclick="javascript:alle_klappen('1', '1');">Expand
	 all</a> (<a href="#" onclick="javascript:alle_klappen('1',
	 '0');">DNS/MAC only</a>) or <a onclick="javascript:alle_klappen('0',
	 '0');" href="#">Unexpand all</a>;
	 click on a <tt>[-]</tt> or <tt>[+]</tt> to toggle extra text.</p>
	<table border="1" width="100%">
	<thead>
	 <tr>
	  <th colspan="2" style="font-size:80%; vertical-align:bottom;"><b><a class="tha" href="overview.cgi?s=ip">IPv4</a>, DNS, <a class="tha" href="overview.cgi?s=ll">MAC</a></b></th>
	  <th><a class="tha" href="overview.cgi?s=tt">Type</a></th>
	  <th><a class="tha" href="overview.cgi?s=hn">FQDN</a></th>
	  <th><a class="tha" href="overview.cgi?s=ts">Last Valid</a></th>
	  <th>Information String</th>
	 </tr>
	</thead><tbody>
EOF

cbgred="#FF0000";	cfgred="#FFFFFF"
cbgyellow="#FFFF00";	cfgyellow="#000000"
cbggreen="#00FF00";	cfggreen="#000000"
cbgblue="#0000FF";	cfgblue="#FFFFFF"
cbgblueold="#0000FF";	cfgblueold="#CCCC00"
cbggrey="#CCCCCC";	cfggrey="#000000"

integer nummern=0 revnr=1 tsnrn=0

sortargs=-r	# by default, sort by tsval
if [[ ,$QUERY_STRING, = *,s=ip,* ]]; then
	sortargs=-k3
elif [[ ,$QUERY_STRING, = *,s=hn,* ]]; then
	sortargs='-k4,4 -k3'
elif [[ ,$QUERY_STRING, = *,s=ll,* ]]; then
	sortargs='-k5,5 -k3'
elif [[ ,$QUERY_STRING, = *,s=tt,* ]]; then
	sortargs='-k6,6 -k3'
elif [[ ,$QUERY_STRING, = *,s=ts,* ]]; then
	sortargs=-r
fi

older=''
print "$(date -d '1 hour ago' +'%Y-%m-%d %H:%M') FFFFFFFF - " | \
    cat - "${files[@]}" | sort -r | while IFS= read -r line; do
	if [[ $line = *''* ]]; then
		older='' # older than an hour
		continue
	fi
	print -r -- "$line" | tr '' "$older"
done | sort $sortargs | sed -ne '/^.* /s///p' |&
while IFS= read -pr line; do
	tsnr=''
	nummer=
	[[ $line = *''* ]] && nummer=$((++nummern))
	[[ $line = *''* ]] && tsnr=$((++tsnrn))
	jsbeg="<tt id=\"pms$nummer\" onclick=\"klappen('$nummer', '$revnr', '$tsnr', '');\"> </tt>"
	jsmid="<pre id=\"txt$nummer\">"
	jsend="</pre>"
	dmbeg="id=\"rev$revnr\" onclick=\"shrev('$revnr', '');\"> </td>"
	dmmid="<tt style=\"font-size:x-small;\" id=\"dns$revnr\">"
	dmend="</tt>"
	tsbeg="<td class=\"tsval "
	tsmid="\" onclick=\"tsrev('$tsnr', '');\">"
	tsend="<pre id=\"tsv$tsnr\">"
	let ++revnr

	sed \
	    -e "s/;/$cbgred; color:$cfgred;/g" \
	    -e "s/;/$cbgyellow; color:$cfgyellow;/g" \
	    -e "s/;/$cbggreen; color:$cfggreen;/g" \
	    -e "s/;/$cbgblue; color:$cfgblue;/g" \
	    -e "s/;/$cbggrey; color:$cfggrey;/g" \
	    -e "s/;/$cbgblueold; color:$cfgblueold;/g" \
	    -e "s\(.*\)\(.*\)${dmbeg}\1${dmmid}\2${dmend}g" \
	    -e "s\(.*\)\(.*\)${jsbeg}\1${jsmid}\2${jsend}g" \
	    -e "s\(.*\)\(.*\)${tsbeg}\1${tsmid}\2${tsend}g" \
	    <<<"$line" | tr '' '\n'
done

cat <<-'EOF'
	</tbody>
	</table>
	<p><a href="#" onclick="javascript:alle_klappen('1', '1');">Expand
	 all</a> (<a href="#" onclick="javascript:alle_klappen('1',
	 '0');">DNS/MAC only</a>) or <a onclick="javascript:alle_klappen('0',
	 '0');" href="#">Unexpand all</a>;
	 click on a <tt>[-]</tt> or <tt>[+]</tt> to toggle extra text.</p>
	<p>Note: on both FQDNs and PTR RRs, the DNS search suffix is cut off.</p>
	<script type="text/javascript"><!--//--><![CDATA[//><!--
	 function alle_klappen(dnsmac, etext) {
EOF
cat <<-EOF
	  for (var i = 1; i <= $nummern; ++i)
	   klappen(i, '', '', etext);
	  for (var i = 1; i < $revnr; ++i)
	   shrev(i, dnsmac);
	  for (var i = 1; i <= $tsnrn; ++i)
	   tsrev(i, etext);
EOF
cat <<-'EOF'
	 }

	 alle_klappen('0', '0');	// initially at page load
	//--><!]]></script>
	<hr />
	<h2>Legende</h2>
	<table style="border:medium outset violet; padding:3px;">
	<tr>
		<th>Colour</th>
		<th>IP/DNS/MAC</th>
		<th>FQDN</th>
		<th>Timestamp</th>
	</tr><tr>
		<td class="bwinverse">inverse</td>
		<td>-</td>
		<td>-</td>
		<td>no NTP; delta &gt; 30 seconds</td>
	</tr><tr>
		<td class="bwnormal">normal</td>
		<td>-</td>
		<td>normal system</td>
		<td>NTP delta &lt; 128 ms</td>
	</tr><tr>
		<td class="greyed">greyed out</td>
		<td>-</td>
		<td>-</td>
		<td>no time delta reported</td>
	</tr><tr>
		<td class="grey">grey</td>
		<td>DHCP</td>
		<td>DHCP</td>
		<td>no NTP; delta &lt; 30 seconds</td>
	</tr><tr>
		<td style="color:#CCCC00; background-color:#0000FF;">yellow/blue</td>
		<td>blue, older than 1 hour</td>
		<td>-</td>
		<td>-</td>
	</tr><tr>
		<td class="blue">blue</td>
		<td>flagged as “needs attention”</td>
		<td>-</td>
		<td>NTP delta &lt; 5 seconds</td>
	</tr><tr>
		<td class="green">green</td>
		<td>not flagged</td>
		<td>-</td>
		<td>NTP delta &lt; 500 ms</td>
	</tr><tr>
		<td class="yellow">yellow</td>
		<td>green, older than 1 hour</td>
		<td>short hostname not FQDN</td>
		<td>NTP delta &lt; 1 second</td>
	</tr><tr>
		<td class="orange">orange</td>
		<td>-</td>
		<td>broken FQDN, run mkhosts(1)</td>
		<td>NTP delta &lt; 1 minute</td>
	</tr><tr>
		<td class="red">red</td>
		<td>hard error in QUERY_STRING, or no MAC address found on eth0</td>
		<td>invalid hostname, run mkhosts(1) immediately</td>
		<td>NTP delta &gt; 1 minute</td>
	</tr>
	</table>
	<hr />
	<p style="font-size:small;">Generated by
	 <tt style="white-space:nowrap;">$Id: overview.cgi 4043 2014-05-23 09:35:30Z tglase $</tt></p>
	<div class="footer"><a href="http://validator.w3.org/check/referer"><img
	 src="http://www.w3.org/Icons/valid-xhtml11" alt="Valid XHTML 1.1"
	 style="border:0px;" height="31" width="88" /></a></div>
	</body></html>
EOF
exit 0
