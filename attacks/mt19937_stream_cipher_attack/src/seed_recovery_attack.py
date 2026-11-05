"""
seed_recovery_attack.py -- MT19937 16-Bit Seed Known-Plaintext Attack Engine
============================================================================
Lab 10 | CryptoLabX Group 01 | 22CPP307

Implements an exhaustive brute-force attack on the 16-bit MT19937 seed space:
    1. Seed space: 2^16 = 65,536 candidate seeds (0x0000 to 0xFFFF)
    2. Known plaintext fragment: 14 consecutive 'A' characters (b"AAAAAAAAAAAAAA")
    3. Offset is unknown to the attacker (5 to 20 byte prefix)
    4. Evaluates candidates using a sliding-window substring match
    5. Fully decrypts and verifies payload integrity with the recovered seed
"""

import time
import sys
from stream_cipher import (
    generate_keystream,
    decrypt,
    generate_vulnerable_plaintext,
    generate_16bit_seed,
    encrypt
)


def brute_force_16bit_seed(
    ciphertext: bytes,
    known_sequence: bytes = b"AAAAAAAAAAAAAA",
    max_seed: int = 65535,
    callback=None
) -> dict:
    """
    Exhaustively searches all candidate seeds from 0 to max_seed.
    For each candidate seed, decrypts the ciphertext and checks if
    the known_sequence appears anywhere as a contiguous substring.

    Args:
        ciphertext: Intercepted ciphertext bytes.
        known_sequence: Known plaintext fragment (default: 14 'A's).
        max_seed: Maximum seed value to test (default: 65,535).
        callback: Optional callable for logging progress (tested, elapsed).

    Returns:
        dict: Detailed attack and recovery metrics.
    """
    start_time = time.time()
    ct_len = len(ciphertext)
    recovered = None
    seeds_tested = 0

    # Search through all 65,536 candidate seeds
    for candidate_seed in range(max_seed + 1):
        seeds_tested += 1

        # Periodic progress notification
        if callback and (seeds_tested % 10000 == 0 or candidate_seed == max_seed):
            callback(seeds_tested, time.time() - start_time)

        # Generate candidate keystream of exact ciphertext length
        # Using decrypt() logic: C_i ^ K_i
        candidate_keystream = generate_keystream(candidate_seed, ct_len)
        candidate_pt = bytes(c ^ k for c, k in zip(ciphertext, candidate_keystream))

        # Check if known sequence is present anywhere in candidate plaintext
        if known_sequence in candidate_pt:
            elapsed = time.time() - start_time
            offset = candidate_pt.find(known_sequence)

            # Verification: re-decrypt and confirm consistency
            verified_pt = decrypt(ciphertext, candidate_seed)
            verification_pass = (verified_pt == candidate_pt) and (known_sequence in verified_pt)

            recovered = {
                "recovered_seed": candidate_seed,
                "recovered_seed_hex": f"0x{candidate_seed:04X}",
                "recovered_plaintext_bytes": candidate_pt,
                "recovered_plaintext_str": candidate_pt.decode("latin1", errors="replace"),
                "known_sequence_offset": offset,
                "seeds_tested": seeds_tested,
                "total_seed_space": max_seed + 1,
                "search_percentage": (seeds_tested / (max_seed + 1)) * 100.0,
                "elapsed_seconds": elapsed,
                "seeds_per_second": seeds_tested / elapsed if elapsed > 0 else 0.0,
                "verified": verification_pass,
            }
            break

    if recovered is None:
        elapsed = time.time() - start_time
        recovered = {
            "recovered_seed": None,
            "recovered_seed_hex": None,
            "recovered_plaintext_bytes": None,
            "recovered_plaintext_str": None,
            "known_sequence_offset": -1,
            "seeds_tested": seeds_tested,
            "total_seed_space": max_seed + 1,
            "search_percentage": 100.0,
            "elapsed_seconds": elapsed,
            "seeds_per_second": seeds_tested / elapsed if elapsed > 0 else 0.0,
            "verified": False,
        }

    return recovered


if __name__ == "__main__":
    print("=" * 72)
    print("CryptoLabX Lab 10 - Part A: 16-Bit Seed Recovery Attack Demo")
    print("=" * 72)

    # 1. Setup simulated vulnerable environment
    known_seq = b"AAAAAAAAAAAAAA"
    original_pt_str, prefix_str, prefix_len = generate_vulnerable_plaintext(min_prefix=5, max_prefix=20)
    secret_seed = generate_16bit_seed()
    ciphertext = encrypt(original_pt_str.encode("ascii"), secret_seed)

    print(f"\n[+] Simulated Sender:")
    print(f"    Secret Seed (Target)  : {secret_seed} (0x{secret_seed:04X})")
    print(f"    Secret Plaintext      : '{original_pt_str}'")
    print(f"    True Prefix Length    : {prefix_len} bytes")
    print(f"    Ciphertext (Hex)      : {ciphertext.hex()}")

    print(f"\n[*] Attacker Perspective:")
    print(f"    Known Sequence        : '{known_seq.decode('ascii')}' ({len(known_seq)} bytes)")
    print(f"    Known Sequence Offset : UNKNOWN (somewhere after 5-20 char prefix)")
    print(f"    Total Seed Space      : 65,536 seeds (2^16)")
    print(f"    Launching exhaustive brute-force search...")

    def progress_log(tested, elapsed):
        sys.stdout.write(f"\r    -> Testing candidates: {tested:,} / 65,536 ({tested/65536*100:5.1f}%) | Elapsed: {elapsed:.2f}s")
        sys.stdout.flush()

    attack_result = brute_force_16bit_seed(ciphertext, known_seq, callback=progress_log)
    print("\n")

    print("[*] Attack Results:")
    print("-" * 72)
    print(f"    Recovered Seed        : {attack_result['recovered_seed']} ({attack_result['recovered_seed_hex']})")
    print(f"    Correct Seed Match    : {'YES' if attack_result['recovered_seed'] == secret_seed else 'NO'}")
    print(f"    Recovered Plaintext   : '{attack_result['recovered_plaintext_str']}'")
    print(f"    Detected Known Offset : Byte {attack_result['known_sequence_offset']}")
    print(f"    Seeds Tested          : {attack_result['seeds_tested']:,} / {attack_result['total_seed_space']:,}")
    print(f"    Execution Time        : {attack_result['elapsed_seconds']:.4f} seconds")
    print(f"    Search Throughput     : {attack_result['seeds_per_second']:,.0f} seeds/second")
    print(f"    Solution Verification : [{'PASS' if attack_result['verified'] else 'FAIL'}]")
    print("=" * 72)

