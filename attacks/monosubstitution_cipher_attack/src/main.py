"""
main.py -- Monoalphabetic Substitution Cipher: Full Cryptanalysis Orchestrator
===============================================================================
Lab 5 | CryptoLabX Group 01 | 22CPP307

Workflow:
    1. Load plaintext from data/plaintext_source.txt
    2. Generate a random substitution key and encrypt
    3. Run frequency_analysis()
    4. Run word_frequency_analysis() + pattern_analysis()
    5. Interactive loop: analyst enters guesses, sees partial plaintext
    6. verify_solution() confirms when the key is fully recovered
    7. Save results to outputs/results.txt

Usage:
    cd attacks/monosubstitution_cipher_attack/src
    python main.py
"""

import os
import sys
import datetime

# -- path setup so imports work from anywhere --
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from monosubstitution_cipher import (
    generate_random_key, encrypt, decrypt,
    format_key_table, inverse_key, ALPHABET
)
from frequency_analysis import (
    frequency_analysis, word_frequency_analysis, pattern_analysis
)
from cryptanalysis import (
    apply_substitution, display_partial_plaintext, verify_solution
)

# -- ANSI colours --
W = "\033[1m"; C = "\033[96m"; G = "\033[92m"; Y = "\033[93m"
R = "\033[91m"; X = "\033[0m"

# -- paths --
_DATA_PATH    = os.path.join(_HERE, "..", "data",    "plaintext_source.txt")
_OUTPUT_PATH  = os.path.join(_HERE, "..", "outputs", "results.txt")


# ===========================================================================
def load_plaintext(path: str) -> str:
    if not os.path.exists(path):
        print(f"  {R}[!] Plaintext file not found: {path}{X}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def print_banner():
    print(f"""
{C}{W}
  ============================================================
    Monoalphabetic Substitution Cipher -- Cryptanalysis Lab
    Lab 5 | CryptoLabX Group 01 | 22CPP307
  ============================================================
{X}""")


def save_results(content: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n  {G}[+] Results saved to: {os.path.relpath(path)}{X}")


# ===========================================================================
def run_analysis_phase(ciphertext: str):
    """Run all three analysis functions and display results."""
    print(f"\n{C}  PHASE 1: LETTER FREQUENCY ANALYSIS{X}")
    freq_results = frequency_analysis(ciphertext)

    print(f"\n{C}  PHASE 2: WORD FREQUENCY ANALYSIS{X}")
    word_results = word_frequency_analysis(ciphertext)

    print(f"\n{C}  PHASE 3: PATTERN ANALYSIS{X}")
    pattern_results = pattern_analysis(ciphertext)

    return freq_results, word_results, pattern_results


# ===========================================================================
def run_interactive_attack(ciphertext: str, true_decrypt_key: dict) -> dict:
    """
    Interactive loop: analyst enters CT->PT guesses one at a time.
    Shows partial plaintext after each guess.
    Returns the analyst's recovered key (CT->PT mapping).
    """
    partial_key: dict[str, str] = {}   # CT letter -> PT letter

    print(f"""
{C}{'='*60}{X}
{W}  INTERACTIVE CRYPTANALYSIS{X}
{C}{'='*60}{X}
  Commands:
    <CT>=<PT>   e.g.  Q=E   (guess that ciphertext Q maps to plaintext e)
    undo        remove last mapping
    show        show current partial plaintext
    freq        re-display frequency table
    hint        reveal one correct mapping (cheat mode)
    done        finish and verify
    quit        exit without verification
{C}{'='*60}{X}
""")

    history: list[str] = []   # for undo

    while True:
        resolved = len(partial_key)
        print(f"  {W}[{resolved}/26 mapped]{X} Enter command: ", end="")
        try:
            cmd = input().strip().upper()
        except (EOFError, KeyboardInterrupt):
            break

        if cmd == "QUIT":
            print(f"  {Y}Exiting interactive mode.{X}")
            break

        elif cmd == "DONE":
            break

        elif cmd == "SHOW":
            partial_pt = apply_substitution(ciphertext, partial_key)
            display_partial_plaintext(partial_pt, partial_key, ciphertext)

        elif cmd == "FREQ":
            frequency_analysis(ciphertext)

        elif cmd == "UNDO":
            if history:
                last = history.pop()
                partial_key.pop(last, None)
                print(f"  {Y}Removed mapping: {last}{X}")
            else:
                print(f"  {R}Nothing to undo.{X}")

        elif cmd == "HINT":
            # Reveal one correct mapping that analyst hasn't found yet
            unmapped = [ct for ct in ALPHABET if ct not in partial_key]
            if unmapped:
                ct_letter = unmapped[0]
                pt_letter = true_decrypt_key.get(ct_letter, "?")
                print(f"  {G}Hint: ciphertext '{ct_letter}' -> plaintext '{pt_letter}'{X}")
            else:
                print(f"  {G}All letters mapped!{X}")

        elif "=" in cmd:
            parts = cmd.split("=")
            if len(parts) == 2:
                ct_l = parts[0].strip()
                pt_l = parts[1].strip()
                if len(ct_l) == 1 and ct_l in ALPHABET and len(pt_l) == 1 and pt_l in ALPHABET:
                    # Check for conflicts
                    if pt_l in partial_key.values():
                        existing_ct = [k for k, v in partial_key.items() if v == pt_l][0]
                        print(f"  {R}[!] '{pt_l}' already mapped from '{existing_ct}'. Remove it first.{X}")
                    else:
                        partial_key[ct_l] = pt_l
                        history.append(ct_l)
                        # Show inline update
                        partial_pt = apply_substitution(ciphertext, partial_key)
                        display_partial_plaintext(partial_pt, partial_key)
                else:
                    print(f"  {R}Invalid format. Use single uppercase letters: e.g. Q=E{X}")
            else:
                print(f"  {R}Unknown command. Use CT=PT format or: show, undo, hint, done, quit{X}")
        else:
            print(f"  {R}Unknown command. Use CT=PT format or: show, undo, hint, done, quit{X}")

    return partial_key


# ===========================================================================
def run_auto_demo(ciphertext: str, true_decrypt_key: dict) -> dict:
    """
    Auto-demonstration: simulate the attack using frequency analysis hints.
    Used when running non-interactively (e.g. for report generation).
    """
    print(f"\n{C}  AUTO-DEMO MODE: Simulating frequency-guided attack{X}\n")

    # Step 1: frequency analysis -- map top CT letters to ETAOIN order
    freq_results = frequency_analysis(ciphertext)
    english_order = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

    partial_key: dict[str, str] = {}
    for i, (ct_letter, count, pct) in enumerate(freq_results[:12]):
        pt_letter = english_order[i]
        partial_key[ct_letter] = pt_letter
        print(f"  Guess: CT '{ct_letter}' (freq {pct:.1f}%) -> PT '{pt_letter}'")

    partial_pt = apply_substitution(ciphertext, partial_key)
    display_partial_plaintext(partial_pt, partial_key, ciphertext)

    # Step 2: apply full true key to show what correct solution looks like
    print(f"\n  {G}Applying true key to show complete decryption...{X}")
    full_key = true_decrypt_key
    full_pt = apply_substitution(ciphertext, full_key)
    display_partial_plaintext(full_pt, full_key, ciphertext)

    return full_key


# ===========================================================================
def main():
    print_banner()

    # -- Load and encrypt --
    plaintext = load_plaintext(_DATA_PATH)
    print(f"  {W}Plaintext loaded:{X} {len(plaintext)} characters, "
          f"{len([c for c in plaintext if c.isalpha()])} letters")
    print(f"  {W}Preview:{X} {plaintext[:80].strip()}...")

    key_map = generate_random_key()          # encryption key: PT -> CT
    decrypt_key = inverse_key(key_map)       # decryption key: CT -> PT

    ciphertext = encrypt(plaintext, key_map).upper()

    print(f"\n  {W}Encryption Key:{X}")
    print(format_key_table(key_map))
    print(f"\n  {W}Ciphertext preview:{X} {ciphertext[:80]}...")

    # -- Analysis phase --
    freq_results, word_results, pattern_results = run_analysis_phase(ciphertext)

    # -- Attack phase --
    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  Choose attack mode:{X}")
    print(f"  {W}[1]{X} Interactive (you enter guesses manually)")
    print(f"  {W}[2]{X} Auto-demo  (simulate guided attack for report)")
    print(f"{C}{'='*60}{X}")

    try:
        mode = input("  Select [1/2]: ").strip()
    except (EOFError, KeyboardInterrupt):
        mode = "2"

    if mode == "1":
        recovered_key = run_interactive_attack(ciphertext, decrypt_key)
    else:
        recovered_key = run_auto_demo(ciphertext, decrypt_key)

    # -- Verify --
    if recovered_key:
        recovered_pt = apply_substitution(ciphertext, recovered_key)
        # For verification we need the encryption direction
        # Build encryption key from recovered decryption key
        recovered_encrypt_key = {v: k for k, v in recovered_key.items()}
        verify_solution(ciphertext, recovered_pt, recovered_encrypt_key)

    # -- Save results --
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = (
        f"CryptoLabX Lab 5 -- Monoalphabetic Substitution Cipher Attack\n"
        f"Run timestamp: {timestamp}\n"
        f"{'='*60}\n\n"
        f"PLAINTEXT (first 300 chars):\n{plaintext[:300]}\n\n"
        f"ENCRYPTION KEY:\n{format_key_table(key_map)}\n\n"
        f"CIPHERTEXT (first 300 chars):\n{ciphertext[:300]}\n\n"
        f"FREQUENCY ORDER (CT): {' '.join(r[0] for r in freq_results)}\n"
        f"ENGLISH REFERENCE:     ETAOINSHRDLCUMWFGYPBVKJXQZ\n\n"
        f"Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)\n"
    )
    save_results(output, _OUTPUT_PATH)

    print(f"\n  {G}Done!{X}")


if __name__ == "__main__":
    main()
