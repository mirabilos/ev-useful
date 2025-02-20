/*-
 * © 2025 mirabilos Ⓕ MirBSD
 * Excerpts from Linux dm-integrity.c 🄯 GPLv2
 *
 * Obtains size of a split (--data-device=) dm-integrity metadata device.
 */

#include <sys/types.h>
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define SECTOR_SHIFT 9

#define JOURNAL_SECTOR_DATA ((1U << SECTOR_SHIFT) - sizeof(commit_id_t))
#define JOURNAL_MAC_PER_SECTOR 8
#define JOURNAL_BLOCK_SECTORS 8

#define SB_SECTORS 8
#define DEFAULT_BUFFER_SECTORS 128

/* types from dm-integrity.c */
typedef unsigned long long commit_id_t;
struct journal_entry {
	unsigned long long u;
	commit_id_t last_bytes[];
};

static struct {
	unsigned long long Meta_sectors;
	unsigned long long provided_data_sectors;
	unsigned int tag_size;
	unsigned int initial_sectors;
	unsigned int journal_sections;
	unsigned int journal_entries;
	unsigned short journal_entry_size;
	unsigned short journal_section_sectors;
	unsigned char journal_entries_per_sector;
	unsigned char journal_section_entries;
	unsigned char sectors_per_block;
	unsigned char log2_buffer_sectors;
	struct {
		unsigned long long provided_data_sectors;
		unsigned int journal_sections;
		unsigned short integrity_tag_size;
		unsigned char log2_interleave_sectors;
		unsigned char log2_sectors_per_block;
		unsigned int flags;
//		unsigned char log2_blocks_per_bitmap_bit;
	} hsb;
} pic;
#define ic (&pic)

static unsigned char buf[1U << SECTOR_SHIFT];

static void fill_sb(void);

/* from Linux */
static inline unsigned long
__fls(unsigned long word)
{
	return (sizeof(word) * 8) - 1U - __builtin_clzl(word);
}

#define min(a,b) ((a) < (b) ? (a) : (b))

int
main(int argc, char *argv[])
{
	unsigned long long ul;
	unsigned int ui;
	int fd;

	if (argc != 2)
		errx(1, "Usage: isize /dev/sdX1 (or - for stdin)");
	if (argv[1][0] == '-' && !argv[1][1])
		fd = 0;
	else if ((fd = open(argv[1], O_RDONLY)) < 0)
		err(1, "%s: open", argv[1]);
	fprintf(stderr, "I: using %s\n", fd ? argv[1] : "<stdin>");

	/* for short reads */
	errno = ENOSR;
	if ((size_t)read(fd, buf, sizeof(buf)) != sizeof(buf))
		err(1, "read");
	fill_sb();
	close(fd);

	ui = DEFAULT_BUFFER_SECTORS;
	ic->log2_buffer_sectors = min((int)__fls(ui), 31 - SECTOR_SHIFT);

 try_smaller_buffer:
	ui = JOURNAL_SECTOR_DATA;
	ic->journal_sections = ic->hsb.journal_sections;
	ic->journal_entry_size = offsetof(struct journal_entry, last_bytes[ic->sectors_per_block]) +
	    ic->tag_size;
	/* round up to JOURNAL_ENTRY_ROUNDUP == 8 */
	ic->journal_entry_size = ((ic->journal_entry_size - 1U) | 7U) + 1U;
	if (ic->hsb.flags & 1U)
		ui -= JOURNAL_MAC_PER_SECTOR;
	ic->journal_entries_per_sector = ui / ic->journal_entry_size;
	ic->journal_section_entries = ic->journal_entries_per_sector * JOURNAL_BLOCK_SECTORS;
	ic->journal_section_sectors = (ic->journal_section_entries << ic->hsb.log2_sectors_per_block) +
	    JOURNAL_BLOCK_SECTORS;
	ic->journal_entries = ic->journal_section_entries * ic->journal_sections;

	ul = ic->journal_section_sectors;
	ul *= ic->journal_sections;
	ul += SB_SECTORS;
	if (ul > UINT_MAX)
		errx(1, "initial_sectors too large: %llu", ul);
	ic->initial_sectors = ul;

	ul = (ic->provided_data_sectors >> ic->hsb.log2_sectors_per_block) * ic->tag_size;
	ul += (1U << (ic->log2_buffer_sectors + SECTOR_SHIFT)) - 1U;
	ul >>= ic->log2_buffer_sectors + SECTOR_SHIFT;
	ul <<= ic->log2_buffer_sectors;
	if ((unsigned long long)ic->initial_sectors + ul <
	    (unsigned long long)ic->initial_sectors) {
		if (ic->log2_buffer_sectors > 3) {
			--ic->log2_buffer_sectors;
			goto try_smaller_buffer;
		}
		errx(1, "meta_size %llu too large (initial_sectors = %u)",
		    ul, ic->initial_sectors);
	}
	ic->Meta_sectors = (unsigned long long)ic->initial_sectors + ul;

	printf("%llu\n", ic->Meta_sectors);
	if (ic->log2_buffer_sectors > 3) {
		--ic->log2_buffer_sectors;
		goto try_smaller_buffer;
	}
	return (0);
}

static inline unsigned long long
get_le(size_t ofs, size_t len)
{
	unsigned long long res = 0;

	while (len--)
		res |= (unsigned long long)buf[ofs + len] << (8U * len);
	return (res);
}

static void
fill_sb(void)
{
	if (memcmp(buf, "integrt", 8))
		errx(1, "invalid magic");
	switch (buf[8]) {
	case 1:
	case 2:
	case 3:
	case 4:
		break;
	default:
		errx(1, "invalid superblock version: %u", buf[8]);
	}
	ic->hsb.integrity_tag_size = get_le(10, 2);
	ic->tag_size = ic->hsb.integrity_tag_size;
	ic->hsb.log2_sectors_per_block = buf[28];
	ic->sectors_per_block = 1U << (int)ic->hsb.log2_sectors_per_block;
	ic->hsb.journal_sections = get_le(12, 4);
	if (!ic->hsb.journal_sections)
		errx(1, "no journal_sections");
	ic->hsb.log2_interleave_sectors = buf[9];
	if (ic->hsb.log2_interleave_sectors)
		errx(1, "not a split data/metadata device");
	ic->hsb.provided_data_sectors = get_le(16, 8);
	ic->hsb.flags = get_le(24, 4);

	ic->provided_data_sectors = ic->hsb.provided_data_sectors;
}
