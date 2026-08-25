from src.data.tokenizer import to_symbols, count_pairs, merge_pair, learn_bpe
from collections import Counter

def test_to_symbols_appends_end_marker():
    """Assert low gives characters plus the end marker."""
    result = to_symbols("low")
    assert result == ("l", "o", "w", "</w>")


def test_count_pairs_weights_by_frequency():
    """Assert pair counts are weighted by word frequency, not just occurrence."""
    vocab = {("l", "o", "w", "</w>"): 5}
    counts = count_pairs(vocab)
    assert counts[("l", "o")] == 5


def test_count_pairs_sums_across_multiple_words():
    """Assert total is the sum when multiple words share a pair."""
    vocab = {
        ("l", "o", "w", "</w>"): 5,
        ("l", "o", "w", "e", "r", "</w>"): 2
    }
    counts = count_pairs(vocab)
    assert counts[("l", "o")] == 7


def test_merge_pair_glues_adjacent_symbols():
    """Assert adjacent symbols are merged and vocabulary frequency is unchanged."""
    vocab = {("l", "o", "w", "</w>"): 5}
    pair = ("l", "o")
    
    updated_vocab = merge_pair(pair, vocab)
    
    assert ("lo", "w", "</w>") in updated_vocab
    assert updated_vocab[("lo", "w", "</w>")] == 5


def test_learn_bpe_matches_paper_example():
    """Assert BPE matches the classic paper example over 6 iterations."""
    wf = Counter({"low": 5, "lower": 2, "newest": 6, "widest": 3})

    merges, _ = learn_bpe(wf, 6)
    
    assert merges == [
        ("e", "s"), ("es", "t"), ("est", "</w>"),
        ("l", "o"), ("lo", "w"), ("e", "w"),
    ]


def test_end_marker_prevents_cross_word_merges():
    """Assert the end marker stops words from bleeding into each other."""
    wf = Counter({"low": 5, "lower": 2, "newest": 6, "widest": 3})
    
    _, final_vocab = learn_bpe(wf, 6)
    
    expected_lower_tuple = ("low", "e", "r", "</w>")
    assert expected_lower_tuple in final_vocab