Hints for setting up dm-integrity devices (e.g. below each RAID member)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This documentation was prepared focussing on Debian bullseye,
which ships with the Linux kernel 5.10; starting with 5.4, if
you use standalone dm-integrity to protect each member of an
mdraid device, it can “self-heal” even silent data corruption.


Setup layouts
─────────────

dm-integrity can be set up within just one block device:

    <-/dev/sdX1----------------------------------------------->
    ┌──────────┬──────────────────────────────────────────────┐
    │ metadata │<-/dev/mapper/isdX1-------------------------->│
    └──────────┴──────────────────────────────────────────────┘

    (for format add --sector-size 4096 where appropriate)
    # integritysetup format /dev/sdX1
    # integritysetup --allow-discards open /dev/sdX1 isdX1

It can also be set up using two separate block devices:

    <-/dev/sdX2>   <-/dev/sdX3----------------------------------->
    ┌──────────┐   ┌─────────────────────────────────────────────┐
    │ metadata │   <-/dev/mapper/isdX3--------------------------->
    └──────────┘   └─────────────────────────────────────────────┘

    # integritysetup --data-device /dev/sdX3 format /dev/sdX2
    # integritysetup --data-device /dev/sdX3 […] open /dev/sdX2 isdX3
    (add --sector-size 4096 to format, --allow-discards to open)

In this split mode, the data written to /dev/mapper/isdX3 (the
integrity-protected device) is passed 1:1 to the underlying block
device (the partition /dev/sdX3 here), which is useful in some
scenarios:

• put a RAID 1 on /dev/mapper/isd{X,Y}3 and put /boot in there;
  GRUB can boot from RAID 1, and this way it won’t have to even
  consider the dm-integrity part, as it accesses /boot read-only

• put the metadata on a separate disc (perhaps SSD), so the
  slowdown from use of dm-integrity is less


Trouble with split setup
────────────────────────

As stated above, with split setup, other tools (like GRUB) can
access the data device without bothering with dm-integrity at
all. This is both an upside and a downside: if you ever boot a
rescue system (*or* don’t change your mdadm.conf) chances are
the RAID atop the integrity devices will be autoconfigured but
witho̲u̲t̲ the integrity protection below (which the next time it
does use the protection will cause errors to be shown as the
md superblock changed, of course, but this is a good test to
see that dm-integrity indeed works). GRUB also has trouble.

To fix these issues, do:

1. change your /etc/mdadm/mdadm.conf to only auto-assemble any
   devices with dm-integrity below (which, see above, we used
   a naming scheme starting with ‘i’ for, I use ‘c’ for LUKS):

   DEVICE /dev/mapper/i*
  … instead of the default
   #DEVICE partitions containers

   Real-world tests indicate that it’s better to not rely on
   auto-assembly (at all)…

   AUTO -all

   … and do assembly by hand, e.g. by using the doraid function
   in /etc/initramfs-tools/scripts/init-premount/dmintegrity.

2. When booting a rescue system ideally make it not assemble
   the RAIDs automatically (grml.org has a boot option named
   “forensic” for that). Unfortunately, the desire to be
   auto-assembled cannot be written into the superblock but,
   as a hack, a different --homehost could be used as well.

   Should they be accidentally configured then disassemble and
   reassemble them before mounting or otherwise writing:
   # mdadm --stop /dev/md126
   # mdadm --assemble /dev/md0 /dev/mapper/isd{X,Y}3

3. GRUB doesn’t add the modules needed to get to /boot into
   the core.img; your first boot will result in landing in its
   rescue mode. Unfortunately, there is no simple way to have
   it include extra modules into core.img but this works:

   - rename the original grub-install:
     # dpkg-divert --rename --divert /usr/sbin/grub-install.ORIG \
           --add /usr/sbin/grub-install
   - create a new shell script named /usr/sbin/grub-install with:

     #!/bin/sh
     mods='diskfilter biosdisk part_msdos part_gpt mdraid1x lvm ext2'
     set -x
     exec /usr/sbin/grub-install.ORIG --modules="$mods" "$@"

   - (you might want to add different ones, these cover common setups)
   - # chown 0:0 /usr/sbin/grub-install; chmod 755 /usr/sbin/grub-install
   - re-run “dpkg-reconfigure -plow grub-pc” to choose which
     devices should be made bootable (ideally, at least all
     that participate in the /boot RAID) and to let it redo
     the GRUB installation


Sizing metadata
───────────────

This is unfortunately a h̲a̲r̲d̲ problem. This repository provides
two useful programs which contain a reproduction of the sizing
code from Linux 5.10, under the following assumptions:

• split setup (--data-device used)
• no fancy options other than --tag-size and --sector-size
  ⇒ defaults (journal mode, etc. used for anything else)
• internal integrity calculation, with either the default
  (--integrity crc32c --tag-size 4) settings or one of the
  hash algorithms, optionally truncated; HMAC is untested

The isize-q program takes exactly one argument, the path to an
already formatted dm-integrity metadata device (split setup),
and tells its guess of that device’s maximum used extent.

(Note that, if a metadata device is too small, the formatting
will not succeed, so no data will be lost in that case.)

The isize-p script takes a (mandatory) argument, which is the
data (not metadata) device, either as full path or just its
numeric size in 512-byte sectors, as well as two optional
arguments, the tag size (4 for crc32c, more for hashes, but you
can truncate hashes, e.g. use 8 for sha1), and the sectors per
block (i.e. 1 for 512-byte sectors and 8 for “4K” discs). It then
compiles a C program (you need ${CC:-cc}) which calculates the
minimum needed metadata size for the current CPU architecture.

So, to summarise, the following options can be given at format time:

• --data-device /dev/sdXn (to enable split setup)
• --sector-size 4096
• --integrity ALGO [--tag-size n]

Note that --data-device, --integrity and --tag-size must be passed
at open time as well if they were used at format time (dm-integrity
only stores insufficient information in the superblock). At open
time, --allow-discards can also be given (and probably should).


Having the root device on dm-integrity protected devices
────────────────────────────────────────────────────────

A useful setup is this:

/boot separate, see above for a useful setup for that.

A number of hard discs, with same-sized partitions each; each
of the partitions becomes its own dm-integrity device; all those
dm-integrity devices are combined, e.g. into RAID 1, or perhaps
a Linux raid10 in “offset” mode with n-1 or n-2 (n is the number
of discs) copies to simulate RAID 5/6 more performantly. Then,
one’d usually put the /dev/mdX into LUKS, create an LVM PV on that
LUKS device, and create the root LV, as well as other filesystems
or VM guest discs needed, in that LVM VG made from that one PV. Of
course, YMMV; in this section, the need to boot where root is on
a dm-integrity device, either directly or not (layered as above).

In Debian, initramfs-utils handle setup of many possible layers
automatically: LVM is scanned automatically, mdraid are assembled,
and for LUKS the crypttab is copied to the initrd and the user is
asked for the password (keyfiles are copied). However, there is no
integritytab equivalent for crypttab, so manual setup is needed.

For simplicity, use of an integritytab device was rejected in favour
of an easy-to-edit shell script that can be used to open all (stand‐
alone) dm-integrity targets needed for the system to boot. (If there
are others besides what’s needed for root you best start them from it
as well, as no initscripts or systemd units exist to start them later
either. This, of course, is mostly only possible if they are located
(as partitions) on devices available during early boot; network block
devices are possible but h̲a̲r̲d̲ and thus not in scope here.)

To begin with:

• add a line “dm_integrity” to /etc/initramfs-tools/modules so the
  necessary kernel module is even available (it is not in d-i’s rescue…)
• copy the lcl-integrity script to /etc/initramfs-tools/hooks/ and
  chown 0:0, chmod 755 it; it ensures the integritysetup binary will
  be available in the initrd
• edit the dmintegrity script: erase the iopen example lines 27/28
  and add new ones that match your setup; the format is…
  “iopen <TARGET> <DEVICE> [<OPTIONS>]”
  … where TARGET is the thing you want under /dev/mapper/ and DEVICE
  is the metadata (or combined) block device; OPTIONS as needed for
  open (see above); for example, you could use…
     iopen isdX1 /dev/sdX1 --allow-discards
     iopen isdX3 /dev/sdX2 --allow-discards --data-device /dev/sdX3
  … for the examples at the top. However, /dev/sdX names are not
  stable (adding another HDD to a VM can move them), so it is better
  in general to use UUIDs (or LABELs) for identification; sadly, a
  dm-integrity metadata device has neither, so we must use PARTUUID
  and hope they are unique in the system; obtain them via “blkid”
  (nnnnnnnn-nn scheme for MBR, UUID for GPT partitions, etc.) then
  copy the edited script to the following path, again 0:0 chmod 755:
  /etc/initramfs-tools/scripts/init-premount/dmintegrity
• run update-initramfs to regenerate the initrd

Note the script is written so that the devices are started one after
another and that any errors are not fatal, so you can see problems
on the screen (or serial console).


TRIM (discards) — side note
───────────────

It is usually good tone to pass discards through the block device
stack, so I have included it with the examples. mdraid levels 1,
10, and others also pass through discards; for LVM edit the file
/etc/lvm/lvm.conf and change issue_discards = 1 (also useful to
change archive = 0 while here if you use etckeeper / restic), and
add the “discard” keyword to column 4 (options) for each device
in /etc/crypttab unless you need the extra obscurity that comes
from not using it. “lsblk -D” shows whether they’re capable.


dm-integrity with LVM RAID
──────────────────────────

Users are reporting that they have trouble booting this; it needs
the initramfs scripts for setting up as well.


dm-integrity with LUKS
──────────────────────

LUKS can protect data integrity using (nōn-standalone) dm-integrity
as well (the AUTHENTICATED DISK ENCRYPTION (EXPERIMENTAL) section in
the manual page). This applies to the encrypted device (the integrity
tags are even authenticated) and has better performance (only one copy
of the data is hashed all the time) but cannot be used to make a RAID
self-healing because it sits on top, not below, the RAID and directly
in the LUKS layer. If this level of protection is desired I’d recommend
using both (standalone) dm-integrity below RAID (for self-healing) and
(integrated) dm-integrity in LUKS (for authentication of the encrypted
data) and accept the resulting performance cost.

Note the LUKS-integrated dm-integrity can be started by cryptsetup and
therefore does NOT need integritysetup nor the initramfs scripts. (If
both are used the standalone part of course does need them.)
