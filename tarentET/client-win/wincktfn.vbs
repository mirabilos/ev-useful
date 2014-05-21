' $Id: wincktfn.vbs 3875 2013-12-11 13:39:34Z tglase $
' -
' Copyright (c) 2011, 2012, 2013
'	Thorsten Glaser <t.glaser@tarent.de>
'
' Provided that these terms and disclaimer and all copyright notices
' are retained or reproduced in an accompanying document, permission
' is granted to deal in this work without restriction, including un-
' limited rights to use, publicly perform, distribute, sell, modify,
' merge, give away, or sublicence.
'
' This work is provided "AS IS" and WITHOUT WARRANTY of any kind, to
' the utmost extent permitted by applicable law, neither express nor
' implied; without malicious intent or gross negligence. In no event
' may a licensor, author or contributor be held liable for indirect,
' direct, other damage, loss, or other issues arising in any way out
' of dealing in the work, even if advised of the possibility of such
' damage or existence of a defect, except proven that it results out
' of said person's immediate fault when using the work as intended.

debg = False
vsn = "$Revision: 3875 $"

set re = new regexp
re.pattern = "^.* ([0-9]*) .*$"
set matches = re.execute(vsn)
vsn = matches(0).submatches(0)

function regread(ByRef wss, key)
	on error resume next
	res = ""
	res = trim(wss.RegRead(key))
	regread = res
end function

function getescaped(intro, dbgas, values)
	on error resume next
	res = ""
	for each value in values
		if debg then wscript.echo dbgas, value
		if trim(value) <> "" then res = res + intro + escape(value)
	next
	getescaped = res
end function

function gettimezone()
	gesetzt = 0
	for each os in GetObject("winmgmts:").InstancesOf("Win32_OperatingSystem")
		z = os.CurrentTimeZone
		if z < 0 then
			tz = "-"
			z = -z
		else
			tz = "+"
		end if
		tz = tz + right("00" & (z / 60), 2) + right("00" & (z mod 60), 2)
		if gesetzt = 0 then gettimezone = tz : gesetzt = 1
	next
	if gesetzt = 0 then gettimezone = "(unknown time zone)"
end function

function shl(ByVal ax, cl)
	for i=1 to cl
		ax = ax * 2
	next
	shl = ax
end function

function shr(ByVal ax, cl)
	for i=1 to cl
		ax = ax \ 2
	next
	shr = ax
end function

function urlhex(c)
	if c < 16 then res = "%0" else res = "%"
	urlhex = res + hex(c)
end function

function urlstr(s)
	res = ""
	for i = 1 to len(s)
		c = mid(s, i, 1)
		wc = ascW(c)

		' Interesting brokenness: ascW returns signed short
		if wc < 0 then wc = wc + 65536

		if wc < 128 then
			res = res + escape(c)
		elseif wc < 2048 then
			c1 = shr(wc, 6) or &hC0
			c2 = (wc and &h3F) or &h80
			res = res + urlhex(c1) + urlhex(c2)
		else
			c1 = shr(wc, 12) or &hE0
			c2 = (shr(wc, 6) and &h3F) or &h80
			c3 = (wc and &h3F) or &h80
			res = res + urlhex(c1) + urlhex(c2) + urlhex(c3)
		end if
	next
	urlstr = res
end function

argstr = "tarent-windows r" + vsn
blau = ""

set wss = CreateObject("WScript.Shell")

osver = regread(wss, "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProductName")
if left(osver, 10) = "Microsoft " then osver=mid(osver, 11)
osrev = regread(wss, "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\CurrentVersion")
osver = osver + " (" + osrev
osver = osver + ", " + regread(wss, "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\CSDVersion")
osver = osver + ")"

set WshNetwork = CreateObject("WScript.Network")
set WMIService = GetObject("winmgmts:!\\.\root\cimv2")

gesetzt = 0
set processors = WMIService.ExecQuery("SELECT * FROM Win32_Processor")
for each cpu in processors
	if gesetzt = 0 then
		select case cpu.architecture
		case 0
			argstr = argstr + " (i386)"
			gesetzt = 1
		case 1
			argstr = argstr + " (mips)"
			gesetzt = 1

		case 2
			argstr = argstr + " (alpha32)"
			gesetzt = 1

		case 3
			argstr = argstr + " (powerpc)"
			gesetzt = 1

		case 4
			argstr = argstr + " (shx)"
			gesetzt = 1

		case 5
			argstr = argstr + " (arm)"
			gesetzt = 1

		case 6
			argstr = argstr + " (IA64)"
			gesetzt = 1
		case 7
			argstr = argstr + " (alpha)"
			gesetzt = 1

		case 8
			argstr = argstr + " (MSIL)"
			gesetzt = 1

		case 9
			argstr = argstr + " (amd64)"
			gesetzt = 1
		case 10
			argstr = argstr + " (ia32w64)"
			gesetzt = 1

		end select
	end if
next
if gesetzt = 0 then argstr = argstr + " (unknown)"

argstr = argstr + "%0A" + osver + "%0A"
if debg then wscript.echo "Running on:", osver

argstr = argstr + "%0Acurrent time%09" + FormatDateTime(Now()) + " " + gettimezone()

ntpsvr = regread(wss, "HKLM\SYSTEM\CurrentControlSet\Services\W32Time\Parameters\NtpServer")
if ntpsvr <> "" then argstr = argstr + "%0ANTP Server%09" + ntpsvr

if debg then wscript.echo "NTP Server:", ntpsvr

check_antivir = 0
if check_antivir <> 0 then
	avversion = ""
	gesetzt = regread(wss, "HKLM\SOFTWARE\Avira\AntiVir Server\EngineVersion")
	if gesetzt <> "" then avversion = "Server Native " + gesetzt
	if avversion = "" then
		gesetzt = regread(wss, "HKLM\SOFTWARE\Wow6432Node\Avira\AntiVir Server\EngineVersion")
		if gesetzt <> "" then avversion = "Server W32oW64 " + gesetzt
	end if
	if avversion = "" then
		gesetzt = regread(wss, "HKLM\SOFTWARE\Avira\AntiVir Desktop\EngineVersion")
		if gesetzt <> "" then avversion = "Desktop Native " + gesetzt
	end if
	if avversion = "" then
		gesetzt = regread(wss, "HKLM\SOFTWARE\Wow6432Node\Avira\AntiVir Desktop\EngineVersion")
		if gesetzt <> "" then avversion = "Desktop W32oW64 " + gesetzt
	end if
	if avversion = "" then
		avversion = "not installed"
		blau = "!"
	end if
	argstr = argstr + "%0AH+BEDV AntiVir%09" + avversion
end if

set netconfigs = WMIService.ExecQuery("SELECT * FROM Win32_NetworkAdapterConfiguration WHERE IPEnabled=True")

hn = WshNetwork.ComputerName
mac = ""

dim ipaddrs()
dim netmsks()
for each nic in netconfigs
	if mac = "" then mac = nic.MACAddress
	argstr = argstr + "%0A%0A" + urlstr(nic.caption)
	argstr = argstr + "%0All address%09" + escape(nic.MACAddress)
	if debg then wscript.echo nic.MACAddress + " " + nic.caption
	ips = 0
	nms = 0
	for each ip in nic.IPAddress
		ips = ips + 1
		redim preserve ipaddrs(ips)
		ipaddrs(ips) = ip
		if debg then wscript.echo "IP#", ips, "= " + ip
	next
	for each ip in nic.IPSubnet
		nms = nms + 1
		redim preserve netmsks(nms)
		netmsks(nms) = ip
		if debg then wscript.echo "NM#", nms, "= " + ip
	next
	for i = 1 to ips
		if ipaddrs(i) <> "" then
			argstr = argstr + "%0AIP/netmask%09"
			nm = ""
			if i <= nms then nm = " / " + escape(netmsks(i))
			argstr = argstr + escape(ipaddrs(i)) + nm
		end if
	next
	argstr = argstr + getescaped("%0Adefault gw%09", "GW", nic.DefaultIPGateway)
	argstr = argstr + "%0ADHCP used?%09" + escape(nic.DHCPEnabled)
next

tzofs = regread(wss, "HKLM\System\CurrentControlSet\Control\TimeZoneInformation\ActiveTimeBias")
utnow = DateAdd("n", tzofs, Now())

uri = "http://reportingsystem.tarent.de/cgi-bin/report.cgi?8,"
uri = uri & DateDiff("s", "01/01/1970 00:00:00", utnow)
uri = uri + "/,0,4,WinNT:" + osrev + ","
uri = uri + mac + "," + blau + hn + "," + argstr

set hr = CreateObject("WinHttp.WinHttpRequest.5.1")
hr.open "GET", uri
hr.SetCredentials "httpbasicauthuser", "httpbasicauthpass", 0
hr.send
wscript.echo hr.ResponseText
wscript.quit
