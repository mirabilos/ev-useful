#if 0
.if "0" == "1"
#endif

/*-
 * Copyright © 2017
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
 * Buffer standard input into a seekable file, pass that to mplayer.
 */

#include <sys/types.h>
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char tmpf[] = "/tmp/bufmplayer.XXXXXXXXXX";
char s_mplayer[] = "mplayer";

unsigned char debug;

static void c_cat(int, int);

int
main(int argc, char *argv[])
{
	int buffd[2], pipefd[2];
	char *cp, **nargv, dummy;
	unsigned int nsec = 3;

	debug = ((cp = getenv("BUFMPLAYER_DEBUG")) && *cp != 0 && *cp != '0');

	if (pipe(pipefd))
		err(255, "E: pipe");

	if ((cp = getenv("BUFMPLAYER_SLEEP"))) {
		long long res;
		const char *errptr;

		res = strtonum(cp, 1, /* arbitrary */ 255, &errptr);
		if (errptr)
			warn("W: ignoring %s because it is %s: %s",
			    "BUFMPLAYER_SLEEP", errptr, cp);
		else
			nsec = (unsigned int)(unsigned long long)res;
		if (debug)
			fprintf(stderr, "I: sleeping for %u seconds\n", nsec);
	} else if (debug)
		fprintf(stderr, "I: sleeping for %u seconds (default)\n", nsec);

	if ((buffd[1] = mkstemp(tmpf)) == -1)
		err(255, "E: mkstemp %s", tmpf);
	if ((buffd[0] = open(tmpf, O_RDONLY)) == -1) {
		int e = errno;

		if (unlink(tmpf))
			warn("W: unlink %s", tmpf);
		errno = e;
		err(255, "E: open %s", tmpf);
	}
	if (unlink(tmpf))
		warn("W: unlink %s", tmpf);

	/* do we need to double-fork? not, for now */
	switch (fork()) {
	case 0:
		close(buffd[0]);
		close(pipefd[0]);
		c_cat(buffd[1], pipefd[1]);
		_exit(0);
	default:
		break;
	case -1:
		err(255, "E: fork");
	}
	close(buffd[1]);
	close(pipefd[1]);
	close(0);

	if (dup2(2, 0) == -1)
		err(255, "E: dup2 stderr to stdin");

	fprintf(stderr, "I: buffering to %s…", tmpf);
	fflush(stderr);

	if (!(nargv = calloc((size_t)argc - 1 + 3, sizeof(char *))))
		err(255, "E: calloc(%zu, %zu)", (size_t)argc - 1 + 3,
		    sizeof(char *));
	memcpy(nargv, argv, (size_t)argc * sizeof(char *));
	nargv[0] = s_mplayer;
	if (asprintf(&(nargv[(size_t)argc]), "/dev/fd/%u", buffd[0]) == -1)
		err(255, "E: asprintf");
	nargv[(size_t)argc + 1] = NULL;

	/* wait for signal from child */
	errno = 0;
	if (read(pipefd[0], &dummy, 1) != 1)
		warn("\nW: read from child");
	close(pipefd[0]);

	do {
		fprintf(stderr, " .");
		fflush(stderr);
		sleep(1);
	} while (--nsec);
	fprintf(stderr, " done.\n");
	fflush(stderr);

	execvp(nargv[0], nargv);
	err(255, "E: execvp");
}

static void
c_cat(int dfd, int sigfd)
{
	ssize_t n, w;
	unsigned long long total = 0;
	char *cp, buf[32768];

	/* TODO: catch SIGPIPE? */

	while (/* CONSTCOND */ 1) {
		if ((n = read(0, (cp = buf), sizeof(buf))) == -1) {
			if (errno == EINTR)
				continue;
			err(255, "E: read (child)");
		} else if (n == 0)
			/* end of file reached */
			break;
		if (debug)
			fprintf(stderr, "I: read %zd bytes\n", n);
		if (sigfd != -1) {
			/* signal parent after first read */
 resig:
			if ((w = write(sigfd, buf, 1)) == -1) {
				if (errno == EINTR)
					goto resig;
				err(255, "E: write (signal)");
			} else if (w < 1)
				goto resig;
			close(sigfd);
			sigfd = -1;
		}
		while (n) {
			if ((w = write(dfd, cp, n)) == -1) {
				if (errno == EINTR)
					continue;
				err(255, "E: write (child)");
			}
			if (debug) {
				total += w;
				fprintf(stderr,
				    "I: wrote %zd bytes, %llu total\n",
				    w, total);
			}
			n -= w;
			cp += w;
		}
	}
	if (debug)
		fprintf(stderr, "I: child finished\n");
	fflush(stderr);
}

#if 0
.endif

PROG=		bufmplayer
NOMAN=		Yes
BINDIR=		$${HOME}/.etc/bin

realinstall:
	${INSTALL} ${INSTALL_COPY} ${INSTALL_STRIP} \
	    -m ${BINMODE} ${PROG} ${DESTDIR}${BINDIR}/

.include <bsd.prog.mk>
#endif
