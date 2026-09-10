"""
main.py -- Vigenere Cipher Cryptanalysis Orchestrator
======================================================
Lab 6 | CryptoLabX Group 01 | 22CPP307

Full pipeline:
    1. Load and clean ciphertext from data/ciphertext.txt
    2. Kasiski examination  -> candidate key lengths
    3. IC analysis          -> confirm best key length
    4. Frequency analysis   -> recover key letter by letter
    5. Decrypt ciphertext
    6. Verify by re-encryption
    7. Save results to outputs/results.txt
"""

import os
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from vigenere_cipher    import clean_ciphertext, vigenere_decrypt, verify
from kasiski_analysis   import kasiski_analysis
from frequency_analysis import ic_analysis, find_key, frequency_analysis

W = "\033[1m"; C = "\033[96m"; G = "\033[92m"
Y = "\033[93m"; R = "\033[91m"; X = "\033[0m"

_DATA_PATH    = os.path.join(_SRC, "..", "data", "ciphertext.txt")
_OUTPUTS_PATH = os.path.join(_SRC, "..", "outputs", "results.txt")


def banner() -> None:
    os.system("")
    print(f"""
{C}{W}
  =====================================================
   Vigenere Cipher Cryptanalysis Suite
   CryptoLabX | Lab 6 | Group 01
  =====================================================
{X}""")


def load_ciphertext() -> str:
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    ct = clean_ciphertext(raw)
    print(f"  Loaded ciphertext  : {len(ct)} letters")
    print(f"  First 60 chars     : {ct[:60]}")
    return ct


def run_kasiski_phase(ciphertext: str) -> list:
    candidates = kasiski_analysis(ciphertext)
    return candidates


def run_ic_phase(ciphertext: str) -> int:
    return ic_analysis(ciphertext, max_key_length=15)


def run_frequency_phase(ciphertext: str, key_length: int) -> str:
    return find_key(ciphertext, key_length)


def run_decryption(ciphertext: str, key: str) -> str:
    pt = vigenere_decrypt(ciphertext, key)
    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  DECRYPTION RESULT{X}")
    print(f"{C}{'='*60}{X}")
    print(f"  Key              : {G}{W}{key}{X}")
    print(f"  Plaintext (first 80): {G}{pt[:80]}{X}")
    print(f"  Full plaintext   :\n  {pt}")
    print(f"{C}{'='*60}{X}")
    return pt


def run_verification(ciphertext: str, plaintext: str, key: str) -> bool:
    ok = verify(ciphertext, plaintext, key)
    status = f"{G}MATCH -- Verification PASSED{X}" if ok else f"{R}MISMATCH -- Verification FAILED{X}"
    print(f"\n  Verification: {status}\n")
    return ok


def save_results(ciphertext: str, key: str, plaintext: str,
                 kasiski_results: list, key_length: int, verified: bool) -> None:
    os.makedirs(os.path.dirname(_OUTPUTS_PATH), exist_ok=True)
    with open(_OUTPUTS_PATH, "w", encoding="utf-8") as f:
        f.write("Vigenere Cipher Cryptanalysis — Results\n")
        f.write("CryptoLabX Group 01 | Lab 6\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Ciphertext length : {len(ciphertext)}\n")
        f.write(f"Ciphertext (clean): {ciphertext}\n\n")
        f.write(f"Kasiski top candidates: {kasiski_results[:5]}\n")
        f.write(f"Chosen key length : {key_length}\n")
        f.write(f"Recovered key     : {key}\n\n")
        f.write(f"Decrypted plaintext:\n{plaintext}\n\n")
        f.write(f"Verification      : {'PASS' if verified else 'FAIL'}\n")
    print(f"  Results saved -> {_OUTPUTS_PATH}")


def main() -> None:
    banner()

    # Step 1: Load
    print(f"{Y}Step 1: Loading ciphertext...{X}")
    ciphertext = load_ciphertext()

    # Step 2: Kasiski
    print(f"\n{Y}Step 2: Kasiski Examination...{X}")
    kasiski_results = run_kasiski_phase(ciphertext)

    # Step 3: IC analysis
    print(f"\n{Y}Step 3: Index of Coincidence Analysis...{X}")
    ic_best = run_ic_phase(ciphertext)

    # Reconcile: IC is the more reliable indicator for confirming key length.
    # If IC best appears in Kasiski's top-5 candidates, use it.
    kasiski_top5 = [k for k, _ in kasiski_results[:5]] if kasiski_results else []
    if ic_best in kasiski_top5:
        key_length = ic_best
        print(f"  {G}IC confirms a Kasiski candidate: key length = {key_length}{X}")
    elif kasiski_results:
        kasiski_top = kasiski_results[0][0]
        print(f"  {Y}IC ({ic_best}) not in Kasiski top-5 {kasiski_top5}{X}")
        print(f"  {W}IC value for {ic_best} is much closer to English — using IC: {ic_best}{X}")
        key_length = ic_best
    else:
        key_length = ic_best
        print(f"  Using IC result: key length = {key_length}")

    # Step 4: Frequency analysis
    print(f"\n{Y}Step 4: Frequency Analysis (key length = {key_length})...{X}")
    key = run_frequency_phase(ciphertext, key_length)

    # Step 5: Decrypt
    print(f"\n{Y}Step 5: Decrypting...{X}")
    plaintext = run_decryption(ciphertext, key)

    # Step 6: Verify
    print(f"\n{Y}Step 6: Verifying...{X}")
    verified = run_verification(ciphertext, plaintext, key)

    # Step 7: Save
    print(f"\n{Y}Step 7: Saving results...{X}")
    save_results(ciphertext, key, plaintext, kasiski_results, key_length, verified)


if __name__ == "__main__":
    main()
