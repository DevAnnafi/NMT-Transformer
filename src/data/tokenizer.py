from collections import Counter
from pathlib import Path

END_OF_WORD = "</w>"

def build_word_freqs(paths: list[Path]) -> Counter:
    """Count whitespace-separated word types across the given files.
    
    Both languages go in together — the paper uses a shared En-De vocabulary.
    Returns {word: frequency}, which is what every later step operates on 
    rather than the corpus itself.
    """
    word_freqs = Counter()
    for path in paths:
        with open(path, "r", encoding="utf-8", newline="\n") as f:
            for line in f:
                word_freqs.update(line.split())
    return word_freqs

def to_symbols(word: str) -> tuple[str, ...]:
    """Split a word into its starting symbols: one per character, plus </w>.
    
    The end-of-word marker is what stops 'low' and 'lower' sharing a merge 
    that treats the 'low' inside 'lower' as a complete word.
    """
    return tuple(list(word) + [END_OF_WORD])

def count_pairs(vocab: dict[tuple[str, ...], int]) -> Counter:
    """Count every adjacent symbol pair, weighted by word frequency.
    
    vocab maps a symbol tuple to how often that word occurs.
    For each word, walk its symbols and count each (symbol[i], symbol[i+1]) pair, 
    adding the word's frequency rather than 1.
    """
    pair_counts = Counter()
    for symbols, freq in vocab.items():
        for i in range(len(symbols) - 1):
            pair = (symbols[i], symbols[i + 1])
            pair_counts[pair] += freq
    return pair_counts

def merge_pair(pair: tuple[str, str], vocab: dict[tuple[str, ...], int]) -> dict[tuple[str, ...], int]:
    """Apply one merge across the whole vocabulary.
    
    Returns a new vocab where every occurrence of the two symbols adjacent 
    to each other has been replaced by their concatenation.
    Frequencies are unchanged — only the symbol sequences change.
    """
    new_vocab = Counter()
    target_first, target_second = pair
    replacement = target_first + target_second

    for symbols, freq in vocab.items():
        new_symbols = []
        i = 0
        while i < len(symbols):
            # Check if we match the target pair at the current position
            if i < len(symbols) - 1 and symbols[i] == target_first and symbols[i + 1] == target_second:
                new_symbols.append(replacement)
                i += 2  # Skip both matched symbols
            else:
                new_symbols.append(symbols[i])
                i += 1
        new_vocab[tuple(new_symbols)] += freq
        
    return new_vocab

def learn_bpe(word_freqs: Counter, num_merges: int) -> list[tuple[str, str]]:
    """Learn merge rules. Returns them in order — order is the algorithm.
    
    1. Build the initial vocab: to_symbols() on each word, keeping frequencies
    2. Repeat num_merges times:
       - count_pairs()
       - take the most frequent pair (ties broken lexicographically)
       - record it
       - merge_pair() to get the new vocab
    """
    # 1. Build initial vocab mapping symbol tuples to their frequencies
    vocab = {to_symbols(word): freq for word, freq in word_freqs.items()}
    merges = []

    # 2. Iteratively find and merge the most frequent pairs
    for _ in range(num_merges):
        pair_counts = count_pairs(vocab)
        if not pair_counts:
            break  # No more pairs left to merge

        # Tie-breaking logic: Max frequency first. 
        # If frequencies match, sorted() defaults to a stable lexicographical sort on the pair tuple.
        best_pair = max(sorted(pair_counts.keys()), key=lambda p: pair_counts[p])
        
        merges.append(best_pair)
        vocab = merge_pair(best_pair, vocab)

    return merges, vocab
