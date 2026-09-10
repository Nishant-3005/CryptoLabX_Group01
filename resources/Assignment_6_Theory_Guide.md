# Assignment 6 — Theory Guide: Vigenère Cipher Cryptanalysis
## Kasiski Examination & Frequency Analysis
### CryptoLabX Group 01 | 22CPP307

---

## Table of Contents

1. [The Vigenère Cipher — How It Works](#1-the-vigenère-cipher--how-it-works)
2. [Why Simple Frequency Analysis Fails](#2-why-simple-frequency-analysis-fails)
3. [Kasiski Examination — Finding the Key Length](#3-kasiski-examination--finding-the-key-length)
4. [Index of Coincidence (IC)](#4-index-of-coincidence-ic)
5. [Splitting Ciphertext into Groups](#5-splitting-ciphertext-into-groups)
6. [Per-Group Frequency Analysis — Finding Each Shift](#6-per-group-frequency-analysis--finding-each-shift)
7. [Recovering the Full Key](#7-recovering-the-full-key)
8. [Decryption & Verification](#8-decryption--verification)
9. [Worked Example (Mini)](#9-worked-example-mini)
10. [Our Ciphertext (Group 1 — Odd)](#10-our-ciphertext-group-1--odd)

---

## 1. The Vigenère Cipher — How It Works

The Vigenère cipher is a **polyalphabetic substitution cipher**. Unlike the Caesar (shift) cipher which uses one shift for every letter, the Vigenère cipher uses a **keyword** to cycle through multiple shifts.

### Encryption Formula

Given:
- Plaintext letter: `P_i` (as a number 0–25, where A=0, B=1, ..., Z=25)
- Key letter: `K_j` (where `j = i mod m`, and `m` = key length)

```
Encryption:   C_i = (P_i + K_j) mod 26
Decryption:   P_i = (C_i - K_j + 26) mod 26
```

### Example

| Keyword      | L  | E  | M  | O  | N  | L  | E  | M  | O  | N  |
|-------------|----|----|----|----|----|----|----|----|----|----|
| Key values  | 11 | 4  | 12 | 14 | 13 | 11 | 4  | 12 | 14 | 13 |
| Plaintext   | A  | T  | T  | A  | C  | K  | A  | T  | D  | A  |
| Plaintext # | 0  | 19 | 19 | 0  | 2  | 10 | 0  | 19 | 3  | 0  |
| Ciphertext  | L  | X  | F  | O  | P  | V  | E  | F  | R  | N  |

Notice: the letter `T` encrypts to `X` the first time, `F` the second time, and `F` again the third time — because the key letter changes each time. This is what makes Vigenère harder to break than Caesar.

### Why It's Called "Polyalphabetic"

A monoalphabetic cipher maps each plaintext letter to exactly one ciphertext letter (one alphabet). The Vigenère cipher effectively uses **m different Caesar alphabets** (where m = key length), cycling through them. This is what "polyalphabetic" means.

---

## 2. Why Simple Frequency Analysis Fails

In a Caesar cipher, every `E` in plaintext maps to the same ciphertext letter, so the most frequent ciphertext letter is probably `E`. The frequency fingerprint is preserved.

In Vigenère, the letter `E` is encrypted with **different shifts** depending on its position in the message:
- Position 1 uses shift `K_1`
- Position 2 uses shift `K_2`
- etc.

This **flattens** the frequency distribution of the ciphertext. If you just count letter frequencies on the whole ciphertext, you won't see the classic English "ETAOIN" peak pattern — the different shifts smear it out.

**But here's the key insight**: If we knew the key length `m`, we could group every m-th letter together. Each group would have been encrypted with the **same** Caesar shift, and simple frequency analysis would work on each group individually.

So the attack is:
1. **Find the key length** → Kasiski / IC
2. **Break each group** → Frequency analysis (same as a Caesar cipher attack)

---

## 3. Kasiski Examination — Finding the Key Length

### The Core Idea

When the same sequence of plaintext letters aligns with the same sequence of key letters, it produces the same ciphertext sequence. For example, if "THE" appears at position 3 and position 15, and the key is "KEY" (length 3):
- Position 3: key letter at position `3 mod 3 = 0` → K
- Position 15: key letter at position `15 mod 3 = 0` → K
- Both times "THE" aligns with the same key letters → same ciphertext!

The distance between these two occurrences is `15 - 3 = 12`, and `12` is a **multiple of the key length** (12 = 3 × 4).

### Algorithm

```
Step 1: Scan the ciphertext for REPEATED sequences of length >= 3
        (trigrams are most reliable; digrams produce too many coincidences)

Step 2: For each repeated sequence, record the DISTANCES between occurrences
        e.g., "QSV" appears at positions 78 and 168 → distance = 90

Step 3: For each distance, find all its FACTORS
        e.g., 90 → factors: 2, 3, 5, 6, 9, 10, 15, 18, 30, 45, 90

Step 4: Count how often each factor appears across ALL distances
        The most frequent factor is the most likely key length
```

### Example

Suppose we find these repeated trigrams:

| Trigram | Positions       | Distance | Factors (excl. 1)      |
|---------|----------------|----------|------------------------|
| QSV     | 78, 168        | 90       | 2, 3, 5, 6, 9, 10, 15, 18, 30, 45 |
| WKV     | 45, 135        | 90       | 2, 3, 5, 6, 9, 10, 15, 18, 30, 45 |
| SEQ     | 30, 60         | 30       | 2, 3, 5, 6, 10, 15, 30 |

Factor frequency count:
- `5` appears 3 times
- `3` appears 3 times
- `15` appears 3 times ← strong candidate
- `2` appears 3 times

If `5` and `3` both score high, `15` (= 5×3) or `5` or `3` are likely key lengths. We use IC (next section) to disambiguate.

### Why Trigrams (Not Digrams)?

Two random letters have a 1/676 chance of matching. Two random trigrams have a 1/17576 chance. Longer repeated sequences are **much more likely** to be genuine (not coincidental), so the distances are meaningful.

---

## 4. Index of Coincidence (IC)

### What Is IC?

The **Index of Coincidence** measures how likely it is that two randomly chosen letters from a text are the same. It's a statistical fingerprint of a language.

### Formula

For a text of `N` letters where `n_i` is the count of the i-th letter (A=0, B=1, ..., Z=25):

```
             25
IC  =   Σ   n_i × (n_i - 1)
            i=0
        ─────────────────────
           N × (N - 1)
```

### Key IC Values

| Text Type               | IC Value  |
|--------------------------|-----------|
| English plaintext        | **~0.0667** (≈ 1/15) |
| Random/uniform letters   | **~0.0385** (= 1/26) |
| Vigenère ciphertext (whole) | Between 0.038 and 0.067 |
| Single Caesar group      | **~0.0667** (same as English!) |

### How IC Helps Find Key Length

If we guess key length `m` and split the ciphertext into `m` groups:
- **Correct guess**: Each group was encrypted with one shift → IC ≈ 0.065–0.068 (English-like)
- **Wrong guess**: Groups contain letters from different shifts → IC ≈ 0.038–0.045 (flat/random-like)

### Algorithm

```
For each candidate key length m = 2, 3, 4, ..., 20:
    Split ciphertext into m groups (group_j = every m-th letter starting at position j)
    Calculate IC for each group
    Average the ICs across all m groups
    
The value of m that gives the highest average IC (closest to 0.0667) is the key length
```

### Example Calculation

Text: "AABBC" (N = 5)
- n_A = 2, n_B = 2, n_C = 1, all others = 0

```
IC = [2×1 + 2×1 + 1×0] / [5×4]
   = [2 + 2 + 0] / 20
   = 4 / 20
   = 0.20
```

This is high because the text has repeated letters (not diverse).

---

## 5. Splitting Ciphertext into Groups

Once we have a candidate key length `m`, we split the cleaned ciphertext into `m` groups:

```
Given ciphertext: C_0, C_1, C_2, C_3, C_4, C_5, C_6, C_7, ...
Key length m = 3

Group 0: C_0, C_3, C_6, C_9,  ...  (positions ≡ 0 mod 3)
Group 1: C_1, C_4, C_7, C_10, ...  (positions ≡ 1 mod 3)
Group 2: C_2, C_5, C_8, C_11, ...  (positions ≡ 2 mod 3)
```

Each group contains letters all encrypted with the **same key letter** → same Caesar shift → frequency analysis works!

### Python Pseudocode

```python
def split_into_groups(ciphertext: str, key_length: int) -> list[str]:
    groups = ['' for _ in range(key_length)]
    for i, char in enumerate(ciphertext):
        groups[i % key_length] += char
    return groups
```

---

## 6. Per-Group Frequency Analysis — Finding Each Shift

### The Chi-Squared Method

For each group, we want to find which Caesar shift (0–25) best matches English frequency. We use the **chi-squared statistic** (χ²):

```
         25    (O_i - E_i)²
χ²  =   Σ    ─────────────
        i=0       E_i

Where:
    O_i = observed count of letter i in the group
    E_i = expected count = (English frequency of letter i) × (group length)
```

**Lower χ² = better match** (observed matches expected).

### Algorithm for One Group

```
For each candidate shift s = 0, 1, 2, ..., 25:
    "Decrypt" the group by shifting back by s
    Count letter frequencies in the "decrypted" group
    Compute chi-squared against English letter frequencies
    
The shift s with the LOWEST chi-squared value is the most likely key letter
```

### English Letter Frequencies (Reference)

```
A: 8.167%    B: 1.492%    C: 2.782%    D: 4.253%    E: 12.702%
F: 2.228%    G: 2.015%    H: 6.094%    I: 6.966%    J: 0.153%
K: 0.772%    L: 4.025%    M: 2.406%    N: 6.749%    O: 7.507%
P: 1.929%    Q: 0.095%    R: 5.987%    S: 6.327%    T: 9.056%
U: 2.758%    V: 0.978%    W: 2.360%    X: 0.150%    Y: 1.974%
Z: 0.074%
```

### Alternative: Dot-Product / Correlation Method

Instead of chi-squared, you can correlate the group's frequency distribution with the English distribution:

```
For each shift s = 0, 1, 2, ..., 25:
    correlation = Σ (freq_of_letter_i_in_shifted_group × english_freq_i)
    
The shift with the HIGHEST correlation is the best match
```

Both methods give equivalent results for well-behaved ciphertexts.

### Worked Example

Suppose Group 0 has this letter distribution (most frequent first):
```
W: 12.5%,  L: 9.8%,  H: 8.3%,  ...
```

English expects: `E: 12.7%, T: 9.1%, A: 8.2%, ...`

The most frequent letter `W` likely corresponds to `E`.
- W = 22, E = 4
- Shift = (22 - 4) mod 26 = **18** → Key letter = `S` (index 18)

We verify with chi-squared: shifting all letters in the group back by 18 and checking if the distribution matches English.

---

## 7. Recovering the Full Key

After finding the shift for each group, we combine them:

```
Group 0 → shift 11 → Key letter: L
Group 1 → shift 4  → Key letter: E
Group 2 → shift 12 → Key letter: M
Group 3 → shift 14 → Key letter: O
Group 4 → shift 13 → Key letter: N

Key = "LEMON"
```

The shift value directly maps to a letter: shift 0 = A, shift 1 = B, ..., shift 25 = Z.

---

## 8. Decryption & Verification

### Decryption

```
For each ciphertext letter C_i:
    j = i mod m          (which key letter to use)
    P_i = (C_i - K_j + 26) mod 26
```

### Verification (Re-encryption)

To verify correctness:
```
1. Take the recovered plaintext
2. Re-encrypt it using the recovered key
3. Compare with the original ciphertext
4. If they match → key is correct!
```

This is the final sanity check that closes the loop.

---

## 9. Worked Example (Mini)

### Setup

- **Plaintext**: `ATTACKATDAWN`
- **Key**: `LEMON` (length 5)

### Encryption

| Position | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 | 11 |
|----------|----|----|----|----|----|----|----|----|----|----|----|----|
| Plain    | A  | T  | T  | A  | C  | K  | A  | T  | D  | A  | W  | N  |
| P_i      | 0  | 19 | 19 | 0  | 2  | 10 | 0  | 19 | 3  | 0  | 22 | 13 |
| Key      | L  | E  | M  | O  | N  | L  | E  | M  | O  | N  | L  | E  |
| K_j      | 11 | 4  | 12 | 14 | 13 | 11 | 4  | 12 | 14 | 13 | 11 | 4  |
| C_i      | 11 | 23 | 5  | 14 | 15 | 21 | 4  | 5  | 17 | 13 | 7  | 17 |
| Cipher   | L  | X  | F  | O  | P  | V  | E  | F  | R  | N  | H  | R  |

**Ciphertext**: `LXFOPVEFRNH R`

### Breaking It (Kasiski + Frequency)

In a real attack on longer ciphertext:
1. Find repeated trigrams → compute distances → GCD suggests key length ≈ 5
2. Split into 5 groups
3. Each group's frequency matches English when shifted by the right amount
4. Recover key: L, E, M, O, N → "LEMON"
5. Decrypt and verify!

---

## 10. Our Ciphertext (Group 1 — Odd)

This is the ciphertext we will be attacking:

```
DAZFI SFSPA VQLSN PXYSZ WXALC DAFGQ UISMT PHZGA
MKTTF TCCFX KFCRG GLPFE TZMMM ZOZDE ADWVZ WMWKV
GQSOH QSVHP WFKLS LEASE PWHMJ EGKPU RVSXJ XVBWV
POSDE TEQTX OBZIK WCXLW NUOVJ MJCLL OEOFA ZENVM
JILOW ZEKAZ EJAQD ILSWW ESGUG KTZGQ ZVRMN WTQSE
OTKTK PBSTA MQVER MJEGL JQRTL GFJYG SPTZP GTACM
OECBX SESCI YGUFP KVILL TWDKS ZODFW FWEAA PQTFS
TQIRG MPMEL RYELH QSVWB AWMOS DELHM UZGPG YEKZU
KWTAM ZJMLS EVJQT GLAWV OVVXH KWQIL IEUYS ZWXAH
HUSZO GMUZQ CIMVZ UVWIF JJHPW VXFSE TZEDF
```

**Cleaned** (spaces removed): 400 characters

Our program will:
1. Clean this ciphertext
2. Find repeated trigrams and their distances (Kasiski)
3. Use IC to confirm/refine the key length
4. Split into groups and frequency-analyse each
5. Recover the key and decrypt
6. Verify by re-encrypting

---

## Summary of the Attack Pipeline

```
┌─────────────────────────────────────────────┐
│  Raw Ciphertext                             │
│  "DAZFI SFSPA VQLSN ..."                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 1: clean_ciphertext()                 │
│  Remove spaces, normalize to uppercase      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 2: Kasiski Examination                │
│  find_repeated_patterns()                   │
│  calculate_distances()                      │
│  find_factors()                             │
│  kasiski_analysis() → candidate key lengths │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 3: Confirm with IC                    │
│  For each candidate m:                      │
│    split_into_groups(m)                     │
│    calculate_ic() for each group            │
│    average IC → pick best m                 │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 4: Break Each Group                   │
│  For group j = 0..m-1:                      │
│    frequency_analysis(group_j)              │
│    find_shift(group_j) → shift_j            │
│  find_key() = shift_0..shift_m-1            │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Step 5: Decrypt & Verify                   │
│  vigenere_decrypt(ciphertext, key)          │
│  vigenere_encrypt(plaintext, key)           │
│  verify() → match? ✓ or ✗                  │
└─────────────────────────────────────────────┘
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **Polyalphabetic cipher** | A cipher using multiple substitution alphabets |
| **Key length (m)** | Number of letters in the Vigenère keyword |
| **Kasiski examination** | Finding key length by analysing repeated ciphertext patterns |
| **Index of Coincidence (IC)** | Probability that two random letters from a text are identical |
| **Chi-squared (χ²)** | Statistical measure of how well observed data matches expected |
| **Caesar shift** | Each group in Vigenère behaves as a Caesar cipher with one shift |
| **GCD** | Greatest Common Divisor — used to find common factors of distances |

---

*Group 01 — Nishant (2024UCP1773) & Lokesh Saini (2024UCP1505)*
