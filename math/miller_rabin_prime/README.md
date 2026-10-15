# Lab 8 — Cryptographic Prime Generation Using Miller-Rabin (512-bit)

> **Course:** Cryptography Laboratory (22CPP307)  
> **Group:** 01  
> **Authors:** Nishant (2024UCP1773) · Lokesh Saini (2024UCP1505)  
> **Location:** `math/miller_rabin_prime/`

---

## 📌 Overview

This laboratory module implements **cryptographically secure 512-bit prime generation** using the **Miller-Rabin probabilistic primality test** with pre-filtering optimizations and multi-point independent verifications.

Public-key cryptosystems such as RSA, Diffie-Hellman Key Exchange, and DSA rely heavily on generating large, unguessable prime numbers. This module implements the complete prime discovery pipeline:
1. **Candidate Generation**: Cryptographically random odd integers with exact bit length ($2^{511} \le n < 2^{512}$).
2. **Small-Prime Pre-Filtering**: Cheap trial division with primes up to 997, rejecting ~80% of composites before modular exponentiation.
3. **Miller-Rabin Test**: 40 rounds of Miller-Rabin tests with random bases, bounding the error probability to $\le 4^{-40} \approx 8.27 \times 10^{-25}$.
4. **Independent Verification**: Bit-length validation, 12 fixed-base Miller-Rabin checks, extended trial division (up to 50,000), and SymPy `isprime()` verification.

---

## 📁 Folder Structure

```
math/miller_rabin_prime/
├── README.md                    # Module documentation & quick start
├── outputs/
│   └── results.txt              # Generated prime details & benchmark logs
├── reports/
│   └── Miller_Rabin_Report.md   # Comprehensive laboratory evaluation report
└── src/
    ├── miller_rabin.py          # Core Miller-Rabin algorithm & trial division
    ├── prime_generator.py       # 512-bit prime generation pipeline
    ├── verification.py          # Multi-point independent verification suite
    └── main.py                  # CLI orchestrator, benchmark runner & reporter
```

---

## 🚀 Quick Start

From the repository root or module directory:

```bash
# Run the complete pipeline (Generation + Verification + Benchmark + Export)
python math/miller_rabin_prime/src/main.py

# Or test individual modules:
python math/miller_rabin_prime/src/miller_rabin.py
python math/miller_rabin_prime/src/prime_generator.py
python math/miller_rabin_prime/src/verification.py
```

---

## 🔬 Method & Algorithm

### 1. Mathematical Principle
For an odd candidate $n > 2$, write:
$$n - 1 = 2^s \cdot d \quad (d \text{ odd})$$

For a chosen base $a \in [2, n-2]$:
- Compute $x_0 = a^d \pmod n$. If $x_0 \equiv 1$ or $x_0 \equiv n-1 \pmod n$, $n$ passes.
- Otherwise compute $x_{r} = x_{r-1}^2 \pmod n$ for $r \in [1, s-1]$. If any $x_r \equiv n-1 \pmod n$, $n$ passes.
- If $x_r \equiv 1$ before $-1$ or the loop finishes without reaching $n-1$, $n$ is **definitely composite**.

### 2. Error Bound
Each independent round reduces the probability of a false prime declaration to $\le \frac{1}{4}$. For $k = 40$ rounds:
$$P(\text{error}) \le 4^{-40} = 2^{-80} \approx 8.27 \times 10^{-25}$$

---

## 📊 Experimental Results

| Parameter | Value |
| :--- | :--- |
| **Assigned bit length** | **512 bits** |
| **Generated prime candidate (Hex)** | `0xe0f76b265cf06d40ecfcaa588f829d58ceeba43c1861c9dda88027296a2899ee4ea8c38ea191d17dd72da8bb6f349f2184f4926f8e447bea5eb3b7158abd03f5` |
| **Actual bit length of candidate** | **512 bits** |
| **Number of candidates tested** | **651** |
| **Number of Miller-Rabin rounds** | **40 rounds** |
| **Theoretical error bound** | $\le 4^{-40} \approx 8.27 \times 10^{-25}$ |
| **Total execution time** | **0.1270 seconds** |
| **Average time across 5 runs** | **0.0783 seconds** |
| **Independent Verification** | **ALL PASSED (Bit length, 12 Bases, 50k Trial Div, SymPy)** |

---

## 👥 Contributors

- **Nishant** (2024UCP1773) — `prime_generator.py`, `verification.py`, module documentation & README
- **Lokesh Saini** (2024UCP1505) — Theory guide, `miller_rabin.py`, `main.py` orchestrator, experimental report
