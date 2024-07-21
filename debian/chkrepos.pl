#!/usr/bin/env perl
#-
# Copyright © 2024
#	mirabilos <t.glaser@qvest-digital.com>
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
# Check for nōn-identical duplicates across APT repositories. Usage:
# perl chkrepos.pl /var/lib/apt/lists/*_Packages
# perl chkrepos.pl /var/cache/pbuilder/base.cow*/var/lib/apt/lists/*_Packages

use Dpkg::Control::Hash;

my %pkgs = ();

foreach my $fn (@ARGV) {
	my $fh;
	open($fh, '<', $fn) or die "$!";
	while (!eof($fh)) {
		my $c = Dpkg::Control::Hash->new();
		$c->parse($fh, $fn) or die "$!";
		my $pv = $c->{'Package'} . '_' .
		    $c->{'Version'} . '_' . $c->{'Architecture'};
		my $ph = $c->{'Size'} . "\n\t";
		if (defined($c->{'SHA256'})) {
			$ph .= 'SHA256: ' . $c->{'SHA256'};
		} else {
			$ph .= 'MD5sum: ' . $c->{'MD5sum'};
		}
		push @{$pkgs{$pv}{$ph}}, $fn;
	}
	close($fh);
}

my @dups;

foreach my $pv (keys %pkgs) {
	next if (keys %{$pkgs{$pv}}) < 2;
	my $s;
	foreach my $h (keys %{$pkgs{$pv}}) {
		$s .= "DUP $pv (" . join(', ', @{${pkgs}{$pv}{$h}}) .
		    "):\n\tSize: " . $h . "\n";
	}
	push @dups, $s;
}

print join("\n", @dups);
