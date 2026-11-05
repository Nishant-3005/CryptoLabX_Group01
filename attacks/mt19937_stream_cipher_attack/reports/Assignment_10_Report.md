# Lab 10 — MT19937 Stream Cipher Known-Plaintext & Predictable Token Attacks
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)

---

## 1. Aim and Objectives

1. **Aim**: To investigate, implement, and exploit vulnerabilities arising from the misuse of the **Mersenne Twister (MT19937)** pseudorandom number generator in symmetric stream ciphers and web security token generation.
2. **Objectives**:
   - Construct a symmetric toy stream cipher using Python's MT19937 PRNG with an 8-bit keystream and bitwise XOR.
   - Execute an exhaustive known-plaintext brute-force attack to recover a secret 16-bit seed ($2^{16} = 65,536$ search space) using a known sequence of 14 consecutive `'A'`s placed at an unknown offset.
   - Simulate a vulnerable web application that generates 128-bit password reset tokens by seeding MT19937 with the server's integer Unix timestamp.
   - Formulate and execute a timestamp prediction window attack ($T \pm 300\text{s}$, 601 candidates) to recover the server timestamp and regenerate the identical token.
   - Mathematically analyze false positive bounds and formalize secure remediation using OS-level CSPRNGs (`secrets`).

---

## 2. Theoretical Background

### 2.1 The Mersenne Twister (MT19937) Architecture
Developed in 1997 by Makoto Matsumoto and Takuji Nishimura, the Mersenne Twister MT19937 is the default PRNG in Python (`random`), Ruby, PHP (`mt_rand`), and C++ (`std::mt19937`).

Key parameters:
- **Internal State**: 624 words of 32 bits each ($19,937$ bits of internal state).
- **Period**: $2^{19937} - 1$ (a Mersenne prime).
- **Equidistribution**: $k$-distributed up to 623 dimensions for 32-bit accuracy.

### 2.2 Why MT19937 Fails Cryptographically
1. **Completely Linear State Transitions**: All operations in the twist recurrence relation and tempering transformations are linear over $\text{GF}(2)$.
2. **No Backtracking Resistance (Forward Secrecy)**: Given 624 consecutive 32-bit outputs, the internal state can be inverted, revealing every future and past value.
3. **Low Entropy Seeding**: When seeded with small integers (e.g., 16-bit keys or 1-second timestamps), the massive period of $2^{19937}-1$ is irrelevant; the effective security collapses to the entropy of the seed ($2^{16}$ or $600$ states).

---

## 3. Cryptanalytic Methodologies

### 3.1 Part A: 16-bit Seed Known-Plaintext Attack
- **Cipher Model**:
  $$C_i = P_i \oplus K_i, \quad K_i = \text{MT19937}(S) \pmod{256}$$
- **Vulnerable Payload**: A random printable ASCII prefix ($5 \text{ to } 20$ chars) followed by 14 consecutive `'A'`s (`b"AAAAAAAAAAAAAA"`).
- **Attacker Knowledge**:
  - The ciphertext $C$.
  - The presence of `b"AAAAAAAAAAAAAA"` somewhere in the plaintext.
  - The seed $S \in [0, 65535]$ is a 16-bit integer.
  - The exact prefix length and offset are **unknown**.
- **Brute-Force Algorithm**:
  1. For each candidate seed $s \in [0, 65535]$:
  2. Generate candidate keystream $K^{(s)}$ of length $|C|$.
  3. Decrypt: $P^{(s)} = C \oplus K^{(s)}$.
  4. Perform sliding-window match: `if b"AAAAAAAAAAAAAA" in P^(s): return s`.

### 3.2 Part B: Predictable Timestamp-Seeded Token Cracking
- **Vulnerability**: A web server generates reset tokens as:
  $$S = \lfloor \text{time}() \rfloor, \quad \text{Token} = \text{MT19937}(S) \text{ (16 bytes)}$$
- **Attacker Strategy**:
  - Attacker triggers a reset request at client time $T_0$.
  - Defines search interval $[T_0 - 300, T_0 + 300]$ seconds ($601$ candidates).
  - Evaluates each candidate timestamp until generated token matches intercepted token.

---

## 4. Experimental Results and Analysis

Both cryptanalytic attacks were executed using our end-to-end orchestrator ([main.py](file:///c:/Users/LENOVO/Desktop/CryptoLabX_Group01/attacks/mt19937_stream_cipher_attack/src/main.py)).

### 4.1 Summary of Experimental Results

| Attack Vector | Search Space | Candidates Tested | Execution Latency | Search Throughput | Verification Result |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Part A: 16-bit Seed Stream Cipher** | $65,536$ seeds | $32,685$ seeds ($49.87\%$) | **$0.3681$ seconds** | **$88,783$ seeds/sec** | **PASS (Exact Match)** |
| **Part B: Timestamp Reset Token** | $601$ timestamps | $325$ timestamps ($54.08\%$) | **$2.915$ milliseconds** | **$111,492$ tokens/sec** | **PASS (Exact Match)** |

### 4.2 Part A Detailed Metrics
- **Target Plaintext**: `Y,qf1uAAAAAAAAAAAAAA` (Prefix: `'Y,qf1u'`, 6 bytes)
- **Known Plaintext**: `AAAAAAAAAAAAAA` (14 bytes)
- **True Encryption Seed**: `32684` (`0x7FAC`)
- **Recovered Encryption Seed**: `32684` (`0x7FAC`)
- **Ciphertext**: `012a38f4600a40bf7c2742fb72e039fc86d7f437`
- **Recovered Plaintext**: `Y,qf1uAAAAAAAAAAAAAA` (100% fidelity)
- **Detected Known Offset**: Byte 6

### 4.3 Part B Detailed Metrics
- **Client Request Time ($T_0$)**: `1793859916`
- **True Server Issuance Time ($T$)**: `1793859940` (Server latency: $+24$ seconds)
- **Target Intercepted Token**: `70ab0161edd83c126fdd693d33600e83`
- **Recovered Timestamp**: `1793859940` (`0x6AEC2164`)
- **Regenerated Token**: `70ab0161edd83c126fdd693d33600e83` (Identical match)
- **Search Latency**: Less than 3 milliseconds.

---

## 5. Mathematical & Complexity Analysis

### 5.1 Entropy Reduction
| Generator Configuration | Nominal Key Space | Effective Entropy | Brute-Force Feasibility |
| :--- | :---: | :---: | :---: |
| **AES-128 Key** | $2^{128}$ | $128$ bits | Computationally Infeasible ($10^{18}$ CPU years) |
| **16-bit Seed Stream Cipher** | $2^{16} = 65,536$ | $16$ bits | **Instantaneous** ($< 0.5$ seconds) |
| **1-Second Timestamp Reset Token** | $601$ candidates | $\approx 9.23$ bits | **Real-Time** ($< 3$ milliseconds) |

### 5.2 False Positive Probability Theorem
For a random candidate keystream and a known sequence of length $m = 14$ bytes:
$$P(\text{single byte match}) = \frac{1}{256} = 2^{-8}$$
$$P(14 \text{ contiguous bytes match at a fixed offset}) = \left(\frac{1}{256}\right)^{14} = 2^{-112} \approx 1.93 \times 10^{-34}$$

Accounting for the sliding window across $(L - m + 1) \le 20$ offsets and all $65,536 = 2^{16}$ seeds:
$$P(\text{any false positive}) \le 20 \times 2^{16} \times 2^{-112} = 20 \times 2^{-96} \approx 2.5 \times 10^{-28}$$

**Conclusion**: The probability of encountering a false positive is mathematically negligible, ensuring zero false alarms.

---

## 6. Defensive Engineering & Cryptographic Remediation

1. **Rule 1 — Never use `random` for Cryptography**:
   Python's `random` documentation explicitly warns:
   > *"Warning: The pseudo-random generators of this module should not be used for security purposes. Use the secrets module instead."*
2. **Rule 2 — Use OS-Level CSPRNGs for Tokens**:
   ```python
   import secrets
   
   # Secure reset token with 256 bits of true physical entropy
   secure_token = secrets.token_hex(32)
   ```
3. **Rule 3 — Use Authenticated Encryption**:
   Toy stream ciphers lack ciphertext integrity and are malleable. Production systems must employ **AES-GCM** or **ChaCha20-Poly1305**.

---

## 7. Conclusion

Lab 10 demonstrated that high statistical quality (as observed in Lab 9) provides no barrier against practical cryptanalysis when PRNGs are misused. Both the 16-bit MT19937 stream cipher and timestamp-seeded reset tokens were broken in fractions of a second. Secure cryptographic engineering requires high-entropy OS CSPRNGs and authenticated ciphers.
