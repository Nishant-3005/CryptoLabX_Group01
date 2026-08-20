"""
main.py — CryptoLabX | Lab 4 | Shift Cipher Cryptanalysis Suite
================================================================
Course : Cryptography Laboratory (22CPP307) | Group 01
Lab    : 4 — Cryptanalysis of Shift Cipher

This file ties together all three components:
  1. shift_cipher.py          — Encrypt / Decrypt
  2. brute_force_dictionary.py — Brute-force with dictionary scoring
  3. chi_square_attack.py      — Chi-Square statistical analysis

Modes:
  A) Interactive — enter your own ciphertext and run both attacks
  B) Test Suite  — runs 6 built-in test cases and prints a results table

Usage:
  py -3 main.py

Run from the src/ directory or from project root (both work).
"""

import os
import sys

# ── Make sure src/ is importable when run from project root ──────────────────
_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from shift_cipher          import encrypt, decrypt, ALPHABET_SIZE
from brute_force_dictionary import (load_dictionary,
                                    brute_force_dictionary_attack,
                                    print_results as bf_print)
from chi_square_attack      import (chi_square_attack,
                                    print_results as chi_print)

# ── ANSI colours ─────────────────────────────────────────────────────────────
W  = "\033[1m"
C  = "\033[96m"
G  = "\033[92m"
Y  = "\033[93m"
R  = "\033[91m"
X  = "\033[0m"

# ── Built-in test cases (plaintext, key) ─────────────────────────────────────
TEST_CASES = [
    ("the quick brown fox jumps over the lazy dog", 3),
    ("cryptography is the art of writing secret codes", 7),
    ("attack at dawn send reinforcements to the north", 13),
    ("frequency analysis reveals patterns in ciphertext", 17),
    ("zebra xenon quantum voyage", 25),          # short / unusual words
    ("a",                                         5),  # edge: single char
]


def banner() -> None:
    os.system("")   # enable ANSI on Windows
    print(f"""
{C}{W}
  ================================================
   Shift Cipher Cryptanalysis Suite
   CryptoLabX | Lab 4 | Group 01
  ================================================
{X}""")


def print_menu() -> None:
    print(f"""
{C}  --------------------------------{X}
  {W}[1]{X}  Run Built-in Test Suite
  {W}[2]{X}  Interactive Mode
  {W}[0]{X}  {R}Exit{X}
{C}  --------------------------------{X}""")


# ─────────────────────────────────────────────────────────────────────────────
def run_both_attacks(
    ciphertext: str,
    dictionary: set[str],
    actual_key: int | None = None,
    verbose: bool = False
) -> dict:
    """
    Run both attacks on `ciphertext`.  Returns a result dict.
    """
    # --- Dictionary attack ---
    bf_key, bf_plain, bf_all = brute_force_dictionary_attack(
        ciphertext, dictionary, verbose=False
    )

    # --- Chi-Square attack ---
    chi_key, chi_plain, chi_all = chi_square_attack(
        ciphertext, verbose=False
    )

    if verbose:
        bf_print(bf_key, bf_plain, bf_all, ciphertext)
        chi_print(chi_key, chi_plain, chi_all, ciphertext)

    result = {
        "ciphertext"     : ciphertext,
        "actual_key"     : actual_key,
        "dict_key"       : bf_key,
        "chi_key"        : chi_key,
        "dict_plaintext" : bf_plain,
        "chi_plaintext"  : chi_plain,
        "dict_correct"   : (bf_key  == actual_key) if actual_key is not None else None,
        "chi_correct"    : (chi_key == actual_key) if actual_key is not None else None,
    }
    return result


# ─────────────────────────────────────────────────────────────────────────────
def run_test_suite(dictionary: set[str]) -> None:
    """Run all built-in test cases and display a formatted results table."""
    print(f"\n{W}{C}  Running {len(TEST_CASES)} test cases...{X}\n")

    results = []
    for i, (plaintext, true_key) in enumerate(TEST_CASES, start=1):
        ciphertext = encrypt(plaintext, true_key)
        print(f"  [{i}/{len(TEST_CASES)}] Key={true_key:>2}  CT: {ciphertext[:40]}...")
        r = run_both_attacks(ciphertext, dictionary, actual_key=true_key, verbose=False)
        r["plaintext"] = plaintext
        results.append(r)

    # ── Print results table ───────────────────────────────────────────────────
    def tick(val): return f"{G}YES{X}" if val else f"{R}NO {X}"

    print(f"\n{C}{'='*90}{X}")
    print(f"{W}  RESULTS TABLE{X}")
    print(f"{C}{'='*90}{X}")

    hdr = f"  {'#':<3} {'Actual Key':<12} {'Dict Key':<10} {'Chi Key':<10} {'Dict Correct?':<16} {'Chi Correct?'}"
    print(hdr)
    print(f"  {'-'*80}")

    for i, r in enumerate(results, start=1):
        ak  = r["actual_key"]
        dk  = r["dict_key"]
        ck  = r["chi_key"]
        dc  = tick(r["dict_correct"])
        cc  = tick(r["chi_correct"])
        print(f"  {i:<3} {ak:<12} {dk:<10} {ck:<10} {dc}             {cc}")

    # Summary
    dict_ok = sum(1 for r in results if r["dict_correct"])
    chi_ok  = sum(1 for r in results if r["chi_correct"])
    total   = len(results)
    print(f"\n  {W}Dictionary attack accuracy : {dict_ok}/{total}{X}")
    print(f"  {W}Chi-Square attack accuracy : {chi_ok}/{total}{X}")

    # Failure analysis
    failures = [r for r in results if not r["dict_correct"] or not r["chi_correct"]]
    if failures:
        print(f"\n{Y}  FAILURE ANALYSIS:{X}")
        for r in failures:
            if not r["dict_correct"]:
                print(f"  Dict failed  | Key {r['actual_key']:>2} predicted {r['dict_key']:>2}"
                      f" | Likely cause: plaintext has few common dictionary words")
            if not r["chi_correct"]:
                print(f"  Chi  failed  | Key {r['actual_key']:>2} predicted {r['chi_key']:>2}"
                      f" | Likely cause: short text → frequency distribution unreliable")

    print(f"\n  {W}CONCLUSION:{X}")
    print(f"  Both attacks exploit the fact that the Shift Cipher has only")
    print(f"  26 possible keys — making exhaustive search trivial. Dictionary")
    print(f"  scoring works well for natural-language text with common words.")
    print(f"  Chi-Square is more robust for longer texts but may fail on short")
    print(f"  or unusual vocabulary. Neither attack works on random / non-English text.")
    print(f"{C}{'='*90}{X}\n")

    # Save results to outputs/
    _save_results(results)


def _save_results(results: list[dict]) -> None:
    """Save the test results table to outputs/results.txt."""
    out_dir  = os.path.join(_SRC, "..", "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "results.txt")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("Shift Cipher Cryptanalysis — Test Results\n")
        f.write("CryptoLabX Group 01 | Lab 4\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'#':<4} {'Actual Key':<12} {'Dict Key':<10} {'Chi Key':<10}"
                f" {'Dict OK?':<12} {'Chi OK?'}\n")
        f.write("-" * 70 + "\n")
        for i, r in enumerate(results, 1):
            dc = "YES" if r["dict_correct"] else "NO"
            cc = "YES" if r["chi_correct"]  else "NO"
            f.write(f"{i:<4} {r['actual_key']:<12} {r['dict_key']:<10}"
                    f" {r['chi_key']:<10} {dc:<12} {cc}\n")
        dict_ok = sum(1 for r in results if r["dict_correct"])
        chi_ok  = sum(1 for r in results if r["chi_correct"])
        f.write(f"\nDictionary accuracy : {dict_ok}/{len(results)}\n")
        f.write(f"Chi-Square accuracy : {chi_ok}/{len(results)}\n")

    print(f"\n  Results saved → {out_file}")


# ─────────────────────────────────────────────────────────────────────────────
def interactive_mode(dictionary: set[str]) -> None:
    """Let the user enter a ciphertext and run both attacks interactively."""
    print(f"\n{Y}  INTERACTIVE MODE{X}")
    print("  Enter a ciphertext (or press ENTER to use a demo):")
    raw = input("  > ").strip()

    if not raw:
        raw = encrypt("hello world this is a secret message", 10)
        print(f"  Using demo ciphertext: {raw}")

    print(f"\n  Running both attacks on: {raw[:60]}")
    result = run_both_attacks(raw, dictionary, actual_key=None, verbose=True)

    if result["dict_key"] == result["chi_key"]:
        print(f"{G}  [+] Both attacks agree: Key = {result['dict_key']}{X}")
    else:
        print(f"{Y}  [!] Attacks disagree:  Dict Key = {result['dict_key']}"
              f"  |  Chi Key = {result['chi_key']}{X}")
        print("  Consider the dictionary result for short texts,")
        print("  and chi-square for longer ciphertexts.")


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    banner()
    print(f"  Loading dictionary...")
    dictionary = load_dictionary()

    while True:
        print_menu()
        choice = input(f"\n  {W}Select option:{X} ").strip()

        if choice == "1":
            run_test_suite(dictionary)
        elif choice == "2":
            interactive_mode(dictionary)
        elif choice == "0":
            print(f"\n  {G}Goodbye!{X}\n")
            break
        else:
            print(f"  {R}Invalid option.{X}")


if __name__ == "__main__":
    main()
