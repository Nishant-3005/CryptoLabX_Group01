"""
chi_square_attack.py — Chi-Square Statistical Cryptanalysis of the Shift Cipher
================================================================================
Lab 4 | CryptoLabX Group 01 | 22CPP307

Algorithm:
  For each of the 26 possible keys k (0..25):
    1. Decrypt the ciphertext with key k  →  candidate plaintext
    2. Count observed frequency of each letter (A-Z) in the candidate
    3. Compute expected frequency of each letter using standard English
       letter frequency distribution
    4. Calculate Chi-Square statistic:

         χ²(k) = Σ  (Observed_i - Expected_i)²
                i=A      ─────────────────────
                           Expected_i

    5. The key with the LOWEST χ² score is the best fit to English,
       and is therefore the most likely decryption key.

Complexity: O(26 × n)  where n = length of ciphertext

Imported by:
    main.py
"""

from shift_cipher import decrypt, ALPHABET_SIZE


# ── Standard English letter frequencies (%) — Lewand 2000 reference ──────────
# Index 0 = 'A', index 1 = 'B', ... index 25 = 'Z'
ENGLISH_FREQ = [
    8.167,  # A
    1.492,  # B
    2.782,  # C
    4.253,  # D
    12.702, # E
    2.228,  # F
    2.015,  # G
    6.094,  # H
    6.966,  # I
    0.153,  # J
    0.772,  # K
    4.025,  # L
    2.406,  # M
    6.749,  # N
    7.507,  # O
    1.929,  # P
    0.095,  # Q
    5.987,  # R
    6.327,  # S
    9.056,  # T
    2.758,  # U
    0.978,  # V
    2.360,  # W
    0.150,  # X
    1.974,  # Y
    0.074,  # Z
]


def count_letter_frequencies(text: str) -> list[int]:
    """
    Count the raw occurrence of each letter A-Z in `text` (case-insensitive).
    Returns a list of 26 integers.
    """
    counts = [0] * ALPHABET_SIZE
    for ch in text.upper():
        if ch.isalpha():
            counts[ord(ch) - ord('A')] += 1
    return counts


def chi_square_statistic(text: str) -> float:
    """
    Compute the Chi-Square statistic comparing the letter frequency distribution
    of `text` against the expected English letter frequency distribution.

    A LOWER value means the text is MORE likely to be valid English.

    Formula:
        χ² = Σ (O_i - E_i)² / E_i    for i in A..Z

    where:
        O_i = observed count of letter i in text
        E_i = expected count based on English frequency × total letter count
    """
    observed   = count_letter_frequencies(text)
    total      = sum(observed)

    if total == 0:
        return float('inf')   # empty text → undefined, return worst score

    chi_sq = 0.0
    for i in range(ALPHABET_SIZE):
        expected = (ENGLISH_FREQ[i] / 100.0) * total   # scale % to count
        if expected > 0:
            chi_sq += (observed[i] - expected) ** 2 / expected

    return chi_sq


def chi_square_attack(
    ciphertext: str,
    verbose: bool = False
) -> tuple[int, str, list[tuple[float, int, str]]]:
    """
    Attack the shift cipher using the Chi-Square statistical test.

    Tries all 26 possible keys, scores each candidate plaintext
    with chi_square_statistic(), and returns the key with the LOWEST score.

    Returns:
        best_key       (int)   — predicted decryption key
        best_plaintext (str)   — corresponding plaintext
        all_results    (list)  — list of (chi_sq, key, plaintext) sorted ascending
    """
    results = []

    for key in range(ALPHABET_SIZE):
        candidate = decrypt(ciphertext, key)
        score     = chi_square_statistic(candidate)
        results.append((score, key, candidate))

        if verbose:
            print(f"  Key {key:>2} | χ² = {score:>10.4f} | {candidate[:45]}")

    # Ascending sort — LOWEST chi-square = best English match
    results.sort(key=lambda x: x[0])

    best_score, best_key, best_plaintext = results[0]
    return best_key, best_plaintext, results


def print_results(
    best_key: int,
    best_plaintext: str,
    all_results: list[tuple[float, int, str]],
    ciphertext: str
) -> None:
    """Pretty-print Chi-Square attack results."""
    W  = "\033[1m"
    C  = "\033[96m"
    G  = "\033[92m"
    Y  = "\033[93m"
    R  = "\033[0m"

    print(f"\n{C}{'='*60}{R}")
    print(f"{W}  CHI-SQUARE STATISTICAL ATTACK{R}")
    print(f"{C}{'='*60}{R}")
    print(f"  Ciphertext     : {ciphertext[:60]}")
    print(f"\n{Y}  Top 5 candidates (lowest χ² = best English fit):{R}")
    print(f"  {'Key':<6} {'χ² Score':<14} {'Plaintext (first 50 chars)'}")
    print(f"  {'-'*58}")

    for chi_sq, key, plaintext in all_results[:5]:
        marker = f"{G}<-- BEST{R}" if key == best_key else ""
        print(f"  {key:<6} {chi_sq:<14.4f} {plaintext[:48]} {marker}")

    print(f"\n{G}  [+] Predicted Key : {best_key}{R}")
    print(f"  Decrypted Text   : {best_plaintext}")
    print(f"{C}{'='*60}{R}\n")


# ── Standalone demo ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from shift_cipher import encrypt

    original = "The quick brown fox jumps over the lazy dog"
    true_key = 13

    ciphertext = encrypt(original, true_key)
    print(f"\n  Original   : {original}")
    print(f"  True Key   : {true_key}")
    print(f"  Ciphertext : {ciphertext}\n")

    best_key, best_plaintext, all_results = chi_square_attack(ciphertext, verbose=True)
    print_results(best_key, best_plaintext, all_results, ciphertext)

    status = "SUCCEEDED" if best_key == true_key else "FAILED"
    print(f"  [{'OK' if best_key == true_key else 'FAIL'}] Attack {status} -- "
          f"predicted key {best_key}, true key {true_key}")
