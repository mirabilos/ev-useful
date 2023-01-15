#if 0
.if "0" == "1"
#endif
/*-
 * Copyright © 2020
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

#define _XOPEN_SOURCE
#include <locale.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wchar.h>
#include <wctype.h>

#ifdef UD_HDR
#include UD_HDR
#endif

#ifndef ud_iswalnum
#define ud_iswalnum iswalnum
#define ud_iswalpha iswalpha
#define ud_iswblank iswblank
#define ud_iswcntrl iswcntrl
#define ud_iswdigit iswdigit
#define ud_iswgraph iswgraph
#define ud_iswlower iswlower
#define ud_iswprint iswprint
#define ud_iswpunct iswpunct
#define ud_iswspace iswspace
#define ud_iswtitle iswtitle
#define ud_iswupper iswupper
#define ud_iswxdigit iswxdigit
#define ud_towlower towlower
#define ud_towtitle towtitle
#define ud_towupper towupper
#define ud_wcwidth wcwidth
#define ud_wctrans wctrans
#define ud_totrans towctrans
#endif

#if defined(UD_use16)
#define FIN 0xFFFD
#define typ uint16_t
#elif defined(UD_use21)
#define FIN 0x10FFFF
#define typ uint32_t
#endif

struct attrs {
	const char *alnum;
	const char *alpha;
	const char *blank;
	const char *cntrl;
	const char *digit;
	const char *graph;
	const char *lower;
	const char *print;
	const char *punct;
	const char *space;
	const char *title;
	const char *upper;
	const char *xdigit;
	char name[12];
	int width;
	typ wc;
	typ clower;
	typ ctitle;
	typ cupper;
};

const char null[] = "";

int
main(void)
{
	wint_t wc = 0;
	struct attrs a;
#ifdef UD_twt
	wctrans_t tot;
#endif

	setlocale(LC_CTYPE, "");
#ifdef UD_twt
	if (!(tot = ud_wctrans("totitle")))
		fprintf(stderr, "W: no title case\n");
#endif

	do {
		memset(&a, 0, sizeof(a));
		a.alnum = ud_iswalnum(wc) ? " alnum" : null;
		a.alpha = ud_iswalpha(wc) ? " alpha" : null;
		a.blank = ud_iswblank(wc) ? " blank" : null;
		a.cntrl = ud_iswcntrl(wc) ? " cntrl" : null;
		a.digit = ud_iswdigit(wc) ? " digit" : null;
		a.graph = ud_iswgraph(wc) ? " graph" : null;
		a.lower = ud_iswlower(wc) ? " lower" : null;
		a.print = ud_iswprint(wc) ? " print" : null;
		a.punct = ud_iswpunct(wc) ? " punct" : null;
		a.space = ud_iswspace(wc) ? " space" : null;
#if !defined(UD_noti) && !defined(UD_twt)
		a.title = ud_iswtitle(wc) ? " title" : null;
#else
		a.title = null;
#endif
		a.upper = ud_iswupper(wc) ? " upper" : null;
		a.xdigit = ud_iswxdigit(wc) ? " xdigit" : null;
		a.width = ud_wcwidth(wc);
		a.wc = wc;
		a.clower = ud_towlower(wc);
		a.cupper = ud_towupper(wc);
#if !defined(UD_noti) && !defined(UD_twt)
		a.ctitle = ud_towtitle(wc);
#else
#ifdef UD_twt
		if (tot) {
			a.ctitle = ud_totrans(wc, tot);
			if (a.ctitle == a.wc && a.ctitle != a.cupper &&
			    a.ctitle != a.clower)
				a.title = " title";
		} else
#endif
			a.ctitle = a.cupper;
#endif
		snprintf(a.name, sizeof(a.name),
#ifdef UD_use21
		    wc > 0xFFFF ? "U-%08X" :
#endif
		    "U+%04X", (unsigned int)wc);
		printf("%s  attr:%s%s%s%s%s%s%s%s%s%s%s%s\n",
		    a.name, a.alnum, a.alpha, a.blank, a.cntrl,
		    a.digit, a.graph, a.lower, a.print, a.punct,
		    a.space, a.upper, a.xdigit);
		if (a.title != null)
			printf("%s  %s\n", a.name, a.title);
		if (a.clower != a.wc)
			printf("%s  tolower=%05X (%+d)\n",
			    a.name, (unsigned int)a.clower,
			    (int)a.clower - (int)a.wc);
		if (a.cupper != a.wc)
			printf("%s  toupper=%05X (%+d)\n",
			    a.name, (unsigned int)a.cupper,
			    (int)a.cupper - (int)a.wc);
		if (a.ctitle != a.wc && a.ctitle != a.cupper)
			printf("%s  totitle=%05X (%+d)\n",
			    a.name, (unsigned int)a.ctitle,
			    (int)a.ctitle - (int)a.wc);
		printf("%s  width=%d\n\n", a.name, a.width);
	} while (++wc <= FIN);

	printf("ok\n");
	return (0);
}

#if 0
.endif

PROG=		ucsidump
NOMAN=		Yes

.ifdef bmp
CPPFLAGS+=	-DUD_use16
.else
CPPFLAGS+=	-DUD_use21
.endif

.ifdef noti
CPPFLAGS+=	-DUD_noti
.elif defined(twt)
CPPFLAGS+=	-DUD_twt
.endif

.ifdef hdr
CPPFLAGS+=	-DUD_HDR=\"${hdr}\" #"
.endif

.include <bsd.prog.mk>
#endif
