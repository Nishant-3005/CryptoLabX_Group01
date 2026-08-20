# Lab 4 — Shift Cipher Cryptanalysis
## CryptoLabX Group 01 | 22CPP307 Cryptography Laboratory

> **Assignment:** Lab 4 — Cryptanalysis of Shift Cipher
> **Attacks:** Brute Force + Dictionary Scoring | Chi-Square Analysis
> **Language:** Python 3

---

## Folder Structure

```
shift_cipher_attack/
│
├── src/
│   ├── shift_cipher.py          Encrypt / Decrypt using Shift Cipher
│   ├── brute_force_dictionary.py  Brute-force attack with dictionary scoring
│   ├── chi_square_attack.py     Chi-Square frequency analysis attack
│   └── main.py                  Entry point — run both attacks, compare results
│
├── dictionary/
│   └── english_words.txt        Word list used for dictionary scoring
│
├── testcases/                   Sample plaintext/ciphertext test pairs
├── outputs/                     Program output logs
├── screenshots/                 Demo screenshots
├── reports/                     Written analysis report (PDF)
│   └── Assignment_4_Report.pdf
│
├── Lab4_Theory_Guide.md         Theory, math intuition, worked examples
└── README.md                    This file
```

---

## How to Run

```bash
# From project root
python attacks/shift_cipher_attack/src/main.py

# OR from inside src/
cd attacks/shift_cipher_attack/src
python main.py
```

---

## What the Attacks Do

### Attack 1 — Brute Force + Dictionary Scoring
Tries all 26 possible keys. For each key, decrypts the ciphertext and counts how many resulting words appear in the English dictionary. The key with the highest word-match count is declared the winner.

### Attack 2 — Chi-Square Analysis
Tries all 26 keys. For each key, computes the Chi-Square statistic comparing the observed letter frequency of the decryption against known English letter frequencies. The key with the **lowest** χ² score wins.

---

## Commit Plan (as per assignment)

| Commit | Content | Who |
|--------|---------|-----|
| 1 | `feat(lab4): implement shift cipher encrypt/decrypt` | Nishant |
| 2 | `feat(lab4): add brute-force dictionary scoring attack` | Lokesh |
| 3 | `feat(lab4): add chi-square cryptanalysis attack` | Nishant |
| 4 | `feat(lab4): add main.py - run both attacks and compare results` | Lokesh |
| 5 | `docs(lab4): add theory guide, results table, and README` | Lokesh |

---

*CryptoLabX Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | MNIT Jaipur*
