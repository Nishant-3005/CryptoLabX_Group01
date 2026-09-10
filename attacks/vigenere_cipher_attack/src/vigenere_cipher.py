"""
vigenere_cipher.py — Vigenere Cipher: Encrypt, Decrypt, Preprocess, Verify
===========================================================================
Lab 6 | CryptoLabX Group 01 | 22CPP307

The Vigenere cipher is a polyalphabetic substitution cipher that uses a
repeating keyword to shift each plaintext letter by a different amount:

    Encryption: C_i = (P_i + K_{i mod m}) mod 26
    Decryption: P_i = (C_i - K_{i mod m} + 26) mod 26

where K_j is the j-th letter of the key (0-indexed, A=0 ... Z=25)
and m is the key length.
"""

import string

ALPHABET = string.ascii_uppercase


def clean_ciphertext(text: str) -> str:
    """
    Remove spaces, newlines, and all non-alphabetic characters.
    Convert to uppercase.

    Args:
        text: Raw ciphertext (may contain spaces, punctuation)
    Returns:
        Clean uppercase alphabetic string
    """
    return "".join(ch.upper() for ch in text if ch.isalpha())


def vigenere_encrypt(plaintext: str, key: str) -> str:
    """
    Encrypt plaintext using the Vigenere cipher with the given key.

    Formula: C_i = (P_i + K_{i mod m}) mod 26

    Args:
        plaintext: Clean uppercase plaintext (or will be cleaned internally)
        key      : Keyword string (alphabetic, any case)
    Returns:
        Encrypted ciphertext (uppercase)
    """
    pt  = clean_ciphertext(plaintext)
    key = clean_ciphertext(key)
    m   = len(key)

    result = []
    for i, ch in enumerate(pt):
        p = ord(ch)  - ord('A')
        k = ord(key[i % m]) - ord('A')
        result.append(chr((p + k) % 26 + ord('A')))
    return "".join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt ciphertext using the Vigenere cipher with the given key.

    Formula: P_i = (C_i - K_{i mod m} + 26) mod 26

    Args:
        ciphertext: Clean uppercase ciphertext (or will be cleaned internally)
        key       : Keyword string (alphabetic, any case)
    Returns:
        Recovered plaintext (uppercase)
    """
    ct  = clean_ciphertext(ciphertext)
    key = clean_ciphertext(key)
    m   = len(key)

    result = []
    for i, ch in enumerate(ct):
        c = ord(ch)  - ord('A')
        k = ord(key[i % m]) - ord('A')
        result.append(chr((c - k + 26) % 26 + ord('A')))
    return "".join(result)


def verify(ciphertext: str, plaintext: str, key: str) -> bool:
    """
    Verify that re-encrypting plaintext with key produces the original ciphertext.

    Args:
        ciphertext: The original ciphertext (cleaned internally)
        plaintext : The recovered plaintext
        key       : The recovered key
    Returns:
        True if re-encryption matches, False otherwise
    """
    ct_clean = clean_ciphertext(ciphertext)
    re_enc   = vigenere_encrypt(plaintext, key)
    return ct_clean == re_enc


def format_plaintext(text: str, group_size: int = 5, groups_per_line: int = 8) -> str:
    """
    Format a raw uppercase string into spaced groups for readability.

    Mirrors the assignment's ciphertext format:
        DAZFI SFSPA VQLSN PXYSZ WXALC DAFGQ UISMT PHZGA
        MKTTF TCCFX

    Args:
        text           : Raw uppercase string (no spaces)
        group_size     : Letters per group (default 5)
        groups_per_line: Groups per line before wrapping (default 8)
    Returns:
        Formatted multi-line string
    """
    clean = clean_ciphertext(text)
    groups = [clean[i:i + group_size] for i in range(0, len(clean), group_size)]
    lines = []
    for i in range(0, len(groups), groups_per_line):
        lines.append(" ".join(groups[i:i + groups_per_line]))
    return "\n".join(lines)


def key_schedule_display(plaintext: str, key: str, limit: int = 40) -> str:
    """
    Show the key cycling over the plaintext for educational display.

    Returns a formatted string like:
        Plain:  A T T A C K A T D A W N
        Key  :  L E M O N L E M O N L E
        Cipher: L X F O P V E F R N H R

    Args:
        plaintext: Clean text
        key      : Key string
        limit    : Max characters to display
    Returns:
        Formatted 3-line string
    """
    pt  = clean_ciphertext(plaintext)[:limit]
    key_clean = clean_ciphertext(key)
    m   = len(key_clean)

    ct = vigenere_encrypt(pt, key_clean)

    p_line = " ".join(pt)
    k_line = " ".join(key_clean[i % m] for i in range(len(pt)))
    c_line = " ".join(ct)

    return (
        f"  Plain : {p_line}\n"
        f"  Key   : {k_line}\n"
        f"  Cipher: {c_line}"
    )


if __name__ == "__main__":
    msg = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    key = "LEMON"
    ct  = vigenere_encrypt(msg, key)
    pt  = vigenere_decrypt(ct, key)
    ok  = verify(ct, pt, key)
    print(f"Plaintext : {msg}")
    print(f"Key       : {key}")
    print(f"Encrypted : {ct}")
    print(f"Decrypted : {pt}")
    print(f"Verified  : {ok}")
    print(f"\nFormatted ciphertext:\n{format_plaintext(ct)}")
    print(f"\nKey schedule (first 20 chars):\n{key_schedule_display(msg, key, 20)}")
