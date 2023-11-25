/*-
 * Copyright (c) 2008, 2013
 *	Thorsten Glaser <tg@mirbsd.org>
 *
 * Provided that these terms and disclaimer and all copyright notices
 * are retained or reproduced in an accompanying document, permission
 * is granted to deal in this work without restriction, including un-
 * limited rights to use, publicly perform, distribute, sell, modify,
 * merge, give away, or sublicence.
 *
 * This work is provided "AS IS" and WITHOUT WARRANTY of any kind, to
 * the utmost extent permitted by applicable law, neither express nor
 * implied; without malicious intent or gross negligence. In no event
 * may a licensor, author or contributor be held liable for indirect,
 * direct, other damage, loss, or other issues arising in any way out
 * of dealing in the work, even if advised of the possibility of such
 * damage or existence of a defect, except proven that it results out
 * of said person's immediate fault when using the work as intended.
 */

#include <sys/param.h>
#include <libckern.h>

__RCSID("$MirOS: src/kern/c/hdump.c,v 1.4 2013/10/31 20:06:11 tg Exp $");

extern int printf(const char *, ...)
    __attribute__((__format__(__printf__, 1, 2)));

#define nibble(value, index)	(((unsigned)(value) >> ((index) << 2)) & 0x0F)

void
memhexdump(const void *buf_, size_t ofs, size_t len)
{
	uint8_t ch;
	const uint8_t *buf = (const uint8_t *)buf_ + ofs;
	size_t i;

 loop:
	printf("%X%X%X%X%X%X%X%X ", nibble(ofs, 7), nibble(ofs, 6),
	    nibble(ofs, 5), nibble(ofs, 4), nibble(ofs, 3),
	    nibble(ofs, 2), nibble(ofs, 1), nibble(ofs, 0));
	i = 0;
	while (i < 16) {
		if (i < len)
			printf(" %X%X", nibble(buf[i], 1), nibble(buf[i], 0));
		else
			printf("   ");
		if (++i == 8)
			printf(" -");
	}
	printf("  |");
	i = MIN(len, 16);
	while (i--)
		printf("%c", (ch = *buf++) >= 32 && ch < 127 ? ch : '.');
	printf("|\n");

	if (len > 16) {
		ofs += 16;
		len -= 16;
		goto loop;
	}
}
