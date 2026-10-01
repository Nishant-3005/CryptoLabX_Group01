# Lab 7 — Padding Oracle Attack on AES-CBC
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)

---

## Aim

To understand and demonstrate how a **Padding Oracle Attack** can recover the complete plaintext from an AES-CBC encrypted message **without knowing the encryption key**, using only a padding validity oracle.

---

## Brief Theory

### AES-CBC Mode

AES-CBC (Cipher Block Chaining) encrypts 16-byte blocks where each plaintext block is XORed with the previous ciphertext block before encryption:

```
Encryption: C_i = AES_K(P_i XOR C_{i-1})       (C_0 uses IV)
Decryption: P_i = AES_K_inv(C_i) XOR C_{i-1}
```

The crucial property: **plaintext of block `i` depends on two things** — the AES decryption of `C_i` (unknown) and the XOR with `C_{i-1}` (controllable by the attacker).

### PKCS#7 Padding

Messages are padded to a multiple of 16 bytes. If `n` bytes of padding are needed, append `n` bytes each with value `n`:
- 1 byte needed: `\x01`
- 4 bytes needed: `\x04\x04\x04\x04`
- 16 bytes needed: `\x10` × 16

On decryption, the receiver validates that the last `v` bytes all equal `v`.

### The Padding Oracle

A padding oracle is any system that reveals whether decrypted padding is valid. This single bit of information (valid/invalid) is sufficient to recover the entire plaintext byte-by-byte.

---

## Experimental Setup

| Field | Value |
|-------|-------|
| Cipher | AES-128-CBC |
| Key size | 128 bits (16 bytes) |
| Block size | 16 bytes |
| Plaintext | "The Padding Oracle Attack demonstrates that even strong ciphers like AES can be broken if the system leaks padding validity." |
| Plaintext length | 124 bytes |
| Padded length | 128 bytes (8 blocks) |
| Padding | PKCS#7 — 4 bytes of `\x04` |

---

## Attack Results

### Recovered Plaintext

```
The Padding Oracle Attack demonstrates that even strong ciphers 
like AES can be broken if the system leaks padding validity.
```

**Verification: PASS** — recovered plaintext matches original exactly.

### Per-Block Recovery

| Block | Oracle Queries | Recovered Text |
|-------|---------------|----------------|
| 1 | ~2,610 | `The Padding Orac` |
| 2 | ~2,709 | `le Attack demons` |
| 3 | ~1,808 | `trates that even` |
| 4 | ~2,288 | ` strong ciphers ` |
| 5 | ~1,446 | `like AES can be ` |
| 6 | ~1,482 | `broken if the sy` |
| 7 | ~1,777 | `stem leaks paddi` |
| 8 | ~1,792 | `ng validity.\x04\x04\x04\x04` |

### Query Statistics

| Metric | Value |
|--------|-------|
| **Total oracle queries** | **~15,912** |
| Queries per block (avg) | ~1,989 |
| Theoretical maximum | 32,768 (256 × 16 × 8) |
| Efficiency | ~48.6% of worst case |

---

## Analysis

### Why Modifying the Previous Ciphertext Block Affects Plaintext

In CBC decryption, the plaintext of block `i` is:

```
P_i = AES_K_inv(C_i) XOR C_{i-1}
```

Let `I_i = AES_K_inv(C_i)` be the **intermediate value** — this is fixed (determined by `C_i` and the key). The attacker cannot compute `I_i` directly because they don't have the key.

However, by creating a modified previous block `C'_{i-1}`, the oracle decrypts:

```
P'_i = I_i XOR C'_{i-1}
```

When the oracle reports valid padding (e.g., `P'_i[15] = 0x01`), the attacker deduces:

```
I_i[15] = 0x01 XOR C'_{i-1}[15]    (known!)
P_i[15] = I_i[15] XOR C_{i-1}[15]  (real plaintext byte!)
```

This process repeats for each byte position (15 down to 0), using progressively longer padding values (`\x02\x02`, `\x03\x03\x03`, etc.).

### Key Insight

The attack exploits the **separation between AES decryption and the XOR step** in CBC. The XOR with the previous block is the only operation the attacker controls, and the oracle reveals whether the result has valid padding — enough to deduce the intermediate value one byte at a time.

---

## Security Recommendations

### 1. Use Authenticated Encryption (Best Practice)

Replace AES-CBC with **AES-GCM** or **ChaCha20-Poly1305**. These modes verify an authentication tag **before** decryption. If the ciphertext is tampered, the tag check fails and no decryption occurs — eliminating the padding oracle entirely.

### 2. Encrypt-then-MAC

If CBC must be used, apply HMAC over the ciphertext:
1. Encrypt: `C = AES-CBC(K_enc, P)`
2. MAC: `T = HMAC(K_mac, IV || C)`
3. Verify MAC **before** decrypting — reject if tampered

### 3. Generic Error Messages

Never distinguish between "invalid padding" and "invalid MAC" errors. Return a single generic "decryption failed" error with constant-time behavior.

### 4. Rate Limiting

Limit oracle queries per session. The attack requires thousands of queries per block — rate limiting makes it impractical.

---

## Conclusion

The Padding Oracle Attack demonstrates a fundamental principle in cryptographic system design: **security depends not only on the cipher's strength but on how error information is communicated**. AES-128 has a 2^128 key space that makes brute force infeasible, yet a single-bit information leak (valid/invalid padding) is sufficient to recover the entire plaintext in approximately 256 × 16 queries per block.

The attack recovered our 124-byte plaintext using ~15,912 oracle queries without ever accessing the AES key. This is a powerful reminder that **authenticated encryption** (AES-GCM) should always be preferred over plain AES-CBC, and that any observable difference in error handling can become a side-channel vulnerability.

---

*Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 Cryptography Laboratory | MNIT Jaipur*
