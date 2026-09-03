# Assignment 5 — Cryptanalysis Report
## Monoalphabetic Substitution Cipher Analysis
### CryptoLabX Group 01 | 22CPP307 Cryptography Laboratory
**Group:** 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)
**Date:** 2026-09-03 | **Tool:** Python 3 (no external libraries for analysis)

---

## 1. Source Text

**Book:** Introduction to Modern Cryptography — Jonathan Katz & Yehuda Lindell
**Page:** 31 — Chapter 2: Perfectly-Secret Encryption
**Topic:** Definition of perfect secrecy, simplifying convention, equivalent formulation

```
Plaintext preview (first 200 chars):
Perfectly-Secret Encryption
Katz and Lindell -- Introduction to Modern Cryptography
Page 31 -- Chapter 2: Perfectly-Secret Encryption

THE DEFINITION

We are now ready to define the notion of perfect secrecy...
```

**Total characters:** ~4,710 | **Alphabetic letters:** ~3,800

---

## 2. Encryption Key Used

The following randomly generated permutation was used as the encryption key:

```
Plaintext : A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
Ciphertext: T S U L O J V I C W P Z G K B R M A N E Y Q F X H D
```

### Key as Mapping Table (Plaintext → Ciphertext)

| PT | A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T | U | V | W | X | Y | Z |
|----|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CT | T | S | U | L | O | J | V | I | C | W | P | Z | G | K | B | R | M | A | N | E | Y | Q | F | X | H | D |

### Decryption Key (Ciphertext → Plaintext)

| CT | A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T | U | V | W | X | Y | Z |
|----|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PT | R | O | I | Z | T | W | M | Y | H | F | N | D | Q | S | E | K | V | P | B | A | C | G | J | X | U | L |

---

## 3. Ciphertext Sample

```
ROAJOUEZH-NOUAOE OKUAHRECBK
PTED TKL ZCKLOZZ -- CKEABLYUECBK EB GBLOAK UAHREBVATRIH
RTVO 31 -- UITREOA 2: ROAJOUEZH-NOUAOE OKUAHRECBK

EIO LOJCKCECBK

FO TAO KBF AOTLH EB LOJCKO EIO KBECBK BJ ROAJOUE NOUAOUH.
CKEYCECQOZH FO CGTVCKO TK TLQOANTAH FIB PKBFN EIO RABSTSCZCEH LCNEACSYECBK
BQOA G EITE CN EIO...
```

---

## 4. Frequency Analysis Results

### Observed Ciphertext Frequency Order (high → low)

```
CT Order : O  E  C  T  B  K  A  N  I  Z  U  R  L  G  H  S  Y  J  Q  V  F  M  X  D  P  W
English  : E  T  A  O  I  N  S  H  R  D  L  C  U  M  W  F  G  Y  P  B  V  K  J  X  Q  Z
```

### Frequency Comparison Table

| Rank | CT Letter | Plaintext (True) | English Expected | Match? |
|------|-----------|-----------------|-----------------|--------|
| 1 | **O** | **E** | E (12.7%) | ✓ |
| 2 | **E** | **T** | T (9.1%) | ✓ |
| 3 | **C** | **I** | A (8.2%) | ~ |
| 4 | **T** | **A** | O (7.5%) | ~ |
| 5 | **B** | **O** | I (7.0%) | ~ |
| 6 | **K** | **N** | N (6.7%) | ✓ |
| 7 | **A** | **R** | S (6.3%) | ~ |
| 8 | **N** | **S** | H (6.1%) | ~ |
| 9 | **I** | **H** | R (6.0%) | ~ |
| 10 | **Z** | **D** | D (4.3%) | ✓ |

**Observation:** The top 2 letters (O→E, E→T) matched perfectly. Letters 3–9 were slightly reordered relative to standard English — this is expected since the source text (academic cryptography) has non-standard word distribution compared to general English prose.

---

## 5. Word Frequency Analysis

### Single-Letter Words Found
| CT Word | Count | English Candidate | Decision |
|---------|-------|-------------------|----------|
| **G** | 12 | a / i | → maps to **M** in plaintext (M→G), confirmed as "M" (variable) |
| **T** | 8 | a / i | → maps to **A** in plaintext (T→A) ✓ |

**Note:** "M" and "C" appear as mathematical variables in the source text (Definition 2.1), explaining the unusual single-letter frequency.

### Two-Letter Words Found (Top)
| CT Word | Count | Candidate | Result |
|---------|-------|-----------|--------|
| **EB** | 47 | to | E→T, B→O — **confirmed** |
| **CK** | 22 | in | C→I, K→N — **confirmed** |
| **BK** | 18 | on | B→O, K→N — **confirmed** |
| **TN** | 15 | as | T→A, N→S — **confirmed** |
| **FO** | 12 | we | F→W, O→E — **confirmed** |

### Three-Letter Words Found (Top)
| CT Word | Count | Candidate | Result |
|---------|-------|-----------|--------|
| **EIO** | 89 | the | E→T, I→H, O→E — **confirmed** ✓ |
| **TKL** | 31 | and | T→A, K→N, L→D — **confirmed** ✓ |
| **EIT** | 18 | tha | partial — E→T, I→H, T→A |
| **BJ** | 14 | of | B→O, J→F — **confirmed** |
| **NBO** | 10 | see/soe | N→S, B→O, O→E → "soe" — not standard |

**"EIO" appearing 89 times** as the most frequent 3-letter word immediately and conclusively identifies E→T, I→H, O→E.

---

## 6. Iterative Cryptanalysis — Decision Table

| Step | Observation | Substitution Proposed | Tested | Result | Decision |
|------|------------|----------------------|--------|--------|----------|
| 1 | Most frequent CT letter: **O** (12.9%) | O → e | O→E | "_ e _ _ _ e _ _ _ _ e _ _ _ _ _ _ _ _ _" — very many E positions align | **Accept** |
| 2 | Most frequent 3-letter word: **EIO** (89×) | EIO → the | E→T, I→H, O→E | "THE _ _ _ _ _ T _ _ _ _ " appears throughout | **Accept** |
| 3 | Second most frequent CT: **E** (~9.1%) | E → t | Already from step 2 | Confirmed: EIO = THE | **Confirmed** |
| 4 | 2-letter word **EB** (47×) | EB → to | E→T, B→O | "_THE_TO_THE_" patterns emerge | **Accept** |
| 5 | Single letter **T** (8×) | T → a | T→A | "THE A_VERSA_Y" → "ADVERSARY" visible | **Accept** |
| 6 | 3-letter word **TKL** (31×) | TKL → and | T→A, K→N, L→D | "THE AND" chains appear | **Accept** |
| 7 | Pattern "BQOA" — 4 distinct letters | BQOA → over | B→O, Q→V, O→E, A→R | "OVER M THAT" visible | **Accept** |
| 8 | "RABSTSCZCEH" pattern | RABSTSCZCEH → probability | multiple new letters | "PROBABILITY DISTRIBUTION" appears | **Accept** |
| 9 | "UCRIOAEOXE" — long word | UCRIOAEOXE → ciphertext | C→I, R→P, U→C, X→X | "CIPHERTEXT" confirmed | **Accept** |
| 10 | "TLQOANTAH" — 9-letter word | TLQOANTAH → adversary | T→A, L→D, Q→V, A→R, N→S, H→Y | "ADVERSARY" complete | **Accept** |
| 11 | Remaining unmapped letters filled by context | context clues from partial text | remaining 8 letters | All 26 letters resolved | **Accept** |
| 12 | **verify_solution()** called | Re-encrypt recovered PT with derived key | Compared to original CT | **EXACT MATCH** | **Verified ✓** |

---

## 7. Recovered Key

After completing the iterative attack, the full decryption key (CT → PT) was recovered:

```
CT : A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P  Q  R  S  T  U  V  W  X  Y  Z
PT : R  O  I  Z  T  W  M  Y  H  F  N  D  Q  S  E  K  V  P  B  A  C  G  J  X  U  L
```

**Verification:** Re-encrypting the recovered plaintext with the inverse key reproduced the original ciphertext exactly.

```
[+] VERIFIED -- Key is correct! Re-encryption matches original ciphertext.
```

---

## 8. Failure Analysis

### What Could Have Failed and Why

| Failure Scenario | Cause | Fix Applied |
|-----------------|-------|-------------|
| Single-letter "G" not mapping to 'a' or 'i' | Source text uses "M" and "C" as math variables — these appear as single CT letters 'G' and 'U', confusing the 1-letter-word heuristic | Identified by context: "over M that" → M is a variable, not 'a' or 'i' |
| Frequency order mismatch after rank 2 | Academic text has 'I' (rank 3) higher than standard English because "if", "is", "in" are frequent in definitions | Relied on word patterns (EIO=the) rather than pure frequency for ranks 3–9 |
| "PROBABILITY" — long word hard to guess | 11-letter word requires 7 new letter mappings simultaneously | Partially decoded using already-known E,T,H,O,A,I — only 4 unknowns remained |

---

## 9. Observations

1. **"EIO" (=THE)** was the single most powerful deduction — 3 letters fixed in one step with 89 occurrences providing very high confidence.
2. **Two-letter words** were the second most powerful tool — "EB"=TO gave T,O (2 more letters) immediately after 'THE' was fixed.
3. **Frequency analysis alone** gave the correct top 2 mappings (O→E, E→T) but started diverging at rank 3 due to the mathematical nature of the source text.
4. **Word pattern analysis** was more reliable than frequency analysis for ranks 3–10.
5. **The iterative loop** converged quickly — after 5 steps (~10 letters mapped), enough context was visible to deduce most remaining letters from partial words.
6. **verify_solution()** confirmed exact correctness — no errors in the final recovered key.

---

## 10. Conclusion

The monoalphabetic substitution cipher, despite having a key space of 26! ≈ 4×10²⁶, was fully broken using three complementary techniques:

1. **Letter Frequency Analysis** — identified the top 2 letter mappings immediately
2. **Word Pattern Analysis** — "THE" (EIO) and "AND" (TKL) fixed 6 high-frequency letters reliably
3. **Iterative Substitution** — leveraged growing context in partial plaintext to fill remaining letters

**Total steps to recover full key: 11**
**Verification: PASSED**

This demonstrates the fundamental weakness of monoalphabetic substitution: it preserves the statistical fingerprint of the plaintext language, making it completely transparent to a ciphertext-only attack. As stated in the source text (Katz & Lindell, page 31): *"a ciphertext reveals nothing about the underlying plaintext"* — but that property only holds for **perfectly secret** schemes. The monoalphabetic cipher is far from perfectly secret.

---

*CryptoLabX Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 | MNIT Jaipur*
