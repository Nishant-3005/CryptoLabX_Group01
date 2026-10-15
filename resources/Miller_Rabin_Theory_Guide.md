# Miller-Rabin Primality Test — Theory Guide
## Cryptographic Prime Generation for RSA & Other Applications
### CryptoLabX Group 01 | 22CPP307

---

## Table of Contents

1. [Why Primes Matter in Cryptography](#1-why-primes-matter-in-cryptography)
2. [What Is a Primality Test?](#2-what-is-a-primality-test)
3. [Trial Division — The Naive Approach](#3-trial-division--the-naive-approach)
4. [Fermat's Little Theorem — The Foundation](#4-fermats-little-theorem--the-foundation)
5. [Fermat Primality Test & Its Weakness](#5-fermat-primality-test--its-weakness)
6. [The Miller-Rabin Test — Core Algorithm](#6-the-miller-rabin-test--core-algorithm)
7. [Why Miller-Rabin Works — Mathematical Intuition](#7-why-miller-rabin-works--mathematical-intuition)
8. [Error Probability & Number of Rounds](#8-error-probability--number-of-rounds)
9. [Generating Cryptographic Primes (512-bit)](#9-generating-cryptographic-primes-512-bit)
10. [Verification — Independent Checks](#10-verification--independent-checks)
11. [Worked Example](#11-worked-example)
12. [Our Assignment](#12-our-assignment)

---

## 1. Why Primes Matter in Cryptography

Large prime numbers are the foundation of modern public-key cryptography:

| System | How Primes Are Used |
|--------|-------------------|
| **RSA** | Product of two large primes `n = p × q`; security relies on difficulty of factoring n |
| **Diffie-Hellman** | Prime modulus `p` for the cyclic group Z*_p |
| **DSA / ECDSA** | Prime-order subgroups for digital signatures |
| **ElGamal** | Prime modulus for encryption |

For RSA-1024, we need two 512-bit primes. Finding them requires a fast, reliable primality test — that's Miller-Rabin.

---

## 2. What Is a Primality Test?

A **primality test** determines whether a given number is prime (only divisible by 1 and itself).

| Type | Guarantee | Speed | Example |
|------|-----------|-------|---------|
| **Deterministic** | 100% correct | Slow for large numbers | Trial division, AKS |
| **Probabilistic** | "Probably prime" with tunable confidence | Very fast | Miller-Rabin, Fermat |

Miller-Rabin is **probabilistic**: it can declare a number "probably prime" with error probability ≤ 4^(-k) where k = number of rounds. With k = 40 rounds, the error probability is ≤ 2^(-80) — astronomically small.

---

## 3. Trial Division — The Naive Approach

Test if `n` is divisible by any integer from 2 to √n:

```python
def is_prime_trial(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```

**Problem**: For a 512-bit number, √n has 256 bits ≈ 10^77. Testing 10^77 divisors is completely infeasible.

**Use case**: Trial division is still useful as a **pre-filter** — quickly eliminating candidates divisible by small primes (2, 3, 5, 7, ..., 1000) before running Miller-Rabin.

---

## 4. Fermat's Little Theorem — The Foundation

### Statement

If `p` is prime and `a` is any integer not divisible by `p`:

```
a^(p-1) ≡ 1  (mod p)
```

### Contrapositive (The Test)

If `a^(n-1) ≢ 1 (mod n)` for some `a`, then `n` is **definitely composite**.

### Example

Is n = 7 prime? Test with a = 2:
```
2^6 mod 7 = 64 mod 7 = 1  ✓  (consistent with prime)
```

Is n = 15 prime? Test with a = 2:
```
2^14 mod 15 = 16384 mod 15 = 4  ✗  (15 is composite!)
```

---

## 5. Fermat Primality Test & Its Weakness

### The Test

```
For random bases a = a_1, a_2, ..., a_k:
    Compute a^(n-1) mod n
    If any result ≠ 1 → COMPOSITE (certain)
    If all results = 1 → PROBABLY PRIME
```

### The Fatal Weakness: Carmichael Numbers

**Carmichael numbers** are composites where `a^(n-1) ≡ 1 (mod n)` for ALL bases `a` coprime to `n`. They fool the Fermat test completely!

Examples: 561, 1105, 1729 (the Hardy-Ramanujan number)

```
561 = 3 × 11 × 17  (composite!)
But: a^560 ≡ 1 (mod 561) for all a coprime to 561
```

Fermat test says "probably prime" — **wrong!**

Miller-Rabin fixes this by adding an extra check based on square roots of 1.

---

## 6. The Miller-Rabin Test — Core Algorithm

### Setup: Decompose n-1

Write `n - 1 = 2^s × d` where `d` is odd.

This means: factor out all powers of 2 from `n-1`.

```
Example: n = 221, n-1 = 220 = 2^2 × 55
         s = 2, d = 55

Example: n = 561, n-1 = 560 = 2^4 × 35
         s = 4, d = 35
```

### The Test (One Round, One Base a)

```
Input: n (candidate), a (random base, 2 ≤ a ≤ n-2)
Write n-1 = 2^s × d

Step 1: Compute x = a^d mod n

Step 2: If x == 1 or x == n-1:
            return PROBABLY PRIME  (pass this round)

Step 3: For r = 1, 2, ..., s-1:
            x = x^2 mod n
            If x == n-1:
                return PROBABLY PRIME  (pass this round)

Step 4: return COMPOSITE  (definitely not prime)
```

### Multiple Rounds

Run the test `k` times with different random bases. If ANY round says COMPOSITE → n is composite. If ALL rounds say PROBABLY PRIME → n is probably prime with error ≤ 4^(-k).

### Pseudocode

```python
def miller_rabin(n, k=40):
    """Test if n is probably prime using k rounds of Miller-Rabin."""
    if n < 2:       return False
    if n == 2 or n == 3: return True
    if n % 2 == 0:  return False
    
    # Write n-1 = 2^s × d
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # k rounds with random bases
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)          # a^d mod n (fast modular exponentiation)
        
        if x == 1 or x == n - 1:
            continue              # pass this round
        
        for _ in range(s - 1):
            x = pow(x, 2, n)      # x = x^2 mod n
            if x == n - 1:
                break             # pass this round
        else:
            return False          # COMPOSITE
    
    return True                   # PROBABLY PRIME
```

---

## 7. Why Miller-Rabin Works — Mathematical Intuition

### The Key Insight: Square Roots of 1 mod p

If `p` is prime, the equation `x² ≡ 1 (mod p)` has **exactly two solutions**:
```
x ≡ 1 (mod p)     or     x ≡ -1 ≡ p-1 (mod p)
```

These are called **trivial square roots of 1**. In a prime modulus, there are no other square roots of 1.

### What Miller-Rabin Exploits

Starting from `x = a^d mod n`, we repeatedly square:
```
a^d → a^(2d) → a^(4d) → ... → a^(2^s × d) = a^(n-1)
```

By Fermat's theorem, the final value should be 1 (mod n) if n is prime.

Now, working **backwards** from `a^(n-1) ≡ 1`:
- `a^(n-1) ≡ 1` means `(a^((n-1)/2))² ≡ 1`, so `a^((n-1)/2) ≡ ±1`
- If `a^((n-1)/2) ≡ 1`, then `(a^((n-1)/4))² ≡ 1`, so `a^((n-1)/4) ≡ ±1`
- Continue until we reach `a^d`...

If n is prime, the sequence `a^d, a^(2d), a^(4d), ..., a^(n-1)` must either:
1. **Start with 1**: `a^d ≡ 1 (mod n)`
2. **Hit -1 before reaching 1**: some `a^(2^r × d) ≡ n-1 (mod n)`

If neither happens — we found a **non-trivial square root of 1** — which is impossible for primes. Therefore **n must be composite**.

### Why It Beats Fermat

Carmichael numbers pass Fermat (a^(n-1) ≡ 1 for all a), but they can't hide non-trivial square roots of 1 from Miller-Rabin. At least 75% of bases will detect a Carmichael number as composite.

---

## 8. Error Probability & Number of Rounds

### Per Round

For a single random base, the probability of a composite passing Miller-Rabin is **at most 1/4** (proven by Rabin, 1980).

### After k Rounds

```
Pr[composite passes k rounds] ≤ (1/4)^k = 4^(-k)
```

| Rounds (k) | Error Probability | Equivalent Security |
|-----------|-------------------|-------------------|
| 10 | ≤ 2^(-20) ≈ 10^(-6) | One in a million |
| 20 | ≤ 2^(-40) ≈ 10^(-12) | One in a trillion |
| 40 | ≤ 2^(-80) | Stronger than AES-80 |
| 64 | ≤ 2^(-128) | AES-128 level |

For 512-bit primes, **k = 20–40 rounds** is standard practice.

---

## 9. Generating Cryptographic Primes (512-bit)

### Algorithm

```
1. Generate a random 512-bit odd number:
   - Set bit 0 = 1 (odd)
   - Set bit 511 = 1 (ensures exactly 512 bits)
   
2. Pre-filter: check divisibility by small primes (2, 3, 5, ..., 1000)
   - Eliminates ~80% of candidates cheaply
   
3. Apply Miller-Rabin with k rounds
   - If COMPOSITE → go back to step 1
   - If PROBABLY PRIME → accept!

4. Verify:
   - Confirm bit length == 512
   - Confirm passes Miller-Rabin
   - Cross-check with an independent method (e.g., sympy.isprime)
```

### How Many Candidates to Expect?

By the Prime Number Theorem, the density of primes near N is approximately `1 / ln(N)`.

For 512-bit numbers: `ln(2^512) ≈ 355`

So on average, we test about **355 candidates** before finding a prime. With the small-prime pre-filter, this drops to roughly **50–100 candidates** in practice.

### Ensuring Exactly 512 Bits

```python
import random

def generate_candidate(bits=512):
    """Generate a random odd number with exactly `bits` bits."""
    n = random.getrandbits(bits)
    n |= (1 << (bits - 1))   # Set MSB — ensures exactly 512 bits
    n |= 1                    # Set LSB — ensures odd
    return n

# Verify: n.bit_length() == 512
```

---

## 10. Verification — Independent Checks

### Method 1: Python's `sympy.isprime()`

```python
from sympy import isprime
assert isprime(candidate) == True
```

### Method 2: OpenSSL

```bash
openssl prime -hex <hex_representation>
```

### Method 3: Trial Division for Small Factors

Confirm no factor ≤ 10,000 exists (a sanity check, not a full proof).

### Method 4: Multiple Independent Miller-Rabin Runs

Run Miller-Rabin with fixed bases [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] for deterministic results up to certain bounds.

---

## 11. Worked Example

### Test n = 221 with base a = 174

```
n = 221
n - 1 = 220 = 2^2 × 55   →   s = 2, d = 55

Step 1: x = 174^55 mod 221 = 47
Step 2: x ≠ 1 and x ≠ 220   → continue

Step 3 (r = 1):
    x = 47^2 mod 221 = 2209 mod 221 = 220 = n-1
    → PROBABLY PRIME? Not so fast...
```

Actually 221 = 13 × 17 (composite!). One round passed — but with a different base:

### Test n = 221 with base a = 137

```
Step 1: x = 137^55 mod 221 = 188
Step 2: x ≠ 1 and x ≠ 220   → continue

Step 3 (r = 1):
    x = 188^2 mod 221 = 35344 mod 221 = 205
    205 ≠ 220   → no break

Step 4: → COMPOSITE ✓
```

This shows why **multiple rounds are essential** — a single round can miss a composite.

### Test n = 104729 (actually prime)

```
n - 1 = 104728 = 2^3 × 13091   →   s = 3, d = 13091

Base a = 2:
    x = 2^13091 mod 104729 = 104728 = n-1   → PASS (hit -1 immediately)

Base a = 3:
    x = 3^13091 mod 104729 = 1   → PASS (started at 1)
```

All rounds pass → 104729 is probably prime (and it actually is!).

---

## 12. Our Assignment

| Requirement | How We Address It |
|-------------|------------------|
| Generate 512-bit probable prime | `generate_prime(512)` with random candidates |
| Use Miller-Rabin with multiple bases | `miller_rabin(n, k=40)` with random bases |
| Report candidates tested | Counter in generation loop |
| Report execution time | `time.time()` around generation |
| Verify bit length | `n.bit_length() == 512` |
| Verify passes Miller-Rabin | Re-run with different bases |
| Independent verification | `sympy.isprime()` or trial division |

### Deliverables

1. **Python program**: `miller_rabin.py` (core), `prime_generator.py` (generation), `main.py` (runner)
2. **Experimental results table** in the report
3. **Verification** output showing the prime passes all checks

---

## Glossary

| Term | Definition |
|------|-----------|
| **Probable prime** | Number that passes probabilistic primality test; not proven prime but extremely likely |
| **Witness** | A base `a` that proves `n` is composite in Miller-Rabin |
| **Strong liar** | A base `a` that fails to detect a composite (passes the test incorrectly) |
| **Carmichael number** | Composite that passes Fermat test for all coprime bases |
| **Modular exponentiation** | Computing `a^b mod n` efficiently via repeated squaring |
| **Bit length** | Number of bits in binary representation; 512-bit means 2^511 ≤ n < 2^512 |

---

*Group 01 — Nishant (2024UCP1773) & Lokesh Saini (2024UCP1505)*
