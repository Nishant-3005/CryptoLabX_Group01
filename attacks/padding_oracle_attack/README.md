# Padding Oracle Attack on AES-CBC
## Lab 7 | CryptoLabX Group 01 | 22CPP307

> **Objective:** Recover plaintext from AES-CBC ciphertext without ever accessing the key  
> **Cipher:** AES-128-CBC with PKCS#7 padding  
> **Result:** Plaintext fully recovered — verification PASS  
> **Oracle queries:** ~15,912 (brute-force 256 × 2 bytes/block × 8 blocks - 1)

---

## Quick Start

```bash
# Install dependency
pip install pycryptodome

# Run the attack
cd attacks/padding_oracle_attack/src
python main.py
```

---

## Folder Structure

```
padding_oracle_attack/
├── src/
│   ├── aes_cbc.py           AES-CBC encrypt/decrypt + PKCS#7 padding
│   ├── padding_oracle.py    Oracle: validates padding without revealing key
│   ├── attack.py            Byte-by-byte plaintext recovery engine
│   └── main.py              Full pipeline orchestrator
├── outputs/
│   └── results.txt          Auto-generated attack results
├── reports/
│   └── Padding_Oracle_Report.md   Full experimental report
└── README.md                This file
```

---

## Source File Summary

| File | Key Functions | Purpose |
|------|---------------|---------|
| `aes_cbc.py` | `encrypt()`, `decrypt()`, `pad()`, `unpad()` | AES-128-CBC with PKCS#7 padding/unpadding |
| `padding_oracle.py` | `PaddingOracle`, `query()` | Simulates real-world oracle: returns True/False for valid padding (key locked inside) |
| `attack.py` | `recover_block()`, `padding_oracle_attack()` | Block-by-block, byte-by-byte plaintext recovery without the key |
| `main.py` | `main()`, `run_attack()`, `save_results()` | Full pipeline: encrypt → attack → verify → display → save |

---

## Attack Method Overview

### Three Phases

```
Phase 1: Setup
  Generate random AES-128 key and IV
  Encrypt target plaintext → ciphertext (n blocks)
  Key is never shared with the attacker

Phase 2: Oracle Creation
  PaddingOracle object holds key internally
  Exposes only: query(iv, ciphertext) → True/False
  True  = decrypted bytes end with valid PKCS#7 padding
  False = padding is invalid
  This single bit of information is enough to break AES-CBC entirely

Phase 3: Byte-by-Byte Attack
  For each block B_i (working backwards from last block):
    For each byte position j (from last byte to first):
      Brute-force all 256 values of a modified byte in B_{i-1}
      Find the value that makes the oracle return True
      This reveals the intermediate decryption value D_j
      XOR with original B_{i-1}[j] → recover plaintext byte P_j
  Repeat for all blocks → full plaintext recovered
```

### Why It Works

AES-CBC decryption: `P_i = Decrypt(C_i) XOR C_{i-1}`

By controlling `C_{i-1}` (the previous ciphertext block), the attacker controls what `Decrypt(C_i)` XORs with. The oracle's padding validity response reveals the exact XOR value needed — and from that, the plaintext byte. No key required.

---

## Results

| Metric | Value |
|--------|-------|
| Plaintext length | 124 bytes |
| AES blocks | 8 (+ 1 padding block) |
| Oracle queries | ~15,912 |
| Plaintext recovered | ✅ PASS |
| Key accessed by attacker | ❌ Never |

---

## Prevention

This attack exploits the fact that AES-CBC **decrypts then checks padding** and **leaks the padding result**. Prevention:

- **Use AES-GCM** — authenticated encryption; ciphertext is rejected before decryption if tampered
- **Encrypt-then-MAC** — compute HMAC over ciphertext; reject on MAC failure before decrypting
- **Never expose padding errors differently from decryption errors** — timing and error message uniformity matter

---

*CryptoLabX Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 | MNIT Jaipur*
