"""
monosubstitution_cipher.py — Monoalphabetic Substitution Cipher
================================================================
Lab 5 | CryptoLabX Group 01 | 22CPP307

A monoalphabetic substitution cipher replaces each plaintext letter with
a unique ciphertext letter according to a fixed permutation (the key).

Key representation:
    A dict mapping each uppercase plaintext letter → ciphertext letter
    e.g. {'A': 'Q', 'B': 'W', 'C': 'E', ...}
    The key must be a bijection (one-to-one) on the 26-letter alphabet.

Key space: 26! ≈ 4 × 10^26  (brute force is computationally infeasible)
Security: Broken by frequency analysis (the cipher is statistically transparent)

Exported:
    encrypt(plaintext, key_map)     -> str
    decrypt(ciphertext, key_map)    -> str
    generate_random_key()           -> dict[str, str]
    format_key_table(key_map)       -> str
"""

import random
import string

ALPHABET = string.ascii_uppercase   # 'A' .. 'Z'


# ─────────────────────────────────────────────────────────────────────────────
def generate_random_key() -> dict[str, str]:
    """
    Generate a random bijective substitution key.

    Returns a dict where:
        key_map[plaintext_letter] = ciphertext_letter

    Every uppercase letter appears exactly once on each side.
    """
    shuffled = list(ALPHABET)
    random.shuffle(shuffled)
    return {pt: ct for pt, ct in zip(ALPHABET, shuffled)}


def inverse_key(key_map: dict[str, str]) -> dict[str, str]:
    """
    Return the inverse of a substitution key.

    If key_map maps plaintext → ciphertext,
    the inverse maps ciphertext → plaintext.
    """
    return {ct: pt for pt, ct in key_map.items()}


def format_key_table(key_map: dict[str, str]) -> str:
    """
    Return a pretty two-row string showing the substitution table.

    Example:
        Plaintext : A B C D E F G ...
        Ciphertext: Q W E R T Y U ...
    """
    pt_row = "  Plaintext : " + " ".join(sorted(key_map.keys()))
    ct_row = "  Ciphertext: " + " ".join(key_map[k] for k in sorted(key_map.keys()))
    return pt_row + "\n" + ct_row


# ─────────────────────────────────────────────────────────────────────────────
def encrypt(plaintext: str, key_map: dict[str, str]) -> str:
    """
    Encrypt plaintext using a monoalphabetic substitution key.

    Rules:
      - Uppercase letters are substituted using key_map
      - Lowercase letters are substituted using the same map (uppercased first),
        then lowercased in output — preserves case structure
      - Non-alphabetic characters (spaces, punctuation) pass through unchanged

    Args:
        plaintext: The original message
        key_map  : Dict mapping uppercase PT letter → uppercase CT letter

    Returns:
        Ciphertext string
    """
    result = []
    for ch in plaintext:
        if ch.isalpha():
            upper = ch.upper()
            substituted = key_map.get(upper, upper)   # default: identity (safe fallback)
            result.append(substituted if ch.isupper() else substituted.lower())
        else:
            result.append(ch)
    return "".join(result)


def decrypt(ciphertext: str, key_map: dict[str, str]) -> str:
    """
    Decrypt ciphertext using a monoalphabetic substitution key.

    Applies the inverse of key_map (ciphertext letter → plaintext letter).

    Args:
        ciphertext: The encrypted message
        key_map   : Dict mapping uppercase PT letter → uppercase CT letter
                    (same format as used for encryption)

    Returns:
        Recovered plaintext string
    """
    inv = inverse_key(key_map)
    result = []
    for ch in ciphertext:
        if ch.isalpha():
            upper = ch.upper()
            original = inv.get(upper, upper)
            result.append(original if ch.isupper() else original.lower())
        else:
            result.append(ch)
    return "".join(result)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Quick demo
    key = generate_random_key()
    print("Generated Key:")
    print(format_key_table(key))

    msg = "Hello, World! The quick brown fox jumps over the lazy dog."
    ct  = encrypt(msg, key)
    pt  = decrypt(ct,  key)

    print(f"\nOriginal  : {msg}")
    print(f"Encrypted : {ct}")
    print(f"Decrypted : {pt}")
    print(f"Correct   : {msg == pt}")
