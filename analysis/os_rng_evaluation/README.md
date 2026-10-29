# Lab 9 — Evaluation of OS Random Number Generation Mechanisms

> **Course:** Cryptography Laboratory (22CPP307)  
> **Group:** 01  
> **Authors:** Nishant (2024UCP1773) · Lokesh Saini (2024UCP1505)  
> **Location:** `analysis/os_rng_evaluation/`

---

## 📌 Overview

This laboratory module evaluates operating-system random-number generation mechanisms and investigates their suitability for cryptographic applications. 

We generate at least 1 MB ($1,048,576$ bytes) of random data from four distinct sources:
1. **Linux `/dev/urandom`**: Modern kernel CSPRNG stream driven by per-CPU ChaCha20 stream ciphers and BLAKE2s entropy pools.
2. **OpenSSL `rand`**: NIST SP 800-90A AES-256-CTR DRBG seeded by the operating system kernel.
3. **Windows CNG (`BCryptGenRandom`)**: Windows Cryptography Next Generation kernel-mode AES-256 CTR-DRBG.
4. **Python PRNG (Mersenne Twister MT19937)**: Control group non-cryptographic generator demonstrating the statistical vs cryptographic security paradox.

---

## 📁 Folder Structure

```
analysis/os_rng_evaluation/
├── README.md                           # Lab overview and usage guide
├── data/
│   ├── dev_urandom_1mb.bin             # 1 MB from Linux /dev/urandom
│   ├── openssl_1mb.bin                 # 1 MB from OpenSSL rand
│   ├── windows_cng_1mb.bin             # 1 MB from Windows BCryptGenRandom
│   └── python_prng_1mb.bin             # 1 MB from Python random (MT19937)
├── notebooks/
│   └── rng_statistical_analysis.ipynb  # Interactive Jupyter Notebook (Tasks 3 & 5)
├── outputs/
│   ├── byte_distribution.png           # 4-panel byte frequency histograms
│   ├── autocorrelation_plot.png        # Serial autocorrelation curves (Lags 1..20)
│   └── summary_table.txt               # Exported numerical results table
├── reports/
│   └── OS_RNG_Evaluation_Report.md     # Comprehensive Laboratory Evaluation Report
└── src/
    ├── generate_data.py                # Multi-platform 1 MB generation script
    ├── statistical_tests.py            # Complete NIST-compliant statistical test suite
    └── main.py                         # CLI orchestrator & plot/table generator
```

---

## 🚀 Quick Start

From the repository root or module directory:

```bash
# 1. Run the full evaluation pipeline (Runs tests on all 4 files, generates plots & table):
python analysis/os_rng_evaluation/src/main.py

# 2. Run statistical tests on any arbitrary binary file:
python analysis/os_rng_evaluation/src/statistical_tests.py analysis/os_rng_evaluation/data/windows_cng_1mb.bin

# 3. Launch interactive Jupyter Notebook (Tasks 3 & 5):
jupyter notebook analysis/os_rng_evaluation/notebooks/rng_statistical_analysis.ipynb
```

---

## 📊 Summary of Experimental Results (1 MB Datasets)

| Generator / Engine | 1s Proportion | Chi-Square ($\chi^2$) | $\chi^2$ $p$-value | Shannon Entropy | Autocorrelation ($r_1$) | Monte Carlo $\pi$ | Overall Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Linux `/dev/urandom`** | 0.500069 | 222.06 | 0.9328 | 7.999847 | -0.000368 | 3.13803 | **PASS** |
| **OpenSSL `rand`** | 0.499680 | 253.43 | 0.5161 | 7.999826 | +0.000159 | 3.13837 | **PASS** |
| **Windows CNG** | 0.500038 | 266.36 | 0.2997 | 7.999817 | -0.000360 | 3.14005 | **PASS** |
| **Python PRNG (MT19937)**| 0.500137 | 267.79 | 0.2787 | 7.999816 | -0.001404 | 3.14320 | **PASS (Statistical)** |

---

## 🔑 Crucial Cryptographic Insight

> **Passing statistical tests is a NECESSARY condition, but NEVER a SUFFICIENT condition for cryptographic security.**

Notice that **Python's `random` module (Mersenne Twister MT19937) passed every statistical test** with flying colors ($H = 7.999816$, $\chi^2 = 267.79, p = 0.2787$), yet it has **ZERO cryptographic security**.
- An attacker observing just **624 consecutive 32-bit outputs** can invert the linear state transformations, reconstruct the entire internal state, and predict all future and past outputs with 100% precision.
- Cryptographic security requires **computational unpredictability** (Next-Bit Unpredictability / Yao's Test) and **Forward/Backward Secrecy**, which only OS-level CSPRNGs (Linux `/dev/urandom`, Windows CNG `BCryptGenRandom`) provide.

---

## 👥 Contributors

- **Nishant** (2024UCP1773) — `generate_data.py`, raw 1 MB datasets, `rng_statistical_analysis.ipynb`, module documentation
- **Lokesh Saini** (2024UCP1505) — Theory guide, `statistical_tests.py` testing engine, `main.py` orchestrator, `OS_RNG_Evaluation_Report.md`
