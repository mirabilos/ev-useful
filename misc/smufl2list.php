<?php
/*-
 * Copyright © 2021
 *	mirabilos <m@mirbsd.org>
 *
 * Provided that these terms and disclaimer and all copyright notices
 * are retained or reproduced in an accompanying document, permission
 * is granted to deal in this work without restriction, including un‐
 * limited rights to use, publicly perform, distribute, sell, modify,
 * merge, give away, or sublicence.
 *
 * This work is provided “AS IS” and WITHOUT WARRANTY of any kind, to
 * the utmost extent permitted by applicable law, neither express nor
 * implied; without malicious intent or gross negligence. In no event
 * may a licensor, author or contributor be held liable for indirect,
 * direct, other damage, loss, or other issues arising in any way out
 * of dealing in the work, even if advised of the possibility of such
 * damage or existence of a defect, except proven that it results out
 * of said person’s immediate fault when using the work as intended.
 *-
 * Parse SMuFL metadata and output wtf(1) lines.
 */

require_once('/home/tglase/Misc/Vendor/hello-php-world/common/minijson.php');

function bla($msg, $extra=false) {
	if ($extra !== false)
		$msg .= ': ' . minijson_encode($extra);
	fwrite(STDERR, 'E: ' . $msg . "\n");
	exit(1);
}

$rv = 0;
function blub($msg, $extra=false) {
	global $rv;
	if ($extra !== false)
		$msg .= ': ' . minijson_encode($extra);
	fwrite(STDERR, 'E: ' . $msg . "\n");
	$rv = 1;
}
function chk() {
	global $rv;
	if ($rv)
		exit($rv);
}

$Icls = file_get_contents('/tmp/smufl/metadata/classes.json');
if ($Icls === false)
	bla("file_get_contents('/tmp/smufl/metadata/classes.json')");
$Inam = file_get_contents('/tmp/smufl/metadata/glyphnames.json');
if ($Inam === false)
	bla("file_get_contents('/tmp/smufl/metadata/glyphnames.json')");

if (!minijson_decode($Icls, $icls))
	bla('minijson_decode classes', array(
		'input' => $Icls,
		'message' => $icls,
	    ));
if (!minijson_decode($Inam, $inam))
	bla('minijson_decode names', array(
		'input' => $Inam,
		'message' => $inam,
	    ));

$ocls = array();
foreach (array_keys($icls) as $ncls) {
	foreach ($icls[$ncls] as $nam) {
		if (!isset($ocls[$nam]))
			$ocls[$nam] = array();
		$ocls[$nam][] = $ncls;
	}
}
chk();
foreach (array_keys($ocls) as $nam) {
	if (!sort($ocls[$nam], SORT_STRING))
		bla('sort', $ocls[$nam]);
}

function norm($n, $cp) {
	global $inam;

	$c = preg_replace('/^[Uu][+-]/', '', $cp);
	if (!$c)
		return '';
	if (!preg_match('/^0*[0-9a-fA-F]{1,5}$/', $c))
		bla('preg_match', array(
			'Name' => $n,
			'input' => $inam[$n],
			'p' => $c,
		));
	$n = hexdec($c);
	if ($n < 1 || $n > 0x10FFFF)
		bla('hexdec', array(
			'Name' => $n,
			'input' => $inam[$n],
			'pin' => $c,
			'pnum' => $n,
		));
	return sprintf(($n < 0x10000) ? 'U+%04X' : 'U-%08X', $n);
}

$hit = array();
foreach (array_keys($inam) as $nam) {
	$tag = '[SMuFL]';
	if (!isset($ocls[$nam])) {
		$tag .= ' [SMuFL:classless]';
	} else {
		foreach ($ocls[$nam] as $ncls)
			$tag .= sprintf(' [SMuFL:class:%s]', $ncls);
	}
	$desc = $nam . ' “' . $inam[$nam]['description'] . '”';
	$code = norm($nam, $inam[$nam]['codepoint']);
	$alt = norm($nam, isset($inam[$nam]['alternateCodepoint']) ? $inam[$nam]['alternateCodepoint'] : '');
	if ($alt) {
		if (isset($hit[$alt]))
			blub('duplicate', array(
				'alt' => $alt,
				't1' => $hit[$alt],
				't2' => array($nam => $inam[$nam]),
			));
		$hit[$alt] = array($nam => $inam[$nam]);
		printf("%s\t%s %s (cf. %s)\n", $alt, $tag, $desc, $code);
		$desc .= ' (cf. ' . $alt . ')';
	}
	if (isset($hit[$code]))
		blub('duplicate', array(
			'code' => $code,
			't1' => $hit[$code],
			't2' => array($nam => $inam[$nam]),
		));
	$hit[$code] = array($nam => $inam[$nam]);
	printf("%s\t%s %s\n", $code, $tag, $desc);
}
chk();
