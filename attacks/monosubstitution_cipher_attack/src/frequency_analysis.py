"""
frequency_analysis.py -- Frequency & Pattern Analysis for Monoalphabetic Ciphers
==================================================================================
Lab 5 | CryptoLabX Group 01 | 22CPP307

Required functions (as per Assignment 5):
    frequency_analysis(ciphertext)         -> sorted list of (letter, count, %)
    word_frequency_analysis(ciphertext)    -> dict grouped by word length
    pattern_analysis(ciphertext)           -> list of (word, pattern, candidates)

No library functions used for the analysis logic itself.
"""

import string

ALPHABET = string.ascii_uppercase

# ------------------------------------------------------------------
# English reference data (for display/comparison — no library calls)
# ------------------------------------------------------------------
ENGLISH_FREQ_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

COMMON_1 = {"A", "I"}
COMMON_2 = {"OF", "TO", "IN", "IS", "IT", "BE", "AS", "AT", "SO",
            "WE", "HE", "BY", "OR", "ON", "DO", "IF", "ME", "MY",
            "UP", "AN", "GO", "NO", "US", "AM"}
COMMON_3 = {"THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
            "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET",
            "HAS", "HIM", "HIS", "HOW", "ITS", "LET", "MAN", "NEW",
            "NOW", "OLD", "SEE", "TWO", "WAY", "WHO", "DID", "PUT",
            "SAY", "SHE", "TOO", "USE", "HAD", "HIM", "ITS", "MAY"}


# ===========================================================================
# 1. frequency_analysis
# ===========================================================================
def frequency_analysis(ciphertext: str) -> list[tuple[str, int, float]]:
    """
    Count and rank every letter in the ciphertext by frequency.

    Steps (no library functions):
        1. Strip to letters only, uppercase
        2. Count each A-Z manually
        3. Calculate percentage of each
        4. Sort descending by count
        5. Print a formatted bar chart + table
        6. Return sorted list of (letter, count, percent)

    Args:
        ciphertext : str -- the encrypted text (any case, spaces/punct ok)

    Returns:
        List of tuples (letter, count, percent) sorted highest-count first
    """
    # Step 1 -- extract letters only
    letters = [ch.upper() for ch in ciphertext if ch.isalpha()]
    total = len(letters)

    if total == 0:
        print("  [!] No alphabetic characters found in ciphertext.")
        return []

    # Step 2 -- count each A-Z
    counts = {}
    for letter in ALPHABET:
        counts[letter] = 0
    for letter in letters:
        counts[letter] += 1

    # Step 3 -- percentages
    results = []
    for letter in ALPHABET:
        pct = (counts[letter] / total) * 100
        results.append((letter, counts[letter], pct))

    # Step 4 -- sort descending by count
    results.sort(key=lambda x: x[1], reverse=True)

    # Step 5 -- print table
    W = "\033[1m"; C = "\033[96m"; G = "\033[92m"; Y = "\033[93m"; X = "\033[0m"
    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  LETTER FREQUENCY ANALYSIS{X}")
    print(f"  Total letters in ciphertext: {total}")
    print(f"{C}{'='*60}{X}")
    print(f"  {'Rank':<5} {'CT':<5} {'Count':<8} {'%':<8} {'Bar'}")
    print(f"  {'-'*55}")

    for rank, (letter, count, pct) in enumerate(results, 1):
        bar_len = int(pct * 2)          # scale: 2 chars per percent
        bar = G + '#' * bar_len + X
        print(f"  {rank:<5} {Y}{letter}{X}     {count:<8} {pct:<8.2f} {bar}")

    print(f"\n  {W}Frequency order (high to low):{X} ", end="")
    print(" ".join(r[0] for r in results))
    print(f"  {W}English reference order:     {X}  {ENGLISH_FREQ_ORDER}")
    print(f"{C}{'='*60}{X}\n")

    return results


# ===========================================================================
# 2. word_frequency_analysis
# ===========================================================================
def word_frequency_analysis(ciphertext: str) -> dict[str, list[tuple[str, int]]]:
    """
    Identify and count words in the ciphertext, grouped by word length.

    Steps:
        1. Split ciphertext into words, strip punctuation, uppercase
        2. Group by length: 1-letter, 2-letter, 3-letter, 4-letter, longer
        3. Count each unique word per group
        4. Sort each group by count descending
        5. Print results + highlight English candidates
        6. Return dict keyed by length label

    Args:
        ciphertext : str -- encrypted text

    Returns:
        Dict { "1-letter": [(word, count), ...],
               "2-letter": [...],
               "3-letter": [...],
               "4-letter": [...],
               "longer"  : [...] }
    """
    # Step 1 -- extract and clean words
    punct = ".,!?;:\"'()-"
    raw_words = ciphertext.upper().split()
    cleaned = []
    for w in raw_words:
        stripped = w.strip(punct)
        if stripped.isalpha():
            cleaned.append(stripped)

    if not cleaned:
        print("  [!] No words found.")
        return {}

    # Step 2 & 3 -- group and count
    groups: dict[str, dict[str, int]] = {
        "1-letter": {}, "2-letter": {}, "3-letter": {},
        "4-letter": {}, "longer":   {}
    }

    for word in cleaned:
        length = len(word)
        if length == 1:
            key = "1-letter"
        elif length == 2:
            key = "2-letter"
        elif length == 3:
            key = "3-letter"
        elif length == 4:
            key = "4-letter"
        else:
            key = "longer"
        groups[key][word] = groups[key].get(word, 0) + 1

    # Step 4 -- sort each group
    sorted_groups: dict[str, list[tuple[str, int]]] = {}
    for key, word_dict in groups.items():
        sorted_groups[key] = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)

    # Step 5 -- print
    W = "\033[1m"; C = "\033[96m"; G = "\033[92m"; Y = "\033[93m"; X = "\033[0m"
    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  WORD FREQUENCY ANALYSIS{X}")
    print(f"{C}{'='*60}{X}")

    hints = {
        "1-letter": f"English candidates: {', '.join(sorted(COMMON_1))}",
        "2-letter": f"Common: OF TO IN IS IT BE AS AT ...",
        "3-letter": f"Most common: THE AND FOR ARE ...",
        "4-letter": f"Common: THAT WITH FROM THEY BEEN ...",
        "longer":   f"Context-dependent",
    }

    for group_name, word_list in sorted_groups.items():
        if not word_list:
            continue
        print(f"\n  {W}{group_name.upper()} WORDS{X}  ({hints[group_name]})")
        print(f"  {'Word':<15} {'Count':<8} {'Candidate?'}")
        print(f"  {'-'*45}")
        for word, count in word_list[:10]:   # top 10 per group
            if group_name == "1-letter":
                candidate = "a / i" if count > 0 else "-"
            elif group_name == "2-letter":
                candidate = "likely common 2-letter word" if count >= 2 else "-"
            elif group_name == "3-letter":
                candidate = "'the' if most frequent" if word_list[0][0] == word else "-"
            else:
                candidate = "-"
            print(f"  {Y}{word:<15}{X} {count:<8} {G}{candidate}{X}")

    print(f"{C}{'='*60}{X}\n")
    return sorted_groups


# ===========================================================================
# 3. pattern_analysis
# ===========================================================================
def _word_to_pattern(word: str) -> str:
    """
    Convert a word to a numeric pattern.
    Example: "QIIQX" -> "01102"
             "QFFQR" -> "01102"  (same pattern as above — repeated structure)
    """
    mapping = {}
    counter = 0
    pattern = []
    for ch in word:
        if ch not in mapping:
            mapping[ch] = str(counter)
            counter += 1
        pattern.append(mapping[ch])
    return "".join(pattern)


# Pre-built pattern→English-word dictionary for common patterns
# (manual -- no library calls)
_PATTERN_DICT: dict[str, list[str]] = {
    "0":        ["a", "i"],
    "01":       ["of", "to", "in", "is", "it", "be", "as", "at", "so",
                 "we", "he", "by", "or", "on", "do", "if", "me", "my",
                 "up", "an", "go", "no", "us", "am"],
    "012":      ["the", "and", "for", "are", "but", "not", "you", "all",
                 "can", "her", "was", "one", "our", "out", "day", "get",
                 "has", "him", "his", "how", "its", "let", "man", "new",
                 "now", "old", "see", "two", "way", "who", "did", "put"],
    "0110":     ["that", "noon", "deed"],
    "0123":     ["then", "from", "they", "been", "more", "also", "into",
                 "some", "time", "very", "when", "your", "each", "only",
                 "over", "such", "even", "most"],
    "0122":     ["less", "call", "tell", "well", "fall", "fill", "kill",
                 "will", "ball", "bell", "bull", "full", "hall", "hill",
                 "mill", "pull", "roll", "sell", "tall", "wall"],
    "01023":    ["there", "where", "these", "those", "their", "other"],
    "01234":    ["which", "about", "would", "could", "should", "every",
                 "after", "first", "being", "given", "since"],
    "010234":   ["secret", "system", "simple"],
    "0123456":  ["encrypt", "decrypt", "message", "plaintext"[:7]],
}


def pattern_analysis(ciphertext: str) -> list[tuple[str, str, list[str]]]:
    """
    Analyse word patterns in ciphertext and suggest English word candidates.

    For each unique ciphertext word:
        1. Compute the pattern (e.g. "0110" for "ABBA"-style words)
        2. Look up the pattern in the known pattern dictionary
        3. Return candidate English words

    Args:
        ciphertext : str -- encrypted text

    Returns:
        List of (ciphertext_word, pattern, [candidate_english_words])
        Sorted by (pattern_match_found DESC, word_length DESC)
    """
    punct = ".,!?;:\"'()-"
    raw_words = ciphertext.upper().split()
    unique_words = {}
    for w in raw_words:
        stripped = w.strip(punct)
        if stripped.isalpha():
            unique_words[stripped] = unique_words.get(stripped, 0) + 1

    results = []
    for word, count in sorted(unique_words.items(), key=lambda x: -x[1]):
        pat = _word_to_pattern(word)
        candidates = _PATTERN_DICT.get(pat, [])
        results.append((word, pat, count, candidates))

    # Print
    W = "\033[1m"; C = "\033[96m"; G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"; X = "\033[0m"
    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  PATTERN ANALYSIS{X}")
    print(f"{C}{'='*60}{X}")
    print(f"  {'CT Word':<15} {'Cnt':<5} {'Pattern':<12} {'English Candidates'}")
    print(f"  {'-'*60}")

    for word, pat, count, candidates in results[:25]:   # top 25
        cands_str = ", ".join(candidates[:6]) if candidates else f"{R}(no match){X}"
        match_col = G if candidates else R
        print(f"  {Y}{word:<15}{X} {count:<5} {pat:<12} {match_col}{cands_str}{X}")

    print(f"\n  {W}Key insight:{X} Most frequent short word is likely 'THE' or 'AND'.")
    print(f"  Single-letter words are always 'A' or 'I'.")
    print(f"{C}{'='*60}{X}\n")

    return [(w, p, c) for w, p, _, c in results]


# ===========================================================================
# Standalone demo
# ===========================================================================
if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(__file__))
    from monosubstitution_cipher import generate_random_key, encrypt

    # Load plaintext
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "plaintext_source.txt")
    with open(data_path, "r", encoding="utf-8") as f:
        plaintext = f.read()

    key = generate_random_key()
    ciphertext = encrypt(plaintext, key).upper()

    print(f"Plaintext (first 100 chars): {plaintext[:100]}")
    print(f"Ciphertext (first 100 chars): {ciphertext[:100]}")

    freq = frequency_analysis(ciphertext)
    word_freq = word_frequency_analysis(ciphertext)
    patterns = pattern_analysis(ciphertext)
