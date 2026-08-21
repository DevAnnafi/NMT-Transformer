import re
import unicodedata
import py3langid as langid
from src.data.download import extract_corpus
from pathlib import Path

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

def is_expected_language(src: str, tgt: str, src_lang: str, tgt_lang: str) -> bool:
    src_result = langid.classify(src)[0]
    tgt_result = langid.classify(tgt)[0]
    return src_result == src_lang and tgt_result == tgt_lang

def is_not_duplicate(src: str, tgt: str, seen: set) -> bool:
    key = (src, tgt) 
    if key in seen:
        return False
    seen.add(key)
    return True

def clean_corpus(entry, cfg) -> dict:
    src_file, tgt_file = extract_corpus(entry, cfg)

    processed_dir = Path(cfg["data"]["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)
    src_lang = cfg["data"]["src_lang"]
    tgt_lang = cfg["data"]["tgt_lang"]
    src_out = processed_dir / f"{entry['name']}.{src_lang}"
    tgt_out = processed_dir / f"{entry['name']}.{tgt_lang}"

    cleaning = cfg["cleaning"]
    min_len = cleaning["min_len"]
    max_len = cleaning["max_len"]
    max_len_ratio = cleaning["max_len_ratio"]
    max_token_chars = cleaning["max_token_chars"]
    language_id = cleaning["language_id"]
    language_id_min_tokens = cleaning["language_id_min_tokens"]

    seen = set()
    stats = {
        "total": 0,
        "empty": 0,
        "length": 0,
        "ratio": 0,
        "giant_token": 0,
        "language": 0,
        "duplicate": 0,
        "kept": 0,
    }

    with open(src_file, encoding="utf-8", newline="\n") as fs, \
         open(tgt_file, encoding="utf-8", newline="\n") as ft, \
         open(src_out, "w", encoding="utf-8") as os_, \
         open(tgt_out, "w", encoding="utf-8") as ot:

        for s, t in zip(fs, ft):
            stats["total"] += 1

            s = normalize(s)
            t = normalize(t)

            if not is_non_empty(s, t):
                stats["empty"] += 1
                continue

            if not within_length(s, t, min_len, max_len):
                stats["length"] += 1
                continue

            if not within_ratio(s, t, max_len_ratio):
                stats["ratio"] += 1
                continue

            if not (has_no_giant_token(s, max_token_chars)
                    and has_no_giant_token(t, max_token_chars)):
                stats["giant_token"] += 1
                continue

            if (language_id
                    and len(s.split()) >= language_id_min_tokens
                    and len(t.split()) >= language_id_min_tokens
                    and not is_expected_language(s, t, src_lang, tgt_lang)):
                stats["language"] += 1
                continue

            if not is_not_duplicate(s, t, seen):
                stats["duplicate"] += 1
                continue

            os_.write(s + "\n")
            ot.write(t + "\n")
            stats["kept"] += 1

    return stats
    



    
