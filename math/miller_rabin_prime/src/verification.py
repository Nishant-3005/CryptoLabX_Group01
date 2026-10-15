"""
verification.py -- Independent Primality and Parameter Verification
===================================================================
Lab 8 | CryptoLabX Group 01 | 22CPP307

Performs independent multi-faceted verification on the generated prime:
    1. Exact bit length check (e.g. 512 bits)
    2. Miller-Rabin test using first 12 fixed prime bases
    3. Extended trial division up to limit (e.g. 50,000)
    4. Independent verification via sympy.isprime (if available)
"""

from miller_rabin import miller_rabin_single, decompose


def verify_bit_length(n: int, expected_bits: int = 512) -> bool:
    """
    Verify that candidate integer has exact expected bit length.
    """
    return n.bit_length() == expected_bits


def verify_miller_rabin_fixed_bases(n: int) -> bool:
    """
    Tests n against first 12 primes:
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] using miller_rabin_single(n, base).
    Returns True if all 12 pass.
    """
    fixed_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for base in fixed_bases:
        if not miller_rabin_single(n, base):
            return False
    return True


def verify_trial_division(n: int, limit: int = 50000) -> bool:
    """
    Checks divisibility up to limit (testing 2 and odd numbers).
    Returns True if no divisor found.
    """
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d <= limit and d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def verify_sympy(n: int) -> bool:
    """
    Optional verification using sympy.isprime.
    If sympy is not installed, gracefully catch ImportError and return True.
    """
    try:
        from sympy import isprime
        return bool(isprime(n))
    except ImportError:
        return True


def run_all_verifications(n: int, bits: int = 512) -> dict:
    """
    Executes all checks and prints nicely formatted pass/fail outputs.
    Returns dictionary of all check results.
    """
    print("=" * 70)
    print("Independent Primality and Parameter Verification")
    print("=" * 70)

    bit_ok = verify_bit_length(n, bits)
    print(f"[*] Bit Length Check ({bits} bits) : [{'PASS' if bit_ok else 'FAIL'}] (Actual: {n.bit_length()} bits)")

    mr_ok = verify_miller_rabin_fixed_bases(n)
    print(f"[*] Miller-Rabin (12 fixed bases) : [{'PASS' if mr_ok else 'FAIL'}]")

    td_ok = verify_trial_division(n, limit=50000)
    print(f"[*] Extended Trial Division (50k) : [{'PASS' if td_ok else 'FAIL'}]")

    sympy_ok = verify_sympy(n)
    try:
        import sympy
        sympy_status = "PASS" if sympy_ok else "FAIL"
        print(f"[*] SymPy Independent isprime()   : [{sympy_status}]")
    except ImportError:
        print(f"[*] SymPy Independent isprime()   : [SKIPPED - sympy not installed]")

    all_passed = bit_ok and mr_ok and td_ok and sympy_ok
    print("-" * 70)
    print(f"Overall Verification Status       : [{'PASS' if all_passed else 'FAIL'}]")
    print("=" * 70)

    return {
        'bit_length_verified': bit_ok,
        'miller_rabin_fixed_bases': mr_ok,
        'trial_division_verified': td_ok,
        'sympy_verified': sympy_ok,
        'all_passed': all_passed
    }


if __name__ == "__main__":
    from prime_generator import generate_prime

    print("Generating a test 512-bit prime for verification...")
    res = generate_prime(bits=512, mr_rounds=40)
    test_prime = res['prime']

    print(f"\nVerifying generated 512-bit prime:")
    results = run_all_verifications(test_prime, bits=512)
