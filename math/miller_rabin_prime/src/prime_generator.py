"""
prime_generator.py -- 512-bit Cryptographic Prime Generator
===========================================================
Lab 8 | CryptoLabX Group 01 | 22CPP307

Generates probable primes of specified bit length (e.g. 512 bits)
using random candidate generation, trial division pre-filtering with
small primes, and the Miller-Rabin probabilistic primality test.
"""

import random
import time
from miller_rabin import miller_rabin

# Prime numbers up to ~1000 for fast pre-filtering
SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
    67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
    139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211,
    223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283,
    293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379,
    383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461,
    463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563,
    569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643,
    647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739,
    743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829,
    839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937,
    941, 947, 953, 967, 971, 977, 983, 991, 997,
]


def generate_candidate(bits: int = 512) -> int:
    """
    Generate an odd random integer of exact bit length.

    Sets MSB to 1 so the integer has bit_length == bits.
    Sets LSB to 1 so the integer is odd.
    """
    n = random.getrandbits(bits)
    n |= (1 << (bits - 1)) | 1  # MSB=1 ensures bit length, LSB=1 ensures odd
    return n


def passes_small_prime_filter(n: int) -> bool:
    """
    Check if n is divisible by any prime in SMALL_PRIMES.

    Returns:
        True if n is prime or has no small prime factor.
        False if n is composite (divisible by a small prime).
    """
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    return True


def generate_prime(bits: int = 512, mr_rounds: int = 40, callback=None) -> dict:
    """
    Generate a cryptographic probable prime of the specified bit length.

    Algorithm:
        1. Repeatedly generate candidate integers of length `bits`.
        2. Filter out candidates divisible by small primes (<1000).
        3. Subject survivor candidates to `mr_rounds` Miller-Rabin rounds.
        4. Return the first candidate that passes all rounds.

    Args:
        bits: bit length of prime to generate (default: 512)
        mr_rounds: number of Miller-Rabin rounds with random bases (default: 40)
        callback: optional callable for logging progress (count, candidate, status)

    Returns:
        dict with prime details and generation metrics.
    """
    start_time = time.time()
    count = 0

    while True:
        count += 1
        candidate = generate_candidate(bits)

        if callback:
            callback(count, candidate, "candidate_generated")

        if not passes_small_prime_filter(candidate):
            continue

        if callback:
            callback(count, candidate, "passed_filter")

        if miller_rabin(candidate, k=mr_rounds):
            elapsed = time.time() - start_time
            if callback:
                callback(count, candidate, "found_prime")
            return {
                'prime': candidate,
                'bit_length': candidate.bit_length(),
                'candidates_tested': count,
                'mr_rounds': mr_rounds,
                'time_seconds': elapsed
            }


if __name__ == "__main__":
    print("=" * 70)
    print("CryptoLabX Lab 8 - 512-bit Cryptographic Prime Generator")
    print("Course: Cryptography Laboratory (22CPP307) | Group 01")
    print("=" * 70)
    print("Generating a 512-bit prime candidate with 40 Miller-Rabin rounds...")

    result = generate_prime(bits=512, mr_rounds=40)

    print("\nGeneration Results:")
    print("-" * 70)
    print(f"Assigned Bit Length   : 512")
    print(f"Actual Bit Length     : {result['bit_length']}")
    print(f"Candidates Tested     : {result['candidates_tested']}")
    print(f"Miller-Rabin Rounds   : {result['mr_rounds']}")
    print(f"Total Execution Time  : {result['time_seconds']:.4f} seconds")
    print("\nGenerated Prime (Decimal):")
    print(result['prime'])
    print("\nGenerated Prime (Hex):")
    print(hex(result['prime']))
    print("=" * 70)
