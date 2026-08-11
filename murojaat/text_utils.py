"""
text_utils.py
─────────────
Normalizes Uzbek Latin text (apostrophe variants, common typos, casing)
and provides stem-based phrase matching so "passportimni", "pasportim",
"pasport" all match the keyword "pasport".
"""
import re

# Uzbek Latin has multiple "valid" apostrophe-like characters that all mean
# the same thing to a human but are different bytes to a computer.
APOSTROPHE_VARIANTS = ["'", "’", "ʻ", "ʼ", "‘", "`"]

# Common doubled-consonant / transliteration typos seen in real user input.
# Add to this list as you observe more patterns in production logs.
TYPO_FIXES = [
    (r"\bpass+port", "pasport"),      # passport, passsport -> pasport
    (r"\bxujjat", "hujjat"),          # x/h confusion
    (r"\bqarindosh+", "qarindosh"),
]

def normalize_text(text: str) -> str:
    """Lowercase, unify apostrophes, fix common typos. Always run before matching."""
    t = text.lower()
    for variant in APOSTROPHE_VARIANTS:
        t = t.replace(variant, "'")
    for pattern, replacement in TYPO_FIXES:
        t = re.sub(pattern, replacement, t)
    # collapse repeated letters that aren't meaningful in Uzbek (e.g. "salomm")
    # be conservative: only 3+ repeats, since doubled letters ARE valid (masalan "kkk" rare)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)
    return t

def normalize_apostrophes(text: str) -> str:
    """Unify apostrophe variants without lowercasing or typo-fixing — for display/keywords."""
    t = text
    for variant in APOSTROPHE_VARIANTS:
        t = t.replace(variant, "'")
    return t


def _stem(word: str, min_stem_len: int = 4) -> str:
    """
    Very lightweight Uzbek suffix stripper — not linguistically complete,
    but enough to collapse pasport/pasportim/pasportimni/pasportga to one form.
    """
    suffixes = [
        "imni", "ingni", "imiz", "ingiz", "lari", "lar",
        "ni", "ga", "da", "dan", "im", "ing", "i", "m",
    ]
    for suf in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suf) and len(word) - len(suf) >= min_stem_len:
            return word[: -len(suf)]
    return word


def phrase_in_text(phrase: str, text_normalized: str, fuzzy: bool = True) -> bool:
    """
    Stem-aware substring/word match. Replaces `kw.lower() in text_lower`.
    - Multi-word phrases (e.g. "nikoh guvohnoma") still use substring match,
      since stemming phrase-by-phrase is unnecessary — the risk is single
      keyword+suffix mismatches, not phrase mismatches.
    - Single-word keywords are matched against every stemmed token in the text.
    """
    phrase_norm = normalize_text(phrase)

    if " " in phrase_norm:
        return phrase_norm in text_normalized

    phrase_stem = _stem(phrase_norm)
    tokens = re.findall(r"[a-z']+", text_normalized)
    for tok in tokens:
        if _stem(tok) == phrase_stem:
            return True
        if fuzzy and _fuzzy_close(tok, phrase_norm):
            return True
    return False


def _fuzzy_close(a: str, b: str, max_edits: int = 1) -> bool:
    """Cheap edit-distance check for short typos (e.g. one dropped/extra letter)."""
    if abs(len(a) - len(b)) > max_edits:
        return False
    # simple Levenshtein, fine for short government-vocab words
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1] <= max_edits