"""
brute_force_dictionary.py — Brute-Force Attack with Dictionary Scoring

Imported by:
    main.py
"""

import os
from shift_cipher import decrypt, ALPHABET_SIZE


# ── Dictionary path (relative to this file) ──────────────────────────────────
_HERE       = os.path.dirname(os.path.abspath(__file__))
_DICT_PATH  = os.path.join(_HERE, "..", "dictionary", "english_words.txt")


def load_dictionary(path: str = _DICT_PATH) -> set[str]:
    """
    Load the English word list from a plain-text file (one word per line).

    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dictionary not found at: {path}\n"
            "Please add 'english_words.txt' to the dictionary/ folder."
        )
    with open(path, "r", encoding="utf-8") as f:
        words = {line.strip().lower() for line in f if line.strip()}
    print(f"  [dict] Loaded {len(words):,} words from '{os.path.basename(path)}'")
    return words


def score_text(text: str, dictionary: set[str]) -> int:
    """
    Count how many words in `text` exist in the dictionary.

    """
    words = text.lower().split()
    return sum(1 for word in words if word.strip(".,!?;:\"'()") in dictionary)


def brute_force_dictionary_attack(
    ciphertext: str,
    dictionary: set[str],
    verbose: bool = False
) -> tuple[int, str, list[tuple[int, int, str]]]:
    """
    Try all 26 keys and return the best one by dictionary score.

    """
    results = []

    for key in range(ALPHABET_SIZE):
        plaintext = decrypt(ciphertext, key)
        score     = score_text(plaintext, dictionary)
        results.append((score, key, plaintext))

        if verbose:
            indicator = " <-- BEST" if score == max(r[0] for r in results) else ""
            print(f"  Key {key:>2} | Score {score:>3} | {plaintext[:50]}{indicator}")

    # Sort by score descending — highest score = best English match
    results.sort(key=lambda x: x[0], reverse=True)

    best_score, best_key, best_plaintext = results[0]
    return best_key, best_plaintext, results


def print_results(
    best_key: int,
    best_plaintext: str,
    all_results: list[tuple[int, int, str]],
    ciphertext: str
) -> None:
    """Pretty-print the attack results to the terminal."""
    W  = "\033[1m"       # bold
    C  = "\033[96m"      # cyan
    G  = "\033[92m"      # green
    Y  = "\033[93m"      # yellow
    R  = "\033[0m"       # reset

    print(f"\n{C}{'='*60}{R}")
    print(f"{W}  BRUTE-FORCE DICTIONARY SCORING ATTACK{R}")
    print(f"{C}{'='*60}{R}")
    print(f"  Ciphertext   : {ciphertext[:60]}")
    print(f"\n{Y}  Top 5 candidates (by dictionary score):{R}")
    print(f"  {'Key':<6} {'Score':<8} {'Plaintext (first 50 chars)'}")
    print(f"  {'-'*55}")

    for score, key, plaintext in all_results[:5]:
        marker = f"{G}<-- BEST{R}" if key == best_key else ""
        print(f"  {key:<6} {score:<8} {plaintext[:50]} {marker}")

    print(f"\n{G}  [+] Predicted Key : {best_key}{R}")
    print(f"  Decrypted Text : {best_plaintext}")
    print(f"{C}{'='*60}{R}\n")


# ── Standalone demo ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    from shift_cipher import encrypt

    # Test with a known message and key
    original = "The quick brown fox jumps over the lazy dog"
    true_key  = 7

    ciphertext = encrypt(original, true_key)
    print(f"\n  Original   : {original}")
    print(f"  True Key   : {true_key}")
    print(f"  Ciphertext : {ciphertext}")

    dictionary = load_dictionary()

    print("\n  Running brute-force dictionary attack...")
    best_key, best_plaintext, all_results = brute_force_dictionary_attack(
        ciphertext, dictionary, verbose=True
    )

    print_results(best_key, best_plaintext, all_results, ciphertext)

    if best_key == true_key:
        print(f"  [OK] Attack SUCCEEDED -- predicted key {best_key} matches true key {true_key}")
    else:
        print(f"  [FAIL] Attack FAILED -- predicted {best_key}, true key was {true_key}")
        print(f"     Possible reason: ciphertext may be too short or lack common words.")
