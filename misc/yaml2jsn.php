<?php
/*-
 * Copyright © 2012, 2017
 *	mirabilos <t.glaser@tarent.de>
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
 */

error_reporting(-1);
require_once(dirname(__FILE__) . '/minijson.php');

function croak($msg) {
	fprintf(STDERR, "E: %s\n", $msg);
	exit(2);
}

function fwrite_all($fh, $str) {
	$slen = strlen($str);
	$done = 0;
	while ($done < $slen) {
		if (($x = fwrite($fh, substr($str, $done))) === false)
			croak("write error");
		$done += $x;
	}
}

function array_sort_all_by_json($x) {
	if (!is_array($x))
		return $x;

	$k = array_keys($x);
	$isnum = true;
	foreach ($k as $v) {
		if (is_int($v)) {
			$y = (int)$v;
			$z = (string)$y;
			if ($v != $z) {
				$isnum = false;
				break;
			}
		} else {
			$isnum = false;
			break;
		}
	}

	if ($isnum) {
		/* all array keys are integers */
		$s = $k;
		sort($s, SORT_NUMERIC);
		/* test keys for order and delta */
		$y = 0;
		foreach ($s as $v) {
			if ($v != $y) {
				$isnum = false;
				break;
			}
			$y++;
		}
	}

	if ($isnum)
		sort($k, SORT_NUMERIC);
	else
		sort($k, SORT_STRING);

	$r = array();
	foreach ($k as $v) {
		$r[$v] = array_sort_all_by_json($x[$v]);
	}
	return $r;
}

$indoc = file_get_contents("php://stdin");
if (!$indoc)
	croak("no input");

$numdocs = -666;
if (($in = yaml_parse($indoc, 0, $numdocs)) === false || $numdocs === -666)
	croak("could not parse input document as YAML");
if ($numdocs !== 1)
	croak("found $numdocs documents but can only handle a single one");
$in = array_sort_all_by_json($in);

$jsn = minijson_encode($in) . "\n";
fwrite_all(STDOUT, $jsn);

if (($out = yaml_parse($jsn)) === false)
	croak("could not reparse JSON output as YAML");

if (($rein = yaml_emit($in, YAML_UTF8_ENCODING, YAML_LN_BREAK)) === false)
	croak("could not emit input document as YAML");
if (($reout = yaml_emit($out, YAML_UTF8_ENCODING, YAML_LN_BREAK)) === false)
	croak("could not emit output document as YAML");
if ($rein === $reout)
	exit(0);

fwrite(STDERR, "E: documents do not emit identical; delta:\n");
$pipes = array();
if (($p = proc_open("diff -u /dev/fd/5 /dev/fd/6", array(
	0 => array("file", "/dev/null", "r"),
	1 => STDERR,
	2 => STDERR,
	5 => array("pipe", "r"),
	6 => array("pipe", "r"),
    ), $pipes)) === false)
	croak("could not spawn diff(1)");
fwrite_all($pipes[5], $rein . "\n");
fwrite_all($pipes[6], $reout . "\n");
fclose($pipes[5]);
fclose($pipes[6]);
$rv = proc_close($p);
if ($rv === -1)
	croak("unknown error closing diff(1) subprocess");
if ($rv === 0)
	croak("diff(1) did not detect any changes");
if ($rv !== 1)
	croak("diff(1) encountered an errorlevel $rv");
exit(1);
