"""
token_generator.py -- Predictable Timestamp-Seeded Token Generator
==================================================================
Lab 10 | CryptoLabX Group 01 | 22CPP307

Simulates a vulnerable web application that generates 16-byte password reset
tokens by seeding Python's MT19937 PRNG with the current integer Unix timestamp:
    1. Records timestamp T = int(time.time()) in Unix seconds
    2. Seeds MT19937 with T
    3. Generates 16 consecutive 8-bit values and combines into a 16-byte token
    4. Formats and displays T and the token in hexadecimal
"""

import random
import time
import sys


def generate_reset_token(timestamp: int = None) -> tuple[int, bytes, str]:
    """
    Generate a 16-byte password reset token using MT19937 seeded with a timestamp.

    Args:
        timestamp: Unix epoch timestamp in integer seconds.
                   If None, the current system time is recorded.

    Returns:
        tuple[int, bytes, str]: (timestamp_seconds, token_raw_bytes, token_hex_string)
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Insecure PRNG initialization using predictable time value
    rng = random.Random(timestamp)

    # Generate exactly 16 consecutive 8-bit values
    token_bytes = bytes(rng.getrandbits(8) for _ in range(16))
    token_hex = token_bytes.hex()

    return timestamp, token_bytes, token_hex


if __name__ == "__main__":
    print("=" * 72)
    print("CryptoLabX Lab 10 - Part B: Vulnerable Token Generator Demo")
    print("Course: Cryptography Laboratory (22CPP307) | Group 01")
    print("=" * 72)

    current_t, raw_tok, hex_tok = generate_reset_token()

    print("\n[+] Password Reset Token Generated:")
    print(f"    Timestamp T (Dec) : {current_t} (Unix epoch seconds)")
    print(f"    Timestamp T (Hex) : 0x{current_t:08X}")
    print(f"    Timestamp (Local) : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(current_t))}")
    print(f"    Token Length      : {len(raw_tok)} bytes (128 bits)")
    print(f"    Token Value (Hex) : {hex_tok}")

    # Reproducibility verification
    re_t, re_raw, re_hex = generate_reset_token(current_t)
    assert re_hex == hex_tok, "Reproducibility verification failed!"
    print(f"    Reproducibility   : [PASS] Identical token produced from timestamp {current_t}")
    print("=" * 72)
