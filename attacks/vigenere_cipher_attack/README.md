# Vigenère Cipher Cryptanalysis
## Lab 6 | CryptoLabX Group 01 | 22CPP307

> **Objective:** Break the Vigenère cipher using Kasiski Examination + Frequency Analysis  
> **Ciphertext:** #1 (Odd Group) — 395 letters  
> **Recovered Key:** `AMBROISETHOMAS`  
> **Plaintext:** Aria from *Mignon* by Ambroise Thomas (1866)

---

## Quick Start

```bash
# From project root
cd attacks/vigenere_cipher_attack/src
py -3 main.py
```

The program automatically:
1. Loads `../data/ciphertext.txt`
2. Runs Kasiski Examination
3. Runs IC Analysis to confirm key length
4. Recovers key letter-by-letter via chi-squared
5. Decrypts and verifies the result
6. Saves output to `../outputs/results.txt`

---

## Folder Structure

```
vigenere_cipher_attack/
├── src/
│   ├── vigenere_cipher.py      Encrypt, decrypt, clean, verify
│   ├── kasiski_analysis.py     Pattern finding, distances, factor counting
│   ├── frequency_analysis.py   IC, chi-squared, key recovery
│   └── main.py                 Full pipeline orchestrator
├── data/
│   └── ciphertext.txt          Assignment ciphertext 1 (odd group)
├── outputs/
│   └── results.txt             Auto-generated run results
├── reports/
│   └── Assignment_6_Report.md  Full analysis report with experimental data
└── README.md                   This file
```

---

## Source File Summary

| File | Functions | Purpose |
|------|-----------|---------|
| `vigenere_cipher.py` | `clean_ciphertext()`, `vigenere_encrypt()`, `vigenere_decrypt()`, `verify()` | Core cipher operations |
| `kasiski_analysis.py` | `find_repeated_patterns()`, `calculate_distances()`, `find_factors()`, `kasiski_analysis()` | Step 1: Estimate key length |
| `frequency_analysis.py` | `calculate_ic()`, `split_into_groups()`, `frequency_analysis()`, `find_shift()`, `find_key()`, `ic_analysis()` | Step 2: Confirm length + recover key |
| `main.py` | `main()`, `load_ciphertext()`, `run_kasiski_phase()`, `run_ic_phase()`, `run_frequency_phase()`, `run_decryption()`, `run_verification()`, `save_results()` | Full orchestration |

---

## Attack Method Overview

### Two-Phase Cryptanalysis

```
Phase 1: Kasiski Examination
  Find repeated 3-5 letter sequences in ciphertext
  Measure distances between repetitions
  Factor each distance (distances are multiples of key length)
  Count factor frequencies → top factor = likely key length

Phase 2: IC + Frequency Analysis
  For each candidate key length m:
    Split ciphertext into m groups (every m-th character)
    Compute average IC across groups
    English text IC ≈ 0.0667; random ≈ 0.0385
    The correct m gives groups closest to English IC

  For each group (= one Caesar cipher):
    Try all 26 shifts, score with chi-squared vs English frequencies
    Lowest chi-squared = correct key letter
```

---

## Results (Ciphertext 1)

| Step | Result |
|------|--------|
| Ciphertext length | 395 letters |
| Repeated patterns | 25 found |
| Key distances | 10 distinct: 14, 57, 98, 112, 114, 182, 210, 294, 330, 336 |
| Kasiski top candidates | [2, 7, **14**, 3, 6] |
| IC at key length 14 | 0.0644 (closest to English 0.0667) |
| **Recovered key** | **`AMBROISETHOMAS`** (14 letters) |
| Verification | ✅ PASS — re-encryption matches original |

---

## Background: The Plaintext

The decrypted text is an English adaptation of the aria **"Connais-tu le pays"** ("Do you know the land") from the opera **Mignon** (1866) by **Ambroise Thomas**, based on the poem "Kennst du das Land" from Goethe's *Wilhelm Meister's Apprenticeship*.

The key is the composer's full name — a meaningful keyword that dramatically illustrates why human-chosen keys are weak: the 26^14 key space is effectively reduced to words and names that people would actually use.

---

*CryptoLabX Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 | MNIT Jaipur*
