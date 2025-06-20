/* © 2023 mirabilos Ⓕ CC0 or MirBSD */

/* gcc -O2 -Wall -Wextra -D_GNU_SOURCE -Iinc -o sd-test sd-test.c ;#*/

#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "mbsdcc.h"
#include "mbsdint.h"
#include "port-cdefs.h"

#include "arcfour_base.c"
#include "arcfour_ksa.c"
/*#include "hdump.c"*/

#define KiB		(1024UL)
#define MiB		(1024UL * 1024UL)
#define GiB		(1024UL * 1024UL * 1024UL)

#define myF_GM		"%llu GiB + %u MiB"
#define myF_GB		"%llu GiB + %u MiB + %u bytes"
#define myA_GM(x)	(x) / GiB, (unsigned)(((x) % GiB) / MiB)
#define myA_GB(x)	(x) / GiB, (unsigned)(((x) % GiB) / MiB), (unsigned)((x) % MiB)

#define MYBUFLEN	(32ULL * MiB)

static uint8_t xbuf[MYBUFLEN] __attribute__((__aligned__(262144)));

static const char *progname;

static __dead void
usage(void)
{
	fprintf(stderr, "Usage:	./%s write «size» '«passkey»' /dev/sdX"
			"\n	./%s check «size» '«passkey»' /dev/sdX"
	    "\n", progname, progname);
	fprintf(stderr,
	    "    Where «size» is in KiB (e.g. from /proc/partitions third column)\n"
	    "    and «passkey» is an up-to-256-octet-long arbitrary string\n"
	    "    used in generation and comparison so a drive cannot cheat.\n");
	fflush(stderr);
	exit(2);
}

static const char val_answer[] = "Yes\n";

int
main(int argc, char *argv[])
{
	unsigned long long i, z, tot;
	unsigned long long nbytes;
	struct arcfour_status c;
	int fd;
	ssize_t s;
	char *cp = NULL;
	struct stat sb;

	progname = argc > 0 && argv[0] ? argv[0] : "sd-test";
	if (strrchr(progname, '/') != NULL)
		progname = strrchr(progname, '/') + 1U;

	if ((mbiHUGE_U)MYBUFLEN > (mbiHUGE_U)SIZE_MAX ||
	    (mbiHUGE_U)MYBUFLEN > (mbiHUGE_U)INT_MAX) {
		fprintf(stderr, "E: MYBUFLEN too large\n");
		return (255);
	}

	/* parse command line */

	if (argc != 5)
		usage();

	errno = 0;
	i = strtoull(argv[2], &cp, 0);
	if (cp == argv[2] || *cp != '\0' || errno ||
	    i < 1ULL || i > (ULLONG_MAX / 1024ULL)) {
		fprintf(stderr,
		    "E: could not parse KiB <%s> or too small/large\n",
		     argv[2]);
		usage();
	}
	nbytes = i * 1024ULL;

	if (argv[3][0] == '\0') {
		fprintf(stderr, "E: empty passkey\n");
		usage();
	}

	if (strcmp(argv[4], "-")) {
		if (stat(argv[4], &sb)) {
			fprintf(stderr, "E: could not stat %s: %s\n",
			    argv[4], strerror(errno));
			usage();
		}
		switch (sb.st_mode & S_IFMT) {
		case S_IFBLK:
		case S_IFREG: /* for testing */
			break;
		default:
			fprintf(stderr, "E: %s is not a block device\n", argv[4]);
			usage();
		}
	}

	/* initialise aRC4 */
	arcfour_init(&c);
	arcfour_ksa(&c, (const void *)argv[3], strlen(argv[3]) + 1U);

	if (!strcmp(argv[1], "write")) {
		fprintf(stderr, "W: this will overwrite the output device!\n"
		    "I: type “yes” with an initial uppercase letter to continue!\n");
		fflush(stderr);
		if (fgets((void *)xbuf, 16, stdin) != (void *)xbuf ||
		    memcmp(xbuf, val_answer, sizeof(val_answer))) {
			fflush(NULL);
			fprintf(stderr, "\nE: user did not confirm, aborted\n");
			fflush(stderr);
			return (2);
		}

		if (!strcmp(argv[4], "-"))
			fd = 1;
		else if ((fd = open(argv[4], O_WRONLY | O_DIRECT /*| O_SYNC*/)) < 0) {
			fprintf(stderr, "E: could not open %s for %s: %s\n",
			    argv[4], "writing", strerror(errno));
			usage();
		}

		tot = 0;
		while (tot < nbytes) {
			fprintf(stderr, "\rI: " myF_GM "...        \b\b\b\b\b\b\b\b",
			    myA_GM(tot));
			fflush(stderr);

			z = nbytes - tot;
			if (z > MYBUFLEN)
				z = MYBUFLEN;

			i = 0;
			while (i < z)
				xbuf[i++] = arcfour_byte(&c);

			s = write(fd, xbuf, (size_t)z);
			if (s == -1) {
				fprintf(stderr,
				    "\nE: error writing %llu bytes: %s\n",
				    z, strerror(errno));
				return (3);
			}
			if ((unsigned long long)s != z) {
				fprintf(stderr,
				    "\nE: wrote %zd instead of %llu bytes\n",
				    s, z);
				return (3);
			}

			tot += z;
			if (tot > nbytes) {
				fprintf(stderr, "\nE: cannot happen\n");
				return (255);
			}
		}

		fprintf(stderr, "\rI: " myF_GB " total\n", myA_GB(tot));
		if (close(fd))
			fprintf(stderr, "W: close(2): %s\n", strerror(errno));
		fprintf(stderr,
		    "I: now sync(1) then eject, re-insert, run ./%s check\n",
		    progname);
	} else if (!strcmp(argv[1], "check")) {
		int rv = 0;

		if (!strcmp(argv[4], "-"))
			fd = 0;
		else if ((fd = open(argv[4], O_RDONLY | O_DIRECT)) < 0) {
			fprintf(stderr, "E: could not open %s for %s: %s\n",
			    argv[4], "reading", strerror(errno));
			usage();
		}

		tot = 0;
		while (tot < nbytes) {
			fprintf(stderr, "\rI: " myF_GM "...        \b\b\b\b\b\b\b\b",
			    myA_GM(tot));
			fflush(stderr);

			z = nbytes - tot;
			if (z > MYBUFLEN)
				z = MYBUFLEN;

			s = read(fd, xbuf, (size_t)z);
			if (s == -1) {
				fprintf(stderr,
				    "\nE: error reading %llu bytes: %s\n",
				    z, strerror(errno));
				return (3);
			}
			if ((unsigned long long)s != z) {
				fprintf(stderr,
				    "\nE: read %zd instead of %llu bytes",
				    s, z);
				rv = 3;
				z = (unsigned long long)s;
			}

			i = 0;
			while (i < z)
				if (xbuf[i++] != arcfour_byte(&c)) {
					--i;
					tot += i;
					fprintf(stderr,
					    "\nE: comparison error at byte %llu\n"
					    "I: at %llu MiB + %u bytes (" myF_GB ")\n"
					    "I: %llu bytes after this remaining (%u in this block)\n",
					    tot,
					    tot / MiB, (unsigned)(tot % MiB), myA_GB(tot),
					    nbytes - tot, (unsigned)(z - i));
					rv = 1;
					break;
				}

			if (rv) {
				if (rv == 3) {
					tot += z;
					fprintf(stderr,
					    "\nI: no comparison error until here "
					    "(%llu bytes remaining)\n",
					    nbytes - tot);
				}
				return (rv);
			}

			tot += z;
			if (tot > nbytes) {
				fprintf(stderr, "\nE: cannot happen\n");
				return (255);
			}
		}

		fprintf(stderr, "\rI: " myF_GB " total\n", myA_GB(tot));
		if (close(fd))
			fprintf(stderr, "W: close(2): %s\n", strerror(errno));
		fprintf(stderr, "I: test completed successfully\n");
	} else
		usage();
	return (0);
}
