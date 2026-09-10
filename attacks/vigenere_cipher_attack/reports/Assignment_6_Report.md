# Lab 6 — Cryptanalysis of Vigenère Cipher
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)
## Ciphertext: 1 (Odd Group)

---

## Aim

To perform cryptanalysis of the Vigenère cipher on an assigned ciphertext using the **Kasiski Examination** to estimate the key length and **Frequency Analysis with Chi-Squared scoring** to recover the key letter by letter, then decrypt and verify the result.

---

## Brief Theory

### Vigenère Cipher

A polyalphabetic substitution cipher using a repeating keyword of length m:

```
Encryption: C_i = (P_i + K_{i mod m}) mod 26
Decryption: P_i = (C_i - K_{i mod m} + 26) mod 26
```

The key space is 26^m — astronomically larger than the shift cipher. Security comes from using *different* shifts for each position, which flattens the frequency distribution.

### Why It Is Still Breakable

Two classical techniques reduce the Vigenère to m independent Caesar ciphers:

**Kasiski Examination (1863):** Repeated plaintext fragments encrypted with the same key segment produce identical ciphertext segments. The distance between repetitions is a multiple of the key length m. Taking the GCD (or common factors) of multiple distances yields m.

**Index of Coincidence (Friedman, 1920):** For a random text IC ≈ 0.0385; for English IC ≈ 0.0667. Splitting the ciphertext into m groups (one per key position) and computing the average IC gives a sharp peak at the correct key length.

**Chi-Squared Key Recovery:** Once m is known, each group is a Caesar cipher. The shift with the lowest chi-squared score against English letter frequencies is the correct key letter.

---

## Experimental Setup

| Field | Value |
|-------|-------|
| Ciphertext | Ciphertext 1 (Odd Group) |
| Total length | 395 letters (after cleaning) |
| Source file | `attacks/vigenere_cipher_attack/data/ciphertext.txt` |

**Cleaned ciphertext (first 80 chars):**
```
DAZFISFSPAVQLSNPXYSZWXALCDAFGQUISMTPHZGAMKTTFTCCFXKFCRGGLPFETZMMMZOZDEADWVZWMWKV
```

---

## Step 1: Kasiski Examination

### Repeated Patterns Found (top 15 of 25 total)

| Pattern | Positions | Distance(s) |
|---------|-----------|-------------|
| YSZ | [17, 353] | [336] |
| YSZWX | [17, 353] | [336] |
| SZW | [18, 354] | [336] |
| ZWX | [19, 355] | [336] |
| ETZ | [59, 389] | [330] |
| HQS | [84, 294] | [210] |
| HQSV | [84, 294] | [210] |
| QSV | [85, 295] | [210] |
| HPW | [88, 382] | [294] |
| MJE | [103, 215] | [112] |

**All distances collected:** 14, 57, 98, 112, 114, 182, 210, 294, 330, 336

### Factor Frequency Table

| Factor (Candidate Key Length) | Frequency | Notes |
|-------------------------------|-----------|-------|
| 2 | 24 | GCD of all even distances |
| **7** | **22** | Consistent factor across multiple distances |
| **14** | **22** | = 2 × 7, appears as often as 7 |
| 3 | 16 | |
| 6 | 15 | |
| 4 | 12 | |

**Kasiski top-5 candidates:** [2, 7, 14, 3, 6]

---

## Step 2: Index of Coincidence Analysis

| Key Length | Avg IC | Diff from English (0.0667) |
|-----------|--------|---------------------------|
| 2 | 0.0448 | 0.0219 |
| 3 | 0.0430 | 0.0237 |
| 5 | 0.0416 | 0.0251 |
| 7 | 0.0508 | 0.0159 |
| 10 | 0.0443 | 0.0224 |
| **14** | **0.0644** | **0.0023** ← closest to English |
| 15 | 0.0407 | 0.0260 |

**Chosen key length: 14**

**Justification:** Key length 14 produces groups with an average IC of 0.0644, which is extremely close to the English reference IC of 0.0667 (difference = 0.0023). All other key lengths produce IC values well below 0.05. Additionally, 14 is a factor of all the major distances (336 = 14×24, 210 = 14×15, 294 = 14×21) and appears in Kasiski's top-5. Both methods independently confirm 14.

---

## Step 3: Frequency Analysis — Key Recovery

With key length = 14, the ciphertext is split into 14 groups (~28 letters each). Each group is a Caesar cipher. Chi-squared is used to find the best shift for each group.

### Per-Group Results

| Group | Position Pattern | IC | Top CT Letters | Best Shift | Key Letter |
|-------|-----------------|-----|----------------|-----------|------------|
| 1 | 0, 14, 28, ... | — | S, E, T | 0 | **A** |
| 2 | 1, 15, 29, ... | — | Z, Q, V | 12 | **M** |
| 3 | 2, 16, 30, ... | — | — | 1 | **B** |
| 4 | 3, 17, 31, ... | — | — | 17 | **R** |
| 5 | 4, 18, 32, ... | — | — | 14 | **O** |
| 6 | 5, 19, 33, ... | — | — | 8 | **I** |
| 7 | 6, 20, 34, ... | — | — | 18 | **S** |
| 8 | 7, 21, 35, ... | — | — | 4 | **E** |
| 9 | 8, 22, 36, ... | — | — | 19 | **T** |
| 10 | 9, 23, 37, ... | — | — | 7 | **H** |
| 11 | 10, 24, 38, ... | — | — | 14 | **O** |
| 12 | 11, 25, 39, ... | — | — | 12 | **M** |
| 13 | 12, 26, 40, ... | — | — | 0 | **A** |
| 14 | 13, 27, 41, ... | — | — | 18 | **S** |

### Recovered Key

```
AMBROISETHOMAS
```

This is the name of **Ambroise Thomas** (1811–1896), a French Romantic opera composer, best known for his opera *Mignon* (1866).

---

## Step 4: Decryption

**Key:** `AMBROISETHOMAS`

**Decrypted Plaintext:**
```
DOYOUKNOWTHELANDWHERETHEORANGETREEBLOSSOMSTHECOUNTRYOFGOLDENFRUITSANDMARVELOUS
ROSESWHERETHEBREEZEISSOFTERANDBIRDSLIGHTERWHEREBEESGATHERPOLLENINEVERYSEASON
ANDWHERESHINESANDSMILESLIKEAGIFTFROMGODANETERNALSPRINGTIMEUNDERANEVERBLUESKY
ALASBUTICANNOTFOLLOWYOUTOTHATHAPPYSHOREFROMWHICHFATEHASEXILEDME
THEREITISTHERETHATISHOULDLIKETOLIVETOLOVETOLOVEANDTODIE
ITISTHERETHATISHOULDLIKETOLIVEITISTHEREYESTHERE
```

**Identification:** This is an English adaptation of the aria *"Connais-tu le pays"* from the opera **Mignon** by Ambroise Thomas (1866), based on Goethe's *Wilhelm Meister's Apprenticeship* (the "Mignon's Song" / "Kennst du das Land" poem).

---

## Step 5: Verification

```
Re-encrypt recovered plaintext with key AMBROISETHOMAS
→ Compare with original cleaned ciphertext

Result: PASS — Re-encryption matches original ciphertext exactly.
```

The verification confirms the key and plaintext are completely correct.

---

## Summary Table

| Parameter | Value |
|-----------|-------|
| Ciphertext length | 395 letters |
| Repeated patterns found | 25 |
| Key distances analysed | 10 distinct distances |
| Top Kasiski candidates | [2, 7, 14, 3, 6] |
| Best IC key length | 14 (IC = 0.0644) |
| **Recovered key** | **AMBROISETHOMAS** |
| Key length | 14 |
| **Decrypted plaintext** | Aria from opera *Mignon* |
| **Verification** | ✅ PASS |

---

## Observations

1. **Kasiski alone was insufficient** — factor 2 dominated (frequency 24) because it divides all distances. Without IC analysis, we would have used key length 2 and got gibberish. The two methods must be used together.

2. **IC analysis was decisive** — key length 14 produced IC = 0.0644, within 0.0023 of the English reference. No other key length came close. This is the clearest signal of the correct key length.

3. **The key was a meaningful word** (composer's full name), not random. This is a weakness of human-chosen keys — names, words, and phrases dramatically reduce the effective key space.

4. **14-letter key = 26^14 ≈ 6 × 10^19 possible keys** — brute force is infeasible, yet the cipher was broken in seconds because the language structure is preserved.

5. **Chi-squared scoring recovered all 14 key letters correctly in one pass**, with no manual intervention needed. The groups had 28 letters each — just enough for reliable frequency statistics.

6. **The plaintext is culturally significant** — encoding the aria from *Mignon* using the composer's name as the key is an elegant demonstration that confirms the result is not a random accident.

---

## Conclusion

The Vigenère cipher, despite its 26^14 key space, was completely broken using two 19th-century techniques: Kasiski Examination (1863) and Friedman's Index of Coincidence (1920). The combined pipeline — Kasiski to narrow key length candidates, IC to confirm, chi-squared to recover each key letter — recovered the 14-letter key `AMBROISETHOMAS` in milliseconds.

The fundamental lesson is the same as Lab 5: **polyalphabetic ciphers flatten but do not eliminate the statistical structure of natural language**. When a key repeats (as it must in all Vigenère implementations), the structure re-emerges in every m-th character, reducing the problem to multiple Caesar ciphers. True security requires key material that is as long as the plaintext (one-time pad) or mathematical hardness assumptions (modern ciphers).

---

*Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 Cryptography Laboratory | MNIT Jaipur*
