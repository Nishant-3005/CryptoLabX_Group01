# Lab 8 — Cryptographic Prime Generation Using Miller-Rabin
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)

---

## 1. Aim and Objectives

1. **Aim**: To generate a cryptographically strong probable prime of exact 512-bit length using the Miller-Rabin probabilistic primality test.
2. **Objectives**:
   - Generate cryptographically random odd candidate integers of exactly 512 bits.
   - Implement an efficient two-tier primality pipeline: fast trial division pre-filtering with small primes (< 1,000) followed by 40-round Miller-Rabin tests.
   - Verify that the generated candidate satisfies exact bit-length criteria and passes multi-point independent primality tests (12 fixed prime bases, extended trial division up to 50,000, and SymPy `isprime()`).
   - Measure and analyze empirical candidate search counts, execution latency, and error bounds.

---

## 2. Mathematical Foundation

### 2.1 The Need for Large Primes in Cryptography
Public-key cryptosystems such as RSA, Diffie-Hellman Key Exchange (DHKE), and the Digital Signature Algorithm (DSA) rely on the mathematical difficulty of the Integer Factorization Problem (IFP) or the Discrete Logarithm Problem (DLP). 

In RSA, the modulus $n = p \cdot q$ is the product of two distinct large prime numbers. Generating secure RSA keys requires selecting random 512-bit, 1024-bit, or 2048-bit primes that cannot be factored by known general-purpose algorithms like the General Number Field Sieve (GNFS).

### 2.2 Prime Number Theorem and Candidate Density
By the **Prime Number Theorem (PNT)**:
$$\pi(x) \approx \frac{x}{\ln x}$$

For numbers around $N = 2^{512}$:
$$\text{Density of primes} \approx \frac{1}{\ln(2^{512})} = \frac{1}{512 \cdot \ln 2} \approx \frac{1}{354.89}$$

Because all even numbers except 2 are composite, restricting candidate search exclusively to odd integers doubles the density:
$$\text{Average odd candidates before finding a prime} \approx \frac{354.89}{2} \approx 177$$

Pre-filtering with the first 168 small primes up to 997 eliminates approximately 80% of composites immediately with inexpensive modular reductions before invoking Miller-Rabin exponentiations.

### 2.3 The Miller-Rabin Primality Test
The Miller-Rabin test improves upon Fermat's test ($a^{n-1} \equiv 1 \pmod n$) by detecting Carmichael numbers (composite numbers like $561$ for which Fermat's test falsely outputs prime for all coprime bases).

For any odd candidate $n > 2$:
1. Factor out all powers of 2 from $n - 1$:
   $$n - 1 = 2^s \cdot d \quad \text{where } d \text{ is odd, } s \ge 1$$
2. Choose a random base $a \in [2, n - 2]$ and compute:
   $$x_0 = a^d \pmod n$$
3. If $x_0 \equiv 1 \pmod n$ or $x_0 \equiv n - 1 \pmod n$, $n$ passes this round.
4. Otherwise, compute successive squares for $r = 1, 2, \dots, s - 1$:
   $$x_r = x_{r-1}^2 \equiv a^{2^r \cdot d} \pmod n$$
   - If $x_r \equiv n - 1 \pmod n$, $n$ passes this round.
   - If $x_r \equiv 1 \pmod n$ before encountering $-1$, a non-trivial square root of 1 modulo $n$ has been found, proving $n$ is **definitely composite**.
5. If the sequence terminates without ever reaching $n - 1$, $n$ is **definitely composite**.

### 2.4 Error Probability Bound
If $n$ is composite, the probability that a randomly chosen base $a$ falsely declares $n$ prime (i.e., $a$ is a Miller-Rabin liar) is at most $\frac{1}{4}$:
$$P(\text{composite passes } k \text{ independent rounds}) \le \left(\frac{1}{4}\right)^k = 4^{-k} = 2^{-2k}$$

For $k = 40$ rounds (as recommended by NIST FIPS 186-4):
$$P_{\text{error}} \le 4^{-40} = 2^{-80} \approx 8.27 \times 10^{-25}$$

This probability is smaller than the probability of hardware cosmic ray bit-flips during computation, making it cryptographically negligible.

---

## 3. Implementation Architecture

The implementation in `math/miller_rabin_prime/` is modularized into three core components:

```
math/miller_rabin_prime/
├── README.md                    # Module documentation, usage instructions & architecture
├── outputs/
│   └── results.txt              # Auto-generated verification outputs & experimental data
├── reports/
│   └── Miller_Rabin_Report.md   # Comprehensive laboratory evaluation report
└── src/
    ├── miller_rabin.py          # Core Miller-Rabin engine with trial division
    ├── prime_generator.py       # 512-bit odd candidate generator with small prime filter
    ├── verification.py          # Multi-faceted verification suite
    └── main.py                  # Main CLI pipeline, benchmark runner, and exporter
```

### Module Responsibilities
1. **`miller_rabin.py`**:
   - `decompose(n)`: Decomposes $n - 1$ into $2^s \cdot d$ using fast bitwise shifts.
   - `miller_rabin_single(n, a)`: Executes a single test round against base $a$.
   - `miller_rabin(n, k=40)`: Runs $k$ independent tests using cryptographically randomized bases.
2. **`prime_generator.py`**:
   - `generate_candidate(bits=512)`: Generates a random integer with MSB ($2^{511}$) set to guarantee exact 512-bit size, and LSB set to guarantee oddness.
   - `passes_small_prime_filter(n)`: Filters candidates divisible by primes $\le 997$.
   - `generate_prime(bits=512, mr_rounds=40)`: Orchestrates the search loop until a candidate survives all 40 rounds.
3. **`verification.py`**:
   - `verify_bit_length(n, 512)`: Asserts `n.bit_length() == 512`.
   - `verify_miller_rabin_fixed_bases(n)`: Evaluates against the first 12 deterministic prime bases $[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]$.
   - `verify_trial_division(n, limit=50000)`: Tests absence of small factors up to 50,000.
   - `verify_sympy(n)`: Cross-verifies using SymPy's certified `isprime()` algorithm.
4. **`main.py`**:
   - Orchestrates prime generation, triggers verifications, executes statistical benchmarking, and persists output to `outputs/results.txt`.

---

## 4. Experimental Results

The program was executed on the laboratory system. Below is the experimental results table specified in the assignment submission criteria:

### Submission Experimental Results Table

| Parameter | Value |
| :--- | :--- |
| **Assigned bit length** | **512 bits** |
| **Generated prime candidate (Decimal)** | `11782450536905235218713119628538849294462052458807057413077746370546213829238512171262933291414995695830135485255405162230616138927192051672382486731359221` |
| **Generated prime candidate (Hexadecimal)**| `0xe0f76b265cf06d40ecfcaa588f829d58ceeba43c1861c9dda88027296a2899ee4ea8c38ea191d17dd72da8bb6f349f2184f4926f8e447bea5eb3b7158abd03f5` |
| **Actual bit length of candidate** | **512 bits** |
| **Number of candidates tested** | **651** |
| **Number of Miller-Rabin rounds** | **40 rounds** |
| **Theoretical error bound** | $\le 4^{-40} \approx 8.27 \times 10^{-25}$ |
| **Total execution time** | **0.1270 seconds** |

---

## 5. Independent Verification

All four verification criteria were independently evaluated on the generated prime:

| Verification Test | Test Description | Result |
| :--- | :--- | :---: |
| **1. Bit Length Verification** | Verified that $\lfloor \log_2(n) \rfloor + 1 = 512$ | **PASS** (512 bits) |
| **2. Fixed Base Miller-Rabin** | Tested against first 12 primes: $[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]$ | **PASS** |
| **3. Extended Trial Division** | Verified no prime divisors up to limit = 50,000 | **PASS** |
| **4. SymPy `isprime()`** | Tested against SymPy's Baillie-PSW / APRCL primality check | **PASS** |
| **Overall Primality Decision** | Verified probable prime with error probability $\le 8.27 \times 10^{-25}$ | **CONFIRMED PRIME** |

---

## 6. Statistical Benchmark and Performance Analysis

To evaluate the consistency and stability of candidate generation, 5 consecutive 512-bit primes were generated and evaluated:

| Run # | Candidates Tested | Execution Time (s) | Bit Length | Verification Status |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 651 | 0.1270 s | 512 | PASS |
| 2 | 269 | 0.0737 s | 512 | PASS |
| 3 | 168 | 0.0528 s | 512 | PASS |
| 4 | 4 | 0.0289 s | 512 | PASS |
| 5 | 516 | 0.1089 s | 512 | PASS |
| **Average** | **321.6 candidates** | **0.0783 s** | **512** | **ALL PASSED** |

### Observations:
1. **Efficiency of Pre-Filtering**: Filtering with small primes up to 997 rejects ~80% of composite candidates before modular exponentiation, resulting in generation times under 0.15 seconds per 512-bit prime.
2. **Variance in Candidates**: Because prime distribution follows Poisson-like spacing locally, candidate counts varied from 4 to 651, with an empirical mean of 321.6 (consistent with the theoretical expectation of $\approx 177$ survivor candidates).
3. **Execution Latency**: Python's built-in 3-argument `pow(a, d, n)` leverages optimized C-level Montgomery multiplication, yielding sub-millisecond execution for each 40-round Miller-Rabin test.

---

## 7. Security Best Practices

1. **Rounds Selection ($k=40$)**: While 20 rounds are often used for general testing ($2^{-40}$ error bound), 40 rounds are mandated by NIST SP 800-56B and FIPS 186-4 for generating primes in RSA key pairs ($2^{-80}$ security margin).
2. **Cryptographic Randomness**: For production use, candidate bits must originate from an OS-level Cryptographically Secure Pseudorandom Number Generator (CSPRNG) such as `secrets.randbits()` or `/dev/urandom` to prevent prime prediction attacks.
3. **Avoidance of Fermat-Only Tests**: Relying solely on Fermat's Little Theorem leaves cryptosystems completely open to false positives caused by Carmichael numbers ($561, 1105, 1729, \dots$). The Miller-Rabin algorithm eliminates this vulnerability by checking non-trivial square roots of 1 modulo $n$.

---

## 8. Conclusion

A cryptographically sound, verified 512-bit prime was successfully generated using the Miller-Rabin algorithm. The implementation demonstrated:
- Strict compliance with exact 512-bit MSB/LSB boundaries.
- Rapid generation times ($< 0.1$ seconds on average) enabled by trial division pre-filtering.
- Thorough validation across 40 random bases, 12 fixed deterministic bases, trial division, and SymPy's independent primality checker.
- Complete alignment with the course requirements for Lab 8.
