"""
aes_cbc.py -- AES-CBC Encryption/Decryption with PKCS#7 Padding
================================================================
Lab 7 | CryptoLabX Group 01 | 22CPP307

Provides AES-CBC encrypt/decrypt using pycryptodome, plus PKCS#7
padding utilities. The AES key is generated externally and passed in;
the attack module must NEVER receive the key directly.

Dependencies:
    pip install pycryptodome
"""

from Crypto.Cipher import AES
import os

BLOCK_SIZE = 16  # AES block size in bytes (128 bits)


# ── PKCS#7 Padding ──────────────────────────────────────────────────────────

def pkcs7_pad(data: bytes) -> bytes:
    """
    Apply PKCS#7 padding to make data a multiple of BLOCK_SIZE.

    Rule: append n bytes, each of value n, where n = BLOCK_SIZE - (len(data) % BLOCK_SIZE).
    If data is already a multiple of BLOCK_SIZE, a full 16-byte padding block is added.

    Args:
        data: raw bytes to pad
    Returns:
        Padded bytes (length is a multiple of BLOCK_SIZE)

    Examples:
        b"HELLO"       -> b"HELLO" + b"\\x0b" * 11  (11 bytes padding)
        b"A" * 16      -> b"A" * 16 + b"\\x10" * 16  (full block padding)
        b"AB"          -> b"AB" + b"\\x0e" * 14
    """
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes) -> bytes:
    """
    Remove and validate PKCS#7 padding.

    Reads the last byte to determine the padding length, then verifies
    that all padding bytes have the correct value.

    Args:
        data: padded bytes (length must be a multiple of BLOCK_SIZE)
    Returns:
        Unpadded bytes
    Raises:
        ValueError: if padding is invalid
    """
    if len(data) == 0:
        raise ValueError("Empty data — cannot unpad")
    if len(data) % BLOCK_SIZE != 0:
        raise ValueError(f"Data length ({len(data)}) is not a multiple of {BLOCK_SIZE}")

    pad_len = data[-1]

    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError(f"Invalid padding value: {pad_len:#04x}")

    # Verify all padding bytes match
    for i in range(1, pad_len + 1):
        if data[-i] != pad_len:
            raise ValueError(
                f"Invalid padding at byte -{i}: expected {pad_len:#04x}, "
                f"got {data[-i]:#04x}"
            )

    return data[:-pad_len]


def pkcs7_validate(data: bytes) -> bool:
    """
    Check if data has valid PKCS#7 padding WITHOUT raising an error.

    This is the function used by the padding oracle — it returns only
    True or False, leaking no other information.

    Args:
        data: bytes to validate (should be a multiple of BLOCK_SIZE)
    Returns:
        True if padding is valid, False otherwise
    """
    try:
        pkcs7_unpad(data)
        return True
    except (ValueError, IndexError):
        return False


# ── AES-CBC Operations ──────────────────────────────────────────────────────

def generate_key(key_size: int = 16) -> bytes:
    """
    Generate a random AES key.

    Args:
        key_size: 16 (AES-128), 24 (AES-192), or 32 (AES-256)
    Returns:
        Random key bytes
    """
    if key_size not in (16, 24, 32):
        raise ValueError(f"Invalid AES key size: {key_size}")
    return os.urandom(key_size)


def aes_cbc_encrypt(plaintext: bytes, key: bytes) -> tuple:
    """
    Encrypt plaintext using AES-CBC with PKCS#7 padding.

    A random IV is generated for each encryption.

    Args:
        plaintext: raw bytes to encrypt
        key      : 16/24/32-byte AES key
    Returns:
        (iv, ciphertext) tuple — both are bytes objects
    """
    padded = pkcs7_pad(plaintext)
    iv = os.urandom(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded)
    return iv, ciphertext


def aes_cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Decrypt ciphertext using AES-CBC and remove PKCS#7 padding.

    Args:
        ciphertext: encrypted bytes (multiple of BLOCK_SIZE)
        key       : AES key (same as used for encryption)
        iv        : 16-byte initialization vector
    Returns:
        Decrypted and unpadded plaintext bytes
    Raises:
        ValueError: if padding is invalid after decryption
    """
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    return pkcs7_unpad(decrypted)


def aes_cbc_decrypt_raw(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Decrypt ciphertext using AES-CBC WITHOUT removing padding.

    Used internally by the padding oracle — returns the raw decrypted
    bytes with padding still present so that pkcs7_validate() can
    check it.

    Args:
        ciphertext: encrypted bytes (multiple of BLOCK_SIZE)
        key       : AES key
        iv        : 16-byte initialization vector
    Returns:
        Raw decrypted bytes (padding NOT stripped)
    """
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)


# ── Quick demo ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("AES-CBC + PKCS#7 Padding Demo")
    print("=" * 50)

    key = generate_key(16)
    msg = b"Hello, Padding Oracle Attack!"

    print(f"Plaintext       : {msg}")
    print(f"Plaintext hex   : {msg.hex()}")
    print(f"Plaintext len   : {len(msg)} bytes")

    # Pad
    padded = pkcs7_pad(msg)
    print(f"\nPadded hex      : {padded.hex()}")
    print(f"Padded len      : {len(padded)} bytes")
    print(f"Padding bytes   : {padded[len(msg):]}")

    # Encrypt
    iv, ct = aes_cbc_encrypt(msg, key)
    print(f"\nIV              : {iv.hex()}")
    print(f"Ciphertext      : {ct.hex()}")
    print(f"Ciphertext len  : {len(ct)} bytes ({len(ct) // BLOCK_SIZE} blocks)")

    # Decrypt
    pt = aes_cbc_decrypt(ct, key, iv)
    print(f"\nDecrypted       : {pt}")
    print(f"Match           : {pt == msg}")

    # Validate padding
    raw = aes_cbc_decrypt_raw(ct, key, iv)
    print(f"\nRaw decrypt hex : {raw.hex()}")
    print(f"Valid padding?  : {pkcs7_validate(raw)}")

    # Test invalid padding
    tampered = bytearray(raw)
    tampered[-1] ^= 0xFF
    print(f"Tampered valid? : {pkcs7_validate(bytes(tampered))}")
