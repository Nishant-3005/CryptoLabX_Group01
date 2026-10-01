# Padding Oracle Attack — Theory Guide
## AES-CBC Mode, PKCS#7 Padding, and the Padding Oracle Vulnerability
### CryptoLabX Group 01 | 22CPP307

---

## Table of Contents

1. [AES Block Cipher — The Foundation](#1-aes-block-cipher--the-foundation)
2. [CBC Mode of Operation](#2-cbc-mode-of-operation)
3. [PKCS#7 Padding](#3-pkcs7-padding)
4. [What Is a Padding Oracle?](#4-what-is-a-padding-oracle)
5. [The Padding Oracle Attack — Step by Step](#5-the-padding-oracle-attack--step-by-step)
6. [Mathematical Foundation — Why Modifying C' Works](#6-mathematical-foundation--why-modifying-c-works)
7. [Worked Example — Recovering One Byte](#7-worked-example--recovering-one-byte)
8. [Full Block Recovery Algorithm](#8-full-block-recovery-algorithm)
9. [Query Complexity](#9-query-complexity)
10. [Prevention & Countermeasures](#10-prevention--countermeasures)
11. [Our Implementation Plan](#11-our-implementation-plan)

---

## 1. AES Block Cipher — The Foundation

**AES (Advanced Encryption Standard)** is a symmetric block cipher that operates on fixed-size blocks of **16 bytes (128 bits)**.

```
Key sizes:  128, 192, or 256 bits
Block size: 128 bits (16 bytes) — always
```

AES by itself is a **single-block** function:
```
Encrypt:  C = AES_K(P)     — 16 bytes in, 16 bytes out
Decrypt:  P = AES_K⁻¹(C)   — 16 bytes in, 16 bytes out
```

To encrypt messages **longer than 16 bytes**, we need a **mode of operation** — the most common (and vulnerable) being CBC.

---

## 2. CBC Mode of Operation

### Encryption (CBC)

**CBC = Cipher Block Chaining**. Each plaintext block is XORed with the **previous ciphertext block** before encryption:

```
C_0 = AES_K(P_0 ⊕ IV)           — first block uses IV
C_i = AES_K(P_i ⊕ C_{i-1})      — subsequent blocks chain
```

Where:
- `IV` = Initialization Vector (random, sent alongside ciphertext)
- `⊕` = XOR (bitwise exclusive OR)
- `C_i` = i-th ciphertext block
- `P_i` = i-th plaintext block

### Decryption (CBC)

```
P_0 = AES_K⁻¹(C_0) ⊕ IV
P_i = AES_K⁻¹(C_i) ⊕ C_{i-1}
```

**Key insight for the attack**: The plaintext of block `i` depends on **two** things:
1. The AES decryption of `C_i` (which we can't control — we don't have the key)
2. The XOR with `C_{i-1}` (which we **CAN** control by modifying bytes in the previous block!)

### Diagram

```
Encryption:
  P_0 ──⊕──► AES_K ──► C_0 ──⊕──► AES_K ──► C_1 ──⊕──► AES_K ──► C_2
         ▲                    ▲                    ▲
         IV                  C_0                  C_1

Decryption:
  C_0 ──► AES_K⁻¹ ──⊕──► P_0    C_1 ──► AES_K⁻¹ ──⊕──► P_1
                     ▲                              ▲
                     IV                            C_0
```

---

## 3. PKCS#7 Padding

Since AES works on 16-byte blocks, the plaintext must be padded to a multiple of 16. **PKCS#7** is the standard:

### Rule

If `n` bytes of padding are needed (1 ≤ n ≤ 16):
- Append `n` bytes, each with the **value** `n`.

### Examples

```
Plaintext: "HELLO"         (5 bytes) → needs 11 bytes padding
Padded:    "HELLO" + 0x0B 0x0B 0x0B 0x0B 0x0B 0x0B 0x0B 0x0B 0x0B 0x0B 0x0B

Plaintext: "HELLO WORLD!!!!" (16 bytes) → needs 16 bytes padding (full block!)
Padded:    "HELLO WORLD!!!!" + 0x10 × 16

Plaintext: "HELLO WORLD!!!" (15 bytes) → needs 1 byte padding
Padded:    "HELLO WORLD!!!" + 0x01

Plaintext: "HELLO WORLD!!"  (14 bytes) → needs 2 bytes padding
Padded:    "HELLO WORLD!!"  + 0x02 0x02
```

### Validation

On decryption, the receiver:
1. Looks at the **last byte** of the decrypted block → value `v`
2. Checks that the last `v` bytes are ALL equal to `v`
3. If yes → **valid padding** → strip and return plaintext
4. If no → **invalid padding** → return error

### Valid vs Invalid Examples

```
... 0x04 0x04 0x04 0x04     ← VALID (last 4 bytes are all 0x04)
... 0x04 0x04 0x04 0x03     ← INVALID (expected 0x03 0x03 0x03, got wrong prefix)
... 0x00                     ← INVALID (0x00 is not a valid pad value)
... 0x01                     ← VALID (last 1 byte is 0x01)
```

---

## 4. What Is a Padding Oracle?

A **padding oracle** is any system that tells you whether the padding of a decrypted ciphertext is **valid or invalid**. The system doesn't need to tell you the plaintext — it just needs to give a **different response** for valid vs. invalid padding.

### Real-World Examples

| System Behavior | Oracle? |
|----------------|---------|
| Server returns HTTP 200 for valid, HTTP 500 for invalid | ✅ Yes |
| Error message says "Invalid padding" vs. "Decryption failed" | ✅ Yes |
| Response takes 50ms for valid, 200ms for invalid (timing) | ✅ Yes |
| Server always returns same error regardless | ❌ No oracle |

### Why This Is Dangerous

The oracle lets an attacker **recover the entire plaintext** byte-by-byte without knowing the key. They only need:
- The ciphertext (including IV)
- Access to the oracle function

The key is **never** accessed or used by the attacker.

---

## 5. The Padding Oracle Attack — Step by Step

### Goal

Given ciphertext blocks `[IV, C_0, C_1, ..., C_n]` and access to a padding oracle, recover all plaintext blocks `P_0, P_1, ..., P_n`.

### The Attack Targets One Block at a Time

To attack block `C_i`:
1. We create a **modified** copy of the previous block: `C'_{i-1}`
2. We send `[C'_{i-1}, C_i]` to the oracle
3. The oracle decrypts: `P'_i = AES_K⁻¹(C_i) ⊕ C'_{i-1}`
4. If padding is valid, we learn something about `AES_K⁻¹(C_i)` — the **intermediate value**

### The Key Equation

Let `I_i = AES_K⁻¹(C_i)` be the **intermediate value** (the AES decryption output before XOR).

```
Original:    P_i[j] = I_i[j] ⊕ C_{i-1}[j]
Modified:    P'_i[j] = I_i[j] ⊕ C'_{i-1}[j]
```

If we find a `C'_{i-1}[j]` that makes the padding valid, we can deduce `I_i[j]`, and then:

```
I_i[j] = P'_i[j] ⊕ C'_{i-1}[j]
P_i[j] = I_i[j] ⊕ C_{i-1}[j]     ← the REAL plaintext byte!
```

---

## 6. Mathematical Foundation — Why Modifying C' Works

### Recovering the Last Byte (Position 15)

We want the padding `\x01` (valid 1-byte padding). We try all 256 values for `C'_{i-1}[15]`:

```
For g = 0, 1, 2, ..., 255:
    Set C'_{i-1}[15] = g
    Send [C'_{i-1}, C_i] to oracle
    
    Oracle decrypts:
        I_i[15] = AES_K⁻¹(C_i)[15]     (fixed, unknown)
        P'_i[15] = I_i[15] ⊕ g
    
    If oracle says VALID:
        P'_i[15] = 0x01  (most likely — 1-byte padding)
        Therefore: I_i[15] = 0x01 ⊕ g
        Therefore: P_i[15] = I_i[15] ⊕ C_{i-1}[15]
                            = (0x01 ⊕ g) ⊕ C_{i-1}[15]
```

### Recovering Byte 14 (Second from Last)

Now we know `I_i[15]`. We want 2-byte padding: `\x02 \x02`

```
Set C'_{i-1}[15] = I_i[15] ⊕ 0x02     (forces P'[15] = 0x02)
For g = 0, 1, 2, ..., 255:
    Set C'_{i-1}[14] = g
    Send to oracle
    
    If VALID:
        P'_i[14] = 0x02
        I_i[14] = 0x02 ⊕ g
        P_i[14] = I_i[14] ⊕ C_{i-1}[14]
```

### General Pattern for Byte Position `j`

Target padding value: `pad = 16 - j`

```
For all already-known bytes k > j:
    Set C'_{i-1}[k] = I_i[k] ⊕ pad     (ensures P'[k] = pad)

For g = 0, 1, ..., 255:
    Set C'_{i-1}[j] = g
    If oracle says VALID:
        I_i[j] = pad ⊕ g
        P_i[j] = I_i[j] ⊕ C_{i-1}[j]
        Break
```

---

## 7. Worked Example — Recovering One Byte

### Setup

```
C_{i-1} = [0x4A, 0x3B, ..., 0x7F]   (16 bytes, original previous block)
C_i     = [0xDE, 0xAD, ..., 0xBE]   (16 bytes, block we're attacking)
I_i     = AES_K⁻¹(C_i) = [??, ??, ..., ??]  (unknown intermediate)
```

### Step 1: Find the Last Byte

We try all 256 values for `C'_{i-1}[15]`:

```
g = 0x00: C'[15] = 0x00, oracle says INVALID
g = 0x01: C'[15] = 0x01, oracle says INVALID
...
g = 0x5C: C'[15] = 0x5C, oracle says VALID ✓
```

When the oracle says valid at `g = 0x5C`:
```
P'_i[15] = 0x01   (1-byte padding)
I_i[15]  = 0x01 ⊕ 0x5C = 0x5D
P_i[15]  = 0x5D ⊕ 0x7F = 0x22 = '"'
```

We recovered the last plaintext byte: `"` (ASCII 0x22)!

### Step 2: Find Byte 14

Now set `C'[15] = I_i[15] ⊕ 0x02 = 0x5D ⊕ 0x02 = 0x5F` (forces P'[15] = 0x02)

Try all 256 values for `C'_{i-1}[14]`:
```
g = 0x00: oracle INVALID
...
g = 0xA3: oracle VALID ✓
```

```
I_i[14]  = 0x02 ⊕ 0xA3 = 0xA1
P_i[14]  = 0xA1 ⊕ C_{i-1}[14]
```

Continue for bytes 13, 12, ..., 0 to recover the entire block.

---

## 8. Full Block Recovery Algorithm

```python
def attack_block(prev_block, target_block, oracle):
    """Recover plaintext of target_block using the padding oracle."""
    intermediate = [0] * 16    # I_i = AES_K⁻¹(target_block)
    plaintext    = [0] * 16
    
    # Recover bytes from right (15) to left (0)
    for byte_pos in range(15, -1, -1):
        pad_value = 16 - byte_pos   # target padding: 0x01, 0x02, ..., 0x10
        
        # Build the crafted previous block
        crafted = [0] * 16
        
        # Set already-known bytes to produce correct padding
        for k in range(byte_pos + 1, 16):
            crafted[k] = intermediate[k] ^ pad_value
        
        # Brute-force the target byte
        for guess in range(256):
            crafted[byte_pos] = guess
            
            # Query the oracle with [crafted, target_block]
            if oracle(bytes(crafted) + bytes(target_block)):
                # Valid padding! Deduce intermediate value
                intermediate[byte_pos] = pad_value ^ guess
                plaintext[byte_pos] = intermediate[byte_pos] ^ prev_block[byte_pos]
                break
    
    return bytes(plaintext)
```

### Multi-Block Attack

```python
def full_attack(iv, ciphertext_blocks, oracle):
    """Recover all plaintext blocks."""
    all_blocks = [iv] + ciphertext_blocks
    plaintext = b""
    
    for i in range(1, len(all_blocks)):
        prev_block = all_blocks[i - 1]
        target_block = all_blocks[i]
        plaintext += attack_block(prev_block, target_block, oracle)
    
    # Remove PKCS#7 padding from last block
    pad_len = plaintext[-1]
    plaintext = plaintext[:-pad_len]
    
    return plaintext
```

---

## 9. Query Complexity

### Per Byte
- Worst case: **256 guesses** (try all possible values)
- Average case: **128 guesses** (on average, hit the right one halfway)

### Per Block (16 bytes)
- Worst case: **256 × 16 = 4,096 oracle queries**
- Average case: **~2,048 queries**

### Per Message (N blocks)
- Worst case: **4,096 × N queries**
- Average case: **~2,048 × N queries**

### Example
A 48-byte message (3 blocks):
- Worst case: 4,096 × 3 = **12,288 queries**
- Average: ~6,144 queries

This is remarkably efficient — the attacker doesn't need the key, yet can recover the entire message with at most a few thousand oracle calls.

---

## 10. Prevention & Countermeasures

### 1. Authenticated Encryption (Best Solution)

Use **AES-GCM** or **ChaCha20-Poly1305** instead of plain AES-CBC. These modes provide:
- Confidentiality (encryption)
- Integrity (authentication tag)
- The tag is verified **before** decryption — no padding oracle is possible

```
AES-GCM: If ciphertext is tampered → tag mismatch → reject immediately
          No decryption happens → no padding information leaks
```

### 2. Encrypt-then-MAC

If you must use CBC:
```
1. Encrypt: C = AES-CBC(K_enc, P)
2. MAC:     T = HMAC-SHA256(K_mac, IV || C)
3. Send:    (IV, C, T)

On receive:
1. Verify:  T' = HMAC-SHA256(K_mac, IV || C)
             If T' ≠ T → reject (no decryption!)
2. Decrypt: P = AES-CBC⁻¹(K_enc, C)
```

### 3. Constant-Time Error Handling

Never leak **which** error occurred:
```python
# BAD — leaks information
if padding_invalid:
    raise PaddingError("Invalid padding")
elif mac_invalid:
    raise MACError("Invalid MAC")

# GOOD — same error for everything
if not verify_and_decrypt(ciphertext):
    raise Error("Decryption failed")  # generic error, constant time
```

### 4. Key Takeaway

> **The vulnerability is not in AES itself, but in how the system communicates error information.** Any observable difference (error codes, timing, behavior) between "valid padding" and "invalid padding" creates an oracle.

---

## 11. Our Implementation Plan

We will build:

| Module | Purpose |
|--------|---------|
| `aes_cbc.py` | AES-CBC encryption/decryption + PKCS#7 padding (uses `pycryptodome`) |
| `padding_oracle.py` | Simulated padding oracle (returns True/False for valid padding) |
| `attack.py` | The padding oracle attack — recovers plaintext without the key |
| `main.py` | Orchestrator — encrypts a message, runs the attack, displays results |

The attack must:
1. **Not access the AES key** — only the oracle function
2. **Not use a ready-made attack library** — implement from scratch
3. **Work for any plaintext** — not hardcoded to specific content

---

## Glossary

| Term | Definition |
|------|-----------|
| **AES** | Advanced Encryption Standard — 128-bit block cipher |
| **CBC** | Cipher Block Chaining — mode where each block is XORed with the previous ciphertext |
| **IV** | Initialization Vector — random value used for the first block |
| **PKCS#7** | Padding standard: append `n` bytes each of value `n` |
| **Padding Oracle** | Any system that reveals whether decrypted padding is valid |
| **Intermediate Value** | `I_i = AES_K⁻¹(C_i)` — the AES output before the CBC XOR |
| **XOR (⊕)** | Bitwise exclusive OR — the fundamental operation exploited |
| **GCM** | Galois/Counter Mode — authenticated encryption (prevents this attack) |

---

*Group 01 — Nishant (2024UCP1773) & Lokesh Saini (2024UCP1505)*
