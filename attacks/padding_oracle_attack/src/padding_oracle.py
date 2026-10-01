"""
padding_oracle.py -- Padding Oracle Simulation
===============================================
Lab 7 | CryptoLabX Group 01 | 22CPP307

Simulates a server-side padding oracle.
The oracle takes a ciphertext (IV + encrypted blocks), decrypts it using
the hidden AES key, and returns ONLY whether the padding is valid or not.

The oracle MUST NOT return:
    - The decrypted plaintext
    - Any information about which byte failed
    - The key

This is the ONLY interface the attacker has with the "server".
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from aes_cbc import aes_cbc_decrypt_raw, pkcs7_validate, BLOCK_SIZE

# ANSI colour helpers
W = "\033[1m"; C = "\033[96m"; G = "\033[92m"
Y = "\033[93m"; R = "\033[91m"; X = "\033[0m"


class PaddingOracle:
    """
    Simulates a padding oracle with an internally stored AES key.

    The key is set once at construction and NEVER exposed.
    The only public method is query(), which returns True/False.

    Usage:
        oracle = PaddingOracle(secret_key)
        result = oracle.query(iv_and_ciphertext)  # True or False
    """

    def __init__(self, key: bytes):
        """
        Store the AES key internally.
        The attack code must NOT access self._key.
        """
        self._key = key
        self._query_count = 0

    @property
    def query_count(self) -> int:
        """Number of oracle queries made so far."""
        return self._query_count

    def reset_count(self) -> None:
        """Reset the query counter to zero."""
        self._query_count = 0

    def query(self, iv_and_ciphertext: bytes) -> bool:
        """
        The padding oracle function.

        Takes the concatenation of a 16-byte IV and one or more 16-byte
        ciphertext blocks.  Decrypts using the hidden key and returns
        ONLY whether the resulting PKCS#7 padding is valid.

        Args:
            iv_and_ciphertext: bytes of length >= 32
                               (16-byte IV + at least one 16-byte block)

        Returns:
            True  if the decrypted padding is valid PKCS#7
            False if padding is invalid or input is malformed

        This is the ONLY information the attacker receives.
        """
        self._query_count += 1

        # Basic sanity checks
        if len(iv_and_ciphertext) < 2 * BLOCK_SIZE:
            return False
        if len(iv_and_ciphertext) % BLOCK_SIZE != 0:
            return False

        iv = iv_and_ciphertext[:BLOCK_SIZE]
        ct = iv_and_ciphertext[BLOCK_SIZE:]

        try:
            decrypted = aes_cbc_decrypt_raw(ct, self._key, iv)
            return pkcs7_validate(decrypted)
        except Exception:
            return False


# ── Quick demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from aes_cbc import generate_key, aes_cbc_encrypt

    print("Padding Oracle Demo")
    print("=" * 50)

    key = generate_key()
    oracle = PaddingOracle(key)

    msg = b"Test message for oracle"
    iv, ct = aes_cbc_encrypt(msg, key)

    # Valid ciphertext
    valid = oracle.query(iv + ct)
    print(f"Valid ciphertext   : oracle says {valid}")

    # Tampered ciphertext (flip last byte)
    tampered_ct = bytearray(ct)
    tampered_ct[-1] ^= 0xFF
    invalid = oracle.query(iv + bytes(tampered_ct))
    print(f"Tampered ciphertext: oracle says {invalid}")

    print(f"Total queries      : {oracle.query_count}")
