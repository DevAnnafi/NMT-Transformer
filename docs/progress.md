# Progress

## Day 1 — Data acquisition

**Status:** complete.

`python -m scripts.download_data --all` fetches, verifies, and extracts all
five WMT14 archives. Re-running makes no network calls.

### Measured

| Corpus | Archive bytes | Pairs |
|---|---|---|
| news_commentary | 80,418,416 | 201,288 |
| europarl | 657,632,379 | 1,920,209 |
| commoncrawl | 918,311,367 | 2,399,123 |
| newstest2013 (dev) | 17,742,707 | 3,000 |
| newstest2014 (test) | 3,255,445 | 3,003 |

Training total: 4,520,620 pairs. Both sides of every training corpus have
equal line counts.

### Decisions

**newstest2014 uses `test-full.tgz`, not `test-filtered.tgz`.** The filtered
set has 2,737 segments (verified with `grep -c '<seg'`); the full set has
3,003. Published BLEU numbers, including the paper's 27.3, are computed on all
3,003, so the filtered set would give an incomparable score. Caught by counting
segments rather than trusting the documented figure.

**Line counting uses `newline="\n"`.** Python's universal-newline mode treats a
bare `\r` as a line terminator, which made counts disagree with `wc -l` by 707
lines on the English side of news_commentary. Restricting to `\n` makes counts
reproducible across tools.

---

## Corpus observations

### news_commentary

From reading the first 50 lines of both sides. This is the *clean* corpus and
its problems are still subtle.

**Control characters.** 3,938 bare `\r` in the German side. Strip control
characters first, before any other filter touches the text.

**Trailing and internal whitespace.** Several German lines end in two spaces
(`verzehnfachen?  `, `Reiz des Goldes.  `). Line 4 has a double space
mid-sentence (`des Goldes  hinwiesen`). Strip and collapse whitespace runs.

**Multiple sentences per line.** Line 26 is two sentences on both sides. A
`max_len` filter cannot assume one sentence per line, or it will drop
legitimate long pairs.

**Typographic punctuation.** English uses U+2019 for apostrophes and
U+201C/U+201D for quotes; German uses U+201E/U+201C (low-9 opening). Both use
en dash U+2013. Folded to ASCII in `normalize()`; the en dash is left alone as
meaningful punctuation rather than an encoding artifact.

**Language-specific number formatting.** `$10,000` ↔ `10.000 Dollar`,
`$1,300` ↔ `1.300 Dollar`. German swaps the thousands separator and spells out
the currency. Not a defect — do not "normalise" German decimal points. Both are
regression-tested in `tests/test_clean.py`.

**Document boundaries are invisible.** Articles run together with no marker.
Headlines appear as their own lines (`$10,000 Gold?`, `A Conservative Europe`),
so short fragments skew the length distribution, and adjacent lines are not
necessarily from the same document.

**Translations are idiomatic, not literal.** Line 5: "Wouldn't you know it?" ↔
"Und es kam, wie es kommen musste." Any filter assuming word-level
correspondence will flag correct pairs.

**Chinese source lines.** Some pairs have Chinese where English should be,
correctly translated into German. Found while inspecting ratio outliers.

**Space-stripped lines.** Real German sentences with every space removed, e.g.
`WelcheLektionenlassensichnunausdiesembetrüblichenStandderDingelernen?`. These
pass as a handful of "tokens" and were only caught by the ratio filter because
the other side happened to be long — a shorter one would survive. Also seen:
`itwill`, and a soft hyphen U+00AD inside `it\xadwill`.

### commoncrawl

From reading lines 1–40 and 1,200,000–1,200,030 of both sides.

**Wholesale misalignment.** Lines 1–7 align correctly. From line 8 onward the
two sides diverge completely: English line 8 is "Translator Internet is a
Toolbar for MS Internet Explorer", German line 8 is "ACDSee 9 Photo Manager
Organize your photos." Different products entirely — and the German side of
that block is written in English. Thousands of "German" lines contain no
German.

**Isolated bad pairs also occur.** Around line 1.2M the alignment is otherwise
good — a long article on the Ligna radio ballet translates line for line — but
one pair breaks ("Our goal is to limit the environmental pollution…" against
„EKO OSTA" ist das führende Unternehmen für Entsorgung…") and the next line
realigns. Block drift and isolated noise both occur.

**Topically related but not parallel.** The largest and least tractable
failure. Inspecting 15 pairs above ratio 2.5 found several like "AKVIS
Chameleon is a fun to use tool for photo collage creation" against a longer,
independently written German blurb about the same product. Both sides are the
right language and the right topic; neither is a translation of the other.
**No cheap filter catches this.** Language ID passes them, the ratio filter
only catches the lopsided ones. This is the strongest argument for weighting
the `max_pairs` subsample toward europarl and news_commentary rather than
sampling uniformly.

**Scraping artifacts.** Missing spaces where HTML was stripped (`andrelates`,
`tothe`, `downloadthe`). Truncation ellipses ending a large share of lines —
listing pages cut off mid-sentence. Space before punctuation (`Stahlguss .`,
`phrases ?`). Corrupted quote characters: `#nickvoices#` where the English side
has `'nickvoices'`.

**Near-duplicates.** The WordBanker blurb appears twice, differing only in
"French people" versus "Italian people". These are *not* duplicates to remove —
they are different sentences with different correct German translations.

**German lines starting lowercase** (`die Mitteilungen`, `der Vertrieb`).
German capitalises sentence starts and all nouns, so this is a cheap quality
signal. Not currently used.

---

## Day 2 — Cleaning and filtering

### Filter order

1. Normalise: strip control characters, fold punctuation, collapse whitespace
2. Drop pairs where either side is empty
3. Length, length-ratio, and longest-token filters
4. Language ID — **all three corpora**, not just commoncrawl
5. Exact deduplication on the `(src, tgt)` pair

Cheap filters first, expensive last, each shrinking the input to the next.

**Normalise before dedup, not after.** Byte-level hashing of raw text treats
`"Der Bau.  "` and `"Der Bau."` as distinct, so both survive. Normalising first
means exact dedup catches strictly more, at no extra cost since the text is
being normalised anyway.

**Dedup on the pair, never per side.** Hashing the two files independently
would delete different row indices from each and destroy the alignment verified
on Day 1. One hash per `(src, tgt)` tuple; drop the row from both files or
neither.

**Exact dedup only, no fuzzy/MinHash.** Jaccard-similarity deduplication would
delete the WordBanker pairs, which are legitimate distinct sentences, and would
do the same at scale to europarl's repetitive procedural language. Standard MT
practice is exact pair-level dedup.

### Thresholds measured

Whitespace-token counts, 99.9th percentile except where noted:

| corpus | en | de | ratio | max len (en/de) |
|---|---|---|---|---|
| news_commentary | 76 | 78 | 2.9 | 171 / 193 |
| europarl | 107 | 100 | 4.0 | 668 / 426 |
| commoncrawl | 103 | 94 | 8.2 | 4225 / 2937 |

commoncrawl's 4,225-token maximum is a scraped page dumped onto one line.

Set from these numbers, not from convention:

- `max_len: 100` — just above europarl's 99.9th percentile
- `max_len_ratio: 2.5` — 15 commoncrawl pairs above this were inspected by
  hand; none were worth keeping
- `max_token_chars: 40` — catches the space-stripped lines directly rather
  than relying on the ratio filter to catch them by accident
- `min_len: 1`

### Language ID

**py3langid, not fastText.** fastText is the conventional choice, but
`fasttext-wheel` calls `np.array(probs, copy=False)`, which NumPy 2 rejects.
Pinning NumPy below 2 would conflict with PyTorch on Day 6. py3langid ships its
model with the package, so there is no 130MB gitignored artifact either.

**No confidence threshold.** py3langid returns an unnormalised log-likelihood,
not a probability: confident English scores −77, ambiguous "OK." scores +9.
Lower is more confident and the scale is unbounded, so there is no principled
cutoff. Label-only comparison, with `min_len` keeping the shortest strings away
from the filter.

**Verified against ground truth.** The commoncrawl block at lines 8–15, where
the German side is English, is rejected. Lines 1–7 pass.

**False positive rate: 0.4%** — 2 of the first 500 news_commentary pairs, both
short headlines where the classifier has little to work with. Measured on raw
text; normalisation runs first in the real pipeline, so the true rate is likely
lower. One inspected failure classified an English line as French, with English
ranked second by a 10-point margin — the line contained `restant`, a corpus
typo for "resistant".

---

## Caveat carried forward

Equal line counts prove the files were not truncated and did not drift as a
whole. They say nothing about whether line *n* on each side are translations of
each other — commoncrawl is the proof, with 2,399,123 lines on both sides and
large blocks that are not parallel at all.