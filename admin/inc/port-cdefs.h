/**	From MirOS: src/sys/sys/cdefs.h,v 1.35 2023/01/09 01:01:27 tg Exp $ */

/*-
 * Copyright © 2005, 2006, 2011, 2013, 2014, 2021, 2022
 *	mirabilos <m@mirbsd.org>
 * Copyright (c) 1991, 1993
 *	The Regents of the University of California.  All rights reserved.
 *
 * This code is derived from software contributed to Berkeley by
 * Berkeley Software Design, Inc.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the University nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 *	@(#)cdefs.h	8.7 (Berkeley) 1/21/94
 */

#ifndef PORT_CDEFS_H_
#define PORT_CDEFS_H_

#if defined(__cplusplus)
#define	__BEGIN_DECLS	extern "C" {
#define	__END_DECLS	}
#else
#define	__BEGIN_DECLS
#define	__END_DECLS
#endif

/*
 * Macro to test if we're using a specific version of gcc or later.
 */
#ifdef lint
#undef __GNUC__
#endif
#ifdef __GNUC__
#define __GNUC_PREREQ__(ma, mi) \
	((__GNUC__ > (ma)) || (__GNUC__ == (ma) && __GNUC_MINOR__ >= (mi)))
#else
#define __GNUC_PREREQ__(ma, mi) 0
#endif

/*
 * The __CONCAT macro is used to concatenate parts of symbol names, e.g.
 * with "#define OLD(foo) __CONCAT(old,foo)", OLD(foo) produces oldfoo.
 * The __CONCAT macro is a bit tricky -- make sure you don't put spaces
 * in between its arguments.  __CONCAT can also concatenate double-quoted
 * strings produced by the __STRING macro, but this only works with ANSI C.
 */
#ifndef __P
#define	__P(protos)	protos		/* full-blown ANSI C */
#endif
#define	__CONCAT(x,y)	x ## y
#define	__STRING(x)	#x

#define	__const		const		/* define reserved names to standard */
#define	__signed	signed
#define	__volatile	volatile
#if !defined(__inline)
#define	__inline	inline		/* convert to C++/C99 keyword */
#endif

/*
 * GCC >= 2.5 uses the __attribute__((__attrs__)) style. All of these
 * work for GNU C++ (modulo a slight glitch in the C++ grammar in
 * the distribution version of 2.5.5).
 */
#define __dead		__attribute__((__noreturn__))
#define __pure		__attribute__((__const__))

/*
 * GNU C version 2.96 adds explicit branch prediction so that
 * the CPU back-end can hint the processor and also so that
 * code blocks can be reordered such that the predicted path
 * sees a more linear flow, thus improving cache behavior, etc.
 *
 * The following two macros provide us with a way to utilize this
 * compiler feature.  Use __predict_true() if you expect the expression
 * to evaluate to true, and __predict_false() if you expect the
 * expression to evaluate to false.
 *
 * A few notes about usage:
 *
 *	* Generally, __predict_false() error condition checks (unless
 *	  you have some _strong_ reason to do otherwise, in which case
 *	  document it), and/or __predict_true() 'no-error' condition
 *	  checks, assuming you want to optimize for the no-error case.
 *
 *	* Other than that, if you don't know the likelihood of a test
 *	  succeeding from empirical or other 'hard' evidence, don't
 *	  make predictions.
 *
 *	* These are meant to be used in places that are run 'a lot'.
 *	  It is wasteful to make predictions in code that is run
 *	  seldomly (e.g. at subsystem initialization time) as the
 *	  basic block reordering that this affects can often generate
 *	  larger code.
 */
#if defined(lint)
#define __predict_true(exp)	(exp)
#define __predict_false(exp)	(exp)
#elif __GNUC_PREREQ__(2, 96)
#define __predict_true(exp)	__builtin_expect(!!(exp), 1)
#define __predict_false(exp)	__builtin_expect(!!(exp), 0)
#else
#define __predict_true(exp)	(!!(exp))
#define __predict_false(exp)	(!!(exp))
#endif

#if (__GNUC__ >= 3) || __GNUC_PREREQ__(2, 7)
#define	__packed		__attribute__((__packed__))
#elif defined(__PCC__)
#define	__packed		_Pragma("packed 1")
#elif defined(lint)
#define	__packed
#endif

#if !__GNUC_PREREQ__(2, 8)
#define	__extension__
#endif

#ifdef lint
#define __aligned(x)
#define __func__		"__func__"
#define __restrict
#define __unused
#define __a_used
#define __a_deprecated
#define __mb_typecoerce(c,t,v)	((t)(v))
#elif defined(__PCC__)
#define __aligned(x)		_Pragma("aligned " #x)
#define __restrict		restrict
#define __unused		__attribute__((__unused__))
#define __a_used
#define __a_deprecated
#define __mb_typecoerce(c,t,v)	((t)(v))
#else
#define __aligned(x)		__attribute__((__aligned__(x)))
#define __unused		__attribute__((__unused__))
#define __a_used		__attribute__((__used__))
#define __a_deprecated		__attribute__((__deprecated__))
#define __mb_typecoerce(c,t,v)	__builtin_choose_expr( \
	__builtin_types_compatible_p(__typeof__(v), c), \
	(t)(v), (v))
#endif

#define __mb_constcharmalmal(v)	__mb_typecoerce(char **, const char **, (v))

#if !defined(__restrict) && !defined(__cplusplus)
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
#define __restrict		restrict
#else
#define __restrict
#endif
#endif
#define __restrict__		__restrict

#if defined(__ELF__) && defined(__GNUC__) && \
    !defined(__llvm__) && !defined(__NWCC__)
#define __IDSTRING(prefix, string)				\
	__asm__(".section .comment"				\
	"\n	.ascii	\"@(\"\"#)" #prefix ": \""		\
	"\n	.asciz	\"" string "\""				\
	"\n	.previous")
#else
#define __IDSTRING_CONCAT(l,p)		__LINTED__ ## l ## _ ## p
#define __IDSTRING_EXPAND(l,p)		__IDSTRING_CONCAT(l,p)
#define __IDSTRING(prefix, string)				\
	static const char __IDSTRING_EXPAND(__LINE__,prefix) []	\
	    __a_used = "@(""#)" #prefix ": " string
#endif
#define __COPYRIGHT(x)		__IDSTRING(copyright,x)
#define __KERNEL_RCSID(n,x)	__IDSTRING(rcsid_ ## n,x)
#define __RCSID(x)		__IDSTRING(rcsid,x)
#define __SCCSID(x)		__IDSTRING(sccsid,x)
#define __FBSDID(x)		__IDSTRING(fbsdid,x)

#ifdef __NEED_NETBSD_COMPAT	/* one of the worst */
#ifdef __GNUC__
#define __UNCONST(x) __extension__({	\
	union {				\
		const void *cptr;	\
		void *vptr;		\
	} __UC_v;			\
					\
	__UC_v.cptr = (x);		\
	(__UC_v.vptr);			\
})
#else
#define __UNCONST(a)		((void *)(unsigned long)(const void *)(a))
#endif
#endif

#endif /* !_CDEFS_H_ */
