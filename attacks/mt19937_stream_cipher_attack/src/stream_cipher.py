"""
stream_cipher.py -- MT19937 Toy Stream Cipher Implementation
============================================================
Lab 10 | CryptoLabX Group 01 | 22CPP307

Implements a symmetric toy stream cipher using Python's inbuilt MT19937 PRNG:
    1. Generates 8-bit keystream values from MT19937: K_i in [0, 255]
    2. Encrypts plaintext via bitwise XOR: C_i = P_i ^ K_i
    3. Decrypts ciphertext via identical XOR: P_i = C_i ^ K_i
    4. Generates vulnerable test payloads (random printable prefix + 14 consecutive 'A's)
"""

import random
import string
import sys


def generate_keystream(seed: int, length: int) -> bytes:
    """
    Generate an 8-bit keystream of specified length using MT19937.

    Args:
        seed: Initializer for MT19937 PRNG (e.g. 16-bit integer).
        length: Number of keystream bytes to produce.

    Returns:
        bytes: Stream of pseudo-random bytes.
    """
    rng = random.Random(seed)
    return bytes(rng.getrandbits(8) for _ in range(length))


def encrypt(plaintext: bytes, seed: int) -> bytes:
    """
    Encrypt plaintext bytes using the MT19937 stream cipher.

    Args:
        plaintext: Raw plaintext bytes to encrypt.
        seed: Secret encryption seed.

    Returns:
        bytes: Resulting ciphertext.
    """
    keystream = generate_keystream(seed, len(plaintext))
    return bytes(p ^ k for p, k in zip(plaintext, keystream))


def decrypt(ciphertext: bytes, seed: int) -> bytes:
    """
    Decrypt ciphertext bytes using the MT19937 stream cipher.
    Because bitwise XOR is self-inverting (symmetric), decryption
    is mathematically identical to encryption with the same seed.

    Args:
        ciphertext: Raw ciphertext bytes to decrypt.
        seed: Secret decryption seed.

    Returns:
        bytes: Recovered plaintext bytes.
    """
    return encrypt(ciphertext, seed)


def generate_vulnerable_plaintext(min_prefix: int = 5, max_prefix: int = 20) -> tuple[str, str, int]:
    """
    Generate a target test plaintext payload per Assignment 10 Part A:
        - Random prefix of 5 to 20 printable characters
        - Followed by 14 consecutive 'A' characters

    Returns:
        tuple[str, str, int]: (full_plaintext, prefix, prefix_length)
    """
    prefix_len = random.randint(min_prefix, max_prefix)
    # Printable ASCII characters (excluding newline/carriage return for clarity)
    charset = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    prefix = "".join(random.choice(charset) for _ in range(prefix_len))
    known_suffix = "A" * 14
    full_plaintext = prefix + known_suffix
    return full_plaintext, prefix, prefix_len


def generate_16bit_seed() -> int:
    """
    Select a random 16-bit seed in range [0, 65535] (0x0000 to 0xFFFF).
    """
    return random.randint(0, 0xFFFF)


if __name__ == "__main__":
    print("=" * 72)
    print("CryptoLabX Lab 10 - MT19937 Toy Stream Cipher Demo")
    print("Course: Cryptography Laboratory (22CPP307) | Group 01")
    print("=" * 72)

    # 1. Test message verification of encrypt / decrypt symmetry
    test_message = b"Cryptography Laboratory - Group 01 Test Payload"
    test_seed = 0x1337
    encrypted = encrypt(test_message, test_seed)
    decrypted = decrypt(encrypted, test_seed)

    print("\n[1] Basic Cipher Symmetry Verification:")
    print(f"    Original Message  : {test_message.decode('ascii')}")
    print(f"    Secret Seed       : {test_seed} (0x{test_seed:04X})")
    print(f"    Ciphertext (Hex)  : {encrypted.hex()}")
    print(f"    Decrypted Message : {decrypted.decode('ascii')}")
    assert decrypted == test_message, "Decryption symmetry failed!"
    print("    [PASS] Encrypt/Decrypt symmetry confirmed.")

    # 2. Assignment 10 Part A Vulnerable Payload Generation
    pt_str, prefix_str, prefix_len = generate_vulnerable_plaintext()
    seed_16bit = generate_16bit_seed()
    ciphertext = encrypt(pt_str.encode("ascii"), seed_16bit)

    print("\n[2] Assignment 10 Part A Target Payload Generation:")
    print(f"    Prefix Length     : {prefix_len} characters")
    print(f"    Random Prefix     : '{prefix_str}'")
    print(f"    Known Sequence    : 'AAAAAAAAAAAAAA' (14 x 'A')")
    print(f"    Full Plaintext    : '{pt_str}'")
    print(f"    Plaintext (Hex)   : {pt_str.encode('ascii').hex()}")
    print(f"    Selected 16b Seed : {seed_16bit} (0x{seed_16bit:04X})")
    print(f"    Ciphertext Length : {len(ciphertext)} bytes")
    print(f"    Ciphertext (Hex)  : {ciphertext.hex()}")
    print("=" * 72)
