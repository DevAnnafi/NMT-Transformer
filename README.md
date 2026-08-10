# NMT Transformer — From Scratch

A Neural Machine Translation system built entirely from scratch in PyTorch,
implementing the Transformer architecture from
["Attention Is All You Need"](https://arxiv.org/abs/1706.03762) with no
high-level seq2seq or modeling libraries. The goal is translating En→De
while understanding — and being able to explain — every component:
attention, positional encoding, the encoder/decoder stack, training
dynamics, and beam search decoding.

This project extends an earlier from-scratch Transformer implementation
(`attention-from-scratch`) into a full end-to-end MT pipeline.

## Why from scratch

Frameworks like HuggingFace `transformers` make this a 10-line script.
The point here isn't the shortest path to a working translator — it's
building every piece by hand (attention, masking, the training loop,
decoding) to actually understand what's happening instead of trusting
an abstraction.

## Status

🚧 Actively in progress. See [`docs/progress.md`](docs/progress.md) for a
running log of decisions, bugs, and results.

## Pipeline

1. **Data** — download, clean, and filter a WMT En-De corpus
2. **Tokenizer** — BPE tokenizer trained from scratch on the corpus
3. **Dataset/DataLoader** — token-count batching, length bucketing
4. **Model** — encoder-decoder Transformer (multi-head attention, positional
   encoding, Add & Norm, feed-forward blocks)
5. **Training** — label smoothing, LR warmup+decay, gradient clipping,
   checkpointing
6. **Inference** — greedy decoding, then beam search
7. **Evaluation** — BLEU (via `sacrebleu`), qualitative error analysis,
   attention map visualization

## Project structure

```
nmt-transformer/
├── data/
│   ├── raw/            # untouched downloaded corpora
│   └── processed/      # cleaned, filtered, tokenized data
├── src/
│   ├── data/           # download, clean, tokenizer training, Dataset/DataLoader
│   ├── model/          # Transformer implementation
│   ├── training/       # training loop, schedulers, checkpointing
│   ├── inference/      # greedy decode, beam search
│   └── eval/           # BLEU scoring, attention visualization
├── tests/              # unit tests for each component
├── configs/            # YAML configs for experiments
├── scripts/            # CLI entry points (train.py, translate.py, evaluate.py)
└── docs/               # progress log, notes
```

## Setup

\```bash
git clone https://github.com/<your-username>/nmt-transformer.git
cd nmt-transformer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\```

## Usage

_(fill in as scripts land — e.g. `python scripts/train.py --config configs/base.yaml`)_

## Results

_(BLEU scores and comparison to the original paper, once training is done)_

## Roadmap

- [ ] Data pipeline + tokenizer
- [ ] Dataset/DataLoader + model wiring
- [ ] Training runs + debugging
- [ ] Beam search, evaluation, writeup

## License

MIT
