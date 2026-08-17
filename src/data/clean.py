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