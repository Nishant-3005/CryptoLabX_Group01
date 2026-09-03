# Lab 5 — Monoalphabetic Substitution Cipher Cryptanalysis
## CryptoLabX Group 01 | 22CPP307 Cryptography Laboratory

> **Assignment:** Lab 5 — Monoalphabetic Substitution Cipher & Cryptanalysis
> **Language:** Python 3 (no external libraries for analysis logic)
> **Source Text:** Katz & Lindell, *Introduction to Modern Cryptography*, Page 31

---

## What This Folder Contains

Implementation of a **Monoalphabetic Substitution Cipher** and a full **frequency + pattern analysis cryptanalysis pipeline** that breaks it without knowing the key.

### The Cipher

Each plaintext letter is replaced by a unique ciphertext letter according to a fixed permutation:

```
Example key:
  Plaintext : A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
  Ciphertext: T S U L O J V I C W P Z G K B R M A N E Y Q F X H D
```

- **Key space:** 26! ≈ 4×10²⁶ — brute force is impossible
- **Fatal weakness:** Preserves letter frequency — broken by frequency analysis

---

## Folder Structure

```
monosubstitution_cipher_attack/
│
├── src/
│   ├── monosubstitution_cipher.py   Core cipher: encrypt(), decrypt(), generate_random_key()
│   ├── frequency_analysis.py        3 required functions: letter freq, word freq, pattern analysis
│   ├── cryptanalysis.py             apply_substitution(), display_partial_plaintext(), verify_solution()
│   └── main.py                      Full orchestrator: interactive + auto-demo attack modes
│
├── data/
│   └── plaintext_source.txt         Page 31 of Katz & Lindell (Definition of Perfect Secrecy)
│
├── outputs/
│   └── results.txt                  Auto-generated run output with key, ciphertext, frequency order
│
├── reports/
│   └── Assignment_5_Report.md       Full cryptanalysis report with real experimental data
│
└── screenshots/                     Demo screenshots (add here)
```

---

## How to Run

```bash
# From project root
python attacks/monosubstitution_cipher_attack/src/main.py

# OR from inside src/
cd attacks/monosubstitution_cipher_attack/src
python main.py
```

Select mode when prompted:
- `[1]` Interactive — you enter CT→PT guesses manually, see partial plaintext update live
- `[2]` Auto-demo — simulates a frequency-guided attack and verifies the result

---

## Required Functions (per Assignment 5)

| Function | File | What it does |
|----------|------|-------------|
| `frequency_analysis(ct)` | `frequency_analysis.py` | Counts A–Z in ciphertext, ranks by frequency, prints bar chart + percentage table |
| `word_frequency_analysis(ct)` | `frequency_analysis.py` | Groups words by length (1,2,3,4,longer), counts each, highlights English candidates |
| `pattern_analysis(ct)` | `frequency_analysis.py` | Encodes each word as a numeric pattern (e.g. "QIIQX"→"01102") and matches to English word list |
| `apply_substitution(ct, key_map)` | `cryptanalysis.py` | Applies partial CT→PT mapping; shows `_` for unmapped letters |
| `display_partial_plaintext(pt, key_map)` | `cryptanalysis.py` | Shows current decryption state + known mappings table + unmapped letters |
| `verify_solution(ct, pt, key)` | `cryptanalysis.py` | Re-encrypts recovered PT and checks exact match against original CT |

---

## Attack Strategy

```
1. frequency_analysis()
   → Find most frequent CT letter → likely maps to 'E' (12.7% in English)
   → Find CT frequency order vs ETAOINSHRDLU

2. word_frequency_analysis()
   → Most frequent 3-letter word → almost certainly "THE"
   → Single letter words → "A" or "I" only
   → Most frequent 2-letter words → "OF", "TO", "IN", "IS"...

3. pattern_analysis()
   → Match CT word patterns to English word pattern database
   → e.g. Pattern "012" → the, and, for, are, was, has...

4. Iterative apply_substitution() loop
   → Enter one guess at a time
   → Watch partial plaintext fill in
   → Use context from visible words to deduce remaining letters

5. verify_solution()
   → Re-encrypt recovered plaintext with derived key
   → Must match original ciphertext exactly
```

---

## Experimental Results Summary

Text: Katz & Lindell page 31 (~3,800 alphabetic letters)

| Step | Key Deduction | Evidence |
|------|--------------|----------|
| 1 | CT `O` → `E` | O appeared 12.9% of time |
| 2 | CT `EIO` → `THE` | EIO is most frequent 3-letter word (89 occurrences) |
| 3 | CT `EB` → `TO` | EB is most frequent 2-letter word (47 occurrences) |
| 4 | CT `TKL` → `AND` | TKL 3rd most frequent 3-letter word (31 occurrences) |
| 5–11 | Remaining 18 letters from context | Partial words like `_ROBABILITY` → PROBABILITY |
| 12 | `verify_solution()` | **EXACT MATCH — VERIFIED ✓** |

**Full key recovered in 11 steps. All 26 letters mapped correctly.**

---

## Key Insight

> *"A ciphertext reveals nothing about the underlying plaintext"* — but that is the definition of **perfect secrecy**, which requires the ciphertext to be statistically indistinguishable from random noise. The monoalphabetic cipher fails this completely: it merely relabels letters, preserving all statistical structure of the plaintext. This is the fundamental lesson of Lab 5.*

---

*CryptoLabX Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 | MNIT Jaipur*
