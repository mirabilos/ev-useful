/* From MirOS: src/kern/include/libckern.h,v 1.48 2022/01/17 01:42:20 tg Exp $ */

/*-
 * Copyright (c) 2008, 2010, 2011, 2013, 2014, 2015, 2019
 *	mirabilos <m@mirbsd.org>
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

#ifndef __LIBCKERN_H_
#define __LIBCKERN_H_

#include <sys/types.h>
#include <stdint.h>

/**
 * An arcfour_status is hereby defined carrying ca.
 * 212 octets (1696 bit) of entropic state, whereas
 * S contains 210 octets and 3.996 additional bits,
 * i is another 8 bit, and j adds enough to make up
 * for the 4 bit of additional entropy we assume.
 */
struct arcfour_status {
	uint8_t S[256];
	uint8_t i;
	uint8_t j;
};

__BEGIN_DECLS
/* arcfour: base cipher */
void arcfour_init(struct arcfour_status *);
void arcfour_ksa(struct arcfour_status *, const uint8_t *, size_t)
    /*__attribute__((__bounded__(__string__, 2, 3)))*/;
uint8_t arcfour_byte(struct arcfour_status *);

void memhexdump(const void *, size_t, size_t);
__END_DECLS

#define imax(a,b) __extension__({			\
	int imax_a = (a), imax_b = (b);			\
	(imax_a > imax_b ? imax_a : imax_b);		\
})
#define imin(a,b) __extension__({			\
	int imin_a = (a), imin_b = (b);			\
	(imin_a < imin_b ? imin_a : imin_b);		\
})
#define lmax(a,b) __extension__({			\
	long lmax_a = (a), lmax_b = (b);		\
	(lmax_a > lmax_b ? lmax_a : lmax_b);		\
})
#define lmin(a,b) __extension__({			\
	long lmin_a = (a), lmin_b = (b);		\
	(lmin_a < lmin_b ? lmin_a : lmin_b);		\
})
#define max(a,b) __extension__({			\
	u_int max_a = (a), max_b = (b);			\
	(max_a > max_b ? max_a : max_b);		\
})
#define min(a,b) __extension__({			\
	u_int min_a = (a), min_b = (b);			\
	(min_a < min_b ? min_a : min_b);		\
})
#define ulmax(a,b) __extension__({			\
	u_long ulmax_a = (a), ulmax_b = (b);		\
	(ulmax_a > ulmax_b ? ulmax_a : ulmax_b);	\
})
#define ulmin(a,b) __extension__({			\
	u_long ulmin_a = (a), ulmin_b = (b);		\
	(ulmin_a < ulmin_b ? ulmin_a : ulmin_b);	\
})

#endif
