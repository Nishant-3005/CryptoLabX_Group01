"""
frequency_analysis.py -- IC Calculation, Chi-Squared Key Recovery
==================================================================
Lab 6 | CryptoLabX Group 01 | 22CPP307

Once the key length m is known (from Kasiski), the Vigenere cipher reduces to
m independent Caesar ciphers. Every m-th character in the ciphertext was
encrypted with the same key letter.

Attack per group:
    1. split_into_groups() -- split ciphertext into m groups
    2. For each group, find_shift() via chi-squared test
       (the shift with lowest chi-sq score = best fit to English)
    3. find_key() -- combine all shifts into the key string

The Index of Coincidence (IC) is also used to confirm the key length:
    IC for English text ~ 0.0667
    IC for random text  ~ 0.0385
    The correct key length produces groups whose IC is close to 0.0667.
"""

from collections import Counter

# ── Reference values ─────────────────────────────────────────────────────────
ENGLISH_FREQ = {
    'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253,
    'E': 0.12702, 'F': 0.02228, 'G': 0.02015, 'H': 0.06094,
    'I': 0.06966, 'J': 0.00153, 'K': 0.00772, 'L': 0.04025,
    'M': 0.02406, 'N': 0.06749, 'O': 0.07507, 'P': 0.01929,
    'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
    'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150,
    'Y': 0.01974, 'Z': 0.00074,
}

ENGLISH_IC = 0.0667   # expected IC for natural English text

# ANSI colour helpers
W = "\033[1m"
C = "\033[96m"
G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
X = "\033[0m"


# ─────────────────────────────────────────────────────────────────────────────
def calculate_ic(text: str) -> float:
    """
    Calculate the Index of Coincidence for a text string.

    Formula:   IC = SUM_i [ n_i * (n_i - 1) ] / [ N * (N - 1) ]

    where n_i = count of letter i (A-Z), N = total letter count.

    Args:
        text: Any string (non-alpha characters ignored)

    Returns:
        IC as a float. English text ~ 0.0667; random text ~ 0.0385.
        Returns 0.0 if fewer than 2 letters.
    """
    letters = [ch for ch in text.upper() if ch.isalpha()]
    N = len(letters)
    if N < 2:
        return 0.0

    counts = Counter(letters)
    numerator = sum(n * (n - 1) for n in counts.values())
    return numerator / (N * (N - 1))


# ─────────────────────────────────────────────────────────────────────────────
def split_into_groups(ciphertext: str, key_length: int) -> list:
    """
    Split ciphertext into key_length groups (columns of a matrix transposition).

    Group j contains every character at position j, j+m, j+2m, j+3m, ...
    i.e. all positions ≡ j (mod key_length).

    Args:
        ciphertext : Clean uppercase string (no spaces)
        key_length : Estimated Vigenere key length m

    Returns:
        List of key_length strings, one per group.

    Example (key_length=3, ciphertext="ABCDEFGHI"):
        group 0 = "ADG"  (positions 0, 3, 6)
        group 1 = "BEH"  (positions 1, 4, 7)
        group 2 = "CFI"  (positions 2, 5, 8)
    """
    return [ciphertext[j::key_length] for j in range(key_length)]


# ─────────────────────────────────────────────────────────────────────────────
def frequency_analysis(text: str) -> list:
    """
    Count A-Z letter frequencies in text and return a sorted table.

    Args:
        text: Any string (non-alpha ignored, case-insensitive)

    Returns:
        List of tuples [(letter, count, percentage), ...]
        sorted by count descending.

    Also prints a formatted frequency table to the terminal.
    """
    letters = [ch for ch in text.upper() if ch.isalpha()]
    total   = len(letters)
    counts  = Counter(letters)

    result = []
    for letter in sorted(counts.keys(), key=lambda l: counts[l], reverse=True):
        pct = counts[letter] / total * 100 if total > 0 else 0
        result.append((letter, counts[letter], pct))

    # Print formatted table
    print(f"  {'Letter':<8} {'Count':<8} {'Percent':<10} {'Bar'}")
    print(f"  {'-'*45}")
    max_c = result[0][1] if result else 1
    for letter, count, pct in result:
        bar = "#" * int(count / max_c * 20)
        print(f"  {letter:<8} {count:<8} {pct:<10.2f} {bar}")
    print(f"  Total letters: {total}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
def find_shift(group: str) -> int:
    """
    Find the best Caesar shift for a single Vigenere group using chi-squared.

    For each candidate shift s (0-25):
        1. "Un-shift" the group by s positions (i.e. decrypt with key letter s)
        2. Compute chi-squared statistic vs ENGLISH_FREQ

    Return the shift s with the LOWEST chi-squared value (best English fit).

    The shift s corresponds to the numeric value of the key letter:
        s=0 -> key letter A, s=1 -> key letter B, ..., s=25 -> key letter Z

    Args:
        group: A string containing only one "column" of the ciphertext

    Returns:
        int in [0, 25] — the most likely key letter value for this group
    """
    letters = [ch for ch in group.upper() if ch.isalpha()]
    N = len(letters)
    if N == 0:
        return 0

    best_shift  = 0
    best_chi_sq = float('inf')

    for s in range(26):
        # Decrypt this group assuming the key letter is chr(s + ord('A'))
        decrypted = [(ord(ch) - ord('A') - s) % 26 for ch in letters]
        counts    = Counter(decrypted)

        chi_sq = 0.0
        for i in range(26):
            letter   = chr(i + ord('A'))
            observed = counts.get(i, 0)
            expected = ENGLISH_FREQ[letter] * N
            if expected > 0:
                chi_sq += (observed - expected) ** 2 / expected

        if chi_sq < best_chi_sq:
            best_chi_sq = chi_sq
            best_shift  = s

    return best_shift


# ─────────────────────────────────────────────────────────────────────────────
def find_key(ciphertext: str, key_length: int) -> str:
    """
    Recover the Vigenere key by analysing each group independently.

    Steps:
        1. split_into_groups(ciphertext, key_length)
        2. For each group: find_shift() -> key letter value
        3. Convert each shift to a letter (0->A, 1->B, ...)
        4. Concatenate to form the key string

    Also prints:
        - IC value for each group
        - Top 3 frequency letters in each group
        - Shift recovered and corresponding key letter

    Args:
        ciphertext : Clean uppercase ciphertext
        key_length : Key length to use (from Kasiski analysis)

    Returns:
        Recovered key as uppercase string (e.g. "LEMON")
    """
    groups = split_into_groups(ciphertext, key_length)
    key_letters = []

    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  FREQUENCY ANALYSIS — KEY RECOVERY (key length = {key_length}){X}")
    print(f"{C}{'='*60}{X}")

    for i, group in enumerate(groups):
        letters = [ch for ch in group.upper() if ch.isalpha()]
        ic      = calculate_ic(group)
        counts  = Counter(letters)
        top3    = [letter for letter, _ in counts.most_common(3)]
        shift   = find_shift(group)
        key_ch  = chr(shift + ord('A'))

        print(f"\n{Y}  Group {i+1} (positions {i}, {i+key_length}, {i+2*key_length}, ...){X}")
        print(f"  Length: {len(letters)}  |  IC: {ic:.4f}  |  Top letters: {' '.join(top3)}")
        print(f"  {G}Best shift: {shift}  ->  Key letter: {key_ch}{X}")

        key_letters.append(key_ch)

    recovered_key = "".join(key_letters)
    print(f"\n{G}{W}  Recovered Key: {recovered_key}{X}")
    print(f"{C}{'='*60}{X}\n")

    return recovered_key


# ─────────────────────────────────────────────────────────────────────────────
def ic_analysis(ciphertext: str, max_key_length: int = 15) -> int:
    """
    Compute IC for each candidate key length 2..max_key_length.
    The key length whose average group IC is closest to ENGLISH_IC is best.

    Prints a table and returns the best candidate key length.

    Args:
        ciphertext    : Clean uppercase ciphertext
        max_key_length: Largest key length to test

    Returns:
        Best candidate key length (int)
    """
    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  INDEX OF COINCIDENCE ANALYSIS{X}")
    print(f"{C}{'='*60}{X}")
    print(f"  English IC = {ENGLISH_IC}  |  Random IC ~ 0.0385")
    print(f"\n  {'Key Len':<10} {'Avg IC':<12} {'Diff from Eng':<16} {'Bar'}")
    print(f"  {'-'*55}")

    best_len  = 2
    best_diff = float('inf')
    results   = []

    for m in range(2, max_key_length + 1):
        groups   = split_into_groups(ciphertext, m)
        avg_ic   = sum(calculate_ic(g) for g in groups) / m
        diff     = abs(avg_ic - ENGLISH_IC)
        results.append((m, avg_ic, diff))
        if diff < best_diff:
            best_diff = diff
            best_len  = m

    for m, avg_ic, diff in results:
        bar    = "#" * int((1 - diff / 0.04) * 20) if diff < 0.04 else ""
        marker = f"  {G}<-- BEST{X}" if m == best_len else ""
        print(f"  {m:<10} {avg_ic:<12.4f} {diff:<16.4f} {bar}{marker}")

    print(f"\n{G}  [+] Best key length by IC: {best_len}{X}")
    print(f"{C}{'='*60}{X}\n")
    return best_len
