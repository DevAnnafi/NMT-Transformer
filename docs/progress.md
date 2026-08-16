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

### Decisions made today

**newstest2014 uses `test-full.tgz`, not `test-filtered.tgz`.** The filtered
set has 2,737 segments (verified with `grep -c '<seg'`); the full set has
3,003. Published BLEU numbers, including the paper's 27.3, are computed on all
3,003, so the filtered set would give an incomparable score. This was caught by
counting segments rather than trusting the documented figure.

**Line counting uses `newline="\n"`.** Python's universal-newline mode treats a
bare `\r` as a line terminator, which made counts disagree with `wc -l` by 707
lines on the English side of news_commentary. Restricting to `\n` makes counts
reproducible across tools.

### Observations for Day 2 — `clean.py`

From reading the first 50 lines of both sides of news_commentary. This is the
*clean* corpus; commoncrawl still needs the same inspection and will be worse.

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
en dash U+2013. Decide whether to fold these to ASCII — leaving them means BPE
learns separate tokens for curly and straight apostrophes.

**Language-specific number formatting.** `$10,000` ↔ `10.000 Dollar`,
`$1,300` ↔ `1.300 Dollar`. German swaps the thousands separator and spells out
the currency. Not a defect — do not "normalise" German decimal points.

**Document boundaries are invisible.** Articles run together with no marker.
Headlines appear as their own lines (`$10,000 Gold?`, `A Conservative Europe`),
so short fragments will skew the length distribution, and adjacent lines are
not necessarily from the same document.

**Translations are idiomatic, not literal.** Line 5: "Wouldn't you know it?" ↔
"Und es kam, wie es kommen musste." Any filter assuming word-level
correspondence will flag correct pairs.

### Caveat

Equal line counts prove the files were not truncated and did not drift. They
say nothing about whether line *n* on each side are translations of each other.
Commoncrawl is known for positionally-aligned pairs that are not translations —
that is what the length-ratio filter and language ID are for.

### Still to do before Day 2

- Read 50 lines of commoncrawl and add findings here
- The misaligned block at lines 8+ where the German side is English, the isolated bad pair at ~1.2M, the missing-space artifacts, the truncation ellipses.
- Record measured `pairs` values in `configs/base.yaml`

