/* SPDX-License-Identifier: MirOS OR CC0-1.0 */
/* © 2024 mirabilos Ⓕ MirBSD or CC0 */

/*XXX doesn’t work due to missing kernel support */
// https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1091448

#include <sys/types.h>
#include <sys/ioctl.h>
#include <linux/cdrom.h>
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>

#if 0
#define DEFAULT_CDROM "/dev/cdrom"
#else
/* udev, on 'cdio lock', drops /dev/cd* entries; gotta love progress! */
#define DEFAULT_CDROM "/dev/sr0"
#endif

enum command {
	CMD_CLOSE,
	CMD_EJECT,
	CMD_LOCK,
};

static volatile sig_atomic_t keeprunning;
/* pointer, not array */
static const char *dvname = DEFAULT_CDROM;

static void initsigs(void);
static void usage(void) __attribute__((__noreturn__));

int
main(int argc, char *argv[])
{
	int i;
	enum command cmd;

	while ((i = getopt(argc, argv, "d:f:sv")) != -1)
		switch (i) {
		case 'd':
		case 's':
		case 'v':
			/* ignored, for MirBSD cdio(1) compatibility */
			break;
		case 'f':
			dvname = optarg;
			break;
		default:
			usage();
		}
	argc -= optind;
	argv += optind;

	if (argc != 1) /* for now */
		usage();
	if (!strcmp(*argv, "close"))
		cmd = CMD_CLOSE;
	else if (!strcmp(*argv, "eject"))
		cmd = CMD_EJECT;
	else if (!strcmp(*argv, "lock"))
		cmd = CMD_LOCK;
	else
		usage();

	/* O_NONBLOCK per <linux/cdrom.h> instructions */
	if ((i = open(dvname, O_RDONLY | O_NONBLOCK)) == -1)
		err(1, "open %s", dvname);
#define tryioctl(name, ...) do {				\
	/* as unknown error indicator */			\
	errno = ENOPROTOOPT;					\
	if (ioctl(i, name, ## __VA_ARGS__) < 0)			\
		err(1, "ioctl(%s, %s)", dvname, #name);		\
} while (/* CONSTCOND */ 0)
	switch (cmd) {
	case CMD_CLOSE:
		if (ioctl(i, CDROMCLOSETRAY, 0) < 0)
			err(1, "ioctl(%s, %s)", dvname, "CDROMCLOSETRAY");
		break;
	case CMD_EJECT:
		/* try unlocking first */
		if (ioctl(i, CDROM_LOCKDOOR, 0) < 0)
			warn("ioctl(%s, %s)", dvname, "CDROM_LOCKDOOR");
		errno = ENOPROTOOPT;
		if (ioctl(i, CDROMEJECT, 0) < 0)
			err(1, "ioctl(%s, %s)", dvname, "CDROMEJECT");
		break;
	case CMD_LOCK:
		if (ioctl(i, CDROM_LOCKDOOR, 1) < 0)
			err(1, "ioctl(%s, %s)", dvname, "CDROM_LOCKDOOR");
		/* assert(!is_interactive); */
		initsigs();
		printf("I: locked; keeping program running until aborted...");
		fflush(NULL);
		keeprunning = 1;
		while (keeprunning)
			pause();
		printf("\nI: signal caught, exiting\n");
		break;
	}
	close(i);
	return (0);
}

static void
usage(void)
{
	fprintf(stderr, "E: usage: cdio [-f %s] <command>\n", DEFAULT_CDROM);
	fprintf(stderr, "N: commands are: close eject lock\n");
	exit(1);
}

static void
handle_sigterm(int signo __attribute__((__unused__)))
{
	keeprunning = 0;
}

static void
initsigs(void)
{
	struct sigaction sa;

	memset(&sa, '\0', sizeof(sa));
	sa.sa_handler = &handle_sigterm;
	sigemptyset(&sa.sa_mask);
	sa.sa_flags = SA_RESETHAND;
	if (sigaction(SIGTERM, &sa, NULL))
		warn("could not install SIGTERM handler");
}
