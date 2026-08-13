# SAST Analysis Report — ATM System (Lab 3)
## CryptoLabX Group 01 | 22CPP307 Cryptography Laboratory

> **Tool:** Bandit v1.6.2
> **Group:** 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)
> **Scan Date:** 2026-08-13
> **Scan Command:** `bandit -r Secure_Application/src/ -o Secure_Application/sast/bandit_report_lab3.txt -f txt`

---

## 1. Application Overview

The ATM System is a console-based Python application that simulates core banking operations. It is built with **4 modules**, and contains **3 deliberate vulnerability categories** for SAST demonstration purposes.

| Module | Role |
|--------|------|
| `atm.py` | Entry point — banner, login loop, authenticated menu |
| `auth.py` | Login and PIN change logic |
| `account.py` | Balance inquiry, withdrawal, deposit |
| `database.py` | In-memory account store — hardcoded data |

---

## 2. Scan Summary

| Metric | Value |
|--------|-------|
| Total issues detected | 6 |
| High Severity | 2 |
| Medium Severity | 0 |
| Low Severity | 4 |
| High Confidence | 4 |
| Medium Confidence | 2 |
| Low Confidence | 0 |

---

## 3. Detailed Findings

---

### Finding 1 — Hardcoded Password String (B105) — ADMIN_PASSWORD

| Field | Detail |
|-------|--------|
| **Rule ID** | B105 — `hardcoded_password_string` |
| **File** | `Secure_Application/src/database.py` |
| **Severity** | Low |
| **Confidence** | Medium |
| **CWE** | CWE-259 — Use of Hard-coded Password |
| **Code** | `ADMIN_PASSWORD = "admin@123"` |

**Explanation:**
Hardcoded credentials embedded directly in source code are immediately readable by anyone with access to the repository. Since the source code is version-controlled on GitHub, the admin password `admin@123` is publicly exposed. This also means rotating the password requires a code change and redeployment.

**Remediation:**
Store credentials in environment variables and access them via `os.environ.get("ADMIN_PASSWORD")`. Use a secrets management tool (e.g., HashiCorp Vault, AWS Secrets Manager) in production environments.

---

### Finding 2 — Hardcoded Password String (B105) — SECRET_KEY

| Field | Detail |
|-------|--------|
| **Rule ID** | B105 — `hardcoded_password_string` |
| **File** | `Secure_Application/src/database.py` |
| **Severity** | Low |
| **Confidence** | Medium |
| **CWE** | CWE-259 |
| **Code** | `SECRET_KEY = "atm_secret_99"` |

**Explanation:**
Same issue as Finding 3. A secret key hardcoded in source is compromised as soon as the code is shared or committed. Secret keys are typically used for signing tokens or encrypting data — their exposure nullifies any security they provide.

**Remediation:**
Load via `os.environ.get("ATM_SECRET_KEY")` and set it in the deployment environment, not in source code.

---

### Finding 3 — Weak MD5 Hash for PIN (B324) — Account 1001234567

| Field | Detail |
|-------|--------|
| **Rule ID** | B324 — `hashlib` (weak hash) |
| **File** | `Secure_Application/src/database.py` |
| **Severity** | **High** |
| **Confidence** | High |
| **CWE** | CWE-327 — Use of a Broken or Risky Cryptographic Algorithm |
| **Code** | `"pin_hash": hashlib.md5(b"1234").hexdigest()` |

**Explanation:**
MD5 is a cryptographically broken hash function. It was deprecated for security purposes over a decade ago due to its susceptibility to collision attacks and preimage attacks. Using MD5 to store or verify PINs provides almost no security — rainbow table lookups can reverse common 4-digit PINs (like `1234`) in milliseconds.

**Remediation:**
Use `hashlib.sha256()` with a random salt, or better, use the `bcrypt` or `argon2` libraries specifically designed for password/PIN hashing. Example:
```python
import hashlib, os
salt = os.urandom(16)
pin_hash = hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100000)
```

---

### Finding 4 — Weak MD5 Hash for PIN (B324) — Account 1009876543

| Field | Detail |
|-------|--------|
| **Rule ID** | B324 — `hashlib` (weak hash) |
| **File** | `Secure_Application/src/database.py` |
| **Severity** | **High** |
| **Confidence** | High |
| **CWE** | CWE-327 |
| **Code** | `"pin_hash": hashlib.md5(b"4321").hexdigest()` |

**Explanation:**
Identical issue as Finding 5, applied to the second test account. Both user PINs are stored as unsalted MD5 hashes — a known insecure practice flagged by OWASP, NIST, and all major security frameworks.

**Remediation:**
Same as Finding 5 — replace MD5 with a proper key derivation function (KDF) such as PBKDF2, bcrypt, or Argon2.

---

## 4. Vulnerabilities NOT Detected by Bandit (Manual Analysis)

Bandit is a static analyser — it detects code patterns, not runtime behaviour. The following two deliberate vulnerabilities required manual code review to identify:

### VULN-2 — Improper Input Validation (CWE-20)
- **Location:** `account.py` — `withdraw()`, `deposit()`
- **Issue:** `float(raw)` accepts negative numbers. Entering `-500` as a withdrawal amount passes the overdraft check (`-500 > balance` is False) and *increases* the balance.
- **Bandit Detection:** ❌ Not detected — this is a logic flaw, not a dangerous API call

### VULN-3 — Information Leakage via Error Messages (CWE-209)
- **Location:** `auth.py` — `print(traceback.format_exc())`; `auth.py` — PIN echoed in confirmation
- **Issue:** Full Python tracebacks leaked to the terminal on login failure; new PIN printed in plaintext after change
- **Bandit Detection:** ❌ Not detected — `traceback` usage is not flagged as inherently insecure

---

## 6. Conclusion

Bandit successfully identified **4 issues** across the 263-line ATM codebase, covering the **Hardcoded Credentials (VULN-1)** and **Weak Cryptography** vulnerability categories with High confidence. The two remaining deliberate vulnerabilities (**VULN-2** input validation and **VULN-3** information leakage) were not detected by Bandit, demonstrating the inherent limitation of static analysis tools — they cannot reason about runtime data flow or business logic flaws.

This exercise illustrates why SAST should be used **in combination** with Dynamic Application Security Testing (DAST), code reviews, and penetration testing for comprehensive security assurance.

