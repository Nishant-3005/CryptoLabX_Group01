"""
miller_rabin.py -- Miller-Rabin Primality Test Implementation
==============================================================
Lab 8 | CryptoLabX Group 01 | 22CPP307

The Miller-Rabin test is a probabilistic primality test.  Given an odd
candidate n > 3, it writes  n-1 = 2^s * d  (d odd) and checks whether
random bases a satisfy one of the two primality conditions:

    (1)  a^d  ==  1   (mod n)          -- sequence starts at 1
    (2)  a^(2^r * d)  ==  n-1  (mod n)  -- sequence hits -1

If neither holds for a given base, n is COMPOSITE (certain).
If both rounds pass for k bases, n is PROBABLY PRIME with
error probability <= 4^(-k).

Usage:
    from miller_rabin import miller_rabin
    miller_rabin(n, k=40)  ->  True / False
"""

import random

# ANSI colour helpers
W = "\033[1m"; C = "\033[96m"; G = "\033[92m"
Y = "\033[93m"; R = "\033[91m"; X = "\033[0m"

# -- Small primes for quick pre-filtering ---------------------------------

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


# -- Core functions -------------------------------------------------------

def decompose(n: int) -> tuple:
    """
    Write n-1 = 2^s * d where d is odd.

    Repeatedly divides (n-1) by 2 until the result is odd.

    Args:
        n: odd integer > 2
    Returns:
        (s, d) tuple where n-1 = 2^s * d and d is odd

    Example:
        decompose(221) -> (2, 55)   because 220 = 2^2 x 55
        decompose(561) -> (4, 35)   because 560 = 2^4 x 35
    """
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    return s, d


def miller_rabin_single(n: int, a: int) -> bool:
    """
    Single round of Miller-Rabin with base a.

    Tests whether n passes the MR conditions for base a:
        (1) a^d == 1 (mod n)
        (2) a^(2^r * d) == n-1 (mod n) for some 0 <= r < s

    Args:
        n: odd candidate > 3
        a: base to test (2 <= a <= n-2)
    Returns:
        True  if n passes (probably prime for this base)
        False if n fails  (definitely composite -- a is a witness)
    """
    s, d = decompose(n)

    # Step 1: x = a^d mod n  (uses Python's built-in fast modular exp)
    x = pow(a, d, n)

    # Condition 1: a^d == 1 (mod n)
    if x == 1 or x == n - 1:
        return True   # pass this round

    # Condition 2: check the squaring chain
    for _ in range(s - 1):
        x = pow(x, 2, n)     # x = x^2 mod n
        if x == n - 1:
            return True       # found -1 -> pass

    # Neither condition met -> n is composite
    return False


def is_prime_trial_division(n: int, limit: int = 10000) -> bool:
    """
    Quick trial-division pre-filter.

    Tests divisibility of n by all primes up to min(limit, sqrt(n)).
    Used to quickly eliminate obviously composite candidates before
    running the more expensive Miller-Rabin test.

    Args:
        n    : integer to test
        limit: check divisors up to this value
    Returns:
        True  if n has no small factor (may still be composite)
        False if n is divisible by a small prime
    """
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if p > limit:
            break
        if n == p:
            return True
        if n % p == 0:
            return False
    return True


def miller_rabin(n: int, k: int = 40) -> bool:
    """
    Full Miller-Rabin primality test with k rounds.

    First handles trivial cases and runs a quick trial-division filter,
    then performs k rounds of Miller-Rabin with random bases.

    Args:
        n: integer to test for primality
        k: number of rounds (error probability <= 4^(-k))
    Returns:
        True  if n is probably prime
        False if n is definitely composite

    Notes:
        - k=40 gives error probability <= 2^(-80), suitable for 512-bit primes
        - Uses Python's pow(a, d, n) for fast modular exponentiation
    """
    # Trivial cases
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Quick trial division pre-filter
    if not is_prime_trial_division(n):
        return False

    # k rounds of Miller-Rabin with random bases
    for _ in range(k):
        a = random.randrange(2, n - 1)
        if not miller_rabin_single(n, a):
            return False    # composite -- a is a witness

    return True    # probably prime


def miller_rabin_verbose(n: int, k: int = 10) -> bool:
    """
    Verbose version of Miller-Rabin that prints each round's result.
    Useful for demonstrations and reports.

    Args:
        n: integer to test
        k: number of rounds
    Returns:
        True if probably prime, False if composite
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        print(f"  {R}n is even -> COMPOSITE{X}")
        return False

    s, d = decompose(n)
    print(f"  n - 1 = {n-1} = 2^{s} x {d}")
    print(f"  Running {k} rounds...\n")
    print(f"  {'Round':<8} {'Base a':<20} {'a^d mod n':<25} {'Result'}")
    print(f"  {'-'*75}")

    for i in range(1, k + 1):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            status = f"{G}PASS (initial){X}"
            print(f"  {i:<8} {a:<20} {x:<25} {status}")
            continue

        passed = False
        for r in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                status = f"{G}PASS (r={r+1}){X}"
                passed = True
                break

        if passed:
            print(f"  {i:<8} {a:<20} {'...':<25} {status}")
        else:
            status = f"{R}FAIL -> COMPOSITE{X}"
            print(f"  {i:<8} {a:<20} {x:<25} {status}")
            return False

    print(f"\n  {G}{W}All {k} rounds passed -> PROBABLY PRIME{X}")
    return True


# -- Quick demo --------------------------------------------------------------

if __name__ == "__main__":
    import time

    print("Miller-Rabin Primality Test Demo")
    print("=" * 60)

    # Test known primes
    test_cases = [
        (7, True), (11, True), (13, True),
        (221, False),     # 13 x 17
        (561, False),     # Carmichael number (3 x 11 x 17)
        (1729, False),    # Carmichael number (7 x 13 x 19)
        (104729, True),   # prime
        (2**31 - 1, True),  # Mersenne prime M31
    ]

    print(f"\n{'n':<20} {'Expected':<12} {'MR Result':<12} {'Match'}")
    print("-" * 55)
    for n, expected in test_cases:
        result = miller_rabin(n, k=20)
        match = "OK" if result == expected else "MISMATCH!"
        print(f"{n:<20} {str(expected):<12} {str(result):<12} {match}")

    # Verbose test on a small prime
    print(f"\n{'='*60}")
    print(f"Verbose test: n = 104729")
    print(f"{'='*60}")
    miller_rabin_verbose(104729, k=5)

    # Verbose test on Carmichael number 561
    print(f"\n{'='*60}")
    print(f"Verbose test: n = 561 (Carmichael number)")
    print(f"{'='*60}")
    miller_rabin_verbose(561, k=5)

    # Quick 512-bit prime generation demo
    print(f"\n{'='*60}")
    print("Generating a 512-bit probable prime...")
    print(f"{'='*60}")
    t0 = time.time()
    candidates = 0
    while True:
        candidates += 1
        n = random.getrandbits(512)
        n |= (1 << 511) | 1   # ensure 512 bits and odd
        if miller_rabin(n, k=40):
            break
    elapsed = time.time() - t0
    print(f"  Found after {candidates} candidates in {elapsed:.3f}s")
    print(f"  Prime: {n}")
    print(f"  Bit length: {n.bit_length()}")
