# Lab 9 — Evaluation of OS Random-Number Generation Mechanisms
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)

---

## 1. Executive Summary & Objectives

Modern cryptographic systems depend fundamentally on **unpredictable randomness**. Encryption keys, initialization vectors (IVs), cryptographic salts, nonces, and Diffie-Hellman ephemeral secrets all require random numbers whose future and past values cannot be determined by an adversary.

### Laboratory Objectives
1. **Empirical Generation**: Generate and capture at least 1 MB ($1,048,576$ bytes) of random data from four independent generation mechanisms:
   - Linux `/dev/urandom` (ChaCha20 kernel stream)
   - OpenSSL `rand` CLI (NIST SP 800-90A DRBG)
   - Windows CNG (`BCryptGenRandom` via Cryptography Next Generation)
   - Python PRNG (Control baseline: non-cryptographic Mersenne Twister MT19937)
2. **Statistical Testing Suite**: Apply standard tests compliant with NIST SP 800-22:
   - Monobit frequency test (0 vs 1 distribution)
   - Byte-frequency distribution and $\chi^2$ goodness-of-fit test (256 discrete bins)
   - Runs test (bit transition frequencies)
   - Serial autocorrelation (lags $1 \le k \le 20$)
   - Shannon entropy calculation ($H \to 8.000000$ bits/byte)
   - Monte Carlo spatial estimation of $\pi$
3. **OS Architectural Investigation**: Examine how the Linux and Windows operating systems harvest physical entropy, maintain entropy pools, and generate secure pseudorandom streams.
4. **The Core Cryptographic Problem**: Explain rigorously why passing statistical tests is a **necessary condition but NEVER a sufficient condition** for cryptographic security.

---

## 2. Foundational Concepts: TRNG vs. PRNG vs. CSPRNG

| Characteristic | True Random Number Generator (TRNG) | Pseudorandom Number Generator (PRNG) | Cryptographically Secure PRNG (CSPRNG) |
| :--- | :--- | :--- | :--- |
| **Entropy Source** | Physical hardware events (thermal noise, clock drift, quantum shot noise) | Completely deterministic algorithm seeded by a small integer or timestamp | High-entropy physical events continuously collected by the OS kernel |
| **Throughput** | Low (kbit/s to a few Mbit/s) | Extremely high (> 1 GB/s) | High (hundreds of MB/s) |
| **Determinism** | Non-deterministic | Completely deterministic given seed | Computationally indistinguishable from uniform white noise |
| **Next-Bit Unpredictability** | Absolute (physically unpredictable) | ❌ **Fails completely** (observing outputs reveals state) | ✅ **Holds** (computationally infeasible under polynomial time) |
| **Forward / Backward Secrecy** | Natural | ❌ **None** | ✅ **Guaranteed via fast key erasure and reseeding** |
| **Applications** | Seeding CSPRNGs, HSMs | Monte Carlo simulations, gaming (`random`, `rand()`) | Key generation, TLS/SSL sessions, IVs, nonces, digital signatures |

---

## 3. OS Random Number Generation Mechanisms Under the Hood (Task 4)

### 3.1 Linux Kernel CSPRNG Architecture (`/dev/urandom`, `/dev/random`, `getrandom`)

The Linux kernel CSPRNG architecture underwent significant overhauls in kernels 4.8, 5.14, and 5.17+ (spearheaded by Jason A. Donenfeld and Ted Ts'o), moving away from legacy SHA-1 mixing:

```
[ Hardware Events ] ---> [ Fast Entropy Mixer ] ---> [ Primary Pool ] ---> [ Per-CPU ChaCha20 DRBG ] ---> /dev/urandom
  - Interrupt Timings       (BLAKE2s hash)             (Shared state)       - Fast Key Erasure            getrandom(2)
  - Storage I/O jitter                                                      - Forward Secrecy
  - Keyboard / Mouse
  - CPU Jitter (RDRAND)
```

1. **Entropy Harvesting**:
   - `add_interrupt_randomness()`: Measures sub-microsecond timing differences between hardware interrupts (network packet arrivals, peripheral events).
   - `add_disk_randomness()`: Captures rotational and SSD request completion jitter.
   - `add_input_randomness()`: Records human inter-keystroke intervals and cursor movements.
   - CPU instructions: Incorporates hardware instructions (`RDRAND`, `RDSEED`) when available.
2. **Entropy Mixing**:
   - Physical entropy is continuously folded into a primary input pool using the **BLAKE2s** cryptographic hash function.
3. **The ChaCha20 Output Engine**:
   - Rather than extracting directly from a central pool, modern Linux maintains per-CPU or per-NUMA **ChaCha20 stream cipher** generators.
   - **Fast Key Erasure (Forward Secrecy)**: Immediately upon generating output blocks for a user process, the ChaCha20 key is updated and overwritten with new pseudorandom bytes. If the kernel memory is dumped at time $t$, earlier outputs cannot be reconstructed.
4. **The Myth of `/dev/random` vs. `/dev/urandom`**:
   - Historically, documentation advised against `/dev/urandom`, claiming it was "insecure" when entropy ran low. This was based on the false assumption that entropy is a physical fluid that gets "used up".
   - In modern cryptography, once a CSPRNG is seeded with 256 bits of true entropy, an adversary cannot distinguish its output from true randomness even after observing $2^{64}$ bytes without breaking the underlying cipher (ChaCha20).
   - In modern Linux kernels, `/dev/urandom` never blocks. `/dev/random` only blocks during the early boot phase until the initial 256 bits of entropy have been accumulated, after which both devices behave identically.
   - The **`getrandom(2)`** system call provides a secure, file-descriptor-free mechanism that blocks only if the system is queried before the initial boot seed is ready.

---

### 3.2 Windows Cryptography Next Generation (CNG / `BCryptGenRandom`)

Windows random number generation evolved through three primary generations:
- **Windows 2000 / XP**: Legacy `CryptoAPI` (`CryptGenRandom`).
- **Windows XP SP3 / Vista**: `RtlGenRandom` (`SystemFunction036` in `advapi32.dll`), introducing AES in counter mode.
- **Windows 7 / 10 / 11 / Server**: **Windows CNG (Cryptography Next Generation)** exposed via `BCryptGenRandom` in `bcrypt.dll`.

1. **Entropy Harvesting Sources**:
   - `QueryPerformanceCounter` high-resolution timer values.
   - Thread dispatch and Deferred Procedure Call (DPC) execution timestamps.
   - ACPI power-management hardware registers.
   - Hardware Trusted Platform Module (TPM) entropy.
   - Intel/AMD hardware instructions (`RDRAND` / `RDSEED`).
2. **Underlying Cryptographic Primitive**:
   - Windows CNG strictly adheres to **NIST SP 800-90A DRBG**.
   - Default algorithm: **AES-256 in Counter (CTR) mode** (CTR-DRBG).
   - Automatically reseeds based on byte counts, thread events, and sleep/wake power state transitions.
3. **Language Bindings**:
   - In Python on Windows, `os.urandom(n)` and `secrets.token_bytes(n)` call `BCryptGenRandom()` directly.
   - In .NET, `System.Security.Cryptography.RandomNumberGenerator` routes directly to CNG.

---

### 3.3 OpenSSL `rand` Utility

- Invocation: `openssl rand -out openssl_1mb.bin 1048576`
- **Internal Design**: OpenSSL 3.x implements a user-space NIST SP 800-90A compliant DRBG (typically AES-256-CTR DRBG).
- **Seeding Chain**:
  - Upon initialization, OpenSSL queries the underlying operating system's CSPRNG (`BCryptGenRandom` on Windows, `getrandom`/`/dev/urandom` on Linux).
  - Mixes in CPU jitter when available.
  - Generates keystream blocks in user-space buffers with automated periodic reseeding after $2^{24}$ requests.

---

## 4. Empirical Statistical Evaluation Results

All four 1 MB ($1,048,576$ bytes) datasets were evaluated using our custom statistical test suite ([statistical_tests.py](file:///c:/Users/LENOVO/Desktop/CryptoLabX_Group01/analysis/os_rng_evaluation/src/statistical_tests.py)).

### 4.1 Statistical Evaluation Results Table

| Generator / Engine | 1s Proportion | Chi-Square ($\chi^2$) | $\chi^2$ $p$-value | Shannon Entropy | Autocorrelation ($r_1$) | Monte Carlo $\pi$ | Overall Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Linux `/dev/urandom`** | 0.500069 | 222.06 | 0.9328 | 7.999847 | -0.000368 | 3.13803 | **PASS** |
| **OpenSSL `rand`** | 0.499680 | 253.43 | 0.5161 | 7.999826 | +0.000159 | 3.13837 | **PASS** |
| **Windows CNG** | 0.500038 | 266.36 | 0.2997 | 7.999817 | -0.000360 | 3.14005 | **PASS** |
| **Python PRNG (MT19937)**| 0.500137 | 267.79 | 0.2787 | 7.999816 | -0.001404 | 3.14320 | **PASS (Statistical)** |

---

### 4.2 Detailed Metric Interpretations

1. **Monobit Frequency Test**:
   - For a sequence of $8,388,608$ bits ($1,048,576$ bytes $\times 8$), all four generators exhibited a proportion of ones extremely close to the theoretical mean of $0.500000$ (deviations $\le 0.03\%$).
   - All Monobit $p$-values exceeded the NIST significance threshold of $\alpha = 0.01$.
2. **Byte-Frequency Distribution & $\chi^2$ Goodness-of-Fit**:
   - With 256 discrete bins and $N = 1,048,576$, the expected frequency per byte is $E = 4,096$.
   - For degrees of freedom $df = 255$, acceptable $\chi^2$ values for $\alpha = 0.01$ fall within $[198.5, 319.4]$.
   - Observed values: Linux $\chi^2 = 222.06$ ($p = 0.9328$), OpenSSL $\chi^2 = 253.43$ ($p = 0.5161$), Windows $\chi^2 = 266.36$ ($p = 0.2997$). All fall cleanly inside the expected distribution.
3. **Shannon Entropy**:
   - Maximum theoretical entropy for 256 byte outcomes is $\log_2(256) = 8.000000$ bits/byte.
   - All four datasets achieved entropy values exceeding $7.9998$ bits/byte, demonstrating near-perfect information density and lack of compression redundancy.
4. **Serial Autocorrelation**:
   - Evaluated across lags $1 \le k \le 20$.
   - For $N = 1,048,576$, the 95% confidence interval is $\pm \frac{1.96}{\sqrt{N}} = \pm 0.001914$, and the 99% confidence interval is $\pm \frac{2.576}{\sqrt{N}} = \pm 0.002516$.
   - All correlation coefficients hovered tightly around zero ($|r_k| < 0.0015$), proving the absence of linear dependence between adjacent bytes.
5. **Monte Carlo Estimation of $\pi$**:
   - 262,144 pairs of coordinates $(x, y) \in [0, 1)^2$ generated estimates of $\pi$ within $0.05\% - 0.11\%$ of the true mathematical constant ($3.14159$).

---

## 5. Critical Analysis: Why Statistical Randomness ≠ Cryptographic Security (Task 5)

The central conceptual takeaway of this laboratory is:

$$\textbf{Passing statistical tests is a NECESSARY condition, but NEVER a SUFFICIENT condition for cryptographic security.}$$

### 5.1 The Python PRNG Paradox: Empirical Evidence
Our empirical results provide a stark demonstration of this truth:
- **Python's `random` module (Mersenne Twister MT19937) passed EVERY single test!**
  - Bit balance: $0.500137$ ($p = 0.4285$)
  - Chi-Square: $267.79$ ($p = 0.2787$)
  - Shannon Entropy: $7.999816$ bits/byte
  - Autocorrelation: well within confidence boundaries
  - Monte Carlo $\pi$: $3.14320$

If an engineer evaluated Python's `random` module using statistical tools alone, they would conclude it is indistinguishable from Windows CNG or Linux `/dev/urandom`.

**Yet, Mersenne Twister has ZERO cryptographic security:**
- The internal state of MT19937 consists of an array of 624 32-bit integers ($19,937$ bits) and an index.
- All operations (matrix rotations, bit shifts, tempering) are **entirely linear** over GF(2).
- By observing just **624 consecutive 32-bit outputs** (or 2,496 bytes), an attacker can invert the tempering equations, reconstruct the exact internal state, and **predict every past and future output with 100% precision**.
- If MT19937 is used to generate private keys or TLS session tokens, an attacker can hijack sessions and forge signatures trivially.

---

### 5.2 Classic Mathematical Counterexamples

#### 1. The Binary Expansion of $\pi$
- Consider a stream of bytes formed by the binary expansion of $\pi = 3.1415926535\dots$.
- Because $\pi$ is believed to be a normal number, its digits exhibit maximal Shannon entropy ($8.000000$), perfect byte uniformity, and zero autocorrelation.
- **Cryptographic Security**: **Zero**. $\pi$ is completely deterministic, publicly known, and contains zero entropy. Any cryptographic key derived from $\pi$ is immediately breakable.

#### 2. AES-CTR with a Known Key
- Let $K = \text{0x0102030405060708090a0b0c0d0e0f10}$ (a fixed, constant key).
- Generate random data as:
  $$S = \text{AES}_K(0) \parallel \text{AES}_K(1) \parallel \text{AES}_K(2) \parallel \dots$$
- Because AES is a cryptographically strong pseudorandom permutation, the output blocks possess ideal statistical randomness (passes NIST SP 800-22 completely).
- **Cryptographic Security**: **Zero**. Anyone who knows the key $K$ can predict every single future byte.

---

### 5.3 Formal Cryptographic Properties of a True CSPRNG

A generator is only cryptographically secure if it provides computational guarantees that statistical tests cannot evaluate:

1. **Next-Bit Unpredictability (Yao's Test)**:
   For any probabilistic polynomial-time (PPT) adversary $\mathcal{A}$, given any prefix $s_1, s_2, \dots, s_k$:
   $$P\left[\mathcal{A}(s_1, \dots, s_k) = s_{k+1}\right] \le \frac{1}{2} + \text{negl}(k)$$
2. **Forward Secrecy (Backtracking Resistance)**:
   If an adversary compromises the generator's internal state at time $t$, they cannot compute any previous outputs ($s_{t-1}, s_{t-2}, \dots$). (Implemented via ChaCha20 fast key erasure in Linux).
3. **Backward Secrecy (Prediction Resistance)**:
   If the internal state is compromised at time $t$, subsequent injection of fresh physical entropy into the pool ensures that future outputs ($s_{t+m}$) become unpredictable again.

Statistical tests only examine the **output distribution**. They have no knowledge of the **state transition functions** or **computational complexity**.

---

## 6. Security Best Practices & Recommendations

1. **Never use non-cryptographic PRNGs for security**: Modules like Python's `random`, C `rand()`, and Java `java.util.Random` must never be used for key generation, salts, IVs, or tokens.
2. **Use OS-level primitives**:
   - Python: Use `secrets` or `os.urandom()`.
   - C / C++: Use `getrandom()` on Linux or `BCryptGenRandom()` on Windows.
   - Web / JS: Use `crypto.getRandomValues()`.
3. **Avoid User-Space Entropy Buffering**: Do not create custom PRNG wrappers or reuse seeds in application memory; rely directly on the OS kernel, which provides automated reseeding and forward secrecy.

---

## 7. Conclusion

This laboratory successfully generated, analyzed, and evaluated 1 MB datasets from Linux `/dev/urandom`, OpenSSL `rand`, Windows CNG, and Python PRNG. While all four generators displayed near-ideal statistical properties (Shannon entropy $> 7.9998$, uniform byte distributions, zero autocorrelation), our architectural investigation demonstrated that statistical randomness alone does not guarantee cryptographic security. True cryptographic security requires mathematical unpredictability, forward secrecy, and state-compromise recovery — properties provided exclusively by OS-level CSPRNGs.
