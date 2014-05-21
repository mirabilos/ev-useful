# $Id: findmail.pl 824 2010-01-15 13:28:47Z tglase $
#-
# Copyright © 2009
#	Thorsten Glaser <t.glaser@tarent.de>
# All rights reserved.
#-
# Derived from Email::Find 0.10
#
# Copyright 2000, 2001 Michael G Schwern <schwern@pobox.com>.
# All rights reserved.
#
# Current maintainer is Tatsuhiko Miyagawa <miyagawa@bulknews.net>.
#
# This module is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.

use strict;

# Need qr//.
require 5.005;

# This is the BNF from RFC 822
my $esc         = '\\\\';
my $period      = '\.';
my $space       = '\040';
my $open_br     = '\[';
my $close_br    = '\]';
my $nonASCII    = '\x80-\xff';
my $ctrl        = '\000-\037';
my $cr_list     = '\n\015';
my $qtext       = qq/[^$esc$nonASCII$cr_list\"]/; #"
my $dtext       = qq/[^$esc$nonASCII$cr_list$open_br$close_br]/;
my $quoted_pair = qq<$esc>.qq<[^$nonASCII]>;
my $atom_char   = qq/[^($space)<>\@,;:\".$esc$open_br$close_br$ctrl$nonASCII]/; #"
my $atom        = qq<$atom_char+(?!$atom_char)>;
my $quoted_str  = qq<\"$qtext*(?:$quoted_pair$qtext*)*\">; #"
my $word        = qq<(?:$atom|$quoted_str)>;
my $local_part  = qq<$word(?:$period$word)*>;

# This is a combination of the domain name BNF from RFC 1035 plus the
# domain literal definition from RFC 822, but allowing domains starting
# with numbers.
my $label       = q/[A-Za-z\d](?:[A-Za-z\d-]*[A-Za-z\d])?/;
my $domain_ref  = qq<$label(?:$period$label)*>;
my $domain_lit  = qq<$open_br(?:$dtext|$quoted_pair)*$close_br>;
my $domain      = qq<(?:$domain_ref|$domain_lit)>;

# Finally, the address-spec regex (more or less)
my $Addr_spec_re   = qr<$local_part\s*\@\s*$domain>;

sub matched {
	my $orig_match = $1;
	my $end_cruft = '';
	if( $orig_match =~ s|([),.'";?!]+)$|| ) { #"')){
		$end_cruft = $1;
	}
	print $orig_match."\n";
	$end_cruft;
}

while (<>) {
    my $r_text = $_;

    $r_text =~ s{($Addr_spec_re)}{
	matched($1);
    }eg;
}
