"""
shift_cipher.py -- Shift Cipher (Caesar Cipher) Implementation
encrypt(plaintext, key)  -> ciphertext
decrypt(ciphertext, key) -> plaintext

"""


ALPHABET_SIZE = 26


def _shift_char(char: str, key: int) -> str:
    """
    Shift a single character by `key` positions (mod 26).
    Preserves case. Non-alpha characters returned unchanged.
    """
    if char.isalpha():
        base = ord('A') if char.isupper() else ord('a')
        # Formula: E(x) = (x + key) mod 26
        return chr((ord(char) - base + key) % ALPHABET_SIZE + base)
    return char


def encrypt(plaintext: str, key: int) -> str:
    """
    Encrypt plaintext using the Shift Cipher with the given key.

    Formula:  C = (P + key) mod 26   for each letter P

    """
    key = key % ALPHABET_SIZE   # normalise keys outside 0-25
    return ''.join(_shift_char(ch, key) for ch in plaintext)


def decrypt(ciphertext: str, key: int) -> str:
    """
    Decrypt ciphertext using the Shift Cipher with the given key.

    Formula:  P = (C - key + 26) mod 26   for each letter C

    """
    # Decryption = Encryption with the inverse key (26 - key)
    key = key % ALPHABET_SIZE
    return ''.join(_shift_char(ch, ALPHABET_SIZE - key) for ch in ciphertext)


def get_all_decryptions(ciphertext: str) -> list[tuple[int, str]]:
    """
    Return all 26 possible decryptions of the ciphertext.

    Useful for brute-force attacks.

    Returns:
        list of (key, plaintext) tuples for keys 0..25
    """
    return [(k, decrypt(ciphertext, k)) for k in range(ALPHABET_SIZE)]


# ── Quick demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    msg = "Hello, World!"
    key = 13   # ROT-13 as a classic example

    ct = encrypt(msg, key)
    pt = decrypt(ct, key)

    print(f"Original   : {msg}")
    print(f"Key        : {key}")
    print(f"Encrypted  : {ct}")
    print(f"Decrypted  : {pt}")
    print(f"Match      : {msg == pt}")

    print("\n-- All 26 decryptions of ciphertext --")
    for k, plaintext in get_all_decryptions(ct):
        print(f"  Key {k:>2}: {plaintext}")
