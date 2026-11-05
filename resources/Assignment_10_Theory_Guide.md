# Assignment 10 — MT19937 Stream Cipher & Predictable Token Attack
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) & Lokesh Saini (2024UCP1505)

---

## Table of Contents
1. [Executive Summary & Lab Objectives](#1-executive-summary--lab-objectives)
2. [MT19937 (Mersenne Twister) Architecture Under the Hood](#2-mt19937-mersenne-twister-architecture-under-the-hood)
   - [2.1 Historical Context & Mathematical Formulation](#21-historical-context--mathematical-formulation)
   - [2.2 State Space and Recurrence Relation](#22-state-space-and-recurrence-relation)
   - [2.3 The Tempering Transform](#23-the-tempering-transform)
   - [2.4 Why MT19937 Is NOT Cryptographically Secure](#24-why-mt19937-is-not-cryptographically-secure)
3. [Part A: MT19937 Toy Stream Cipher](#3-part-a-mt19937-toy-stream-cipher)
   - [3.1 Stream Cipher Design & Keystream Generation](#31-stream-cipher-design--keystream-generation)
   - [3.2 Encryption / Decryption Symmetry](#32-encryption--decryption-symmetry)
   - [3.3 Known-Plaintext Attack (KPA) Formulation](#33-known-plaintext-attack-kpa-formulation)
   - [3.4 The 16-bit Seed Search Space ($2^{16} = 65,536$)](#34-the-16-bit-seed-search-space-216--65536)
   - [3.5 Sliding-Window Matching Algorithm for Unknown Offset](#35-sliding-window-matching-algorithm-for-unknown-offset)
4. [Part B: Predictable Password Reset Tokens](#4-part-b-predictable-password-reset-tokens)
   - [4.1 The Real-World Vulnerability: Timestamp-Seeded PRNG](#41-the-real-world-vulnerability-timestamp-seeded-prng)
   - [4.2 Attack Threat Model & Window Formulation ($T \pm 300\text{s}$)](#42-attack-threat-model--window-formulation-t-pm-300texts)
   - [4.3 Exhaustive Candidate Verification & Time Complexity](#43-exhaustive-candidate-verification--time-complexity)
   - [4.4 Impact on Web Authentication & Account Takeover (ATO)](#44-impact-on-web-authentication--account-takeover-ato)
5. [Mathematical & Complexity Foundations](#5-mathematical--complexity-foundations)
   - [5.1 Entropy of Keystream and Seed](#51-entropy-of-keystream-and-seed)
   - [5.2 Brute-Force Feasibility Comparison Table](#52-brute-force-feasibility-comparison-table)
   - [5.3 False Positive Probability Analysis](#53-false-positive-probability-analysis)
6. [Secure Alternatives & Cryptographic Defenses](#6-secure-alternatives--cryptographic-defenses)
   - [6.1 Cryptographically Secure PRNGs (CSPRNG)](#61-cryptographically-secure-prngs-csprng)
   - [6.2 Production Token Generation Standards](#62-production-token-generation-standards)
7. [Step-by-Step Implementation Roadmap](#7-step-by-step-implementation-roadmap)
   - [Target Folder Structure](#target-folder-structure)
   - [Modular Source File Breakdown](#modular-source-file-breakdown)
   - [Jupyter Notebook Blueprint](#jupyter-notebook-blueprint)
8. [Non-Interleaved Work Distribution Plan](#8-non-interleaved-work-distribution-plan)
   - [Phase 1: Nishant's Complete Block (Commits 1 to 3)](#phase-1-nishants-complete-block-commits-1-to-3)
   - [Phase 2: Lokesh's Complete Block (Commits 4 to 6)](#phase-2-lokeshs-complete-block-commits-4-to-6)

---

## 1. Executive Summary & Lab Objectives

In Assignment 9, we demonstrated that non-cryptographic PRNGs like **Mersenne Twister (MT19937)** can pass rigorous statistical randomness batteries (uniformity, high Shannon entropy, zero serial correlation) while remaining **fundamentally insecure** against cryptographic adversaries.

**Assignment 10 turns that theory into active exploitation.** We demonstrate two practical cryptanalytic attacks against systems that misuse MT19937:

1. **Part A — Breaking an MT19937 Stream Cipher via Known-Plaintext Seed Recovery**:
   - Construct a symmetric stream cipher that encrypts plaintext by XORing individual bytes with 8-bit keystream values extracted from an MT19937 PRNG instance.
   - Encrypt a payload consisting of a random prefix ($5 \text{ to } 20$ printable characters) followed by $14$ consecutive `'A'` characters using a restricted $16$-bit seed ($0 \le S \le 65,535$).
   - Formulate and execute a brute-force attack across all $65,536$ candidate seeds to recover the secret seed and decrypt the full ciphertext, even though the exact offset of the $14$ `'A'`s is initially unknown to the attacker.

2. **Part B — Account Takeover via Predictable Password Reset Tokens**:
   - Simulate a real-world web application that generates $16$-byte hex-encoded security tokens by seeding MT19937 with the server's current integer Unix timestamp $T = \lfloor \text{time}() \rfloor$.
   - Mount a remote token prediction attack assuming an attacker knows the generation occurred within a window of $[T - 300, T + 300]$ seconds ($601$ candidate seeds).
   - Test each candidate seed, successfully identify the identical token, recover the exact server issuance timestamp, and regenerate the valid token.

3. **Notebook & Analytical Synthesis**:
   - Provide mathematical proofs, state transition mechanics, pseudocode, search space analyses, and real-world vulnerability post-mortems.

---

## 2. MT19937 (Mersenne Twister) Architecture Under the Hood

### 2.1 Historical Context & Mathematical Formulation
Developed in 1997 by Makoto Matsumoto and Takuji Nishimura, the **Mersenne Twister MT19937** is the default pseudorandom number generator in Python (`random`), Ruby, PHP (`mt_rand`), MATLAB, and C++ (`std::mt19937`).

Key parameters of MT19937-32:
- **Word size ($w$)**: $32$ bits
- **Degree of recurrence ($n$)**: $624$ words
- **Middle word offset ($m$)**: $397$ words
- **Separation point ($r$)**: $31$ bits
- **Period**: The Mersenne prime $2^{19937} - 1 \approx 4.3 \times 10^{6001}$

### 2.2 State Space and Recurrence Relation
MT19937 maintains an internal state array of $n = 624$ words of $32$ bits each:
$$\mathbf{X} = [x_0, x_1, x_2, \dots, x_{623}]$$

The recurrence relation computes the next state word $x_{k+n}$ from previous words using bitwise operations:
$$y = (x_k \ \& \ \text{upper\_mask}) \mid (x_{k+1} \ \& \ \text{lower\_mask})$$
$$x_{k+n} = x_{k+m} \oplus (y \gg 1) \oplus \begin{cases} \mathbf{0} & \text{if } \text{LSB}(y) = 0 \\ \mathbf{a} & \text{if } \text{LSB}(y) = 1 \end{cases}$$

where:
- $\text{upper\_mask} = \text{0x80000000}$ ($31$ most significant bits)
- $\text{lower\_mask} = \text{0x00000001}$ ($1$ least significant bit)
- Twist matrix vector $\mathbf{a} = \text{0x9908B0DF}$

```
       +-----------------------------------------------------+
State: | x[0] | x[1] | ... | x[k] | x[k+1] | ... | x[k+m] | ... | x[623] |
       +-----------------------------------------------------+
                  \       /                  |
               upper(x[k]) | lower(x[k+1])   |
                      \   /                  |
                        y                    |
                     Twist (y >> 1 ^ a)      |
                            \               /
                             \             /
                              XOR --------+
                                   |
                                x[k+n]  (New State Word)
```

### 2.3 The Tempering Transform
Before outputting a $32$-bit number $z_k$ from state word $x_k$, MT19937 applies an invertible linear transformation called **tempering** to improve $k$-distribution uniformity:

$$y_1 = x_k \oplus (x_k \gg u)$$
$$y_2 = y_1 \oplus ((y_1 \ll s) \ \& \ \mathbf{b})$$
$$y_3 = y_2 \oplus ((y_2 \ll t) \ \& \ \mathbf{c})$$
$$z_k = y_3 \oplus (y_3 \gg l)$$

Standard constants:
- $u = 11$
- $s = 7, \quad \mathbf{b} = \text{0x9D2C5680}$
- $t = 15, \quad \mathbf{c} = \text{0EFC60000}$
- $l = 18$

### 2.4 Why MT19937 Is NOT Cryptographically Secure
Although MT19937 has an astronomical period and excellent equi-distribution up to dimension $623$, it is completely unsuitable for cryptographic use due to three critical architectural flaws:

1. **Strict Linearity over $\mathbb{F}_2$**:
   All state updates and tempering transformations rely solely on bit shifts, bitwise AND masks, and bitwise XOR additions. There are **zero non-linear S-boxes, modular multiplications, or one-way functions**.

2. **Reversible Tempering**:
   Every tempering step is bi-directional. Given an observed $32$-bit output $z_k$, an attacker can **untemper** $z_k$ through inverse bitwise operations to recover the raw internal state word $x_k$ with $100\%$ certainty:
   - For right shifts: $y = z \oplus (z \gg u)$ is inverted bit-by-bit from MSB to LSB.
   - For left shifts: $y = z \oplus ((z \ll s) \ \& \ \mathbf{b})$ is inverted bit-by-bit from LSB to MSB.

3. **Complete State Reconstruction from $624$ Outputs**:
   Observing $624$ consecutive $32$-bit values ($19,968$ bits $\approx 2.5\text{ KB}$) allows an attacker to recover all $624$ state words. From that point onwards, **every future and past output can be predicted with zero error**.

4. **Zero Forward and Backward Secrecy**:
   MT19937 does not erase old states upon output generation, nor does it incorporate fresh environmental entropy dynamically.

---

## 3. Part A: MT19937 Toy Stream Cipher

### 3.1 Stream Cipher Design & Keystream Generation
In a stream cipher, plaintext bits or bytes are combined via bitwise XOR ($\oplus$) with an unpredictable keystream:
$$C_i = P_i \oplus K_i$$

For our MT19937 toy stream cipher:
- An instance of MT19937 is initialized with seed $S$.
- For each byte $i \in \{0, 1, \dots, L-1\}$, the generator produces a pseudorandom $8$-bit keystream byte:
  $$K_i = \text{Extract8Bit}(\text{PRNG}(S))$$
- In Python, using `random.Random(S).getrandbits(8)` or `random.Random(S).randint(0, 255)` guarantees an identical $8$-bit byte extraction sequence.

### 3.2 Encryption / Decryption Symmetry
Because bitwise XOR is an involution ($A \oplus B \oplus B = A$):
$$\text{Decryption: } P_i = C_i \oplus K_i = (P_i \oplus K_i) \oplus K_i = P_i$$

The exact same routine performs both encryption and decryption:
```python
def mt19937_stream_cipher(data: bytes, seed: int) -> bytes:
    rng = random.Random(seed)
    return bytes([b ^ rng.getrandbits(8) for b in data])
```

### 3.3 Known-Plaintext Attack (KPA) Formulation
Suppose an attacker intercepts ciphertext $\mathbf{C}$ of length $L$.
The attacker does not know the full plaintext $\mathbf{P}$, but possesses a **known-plaintext fragment** $\mathbf{M}_{\text{known}}$:
$$\mathbf{M}_{\text{known}} = \text{"AAAAAAAAAAAAAA"} \quad (\text{14 consecutive 'A's})$$
where the byte value is $\text{ord}('A') = 65 = \text{0x41}$.

Because the random prefix length is between $5$ and $20$ characters, the offset $j$ where $\mathbf{M}_{\text{known}}$ starts is unknown to the attacker:
$$j \in [5, 20]$$

```
Plaintext P:  [ r_0 | r_1 | ... | r_{k-1} ] [ 'A' | 'A' | ... | 'A' ]
              <--- 5 to 20 chars --->       <--- 14 chars ('A') --->
Ciphertext C: [ c_0 | c_1 | ... | c_{k-1} ] [ c_k | c_{k+1} | ... | c_{k+13} ]
```

### 3.4 The 16-bit Seed Search Space ($2^{16} = 65,536$)
When the sender restricts the seed to a $16$-bit integer:
$$S \in [0, 2^{16} - 1] = [0, 65535]$$

The total search space $|\mathcal{S}| = 65,536$ is **trivially small**:
- On modern consumer hardware (Python executing on an Intel/AMD CPU), testing $65,536$ seeds takes under **$1.5$ seconds**.
- No specialized cryptographic clusters, GPUs, or cloud resources are needed.

### 3.5 Sliding-Window Matching Algorithm for Unknown Offset
Because the prefix length is variable ($5 \le \text{prefix\_len} \le 20$), the attacker mounts an exhaustive key search:

```
Algorithm 1: Seed Recovery via Known-Plaintext Sliding Window
Input : Ciphertext C, Known Substring M = "AAAAAAAAAAAAAA"
Output: Recovered Seed S*, Decrypted Plaintext P*

1: for candidate_seed = 0 to 65535 do:
2:     rng = Random(candidate_seed)
3:     keystream = [rng.getrandbits(8) for _ in range(len(C))]
4:     candidate_plaintext = C XOR keystream
5:     if M is a contiguous substring of candidate_plaintext then:
6:         return (candidate_seed, candidate_plaintext)
7: return NOT_FOUND
```

---

## 4. Part B: Predictable Password Reset Tokens

### 4.1 The Real-World Vulnerability: Timestamp-Seeded PRNG
Many real-world web applications (historically found in PHP, early Java frameworks, and custom web backends) generate security-sensitive tokens (such as password reset links, CSRF tokens, session IDs, and email verification hashes) using standard library PRNGs seeded by the system clock:

```python
# Vulnerable production token generation
timestamp = int(time.time())  # e.g., 1793864120
rng = random.Random(timestamp)
token = bytes([rng.getrandbits(8) for _ in range(16)]).hex()
```

### 4.2 Attack Threat Model & Window Formulation ($T \pm 300\text{s}$)
1. **Target Action**: The attacker triggers a "Forgot Password" request for a target victim's account (e.g., `admin@target.com`) at approximately time $T_{\text{trigger}}$.
2. **Clock Synchronization**: The attacker observes their local system clock or the HTTP `Date` response header from the target server, establishing the base timestamp $T \approx T_{\text{trigger}}$.
3. **Window Boundary**: Even accounting for network latency, server clock drift, and queue delays, the actual token generation occurred within:
   $$\mathcal{T}_{\text{window}} = [T - 300, T + 300]$$
   The size of this candidate seed space is:
   $$|\mathcal{T}_{\text{window}}| = 300 - (-300) + 1 = 601 \text{ candidate seeds}$$

```
                Search Window: [ T - 300s, T + 300s ]
                    Total Candidates = 601 seconds
       -----------------------|-----------------------
       T - 300               T_target               T + 300
    (5 min before)       (Observed Event)       (5 min after)
```

### 4.3 Exhaustive Candidate Verification & Time Complexity
For each timestamp $t \in \mathcal{T}_{\text{window}}$:
1. Seed an MT19937 generator with $t$: `rng = random.Random(t)`.
2. Generate $16$ bytes: `candidate_token = bytes([rng.getrandbits(8) for _ in range(16)]).hex()`.
3. Compare `candidate_token == target_token`.
4. If identical, the seed $t^* = t$ is recovered.

**Execution Complexity**:
- $601$ candidate generations in Python takes **less than $0.005$ seconds ($5 \text{ ms}$)**.
- Attacker complexity is $O(W)$, where $W$ is the search window size in seconds.

### 4.4 Impact on Web Authentication & Account Takeover (ATO)
Once the token is predicted:
- The attacker constructs the reset URL: `https://vulnerable.com/reset-password?token=<predicted_token>`.
- The attacker changes the victim's password and gains full access to the account without ever intercepting the victim's email or cracking their original password.

---

## 5. Mathematical & Complexity Foundations

### 5.1 Entropy of Keystream and Seed
- The true entropy of a $16$-bit seed is at most:
  $$H(S) = \log_2(65536) = 16 \text{ bits}$$
- An attacker searching an $n$-bit seed space requires at most $2^n$ evaluations and an average of $2^{n-1}$ evaluations.
- For a Unix timestamp known to within $\pm 300$ seconds, the effective entropy is:
  $$H(\text{timestamp}) = \log_2(601) \approx 9.23 \text{ bits}$$
  This provides virtually **zero security margin**.

### 5.2 Brute-Force Feasibility Comparison Table

| Target Mechanism | Seed / Key Space | Search Size | Time to Exhaust (Python) | Security Level |
| :--- | :--- | :--- | :--- | :--- |
| **Unix Timestamp ($\pm 5$ min)** | $\pm 300 \text{ s}$ | $601$ | $\approx 2 \text{ ms}$ | 🔴 Completely Broken |
| **Unix Timestamp ($\pm 24$ hours)** | $\pm 86,400 \text{ s}$ | $172,801$ | $\approx 0.35 \text{ s}$ | 🔴 Completely Broken |
| **Part A 16-bit Seed** | $2^{16}$ | $65,536$ | $\approx 0.85 \text{ s}$ | 🔴 Completely Broken |
| **32-bit Integer Seed** | $2^{32}$ | $4.29 \times 10^9$ | $\approx 2.5 \text{ hours}$ (CPU) | 🟠 Weak (Trivial on GPU) |
| **NIST CSPRNG (AES-128)** | $2^{128}$ | $3.40 \times 10^{38}$ | $> 10^{18} \text{ years}$ | 🟢 Cryptographically Secure |
| **NIST CSPRNG (AES-256)** | $2^{256}$ | $1.15 \times 10^{77}$ | Heat death of universe | 🟢 Cryptographically Secure |

### 5.3 False Positive Probability Analysis
In Part A, the matching criterion requires $14$ consecutive bytes of `'A'` ($\text{0x41}$).
What is the probability that an incorrect random seed produces $14$ consecutive `'A'`s by sheer accident in a message of length $L \approx 30$?

The probability of any random byte matching `'A'` under uniform distribution is $p = \frac{1}{256} = 2^{-8}$.
The probability of $14$ consecutive matches at any fixed offset is:
$$P(\text{false match at offset } j) = \left(\frac{1}{256}\right)^{14} = 2^{-112} \approx 1.93 \times 10^{-34}$$

Across all $65,536$ candidate seeds and all possible offsets ($j \le 20$), by Union Bound:
$$P(\text{any false positive}) \le 65536 \times 20 \times 2^{-112} \approx 2.5 \times 10^{-28} \approx 0$$

Therefore:
$$\textbf{A match is guaranteed to be the unique, authentic seed. False positives are mathematically impossible!}$$

---

## 6. Secure Alternatives & Cryptographic Defenses

### 6.1 Cryptographically Secure PRNGs (CSPRNG)
Applications requiring randomness for cryptographic purposes must **never** use MT19937 or timestamp seeds. Instead, they must use OS-level entropy pools:

| Platform / Language | Insecure (Do NOT Use) | Secure Primitive (Use This) |
| :--- | :--- | :--- |
| **Python** | `import random; random.random()` | `import secrets; secrets.token_hex(16)` |
| **Linux C / C++** | `rand()`, `drand48()`, `mt19937` | `getrandom(2)` syscall, `/dev/urandom` |
| **Windows C / C++** | `rand()`, `std::mt19937` | `BCryptGenRandom()` (Windows CNG) |
| **Java** | `java.util.Random` | `java.security.SecureRandom` |
| **Node.js** | `Math.random()` | `crypto.randomBytes(16)` |

### 6.2 Production Token Generation Standards
To generate secure password reset tokens:
```python
import secrets

def generate_secure_reset_token() -> str:
    # 256 bits of true cryptographic entropy from OS CSPRNG
    return secrets.token_hex(32)  # 64-character hex string
```
- Provides $256$ bits of entropy.
- Immune to timestamp prediction, state inversion, and known-plaintext attacks.

---

## 7. Step-by-Step Implementation Roadmap

### Target Folder Structure
```
attacks/
└── mt19937_stream_cipher_attack/
    ├── README.md                           # Comprehensive documentation & usage
    ├── data/
    │   ├── .gitkeep
    │   └── sample_payloads.txt             # Reference plaintext and tokens
    ├── notebooks/
    │   └── mt19937_cryptanalysis.ipynb     # Interactive Jupyter Notebook (Tasks 12-15)
    ├── outputs/
    │   ├── .gitkeep
    │   └── results.txt                     # Execution log, recovered seeds & tokens
    ├── reports/
    │   └── .gitkeep
    │   └── Assignment_10_Report.md         # Formal academic laboratory report
    └── src/
        ├── __init__.py
        ├── stream_cipher.py                # Part A: MT19937 stream cipher engine
        ├── seed_recovery_attack.py         # Part A: Brute-force 16-bit seed recovery
        ├── token_generator.py              # Part B: Timestamp-based token generator
        ├── token_prediction_attack.py      # Part B: Search window token cracker
        └── main.py                         # Complete CLI demonstration orchestrator
```

### Modular Source File Breakdown

1. **`stream_cipher.py`**:
   - `generate_keystream(seed: int, length: int) -> bytes`
   - `encrypt(plaintext: bytes, seed: int) -> bytes`
   - `decrypt(ciphertext: bytes, seed: int) -> bytes`
   - `generate_vulnerable_plaintext() -> tuple[str, str]` (prefix + 14 'A's)

2. **`seed_recovery_attack.py`**:
   - `brute_force_16bit_seed(ciphertext: bytes, known_sequence: bytes = b"AAAAAAAAAAAAAA") -> dict`
   - Evaluates all $65,536$ seeds, returns recovered seed, decrypted plaintext, elapsed time, and verified status.

3. **`token_generator.py`**:
   - `generate_timestamp_token(timestamp: int = None) -> tuple[int, str]`
   - Extracts $16$ consecutive $8$-bit outputs from MT19937 seeded by Unix timestamp, formatted as hex.

4. **`token_prediction_attack.py`**:
   - `predict_token(target_hex_token: str, base_timestamp: int, window_seconds: int = 300) -> dict`
   - Evaluates $T \pm \text{window\_seconds}$, matches candidate token, returns recovered timestamp and verification.

5. **`main.py`**:
   - End-to-end CLI orchestrator that executes Part A, Part B, prints colored verification tables, and saves results to `outputs/results.txt`.

---

## 8. Non-Interleaved Work Distribution Plan

To enable **uninterrupted end-to-end execution**, the tasks are structured into two independent, non-interleaved blocks:
- **Phase 1 is executed completely by Nishant**.
- **Phase 2 is executed completely by Lokesh**.

---

### **Phase 1: Nishant's Complete Block (Commits 1 to 3)**
*Nishant develops and verifies the foundational core, stream cipher engine, and the Part A known-plaintext attack before handing off.*

| # | Author | Commit Message | Files Affected | Description |
|---|---|---|---|---|
| **1** | **Nishant** | `chore(lab10): initialize mt19937_stream_cipher_attack folder structure and theory guide` | `resources/Assignment_10_Theory_Guide.md`, `attacks/mt19937_stream_cipher_attack/{data,notebooks,outputs,reports,src}/.gitkeep` | Initialize target directories and theory documentation. |
| **2** | **Nishant** | `feat(lab10): implement MT19937 toy stream cipher and 16-bit seed brute-force attack` | `attacks/mt19937_stream_cipher_attack/src/stream_cipher.py`, `attacks/mt19937_stream_cipher_attack/src/seed_recovery_attack.py` | Implement keystream generator, encrypt/decrypt symmetric functions, and exhaustive $65,536$ seed search algorithm. |
| **3** | **Nishant** | `feat(lab10): implement timestamp token generator and predictable token cracker` | `attacks/mt19937_stream_cipher_attack/src/token_generator.py`, `attacks/mt19937_stream_cipher_attack/src/token_prediction_attack.py` | Implement $16$-byte timestamp token generation and $T \pm 300$ candidate search window predictor. |

---

### **Phase 2: Lokesh's Complete Block (Commits 4 to 6)**
*Lokesh completes the orchestrator pipeline, executes the experiments, authors the Jupyter notebook and formal lab report, and updates the repository READMEs.*

| # | Author | Commit Message | Files Affected | Description |
|---|---|---|---|---|
| **4** | **Lokesh** | `feat(lab10): add main.py orchestrator and generate execution outputs` | `attacks/mt19937_stream_cipher_attack/src/main.py`, `attacks/mt19937_stream_cipher_attack/outputs/results.txt` | Build CLI demonstration runner combining Part A and Part B with formatted terminal reporting. |
| **5** | **Lokesh** | `docs(lab10): add mt19937_cryptanalysis interactive Jupyter Notebook` | `attacks/mt19937_stream_cipher_attack/notebooks/mt19937_cryptanalysis.ipynb` | Comprehensive notebook covering MT19937 mechanics, untempering theory, search space math, and attack visualizations. |
| **6** | **Lokesh** | `docs(lab10): add Assignment 10 report, folder README, and update global README` | `attacks/mt19937_stream_cipher_attack/reports/Assignment_10_Report.md`, `attacks/mt19937_stream_cipher_attack/README.md`, `README.md` | Finalize academic lab report, folder documentation, and update global progress table to Labs 1–10. |

---

*CryptoLabX Group 01 — 22CPP307 Cryptography Laboratory | MNIT Jaipur*

