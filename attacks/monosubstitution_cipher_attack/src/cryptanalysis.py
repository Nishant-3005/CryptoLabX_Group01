"""
cryptanalysis.py — Cryptanalysis Helper Functions
==================================================
Lab 5 | CryptoLabX Group 01 | 22CPP307

This module provides the tools to incrementally decode a monoalphabetic
substitution ciphertext as the analyst builds up their key guess:

    apply_substitution()       — decode known letters, mark unknowns as '_'
    display_partial_plaintext()— show progress + known mappings summary table
    verify_solution()          — re-encrypt recovered plaintext and compare

Typical usage flow in main.py:
    1. Analyst observes frequency analysis output
    2. Analyst guesses: ciphertext letter X → plaintext letter E
    3. apply_substitution(ciphertext, partial_key) is called
    4. display_partial_plaintext() shows how much has been decoded
    5. Repeat until full key is recovered
    6. verify_solution() confirms the key is correct

Exported:
    apply_substitution(ciphertext, partial_key_map)   -> str
    display_partial_plaintext(partial, partial_key)   -> None
    verify_solution(original_ct, recovered_pt, key)   -> bool
"""

import string
from monosubstitution_cipher import encrypt, ALPHABET

# ANSI colour helpers (no external deps)
_W  = "\033[1m"    # bold
_C  = "\033[96m"   # cyan
_G  = "\033[92m"   # green
_Y  = "\033[93m"   # yellow
_R  = "\033[91m"   # red
_X  = "\033[0m"    # reset


# ─────────────────────────────────────────────────────────────────────────────
def apply_substitution(ciphertext: str, partial_key_map: dict[str, str]) -> str:
    """
    Apply a (possibly partial) substitution key to a ciphertext.

    For each letter in ciphertext:
      - If the ciphertext letter has a known mapping → output the plaintext letter
      - Otherwise → output '_' (unknown)
    Non-alphabetic characters pass through unchanged.

    Args:
        ciphertext      : Encrypted text (uppercase letters expected)
        partial_key_map : Dict  ciphertext_letter (upper) → plaintext_letter (upper)
                          (the INVERSE direction of the encryption key)

    Returns:
        Partial plaintext string with '_' for undeciphered positions.

    Example:
        ciphertext     = "XYZ ABC"
        partial_key_map = {'X': 'T', 'Y': 'H', 'Z': 'E'}
        result         = "THE ___"
    """
    result = []
    for ch in ciphertext:
        if ch.isalpha():
            upper = ch.upper()
            mapped = partial_key_map.get(upper)
            if mapped:
                # Preserve the case of the original ciphertext character
                result.append(mapped if ch.isupper() else mapped.lower())
            else:
                result.append("_")
        else:
            result.append(ch)
    return "".join(result)


# ─────────────────────────────────────────────────────────────────────────────
def display_partial_plaintext(
    partial_plaintext: str,
    partial_key_map: dict[str, str],
    ciphertext: str = ""
) -> None:
    """
    Display the current partial decryption and the known key mappings.

    Shows:
      1. Partial plaintext (decoded letters + _ for unknowns)
      2. A summary table of  CT letter → PT letter  mappings so far
      3. Coverage: how many of the 26 letters have been mapped

    Args:
        partial_plaintext : Output of apply_substitution()
        partial_key_map   : Dict  CT_letter → PT_letter  (known mappings only)
        ciphertext        : Original ciphertext (optional, for side-by-side display)
    """
    solved   = len(partial_key_map)
    unsolved = 26 - solved
    pct      = (solved / 26) * 100

    print(f"\n{_C}{'='*60}{_X}")
    print(f"{_W}  PARTIAL DECRYPTION PROGRESS{_X}")
    print(f"{_C}{'='*60}{_X}")

    # Side-by-side display if ciphertext provided
    if ciphertext:
        # Wrap at 60 chars for readability
        chunk = 60
        for i in range(0, max(len(ciphertext), len(partial_plaintext)), chunk):
            ct_chunk = ciphertext[i:i+chunk]
            pt_chunk = partial_plaintext[i:i+chunk]
            print(f"  CT: {_Y}{ct_chunk}{_X}")
            print(f"  PT: {_G}{pt_chunk}{_X}")
            print()
    else:
        # Just show the partial plaintext with line wrapping
        chunk = 70
        for i in range(0, len(partial_plaintext), chunk):
            print(f"  {_G}{partial_plaintext[i:i+chunk]}{_X}")

    # Known mappings table
    print(f"\n{_W}  Known Mappings ({solved}/26 — {pct:.0f}% complete){_X}")
    if partial_key_map:
        # Sort by ciphertext letter for consistent display
        items = sorted(partial_key_map.items())
        row = "  "
        for ct_letter, pt_letter in items:
            row += f"{_C}{ct_letter}{_X}->{_G}{pt_letter}{_X}  "
            if len(row) > 70:
                print(row)
                row = "  "
        if row.strip():
            print(row)
    else:
        print("  (none yet)")

    # Unmapped ciphertext letters
    all_letters = set(ALPHABET)
    mapped_ct   = set(partial_key_map.keys())
    unmapped    = sorted(all_letters - mapped_ct)
    if unmapped:
        print(f"\n  {_Y}Unmapped CT letters: {' '.join(unmapped)}{_X}")

    print(f"{_C}{'='*60}{_X}\n")


# ─────────────────────────────────────────────────────────────────────────────
def verify_solution(
    original_ciphertext: str,
    recovered_plaintext: str,
    key_map: dict[str, str]
) -> bool:
    """
    Verify a proposed key by re-encrypting the recovered plaintext and
    comparing it to the original ciphertext.

    The key_map here should be the ENCRYPTION key (PT → CT), not the
    decryption key (CT → PT).

    Args:
        original_ciphertext : The ciphertext that was attacked
        recovered_plaintext : The proposed plaintext after decryption
        key_map             : Encryption key  PT_letter → CT_letter

    Returns:
        True  if re-encrypting recovered_plaintext with key_map reproduces
              original_ciphertext exactly (case-insensitive comparison)
        False otherwise

    Prints a detailed verification report.
    """
    # Re-encrypt the proposed plaintext
    re_encrypted = encrypt(recovered_plaintext, key_map)

    # Compare (ignoring case and non-alpha to be robust)
    orig_alpha = "".join(ch.upper() for ch in original_ciphertext if ch.isalpha())
    re_alpha   = "".join(ch.upper() for ch in re_encrypted       if ch.isalpha())

    match = (orig_alpha == re_alpha)

    print(f"\n{_C}{'='*60}{_X}")
    print(f"{_W}  SOLUTION VERIFICATION{_X}")
    print(f"{_C}{'='*60}{_X}")
    print(f"  Original CT  : {original_ciphertext[:60]}")
    print(f"  Re-encrypted : {re_encrypted[:60]}")
    print(f"  Recovered PT : {recovered_plaintext[:60]}")

    if match:
        print(f"\n  {_G}[+] VERIFIED — Key is correct! Re-encryption matches original ciphertext.{_X}")
    else:
        # Find first mismatch position for debugging
        mismatch_pos = next(
            (i for i, (a, b) in enumerate(zip(orig_alpha, re_alpha)) if a != b),
            len(orig_alpha)  # if one is longer than other
        )
        print(f"\n  {_R}[-] MISMATCH — Key is incorrect.{_X}")
        print(f"  First mismatch at letter position {mismatch_pos}")
        print(f"  Expected: '{orig_alpha[mismatch_pos] if mismatch_pos < len(orig_alpha) else '?'}'  "
              f"Got: '{re_alpha[mismatch_pos] if mismatch_pos < len(re_alpha) else '?'}'")

    print(f"{_C}{'='*60}{_X}\n")
    return match


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Demo: simulate a partial decryption session
    from monosubstitution_cipher import generate_random_key, encrypt, decrypt

    key    = generate_random_key()
    inv_key = {v: k for k, v in key.items()}   # CT → PT (decryption direction)

    msg = "the quick brown fox jumps over the lazy dog"
    ct  = encrypt(msg, key).upper()

    print(f"Ciphertext: {ct}")
    print(f"\n--- Simulating partial key discovery ---")

    # Suppose analyst has found 5 mappings so far (correct ones from inv_key)
    known_ct_letters = list(inv_key.keys())[:5]
    partial = {ct_l: inv_key[ct_l] for ct_l in known_ct_letters}

    partial_pt = apply_substitution(ct, partial)
    display_partial_plaintext(partial_pt, partial, ct)

    # Now verify with the full key
    print("--- Full key verification ---")
    recovered = decrypt(ct, key)
    verify_solution(ct, recovered, key)
