# Assignment 9 — Evaluation of OS Random Number Generation Mechanisms
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) & Lokesh Saini (2024UCP1505)

---

## Table of Contents
1. [Executive Summary & Lab Objectives](#1-executive-summary--lab-objectives)
2. [Is This an Implementation Lab? (How & Where)](#2-is-this-an-implementation-lab-how--where)
3. [Foundational Concepts: TRNG vs PRNG vs CSPRNG](#3-foundational-concepts-trng-vs-prng-vs-csprng)
4. [OS Random Number Generation Mechanisms Under the Hood](#4-os-random-number-generation-mechanisms-under-the-hood)
   - [4.1 Linux Kernel CSPRNG (`/dev/urandom`, `/dev/random`, `getrandom`)](#41-linux-kernel-csprng-devurandom-devrandom-getrandom)
   - [4.2 Windows CSPRNG (`BCryptGenRandom` & Windows CNG)](#42-windows-csprng-bcryptgenrandom--windows-cng)
   - [4.3 OpenSSL `rand` Utility & DRBG Engine](#43-openssl-rand-utility--drbg-engine)
5. [Statistical Randomness vs. Cryptographic Security](#5-statistical-randomness-vs-cryptographic-security)
   - [5.1 The Core Fallacy: Statistical Tests ≠ Security](#51-the-core-fallacy-statistical-tests--security)
   - [5.2 Counterexamples That Pass Statistical Tests But Fail Cryptographically](#52-counterexamples-that-pass-statistical-tests-but-fail-cryptographically)
   - [5.3 Formal Cryptographic Security Requirements](#53-formal-cryptographic-security-requirements)
6. [Statistical Testing Suite for 1 MB Datasets](#6-statistical-testing-suite-for-1-mb-datasets)
   - [6.1 Monobit Test (Bit-Frequency Distribution)](#61-monobit-test-bit-frequency-distribution)
   - [6.2 Byte-Frequency Distribution & Chi-Square ($\chi^2$) Test](#62-byte-frequency-distribution--chi-square-chi2-test)
   - [6.3 Runs Test (Oscillation & Pattern Analysis)](#63-runs-test-oscillation--pattern-analysis)
   - [6.4 Serial Correlation (Autocorrelation Lag-1 & Lag-k)](#64-serial-correlation-autocorrelation-lag-1--lag-k)
   - [6.5 Shannon Entropy Calculation](#65-shannon-entropy-calculation)
   - [6.6 Monte Carlo Estimation of $\pi$](#66-monte-carlo-estimation-of-pi)
7. [Step-by-Step Implementation Roadmap](#7-step-by-step-implementation-roadmap)
   - [Folder Structure](#folder-structure)
   - [Data Collection Phase (1 MB per Source)](#data-collection-phase-1-mb-per-source)
   - [Analysis Script & Jupyter Notebook Phase](#analysis-script--jupyter-notebook-phase)
   - [Lab Report & Theory Synthesis](#lab-report--theory-synthesis)
8. [Commit Division Plan (Lokesh & Nishant)](#8-commit-division-plan-lokesh--nishant)

---

## 1. Executive Summary & Lab Objectives

In modern cryptography, **unpredictable randomness is the foundation of all security guarantees**. If an adversary can guess, bias, or predict random values, every layer built on top collapses instantly:
- **AES-CBC / AES-GCM**: Predictable IVs or nonces lead to plaintext recovery or forgery.
- **RSA / ECC Key Generation**: Biased prime generation or predictable ECDSA ephemeral values $k$ reveal private keys immediately (e.g., the infamous PlayStation 3 ECDSA flaw and Debian OpenSSL CVE-2008-0166).
- **Session Tokens / Nonces**: Predictable tokens permit replay attacks and session hijacking.

### The Assignment Mandate
Assignment 9 requires us to:
1. **Generate at least 1 MB (1,048,576 bytes) of random data** from three distinct cryptographic generators:
   - Linux `/dev/urandom`
   - OpenSSL `rand` utility
   - Windows CNG (`BCryptGenRandom`) or .NET Cryptographic API
   - *(Optional control group)*: A non-cryptographic PRNG (e.g., Python `random` / LCG) to demonstrate the contrast.
2. **Perform Empirical Statistical Analysis**:
   - Byte-frequency distributions
   - Bit distributions (Monobit)
   - Repeated patterns & Runs test
   - Serial correlations (Lag-1 and Lag-$k$)
   - Shannon entropy and Monte Carlo $\pi$ estimation
3. **Jupyter Notebook (`.ipynb`)**:
   - Provide visual plots, histograms, correlation curves, and tabular statistical interpretations.
4. **Deep Architectural Investigation**:
   - Investigate how Linux and Windows harvest physical entropy and manage internal CSPRNG pools.
5. **The Foundational Cryptographic Question**:
   - Compare mechanisms and explain rigorously **why passing statistical tests does not guarantee cryptographic security**.

---

## 2. Is This an Implementation Lab? (How & Where)

### The Short Answer: **YES!**
While Assignment 9 contains extensive theory and architectural comparison, it is **100% an implementation and experimentation laboratory**.

### Why It Requires Real Implementation
1. **Real Data Generation**: You cannot analyze fabricated numbers. You must execute real commands and write code to capture exactly $1,048,576$ raw bytes from each OS generator.
2. **Statistical Test Engine**: You need Python code to parse binary files, convert them to bit streams and byte arrays, calculate histograms, compute Chi-Square ($\chi^2$), compute auto-correlation matrices, calculate Shannon entropy, and simulate Monte Carlo integration.
3. **Jupyter Notebook (`.ipynb`)**: Tasks 3 and 5 explicitly request `(Notebook)`. The notebook will load the datasets, execute the statistical tests, render matplotlib histograms, and display comparative charts.
4. **Automated CLI Tool**: A command-line script that runs the entire test suite on any binary file and outputs an ASCII comparison table.

### Where It Belongs in the Repository
In our repository structure, this belongs in:
```
analysis/os_rng_evaluation/
```
(or `analysis/rng_evaluation/`, since `analysis/` is already established in our root structure).

---

## 3. Foundational Concepts: TRNG vs PRNG vs CSPRNG

| Feature | TRNG (True RNG) | PRNG (Pseudorandom RNG) | CSPRNG (Crypto-Secure PRNG) |
| :--- | :--- | :--- | :--- |
| **Origin of Entropy** | Physical hardware phenomena (thermal noise, quantum jitter, radioactive decay) | Mathematical algorithm starting from an initial seed | Mathematical cryptographic primitive (ChaCha20, AES-CTR) seeded by high-entropy physical events |
| **Speed / Throughput** | Very slow (kbit/s to low Mbit/s) | Extremely fast (GB/s) | Fast (hundreds of MB/s) |
| **Determinism** | Non-deterministic (unrepeatable) | Completely deterministic given seed | Computationally indistinguishable from random |
| **Next-Bit Unpredictability** | Absolute (physically unpredictable) | ❌ **FAILS** (given few outputs, future outputs can be computed) | ✅ **HOLDS** (computationally infeasible to predict next bit) |
| **State Compromise Recovery** | Not applicable | ❌ **FAILS** (state compromised $\implies$ all past & future broken) | ✅ **HOLDS** (continuously reseeds with fresh physical entropy) |
| **Typical Use Cases** | Seeding CSPRNGs, high-security hardware security modules (HSM) | Monte Carlo simulations, gaming, graphic rendering (`random.py`, `rand()`) | Key generation, IVs, nonces, salting, TLS/SSL sessions (`/dev/urandom`, `BCryptGenRandom`) |

---

## 4. OS Random Number Generation Mechanisms Under the Hood

### 4.1 Linux Kernel CSPRNG (`/dev/urandom`, `/dev/random`, `getrandom`)

#### 1. Entropy Harvesting
The Linux kernel continuously monitors non-deterministic hardware timings:
- **Interrupt timings (`add_interrupt_randomness`)**: Time difference between device interrupts (network packet arrivals, storage I/O).
- **Human interface devices**: Keystroke timings, mouse movements.
- **CPU jitter and hardware instructions**: Intel RDRAND/RDSEED, ARM random instructions.

#### 2. The Internal Generator (ChaCha20 Stream Cipher)
Historically (prior to Linux 4.8), Linux mixed entropy into an input pool using SHA-1.
In modern kernels (Linux 4.8+ and revamped in Linux 5.14/5.17+):
- Entropy is accumulated into a primary pool using **BLAKE2s**.
- Per-NUMA node / per-CPU CSPRNG instances are driven by the **ChaCha20 stream cipher**.
- When random bytes are requested, ChaCha20 generates keystream blocks.
- **Fast Reseeding & Backtracking Resistance**: Every request triggers key re-erasure (forward secrecy): immediately after producing output, the key is overwritten so past states cannot be reconstructed.

#### 3. `/dev/random` vs. `/dev/urandom` vs. `getrandom(2)`
- **The Historical Myth**: Old documentation warned that `/dev/urandom` was "insecure" when entropy ran low, and advised `/dev/random` instead.
- **The Modern Reality**: `/dev/random` blocked when the kernel's entropy counter reached zero. This caused severe Denial of Service (DoS) in web servers and cloud VMs.
- Cryptographers (including Daniel J. Bernstein and Ted Ts'o) demonstrated that once seeded with 256 bits of true entropy, a CSPRNG based on ChaCha20 can output $2^{64}$ bytes without any loss of cryptographic security.
- Modern kernels unified `/dev/random` and `/dev/urandom`: once the system has initialized at boot, **`/dev/urandom` never blocks**, and `/dev/random` only blocks during the early boot phase before 256 bits of entropy are collected.
- **`getrandom(2)`**: A direct Linux syscall that avoids filesystem path traversal and guarantees the pool is initialized without blocking unexpectedly.

---

### 4.2 Windows CSPRNG (`BCryptGenRandom` & Windows CNG)

#### 1. Architectural Evolution
- **Windows 2000 / XP**: `CryptoAPI` (`CryptGenRandom`) — proprietary design, opaque implementation.
- **Windows XP SP3 / Vista**: `RtlGenRandom` (`SystemFunction036` in `advapi32.dll`) — based on AES in Counter mode.
- **Windows 7 / 10 / 11 / Server**: **Windows CNG (Cryptography Next Generation)** via `BCryptGenRandom()` in `bcrypt.dll`.

#### 2. Entropy Collection Mechanism
Windows kernel collects system entropy into a central accumulator:
- High-resolution performance counters (`QueryPerformanceCounter`).
- Thread dispatch timings, DPC (Deferred Procedure Call) queues.
- ACPI power-management hardware timers.
- Trusted Platform Module (TPM) hardware entropy if present.
- CPU hardware instructions (`RDRAND` / `RDSEED`).

#### 3. Cryptographic Generator Architecture
Windows CNG implements **NIST SP 800-90A DRBG (Deterministic Random Bit Generator)**:
- Core primitive: **AES-256 in Counter (CTR) mode** or **HMAC-SHA512**.
- Operates in user-mode via RPC to the Local Security Authority Subsystem Service (LSASS) or directly in kernel space via `cng.sys`.
- **Prediction Resistance**: Reseeds periodically or upon system power transitions.

#### 4. .NET & Modern Windows Access
In .NET / C#, `System.Security.Cryptography.RandomNumberGenerator.GetBytes(buffer)` directly wraps `BCryptGenRandom`.
In Python on Windows, `os.urandom(n)` and `secrets.token_bytes(n)` invoke `BCryptGenRandom` under the hood.

---

### 4.3 OpenSSL `rand` Utility & DRBG Engine

#### 1. Command-Line Invocation
```bash
openssl rand -out openssl_1mb.bin 1048576
```
This requests exactly 1,048,576 bytes of cryptographic random data.

#### 2. Under the Hood in OpenSSL (Version 3.x)
- OpenSSL implements NIST SP 800-90A DRBG.
- By default, it employs **AES-256-CTR DRBG** (or HMAC-DRBG with SHA-256).
- **Seeding Chain**:
  - OpenSSL queries the OS kernel CSPRNG (`/dev/urandom` or `getrandom` on Linux, `BCryptGenRandom` on Windows).
  - It also mixes in hardware jitter via RDRAND/RDSEED when available.
  - Generates pseudorandom keystream in user-space with automatic internal reseeding after $2^{24}$ requests.

---

## 5. Statistical Randomness vs. Cryptographic Security

### 5.1 The Core Fallacy: Statistical Tests ≠ Security
The central conceptual trap in computer science and engineering is assuming:
$$\text{"It looks random, so it must be secure."} \quad \leftarrow \textbf{FATALLY FLAWED!}$$

**Statistical randomness is a property of the output distribution.** It only checks whether frequencies of 0s, 1s, byte pairs, and sequences match what a theoretical uniform distribution would produce.

**Cryptographic security is a property of computational unpredictability.** It asks whether an adversary who sees the first $k$ output bits can predict the $(k+1)$-th bit with probability significantly better than $\frac{1}{2}$.

> **A sequence can be 100% statistically random while being 100% predictable!**

---

### 5.2 Counterexamples That Pass Statistical Tests But Fail Cryptographically

#### Counterexample 1: The Digits of $\pi$
- If you compute the binary expansion of $\pi = 3.1415926535\dots$:
- Every byte $0 \dots 255$ appears with frequency $\approx 1/256$.
- Shannon entropy is $\approx 8.0000$ bits/byte.
- Autocorrelation is zero.
- It passes the NIST SP 800-22 test suite and Dieharder test suite.
- **Cryptographic Security**: **ZERO**. An attacker knows $\pi$. Any encryption key generated from $\pi$ can be cracked instantly by anyone who realizes the seed is $\pi$.

#### Counterexample 2: AES-CTR with a Known Key
- Let $K = \text{0x00010203...0f}$ (a fixed, known key).
- Generate random data as:
  $$\text{Block}_0 = E_K(0), \quad \text{Block}_1 = E_K(1), \quad \text{Block}_2 = E_K(2), \quad \dots$$
- Because AES is a cryptographically strong pseudorandom permutation, the output blocks possess perfect statistical properties:
  - Exact 50% 0s and 1s.
  - Uniform byte frequencies.
  - Zero serial correlation.
  - Maximum Shannon entropy ($8.0$ bits/byte).
- **Cryptographic Security**: **ZERO**. Anyone who knows $K$ can predict all past and all future outputs with 100% precision!

#### Counterexample 3: Mersenne Twister (`random` in Python / C++ `std::mt19937`)
- Mersenne Twister has a massive period of $2^{19937} - 1$ and passes almost all standard statistical PRNG test suites.
- **Cryptographic Security**: **ZERO**. The internal state consists of 624 32-bit integers. Observing just 624 consecutive outputs allows an attacker to invert the tempering matrix, recover the exact internal state, and predict **every single future and past output**.

---

### 5.3 Formal Cryptographic Security Requirements

A generator is a **Cryptographically Secure PRNG (CSPRNG)** if and only if it satisfies:

1. **Next-Bit Unpredictability (Yao's Test)**:
   For any polynomial-time algorithm $\mathcal{A}$, given $k$ bits $s_1, s_2, \dots, s_k$:
   $$P\left[\mathcal{A}(s_1, \dots, s_k) = s_{k+1}\right] \le \frac{1}{2} + \text{negl}(k)$$
2. **Backtracking Resistance (Forward Secrecy)**:
   If the internal state $S_t$ at time $t$ is exposed to the adversary, the adversary cannot compute any previous output $s_{t-1}, s_{t-2}, \dots$.
3. **Prediction Resistance (Backward Secrecy)**:
   If the internal state $S_t$ is exposed, subsequent injection of fresh entropy into the pool must restore unpredictability so future outputs $s_{t+m}$ become unpredictable again.

---

## 6. Statistical Testing Suite for 1 MB Datasets

For a dataset of $N = 1,048,576$ bytes ($8,388,608$ bits):

### 6.1 Monobit Test (Bit-Frequency Distribution)
- **Goal**: Verify that the number of zeros and ones are approximately equal.
- Let $S_n = \sum_{i=1}^{n} X_i$ where $X_i \in \{-1, +1\}$.
- For a true random bitstream, the test statistic:
  $$S_{\text{obs}} = \frac{|\sum X_i|}{\sqrt{n}}$$
- The $p$-value is:
  $$p = \text{erfc}\left(\frac{S_{\text{obs}}}{\sqrt{2}}\right)$$
- If $p \ge 0.01$, the sequence passes the Monobit test.

---

### 6.2 Byte-Frequency Distribution & Chi-Square ($\chi^2$) Test
- **Goal**: Check whether each byte value $0 \le v \le 255$ appears uniformly.
- **Expected Frequency**:
  $$E = \frac{1,048,576}{256} = 4,096 \text{ occurrences per byte}$$
- **Chi-Square Statistic**:
  $$\chi^2 = \sum_{i=0}^{255} \frac{(O_i - E)^2}{E}$$
- With degrees of freedom $df = 255$:
  - A good, random dataset yields $\chi^2 \approx 255 \pm \sqrt{2 \times 255} \approx [209, 301]$.
  - If $\chi^2 > 350$ or $\chi^2 < 170$, the distribution deviates from pure randomness.

---

### 6.3 Runs Test (Oscillation & Pattern Analysis)
- **Goal**: Evaluate the total number of continuous runs of identical bits (consecutive 1s or consecutive 0s).
- Too few runs indicate slow transitions (correlation); too many runs indicate rapid oscillation.
- The test statistic:
  $$Z = \frac{V_n - 2n\pi(1-\pi)}{2\sqrt{2n}\pi(1-\pi)}$$
  where $V_n$ is the total number of runs and $\pi$ is the proportion of ones.

---

### 6.4 Serial Correlation (Autocorrelation Lag-1 & Lag-$k$)
- **Goal**: Detect if byte $X_{t}$ has any linear dependence on byte $X_{t+k}$.
- Autocorrelation coefficient at lag $k$:
  $$r_k = \frac{\sum_{i=1}^{N-k} (X_i - \bar{X})(X_{i+k} - \bar{X})}{\sum_{i=1}^{N} (X_i - \bar{X})^2}$$
- For independent white noise, $r_k \approx 0 \pm \frac{1.96}{\sqrt{N}}$.
- For $N = 1,048,576$, the $95\%$ confidence threshold is $\pm \frac{1.96}{\sqrt{1,048,576}} = \pm 0.00191$. Any correlation strictly within $[-0.0019, +0.0019]$ indicates independence.

---

### 6.5 Shannon Entropy Calculation
- **Goal**: Measure the average information density per byte.
- Formula:
  $$H(X) = -\sum_{i=0}^{255} p(i) \log_2 p(i)$$
- **Theoretical Maximum**: For 256 equally probable outcomes ($p(i) = 1/256$):
  $$H_{\max} = -\sum_{i=0}^{255} \frac{1}{256} \log_2\left(\frac{1}{256}\right) = \log_2(256) = 8.000000 \text{ bits/byte}$$
- High-grade cryptographic random data consistently scores $H > 7.9997$ bits/byte.

---

### 6.6 Monte Carlo Estimation of $\pi$
- **Goal**: Treat consecutive pairs of random numbers $(x, y) \in [0, 1) \times [0, 1)$ as points in a 2D unit square.
- Count points inside the unit circle quarter: $x^2 + y^2 \le 1$.
- Ratio of points inside circle approaches $\frac{\pi}{4}$.
- Estimated $\pi \approx 4 \times \frac{\text{points inside}}{\text{total points}}$.
- For 524,288 point pairs from 1 MB, estimated $\pi \approx 3.14159 \pm 0.005$ with low percentage error.

---

## 7. Step-by-Step Implementation Roadmap

### Folder Structure
We will establish:
```
analysis/os_rng_evaluation/
├── README.md                           # Documentation, setup, instructions
├── data/
│   ├── dev_urandom_1mb.bin             # 1 MB generated via /dev/urandom
│   ├── openssl_1mb.bin                 # 1 MB generated via OpenSSL rand
│   ├── windows_cng_1mb.bin             # 1 MB generated via BCryptGenRandom
│   └── python_prng_1mb.bin             # 1 MB weak PRNG control group
├── notebooks/
│   └── rng_statistical_analysis.ipynb  # Interactive Jupyter Notebook (Tasks 3 & 5)
├── outputs/
│   ├── byte_distribution.png           # Frequency histograms
│   ├── autocorrelation_plot.png        # Correlation vs Lag curves
│   └── summary_table.txt               # Complete numerical comparison table
├── reports/
│   └── OS_RNG_Evaluation_Report.md     # In-depth Lab Report
└── src/
    ├── generate_data.py                # Multi-platform 1 MB generation script
    ├── statistical_tests.py            # Complete testing suite engine
    └── main.py                         # CLI orchestrator & report generator
```

### Data Collection Phase (1 MB per Source)
1. **Windows CNG**:
   - In Python: `os.urandom(1048576)` or `secrets.token_bytes(1048576)` calls Windows `BCryptGenRandom` directly.
2. **OpenSSL**:
   - Run `openssl rand -out data/openssl_1mb.bin 1048576`.
3. **Linux `/dev/urandom`**:
   - In WSL/Git Bash/Linux: `head -c 1048576 /dev/urandom > dev_urandom_1mb.bin`.
   - In Python cross-platform generator: reads directly from `/dev/urandom` if on POSIX, or extracts via WSL / subprocess.
4. **Control Group (Weak PRNG)**:
   - Python `random.randbytes(1048576)` or an LCG to highlight the contrast in predictability despite good statistical performance.

---

## 8. Commit Division Plan (Lokesh & Nishant)

To keep our commit balance and modular pair-programming workflow:

### **Lokesh Saini (3 Commits)**
1. **Commit 1**: `docs(lab9): add OS RNG Evaluation Theory Guide and initialize folder structure`
   - Theory guide (`resources/Assignment_9_Theory_Guide.md`), folder layout, `.gitkeep` files.
2. **Commit 2**: `feat(lab9): add statistical_tests.py - Monobit, Chi-Square, Entropy, Runs, and Autocorrelation suite`
   - Core mathematical and statistical testing engine.
3. **Commit 3**: `feat(lab9): add main.py orchestrator, generate summary outputs and OS_RNG_Evaluation_Report.md`
   - Execution pipeline, benchmark results, comprehensive lab report.

### **Nishant (3 Commits)**
1. **Commit 1**: `feat(lab9): add generate_data.py - 1MB random data generation for Windows CNG, OpenSSL, and Linux urandom`
   - Automated data generation script capturing 1 MB binary files.
2. **Commit 2**: `feat(lab9): add rng_statistical_analysis.ipynb interactive Jupyter Notebook with visual plots`
   - Jupyter notebook with histograms, correlation plots, and statistical interpretations.
3. **Commit 3**: `docs(lab9): add os_rng_evaluation README and update global README with Lab 9 progress`
   - Module README, root README update to Labs 1–9, progress table update.

---

*CryptoLabX Group 01 — 22CPP307 Cryptography Laboratory | MNIT Jaipur*
