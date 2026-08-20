# Lab 4 — Cryptanalysis of Shift Cipher
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)

---

## Aim

To implement and evaluate two cryptanalytic techniques — **Brute-Force with Dictionary Scoring** and **Chi-Square Statistical Analysis** — for breaking the Shift (Caesar) Cipher, and to compare their effectiveness across multiple test cases.

---

## Brief Theory

### The Shift Cipher

The Shift Cipher (Caesar Cipher) is a monoalphabetic substitution cipher where each plaintext letter is shifted by a fixed key `k` positions in the alphabet:

```
Encryption:  C = (P + k) mod 26
Decryption:  P = (C - k + 26) mod 26
```

**Key space:** Only 26 possible keys (0–25), making it trivially breakable by exhaustive search. The cryptanalytic challenge is scoring which of the 26 decryptions is the "correct" one — i.e., the one that best resembles natural English.

---

## Algorithm 1: Brute-Force with Dictionary Scoring

### Description

Try all 26 possible keys. For each candidate plaintext, count how many of its words appear in a known English word list. The key that produces the most dictionary matches is declared the winner.

### Algorithm

```
INPUT: ciphertext C, English word dictionary D

FOR key k = 0 TO 25:
    candidate ← decrypt(C, k)
    score(k)  ← count of words in candidate that exist in D

RETURN key with max(score)
```

### Time Complexity

O(26 × n) where n = length of ciphertext  
O(26 × w × L) where w = words in candidate, L = avg word length (for set lookup ≈ O(1))

### Strengths
- Simple and reliable for natural-language texts with common words
- Works even on short ciphertexts if common words (the, and, is) are present

### Weaknesses
- Depends entirely on the quality and size of the dictionary
- Fails if the plaintext uses rare, technical, or non-English vocabulary
- Cannot score non-word text (numbers, names, abbreviations)

---

## Algorithm 2: Chi-Square Statistical Analysis

### Description

For each of the 26 candidate decryptions, compare its letter frequency distribution against the known English letter frequency distribution using the Chi-Square (χ²) goodness-of-fit test. The decryption that most closely matches English letter frequencies has the lowest χ² score — that key is the prediction.

### Algorithm

```
INPUT: ciphertext C
REFERENCE: English letter frequencies E[A..Z] (Lewand 2000)

FOR key k = 0 TO 25:
    candidate ← decrypt(C, k)
    O[i] ← observed count of letter i in candidate  (i = A..Z)
    N    ← total letters in candidate
    E_i  ← (English_freq[i] / 100) × N    (expected count)

    χ²(k) = Σ (O[i] - E_i)² / E_i    for i in A..Z

RETURN key with min(χ²)
```

### English Letter Frequencies Used (reference values)

| Letter | Freq % | Letter | Freq % | Letter | Freq % |
|--------|--------|--------|--------|--------|--------|
| E | 12.702 | T | 9.056  | A | 8.167  |
| O | 7.507  | I | 6.966  | N | 6.749  |
| S | 6.327  | H | 6.094  | R | 5.987  |
| D | 4.253  | L | 4.025  | C | 2.782  |

### Time Complexity

O(26 × n)  where n = length of ciphertext

### Strengths
- Language-agnostic beyond the reference table (no dictionary needed)
- Works well for longer ciphertexts where frequencies converge
- Provides a continuous numerical score — can rank all 26 candidates

### Weaknesses
- Unreliable for short ciphertexts (< ~20 letters) — sample too small
- Fails completely on single-character inputs
- Unusual vocabulary (scientific, proper nouns) skews frequencies

---

## Implementation

### Module Structure

```
attacks/shift_cipher_attack/
├── src/
│   ├── shift_cipher.py           Encrypt / Decrypt (Caesar formula)
│   ├── brute_force_dictionary.py Algorithm 1 — dictionary scoring
│   ├── chi_square_attack.py      Algorithm 2 — Chi-Square test
│   └── main.py                   Unified runner & test suite
└── dictionary/
    └── english_words.txt         262 common English words
```

### Key Functions

| Module | Function | Purpose |
|--------|----------|---------|
| `shift_cipher.py` | `encrypt(pt, k)` | Apply Caesar shift |
| `shift_cipher.py` | `decrypt(ct, k)` | Reverse Caesar shift |
| `shift_cipher.py` | `get_all_decryptions(ct)` | All 26 candidates |
| `brute_force_dictionary.py` | `score_text(text, dict)` | Count dictionary word matches |
| `brute_force_dictionary.py` | `brute_force_dictionary_attack(ct, dict)` | Run Algorithm 1 |
| `chi_square_attack.py` | `chi_square_statistic(text)` | Compute χ² vs English |
| `chi_square_attack.py` | `chi_square_attack(ct)` | Run Algorithm 2 |
| `main.py` | `run_test_suite(dict)` | Run all test cases + print table |

---

## Experimental Results

### Test Cases Run

| # | Plaintext | Key |
|---|-----------|-----|
| 1 | the quick brown fox jumps over the lazy dog | 3 |
| 2 | cryptography is the art of writing secret codes | 7 |
| 3 | attack at dawn send reinforcements to the north | 13 |
| 4 | frequency analysis reveals patterns in ciphertext | 17 |
| 5 | zebra xenon quantum voyage | 25 |
| 6 | a | 5 |

### Results Table

| Test | Actual Key | Dictionary Key | Chi-Square Key | Dictionary Correct? | Chi-Square Correct? |
|------|-----------|----------------|----------------|---------------------|---------------------|
| 1    | 3         | 3              | 3              | ✅ YES              | ✅ YES              |
| 2    | 7         | 7              | 7              | ✅ YES              | ✅ YES              |
| 3    | 13        | 13             | 13             | ✅ YES              | ✅ YES              |
| 4    | 17        | 17             | 17             | ✅ YES              | ✅ YES              |
| 5    | 25        | 0              | 5              | ❌ NO               | ❌ NO               |
| 6    | 5         | 5              | 1              | ✅ YES              | ❌ NO               |

**Dictionary Attack Accuracy : 5/6 (83.3%)**  
**Chi-Square Attack Accuracy : 4/6 (66.7%)**

---

## Comparison: Dictionary Scoring vs Chi-Square

| Criterion | Dictionary Scoring | Chi-Square Analysis |
|---|---|---|
| **Basis** | Lexical (word matching) | Statistical (letter frequencies) |
| **Requirement** | English word list | Reference frequency table |
| **Short text** | Works if common words present | Unreliable (< 20 letters) |
| **Single char** | Correct (if char is a word like "a") | Fails (no frequency data) |
| **Unusual vocab** | Fails (words not in dictionary) | May fail (frequency skewed) |
| **Non-English** | Fails completely | May succeed if language freq known |
| **Score direction** | Higher is better (max score wins) | Lower is better (min χ² wins) |
| **Test 5 result** | Key 0 predicted (wrong) | Key 5 predicted (wrong) |
| **Accuracy (6 tests)** | 83.3% | 66.7% |

---

## Failure Analysis

### Test 5 — `"zebra xenon quantum voyage"`, Key = 25

**Both attacks failed.**

**Dictionary failure:**  
None of the words "zebra", "xenon", "quantum", "voyage" appear in our 262-word common word list. All 26 decryptions score 0 dictionary words, so the algorithm defaults to key 0 (the first one in the tie). The fix is to use a larger dictionary (e.g., 10,000+ words including scientific and technical vocabulary).

**Chi-Square failure:**  
The text is only 26 letters long. With such a small sample, the observed letter frequency distribution is noisy and does not resemble the reference English distribution for any shift. The chi-square statistic is unreliable on texts shorter than ~50 letters. Fix: use longer ciphertexts, or fall back to brute-force display when text is too short.

### Test 6 — `"a"`, Key = 5

**Chi-Square failed, Dictionary succeeded.**

**Dictionary:** The single letter "a" after decryption with key 5 gives "v". But with key 5 applied to "a" shifted by 5, the correct decryption is "a" — which IS in the dictionary. The dictionary correctly identified key 5 because "a" is a valid English word.

**Chi-Square:** With only 1 letter, only one frequency bucket (out of 26) has any data. The chi-square statistic is essentially random noise — it predicted key 1 instead of key 5. Fix: skip chi-square analysis for texts under 10 characters and display a warning instead.

---

## Observations

1. **Both attacks trivially break the shift cipher** on natural English text of reasonable length (> 30 letters). The cipher's key space of 26 is far too small — brute force is instant.

2. **Dictionary scoring is more reliable for short texts** — a single common word ("the", "is", "and") is enough to identify the correct key. Chi-Square needs several dozen letters to produce a reliable frequency estimate.

3. **Chi-Square is language-model-free** — it requires no external word list, only the reference frequency table. This makes it more portable and applicable to languages other than English (with appropriate frequency tables).

4. **Both attacks fail identically on low-frequency or non-English vocabulary** — confirming that the shift cipher's weakness is the *statistical predictability of natural language*, not just the small key space.

5. **The two attacks agreed on the correct key** in 4 out of 6 test cases (66.7%). In all cases where they agreed, they were correct. The disagreements only occurred in the two edge cases (short text and unusual vocabulary).

6. **The shift cipher provides zero cryptographic security** in modern contexts. The only "security" it ever had was obscurity — an adversary who knew the cipher scheme would break it instantly.

---

## Conclusion

This lab demonstrated two fundamentally different approaches to cryptanalysis of the Shift Cipher:

- **Brute-Force with Dictionary Scoring** exploits the *lexical* structure of English — the fact that plaintext words appear in natural-language dictionaries.
- **Chi-Square Analysis** exploits the *statistical* structure of English — the uneven distribution of letter frequencies (E=12.7%, Z=0.07%).

Both attacks are rooted in the same fundamental insight: **natural language is highly non-random**, and a correct decryption of a shift cipher should "look like" natural language by either measure.

The Chi-Square method is historically significant — it was the primary technique used by early 20th-century cryptanalysts including William Friedman to attack monoalphabetic substitution ciphers. The dictionary method is a modern computational shortcut that leverages easily available word lists.

The shift cipher is entirely broken by both attacks. Future labs will study ciphers with larger key spaces (Vigenère, AES) where these simple attacks fail — but the *principles* of frequency analysis and statistical scoring remain at the core of cryptanalysis.

---

*Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 Cryptography Laboratory | MNIT Jaipur*
