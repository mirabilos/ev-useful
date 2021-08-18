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

// https://github.com/tarent/hello-php-world/blob/master/common/minijson.php
require_once(dirname(__FILE__) . '/minijson.php');

/* return value, error handling functions */
$rv = 0;
function warnx($msg, $extra=false) {
	global $rv;
	if ($extra !== false)
		$msg .= ': ' . minijson_encode($extra);
	fwrite(STDERR, 'E: ' . $msg . "\n");
	if (!$rv)
		$rv = 1;
}
function checkAccumulatedErrors() {
	global $rv;
	if ($rv)
		exit($rv);
}
function errx($msg, $extra=false) {
	warnx($msg, $extra);
	checkAccumulatedErrors();
}

/* slurp files; cwd must be git@github.com:w3c/smufl checkout */
$Icls = file_get_contents('metadata/classes.json');
if ($Icls === false)
	errx("file_get_contents('metadata/classes.json')");
$Inam = file_get_contents('metadata/glyphnames.json');
if ($Inam === false)
	errx("file_get_contents('metadata/glyphnames.json')");

/* decode files */
if (!minijson_decode($Icls, $icls))
	errx('minijson_decode classes', array(
		'input' => $Icls,
		'message' => $icls,
	    ));
if (!minijson_decode($Inam, $inam))
	errx('minijson_decode names', array(
		'input' => $Inam,
		'message' => $inam,
	    ));

/* generate output classes: glyphname ⇒ list (later sorted) of classes */
$ocls = array();
foreach (array_keys($icls) as $Ncls) {
	if (!($ncls = strval($Ncls)))
		warnx('class?', $Ncls);
	foreach ($icls[$ncls] as $Nam) {
		if (!($nam = strval($Nam)))
			warnx('class member?', array($ncls => $Nam));
		if (!isset($ocls[$nam]))
			$ocls[$nam] = array();
		$ocls[$nam][] = $ncls;
	}
}
/* and sort them */
foreach (array_keys($ocls) as $nam) {
	if (!sort($ocls[$nam], SORT_STRING))
		warnx('sort', $ocls[$nam]);
}
checkAccumulatedErrors();

/* convert {,U+,U-}nnn to UCS codepoint standard notation */
function normaliseCodepoint($n, $cn) {
	global $inam;

	/* absence of (alternate) codepoint? */
	if (!isset($inam[$n][$cn]))
		return ('');
	$cp = strval($inam[$n][$cn]);
	/* remove præfix if present (it was not in a very old revision) */
	if (($c = preg_replace('/^[Uu][+-]/', '', $cp)) === null)
		errx('preg_replace UCS', $cp);
	/* ensure hex number */
	if (!preg_match('/^0*[0-9a-fA-F]{1,5}$/', $c))
		errx('preg_match UCS', array(
			'Name' => $n,
			'input' => $inam[$n],
			'p' => $c,
		    ));
	/* parse hex number */
	$n = hexdec($c);
	/* type and range check; we deliberately disallow U+0000 */
	if (!is_int($n) || $n < 1 || $n > 0x10FFFF)
		errx('hexdec', array(
			'Name' => $n,
			'input' => $inam[$n],
			'pin' => $c,
			'pnum' => $n,
		    ));
	/* render as UCS codepoint standard notation */
	return (sprintf(($n < 0x10000) ? 'U+%04X' : 'U-%08X', $n));
}

/* possibly emit link at regular codepoint position */
function process_alternateCodepoint($nam, $code, $alt, $body) {
	global $hit;
	global $inam;

	/* cf. https://github.com/w3c/smufl/issues/195 (and 133) */
	if ($nam === 'mensuralBlackSemibrevisVoid' && $alt === 'U-0001D1B9')
		return (0);
	if ($nam === 'mensuralWhiteSemiminima' && $alt === 'U-0001D1BC')
		return (0);
	if ($nam === 'mensuralNoteheadMaximaVoid' && $alt === 'U-0001D1B6')
		return (0);
	if ($nam === 'mensuralNoteheadLongaVoid' && $alt === 'U-0001D1B7')
		return (0);
	if ($nam === 'mensuralNoteheadSemibrevisBlack' && $alt === 'U-0001D1BA')
		return (0);
	if ($nam === 'mensuralNoteheadSemibrevisVoid' && $alt === 'U-0001D1B9')
		return (0);

	/* duplicate check */
	if (isset($hit[$alt]))
		warnx('duplicate', array(
			'alt' => $alt,
			't1' => $hit[$alt],
			't2' => array($nam => $inam[$nam]),
		    ));
	else
		$hit[$alt] = array($nam => $inam[$nam]);
	/* output line */
	printf("%s\t%s [SMuFL:alternateCodepoint] (cf. %s)\n",
	    $alt, $body, $code);
	return (1);
}

/* duplicate codepoint check */
$hit = array();
/* process all glyphnames */
foreach (array_keys($inam) as $Nam) {
	if (!($nam = strval($Nam)))
		warnx('name?', $Nam);
	if (!isset($inam[$nam]['description']))
		$desc = '';
	else
		$desc = strval($inam[$nam]['description']);
	/* fix stray spaces in historic data */
	if (($desc = preg_replace("/[ \n\r\t\v]+/", ' ', $desc)) === null)
		errx('preg_replace desc', array($nam => $inam[$nam]));
	if (!($desc = trim($desc)))
		warnx('missing description', array($nam => $inam[$nam]));
	/* collect wtf RHS */
	$body = '';
	/* tag (omit just [SMuFL] since they all have at least one) */
	if (!isset($ocls[$nam]))
		$body .= '[SMuFL:classless] ';
	else
		foreach ($ocls[$nam] as $ncls)
			$body .= sprintf('[SMuFL:class:%s] ', $ncls);
	/* glyphname and (quoted) description */
	$body .= $nam . ' “' . $desc . '”';
	/* codepoint and alternate */
	if (!($code = normaliseCodepoint($nam, 'codepoint')))
		errx('no codepoint', array($nam => $inam[$nam]));
	if (($alt = normaliseCodepoint($nam, 'alternateCodepoint'))) {
		if (process_alternateCodepoint($nam, $code, $alt, $body))
			$body .= ' (cf. ' . $alt . ')';
	}
	/* duplicate check */
	if (isset($hit[$code]))
		warnx('duplicate', array(
			'code' => $code,
			't1' => $hit[$code],
			't2' => array($nam => $inam[$nam]),
		    ));
	else
		$hit[$code] = array($nam => $inam[$nam]);
	/* and emit main wtf line */
	printf("%s\t%s\n", $code, $body);
}
checkAccumulatedErrors();
