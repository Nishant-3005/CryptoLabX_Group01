# Lab 10 — MT19937 Stream Cipher Known-Plaintext & Predictable Token Attacks

> **Course:** Cryptography Laboratory (22CPP307)  
> **Group:** 01  
> **Authors:** Nishant (2024UCP1773) · Lokesh Saini (2024UCP1505)  
> **Location:** `attacks/mt19937_stream_cipher_attack/`

---

## 📌 Overview

This laboratory module explores the practical cryptanalysis of systems that misuse the **Mersenne Twister (MT19937)** pseudorandom number generator:
1. **Part A — MT19937 Stream Cipher Known-Plaintext Attack**:
   - Implements a symmetric toy stream cipher ($C_i = P_i \oplus K_i$) initialized with a 16-bit seed ($2^{16} = 65,536$).
   - Mounts an exhaustive brute-force attack exploiting a known sequence of 14 `'A'`s placed at an unknown offset.
2. **Part B — Predictable Password Reset Token Cracking**:
   - Simulates a web application that generates 128-bit reset tokens seeded by the Unix timestamp ($T = \lfloor \text{time}() \rfloor$).
   - Mounts a window search attack ($T \pm 300\text{s}$, 601 candidates) to recover the server timestamp and regenerate the token.

---

## 📁 Folder Structure

```
attacks/mt19937_stream_cipher_attack/
├── README.md                           # Documentation, setup, and attack overview
├── data/
│   └── .gitkeep
├── notebooks/
│   └── mt19937_cryptanalysis.ipynb     # Interactive Jupyter Notebook with theory & plots
├── outputs/
│   └── results.txt                     # Execution logs, recovered seeds & tokens
├── reports/
│   └── Assignment_10_Report.md         # Formal academic laboratory report
└── src/
    ├── __init__.py
    ├── stream_cipher.py                # Part A: MT19937 toy stream cipher engine
    ├── seed_recovery_attack.py         # Part A: 16-bit seed brute-force cracker
    ├── token_generator.py              # Part B: Predictable timestamp token generator
    ├── token_prediction_attack.py      # Part B: Candidate window token predictor
    └── main.py                         # Complete CLI demonstration orchestrator
```

---

## 🚀 Quick Start

From the repository root or module directory:

```bash
# 1. Run the complete demonstration pipeline (Executes Part A & Part B, exports results):
python attacks/mt19937_stream_cipher_attack/src/main.py

# 2. Run Part A (Stream Cipher & Seed Recovery):
python attacks/mt19937_stream_cipher_attack/src/seed_recovery_attack.py

# 3. Run Part B (Timestamp Token Cracker):
python attacks/mt19937_stream_cipher_attack/src/token_prediction_attack.py

# 4. Launch interactive Jupyter Notebook:
jupyter notebook attacks/mt19937_stream_cipher_attack/notebooks/mt19937_cryptanalysis.ipynb
```

---

## 📊 Summary of Experimental Results

| Attack Vector | Search Space | Search Time | Search Throughput | Verification Result |
| :--- | :---: | :---: | :---: | :---: |
| **Part A: 16-bit Seed Stream Cipher** | $65,536$ seeds | **$0.368$ seconds** | **$88,783$ seeds/sec** | **PASS (Exact Seed & Plaintext Match)** |
| **Part B: Timestamp Reset Token** | $601$ timestamps | **$2.92$ milliseconds** | **$111,492$ tokens/sec** | **PASS (Exact Token & Timestamp Match)** |

---

## 🔑 Crucial Cryptographic Insight

> **Statistical randomness is completely orthogonal to computational unpredictability.**

Even though MT19937 exhibits a period of $2^{19937}-1$ and passes standard randomness tests (Lab 9), it fails catastrophically when used for cryptographic security:
- **Part A**: Restricting seed size to 16 bits collapses the search space to $65,536$ states, allowing recovery in under $0.5$ seconds.
- **Part B**: Seeding with Unix timestamps reduces effective entropy from 128 bits to $\approx 9.23$ bits ($601$ candidates), enabling instant token prediction.
- **Defense**: Always use cryptographically secure PRNGs (`secrets` in Python, `getrandom` in Linux, `BCryptGenRandom` in Windows).

---

## 👥 Contributors

- **Nishant** (2024UCP1773) — `stream_cipher.py`, `seed_recovery_attack.py`, `token_generator.py`, `token_prediction_attack.py`
- **Lokesh Saini** (2024UCP1505) — Theory guide, `main.py` orchestrator, `mt19937_cryptanalysis.ipynb`, `Assignment_10_Report.md`
