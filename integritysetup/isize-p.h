/*-
 * © 2025 mirabilos Ⓕ MirBSD
 * Excerpts from Linux dm-integrity.c 🄯 GPLv2
 *
 * Obtains size of a split (--data-device=) dm-integrity metadata device
 * on the native architecture before formatting. (helper)
 */

#include <sys/types.h>
#include <err.h>
#include <errno.h>
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
#if (ULONG_MAX) == (UINT_MAX)
#define DEFAULT_MAX_JOURNAL_SECTORS 8192
#else
#define DEFAULT_MAX_JOURNAL_SECTORS 131072
#endif
#define DEFAULT_JOURNAL_SIZE_FACTOR 7

#define SB_SECTORS 8
#define DEFAULT_BUFFER_SECTORS 128
#define METADATA_PADDING_SECTORS 8

#define MAX_TAG_SIZE (JOURNAL_SECTOR_DATA - JOURNAL_MAC_PER_SECTOR - offsetof(struct journal_entry, last_bytes[MAX_SECTORS_PER_BLOCK]))
#define MAX_SECTORS_PER_BLOCK 8

/* types from dm-integrity.c */
typedef unsigned long long commit_id_t;
struct journal_entry {
	unsigned long long u;
	commit_id_t last_bytes[];
};

static struct {
	unsigned long long data_device_sectors;
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
		unsigned int journal_sections;
		unsigned char log2_sectors_per_block;
	} hsb;
} pic;
#define ic (&pic)

/* from Linux */
static inline unsigned long
__ffs(unsigned long word)
{
	return __builtin_ctzl(word);
}
static inline unsigned long
__fls(unsigned long word)
{
	return (sizeof(word) * 8) - 1U - __builtin_clzl(word);
}
static inline int
fls(unsigned int x)
{
	return x ? sizeof(x) * 8 - __builtin_clz(x) : 0;
}

#define min(a,b) ((a) < (b) ? (a) : (b))

int
main(void)
{
	unsigned long long ul;
	unsigned int ui, journal_sections, journal_sectors;
	int test_bit;

	ic->tag_size = hashsize;
#undef hashsize
	ic->sectors_per_block = 1;
	ic->data_device_sectors = datasize;
#undef datasize
	journal_sectors = min((unsigned long long)DEFAULT_MAX_JOURNAL_SECTORS,
	    ic->data_device_sectors >> DEFAULT_JOURNAL_SIZE_FACTOR);

	ui = DEFAULT_BUFFER_SECTORS;
	ic->log2_buffer_sectors = min((int)__fls(ui), 31 - SECTOR_SHIFT);

	if (ic->tag_size > MAX_TAG_SIZE)
		errx(1, "tag size too large");

	ic->hsb.log2_sectors_per_block = __ffs(ic->sectors_per_block);

	ui = JOURNAL_SECTOR_DATA;
	ic->journal_entry_size = offsetof(struct journal_entry, last_bytes[ic->sectors_per_block]) +
	    ic->tag_size;
	/* round up to JOURNAL_ENTRY_ROUNDUP == 8 */
	ic->journal_entry_size = ((ic->journal_entry_size - 1U) | 7U) + 1U;
	ic->journal_entries_per_sector = ui / ic->journal_entry_size;
	ic->journal_section_entries = ic->journal_entries_per_sector * JOURNAL_BLOCK_SECTORS;
	ic->journal_section_sectors = (ic->journal_section_entries << ic->hsb.log2_sectors_per_block) +
	    JOURNAL_BLOCK_SECTORS;

	journal_sections = journal_sectors / ic->journal_section_sectors;
	if (!journal_sections)
		journal_sections = 1;
	ic->provided_data_sectors = ic->data_device_sectors;
	ic->provided_data_sectors &= ~(unsigned long long)(ic->sectors_per_block - 1U);
	if (!ic->provided_data_sectors)
		errx(1, "no medium");
 try1_smaller_buffer:
	ic->hsb.journal_sections = 0;
	for (test_bit = fls(journal_sections) - 1; test_bit >= 0; test_bit--) {
		unsigned int prev_journal_sections = ic->hsb.journal_sections;
		unsigned int test_journal_sections = prev_journal_sections | (1U << test_bit);
		if (test_journal_sections > journal_sections)
			continue;
		ic->hsb.journal_sections = test_journal_sections;

		ui = JOURNAL_SECTOR_DATA;
		ic->journal_sections = ic->hsb.journal_sections;
		ic->journal_entry_size = offsetof(struct journal_entry, last_bytes[ic->sectors_per_block]) +
		    ic->tag_size;
		/* round up to JOURNAL_ENTRY_ROUNDUP == 8 */
		ic->journal_entry_size = ((ic->journal_entry_size - 1U) | 7U) + 1U;
		ic->journal_entries_per_sector = ui / ic->journal_entry_size;
		ic->journal_section_entries = ic->journal_entries_per_sector * JOURNAL_BLOCK_SECTORS;
		ic->journal_section_sectors = (ic->journal_section_entries << ic->hsb.log2_sectors_per_block) +
		    JOURNAL_BLOCK_SECTORS;
		ic->journal_entries = ic->journal_section_entries * ic->journal_sections;

		ul = ic->journal_section_sectors;
		ul *= ic->journal_sections;
		ul += SB_SECTORS;
		if (ul > UINT_MAX) {
			ic->hsb.journal_sections = prev_journal_sections;
			continue;
		}
		printf(">= %llu\n", ul + METADATA_PADDING_SECTORS);
		ic->initial_sectors = ul;

		ul = (ic->provided_data_sectors >> ic->hsb.log2_sectors_per_block) * ic->tag_size;
		ul += (1U << (ic->log2_buffer_sectors + SECTOR_SHIFT)) - 1U;
		ul >>= ic->log2_buffer_sectors + SECTOR_SHIFT;
		ul <<= ic->log2_buffer_sectors;
		if ((unsigned long long)ic->initial_sectors + ul <
		    (unsigned long long)ic->initial_sectors) {
			ic->hsb.journal_sections = prev_journal_sections;
			continue;
		}
		printf(">= %llu\n", (unsigned long long)ic->initial_sectors + ul);
	}
	if (!ic->hsb.journal_sections) {
		if (ic->log2_buffer_sectors > 3) {
			--ic->log2_buffer_sectors;
			goto try1_smaller_buffer;
		}
		errx(1, "could not calculate #journal_sections");
	}

	if (ic->hsb.log2_sectors_per_block != __ffs(ic->sectors_per_block))
		errx(1, "sectors_per_block wrong");

 try_smaller_buffer:
	ui = JOURNAL_SECTOR_DATA;
	ic->journal_sections = ic->hsb.journal_sections;
	ic->journal_entry_size = offsetof(struct journal_entry, last_bytes[ic->sectors_per_block]) +
	    ic->tag_size;
	/* round up to JOURNAL_ENTRY_ROUNDUP == 8 */
	ic->journal_entry_size = ((ic->journal_entry_size - 1U) | 7U) + 1U;
//	if (ic->hsb.flags & 1U)
//		ui -= JOURNAL_MAC_PER_SECTOR;
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
