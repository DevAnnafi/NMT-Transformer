import re
import unicodedata

def normalize(text: str) -> str:
    """Normalise one line of corpus text. Returns the cleaned string."""
    text = unicodedata.normalize("NFKC", text)

    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    mapping = {
        '\u2019': "'",  
        '\u201c': '"',  
        '\u201d': '"',  
        '\u201e': '"',  
        '\u00ad' : None
    }

    translation_table = str.maketrans(mapping)

    text = text.translate(translation_table)

    collapsed = re.sub(r"\s+", " ", text)

    return collapsed.strip()

cases = [
    "des Goldes  hinwiesen",       # double space collapses
    "verzehnfachen?  ",            # trailing space stripped
    "it\u00adwill",                # soft hyphen deleted -> "itwill"
    "\u201eFreak Peak\u201c",      # German quotes -> straight
    "gold\u2019s risks",           # curly apostrophe -> straight
    "10.000 Dollar",               # UNCHANGED
    "$10,000",                     # UNCHANGED
]
for c in cases:
    print(repr(c), "->", repr(normalize(c)))

def is_non_empty(src, tgt):
    return bool(src) and bool(tgt)

def within_length(src, tgt, min_len, max_len):
    src_len = len(src.split())
    tgt_len = len(tgt.split())
    return (min_len <= src_len <= max_len) and (min_len <= tgt_len <= max_len)

def within_ratio(src, tgt, max_ratio):
    src_len = len(src.split())
    tgt_len = len(tgt.split())
    if src_len == 0 or tgt_len == 0:
        return False  
    ratio = max(src_len, tgt_len) / min(src_len, tgt_len)
    return ratio <= max_ratio

def has_no_giant_token(text, max_chars):
    tokens = text.split()
    if not tokens:
        return True  
    max_len = max(len(w) for w in tokens)
    return max_len < max_chars


