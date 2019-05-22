<?php

/* does the parameter match the IP-literal or IPv4address production of RFC 3986? */
function isIPaddress($s) {
	if (($chk = preg_match('/
		(?(DEFINE)
		    (?<h16> [0-9A-Fa-f]{1,4} )
		    (?<ls32> (?: (?&h16) : (?&h16) | (?&IPv4address) ) )
		    (?<IPv6address> (?:
		                                              (?: (?&h16) : ){6} (?&ls32) |
		                                           :: (?: (?&h16) : ){5} (?&ls32) |
		        (?:                     (?&h16) )? :: (?: (?&h16) : ){4} (?&ls32) |
		        (?: (?: (?&h16) :){0,1} (?&h16) )? :: (?: (?&h16) : ){3} (?&ls32) |
		        (?: (?: (?&h16) :){0,2} (?&h16) )? :: (?: (?&h16) : ){2} (?&ls32) |
		        (?: (?: (?&h16) :){0,3} (?&h16) )? ::     (?&h16) :      (?&ls32) |
		        (?: (?: (?&h16) :){0,4} (?&h16) )? ::                    (?&ls32) |
		        (?: (?: (?&h16) :){0,5} (?&h16) )? ::                    (?&h16) |
		        (?: (?: (?&h16) :){0,6} (?&h16) )? :: )
		    )
		    (?<sub_delims> [!$&' . "'" . '()*+,;=] )
		    (?<unreserved> [A-Za-z0-9._~-] )
		    (?<IPvFuture> v [0-9A-Fa-f]+ \. (?: (?&unreserved) | (?&sub_delims) | : ) )
		    (?<IP_literal> \[ (?: (?&IPv6address) | (?&IPvFuture) ) \] )
		    (?<dec_octet> [0-9] | [1-9][0-9] | 2[0-4][0-9] | 25[0-5] )
		    (?<IPv4address> (?&dec_octet) \. (?&dec_octet) \. (?&dec_octet) \. (?&dec_octet) )
		)
		^(?: (?&IP_literal) | (?&IPv4address) )$
	    /x', $s)) === false)
		throw new \Exception('Internal pcre error: ' . preg_last_error());
	elseif ($chk /* regexp matched */)
		return (true);
	else
		return (false);
}
