# nmt-transformer — 14-Day Roadmap

Neural machine translation on WMT14 English–German, built on a from-scratch
Transformer implementation (Vaswani et al., 2017).

The architecture was written independently in
[Attention_From_Scratch](https://github.com/DevAnnafi/Attention_From_Scratch)
and is ported here. This project is the other half of the problem: taking a
verified model and putting a real corpus through it.

---

## Decisions

**Corpus: full WMT14 En-De.**
Europarl v7 + Common Crawl + News Commentary v9, ~4.5M sentence pairs.
Dev: newstest2013. Test: newstest2014.
Rationale: _[why the full corpus over a curated starter set — write this
before Day 1 ends, including what you're uncertain about and what would tell
you the choice was wrong]_

**Training scope: subsampled.**
The pipeline handles the full corpus; training runs on a `max_pairs` slice set
in config. No GPU cluster available, and the paper's base model took 12 hours
across 8 P100s. The full path stays working so the corpus is a config change,
not a rewrite.

**Tokenization: hand-rolled BPE.**
Shared En-De vocabulary, 37k merges, as in the paper. No sentencepiece.
Rationale: _[why]_

**Model: ported, not rewritten.**
Architecture comes in from Attention_From_Scratch as a single attributed copy
commit. Rationale: it was built from first principles once; rebuilding it would
spend days re-solving a solved problem instead of on the data and training work
that is actually new here.

**Out of scope:** _[what you're deliberately not doing — multi-GPU, mixed
precision, alternative architectures, whatever you decide]_

---

## Inherited baseline

What the ported code has already been verified to do, so it doesn't get
re-litigated mid-project:

- Scaled dot-product attention matches a hand-computed test case
- Single-head MHA reduces to raw attention under identity projections
- Causal and padding masks compose as an elementwise AND; masked positions
  receive exactly zero attention weight
- Padded batches produce finite forward passes and finite gradients
- Label smoothing excludes `<pad>` from both the smoothed distribution and the
  loss denominator
- Noam schedule matches the paper's formula to zero error at steps 4000, 4001,
  10000, 50000
- Embedding and projection initialise to N(0, d_model^-0.5); other matrices to
  Xavier uniform — verified at V=37000, d_model=512
- One-batch overfit converges with shifted decoder input and masks applied

**Lesson carried forward:** every bug found in that repo was invisible at toy
dimensions and only appeared when the model was instantiated at WMT14 scale.
Any test that could pass at `d_model=32, V=20` and fail at `d_model=512,
V=37000` needs a large-dimension variant.

---

## Day template

- **Goal** — what exists at the end that didn't at the start
- **Files** — paths touched
- **Done when** — a runnable check, not a feeling
- **Concepts** — what to understand before typing
- **Outcome** — filled in that evening

---

## Day 1 — Data acquisition

**Goal:** Reproducible, resumable download of all five WMT14 archives.

**Files:** `configs/base.yaml`, `src/data/download.py`,
`scripts/download_data.py`, `.gitignore`

**Done when:** `python scripts/download_data.py --corpus news_commentary` runs
twice; the second run skips the fetch and still prints matching per-side line
counts.

**Concepts:** streaming vs. buffered downloads; idempotency for a 900MB fetch;
what a parallel corpus looks like on disk.

**Outcome:**

---

## Day 2 — Cleaning and filtering

**Goal:** Raw corpora → aligned, filtered parallel text in `data/processed/`.

**Files:** `src/data/clean.py`, `tests/test_clean.py`

**Done when:** I can state how many pairs each filter dropped and defend each
number.

**Concepts:** Unicode normalisation; length and length-ratio filtering; why
Common Crawl needs language ID and Europarl mostly doesn't; deduplication.

**Note:** the length cap chosen here sets the floor for `max_len` in
`PositionalEncoding` — leave room for `<bos>` and `<eos>`.

**Outcome:**

---

## Day 3 — BPE, naive implementation

**Goal:** Working `learn_bpe`, correctness over speed.

**Files:** `src/data/tokenizer.py`, `tests/test_tokenizer.py`

**Done when:** merges are produced on News Commentary, and I've timed it and
know exactly how slow it is.

**Concepts:** why `</w>`; why operate on a word-frequency dict rather than the
corpus; where the O(merges × vocab) cost lives.

**Outcome:**

---

## Day 4 — BPE, optimised and applied

**Goal:** 37k shared merges over the full corpus in tolerable time; encode and
decode both work.

**Files:** `src/data/tokenizer.py`, `tests/test_tokenizer.py`

**Done when:** `decode(encode(s)) == s` for sentences with punctuation,
numbers, and German compounds.

**Concepts:** pair → containing-words index; incremental merge updates; why a
shared vocabulary suits this language pair.

**Special tokens:** fix the IDs here and keep them consistent across tokenizer,
masks, and loss — `<pad>`=0, `<unk>`=1, `<bos>`=2, `<eos>`=3 (or your choice,
written down).

**Outcome:**

---

## Day 5 — Dataset and DataLoader

**Goal:** Batches of token IDs with correct padding and masks.

**Files:** `src/data/dataset.py`, `src/data/dataloader.py`,
`tests/test_dataset.py`

**Done when:** one batch prints with expected shapes and the pad mask visibly
zeroes the right positions.

**Concepts:** batching by token count vs. sentence count; bucketing by length
to cut padding waste; where the right-shift for decoder input happens.

**Outcome:**

---

## Day 6 — Port the model

**Goal:** Architecture lands in this repo, tests green, nothing rewritten.

**Files:** `src/model/{attention,embedding,layers,encoder,decoder,transformer,masks}.py`,
`src/training/{loss,scheduler}.py`, `tests/`, `docs/notes/`, `conftest.py`

**Done when:** `pytest tests/` is 22 green with no changes to test logic.

**Sequence:** one pure-copy commit citing the source repo and SHA; then split
`Encoder`/`Decoder` out of `layers.py`; then move `LabelSmoothingLoss` into
`src/training/loss.py`; then fix imports. Separate commits, in that order.

**Not ported:** `experiments/overfit.py` — it hardcodes a toy copy task and is
superseded by Day 9.

**Outcome:**

---

## Day 7 — Config and trainer scaffolding

**Goal:** Nothing hardcoded. Model, data, and training hyperparameters all come
from YAML.

**Files:** `configs/base.yaml`, `configs/exp_small.yaml`,
`src/training/trainer.py`, `src/training/utils.py`

**Done when:** two configs produce two differently-sized models with no code
change.

**Concepts:** what belongs in config vs. code; how `max_pairs` and `max_len`
thread through from config to dataset to model.

**Outcome:**

---

## Day 8 — Wire loss, scheduler, and the training step

**Goal:** A single training step runs end to end on a real batch from the real
dataloader.

**Files:** `src/training/trainer.py`, `tests/test_loss.py`

**Done when:** one forward/backward/step completes on real data with real
masks, and the LR curve is plotted across the full planned step count.

**Concepts:** why post-norm needs warmup; gradient clipping; per-token vs.
per-batch loss normalisation.

**Outcome:**

---

## Day 9 — Overfit one batch on real data

**Goal:** Prove the whole stack is wired correctly at real vocabulary size.

**Files:** `scripts/train.py`, `configs/exp_small.yaml`

**Done when:** loss on one fixed batch of BPE-tokenized WMT14 drops to near
zero.

**Why this isn't redundant:** the inherited overfit check ran at V=20,
d_model=32 on synthetic tokens. This runs at V=37000 on real data through the
real dataloader. Different code path, different failure modes.

**Outcome:**

---

## Day 10 — First real training run

**Goal:** Training on the subsample, with checkpointing and resume.

**Files:** `src/training/trainer.py`, `src/training/utils.py`

**Done when:** training is killed mid-run and restarts from checkpoint with no
loss discontinuity.

**Concepts:** what belongs in a checkpoint besides weights (optimizer state,
scheduler step, epoch, RNG state).

**Outcome:**

---

## Day 11 — Training at length

**Goal:** A run long enough to produce a model worth decoding from, plus the
numbers to describe it.

**Files:** `src/training/trainer.py`, `docs/progress.md`

**Done when:** throughput is measured in tokens/sec, validation loss is
tracked, and `max_pairs` is set to something the hardware can actually finish.

**Outcome:**

---

## Day 12 — Greedy decoding

**Goal:** The model emits German.

**Files:** `src/inference/greedy.py`, `scripts/translate.py`

**Done when:** it produces German-shaped output. Quality irrelevant.

**Concepts:** autoregressive decoding; `<bos>`/`<eos>` handling; why
`encode()` is called once and `decode()` repeatedly.

**Outcome:**

---

## Day 13 — Beam search

**Goal:** Beam search with length penalty.

**Files:** `src/inference/beam_search.py`, `tests/test_beam_search.py`

**Done when:** beam output beats greedy on sentences I've read myself.

**Concepts:** why beams need length normalisation; beam size vs. quality;
batching beams efficiently.

**Outcome:**

---

## Day 14 — Evaluation and write-up

**Goal:** A number and a picture.

**Files:** `src/eval/bleu.py`, `src/eval/visualize_attention.py`,
`tests/test_bleu.py`, `README.md`

**Done when:** BLEU on newstest2014 is computed and an attention heatmap is
saved.

**Concepts:** n-gram precision and the brevity penalty; why my number will sit
below the paper's, and exactly which choices account for the gap — subsampled
training data, shorter schedule, smaller effective batch.

**Outcome:**

---

## Slippage log

Days 2 and 4 are the likeliest to run long — Common Crawl cleaning and making
BPE fast enough to finish on 4.5M pairs. Record actual vs. planned here rather
than silently compressing Days 12–14.

| Day | Planned | Actual | Note |
|-----|---------|--------|------|
|     |         |        |      |