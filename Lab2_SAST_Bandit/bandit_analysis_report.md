# Bandit SAST Analysis Report — CryptoLabX Lab 2
**Tool:** Bandit v1.8.x  
**Target File:** `Secure_Application/insecure.py`  
**Scan Date:** 2026-08-06  
**Analyst:** Nishant (Group 01)

---

## Executive Summary

| Metric | Count |
|---|---|
| Total Issues Found | 10 |
| High Severity | 3 |
| Medium Severity | 2 |
| Low Severity | 5 |
| Lines of Code Scanned | 13 |
| Lines Skipped (`#nosec`) | 0 |
| Confidence Level (all) | High |

---

## Detailed Findings & Remediation

---

### Issue 1 — B404: Import of `subprocess` module
| Field | Detail |
|---|---|
| **Bandit ID** | B404 |
| **Severity** | Low |
| **Confidence** | High |
| **Location** | `insecure.py`, Line 1 |

**Vulnerable Code:**
```python
import subprocess
```

**Why it's risky:**  
The `subprocess` module allows Python to execute system shell commands. If user input is ever passed into a subprocess call (even indirectly), it can lead to **OS Command Injection** — one of the most dangerous vulnerabilities (OWASP A03:2021).

**Remediation:**  
Avoid `subprocess` entirely if not needed. When required, always use it with `shell=False` and pass arguments as a list, never as a string:
```python
# INSECURE
subprocess.call(command, shell=True)

# SECURE
subprocess.run(["ls", "-la"], shell=False)
```

---

### Issue 2 — B403: Import of `pickle` module
| Field | Detail |
|---|---|
| **Bandit ID** | B403 |
| **Severity** | Low |
| **Confidence** | High |
| **Location** | `insecure.py`, Line 3 |

**Vulnerable Code:**
```python
import pickle
```

**Why it's risky:**  
`pickle` deserializes arbitrary Python objects. A maliciously crafted pickle payload can execute any Python code on the host machine during deserialization — this is a known **Remote Code Execution (RCE)** vector.

**Remediation:**  
Never deserialize data from untrusted sources using `pickle`. Use safe alternatives:
```python
# SECURE alternative for structured data
import json
data = json.loads(user_input)   # JSON cannot execute code
```

---

### Issue 3 — B322: Use of `input()` (Python 2 concern flagged)
| Field | Detail |
|---|---|
| **Bandit ID** | B322 |
| **Severity** | High |
| **Confidence** | High |
| **Location** | `insecure.py`, Lines 9 and 14 |

**Vulnerable Code:**
```python
command = input("Enter command: ")
data = input("Enter serialized object: ")
```

**Why it's risky:**  
In Python 2, `input()` evaluates the entered string as Python code — equivalent to `eval()`. Although we are using Python 3, Bandit flags this to alert developers who may write code intended to be compatible with both versions. Additionally, accepting raw user input that is subsequently passed to `subprocess` or `pickle` dramatically amplifies the risk of the downstream vulnerabilities.

**Remediation:**  
In Python 3, `input()` is safe by itself. However, the real fix is to **validate and sanitize** all input before using it in sensitive contexts:
```python
import re
command = input("Enter command: ")
# Only allow alphanumeric characters and spaces
if not re.match(r'^[a-zA-Z0-9 ]+$', command):
    raise ValueError("Invalid command input")
```

---

### Issue 4 — B602: `subprocess.call()` with `shell=True`
| Field | Detail |
|---|---|
| **Bandit ID** | B602 |
| **Severity** | **High** |
| **Confidence** | High |
| **Location** | `insecure.py`, Line 10 |

**Vulnerable Code:**
```python
subprocess.call(command, shell=True)
```

**Why it's risky:**  
`shell=True` passes the command string directly to the OS shell (`/bin/sh` on Linux, `cmd.exe` on Windows). An attacker who controls `command` can inject shell metacharacters:
```
Enter command: ls; rm -rf /
```
This is a textbook **OS Command Injection** attack (CWE-78).

**Remediation:**
```python
# SECURE: shell=False, arguments as list, no user input
import shlex
safe_args = shlex.split(command)  # split safely
subprocess.run(safe_args, shell=False)
```

---

### Issue 5 — B303: Use of MD5 hash function
| Field | Detail |
|---|---|
| **Bandit ID** | B303 |
| **Severity** | Medium |
| **Confidence** | High |
| **Location** | `insecure.py`, Line 12 |

**Vulnerable Code:**
```python
print(hashlib.md5(b"hello").hexdigest())
```

**Why it's risky:**  
MD5 is a **cryptographically broken** hash function. Collision attacks against MD5 have been demonstrated since 2004 (Wang & Yu). It must never be used for:
- Password hashing
- Digital signatures
- Data integrity in security contexts

**Remediation:**
```python
# For general checksums (non-security):
import hashlib
hashlib.sha256(b"hello").hexdigest()

# For password hashing specifically:
import hashlib
hashlib.scrypt(b"password", salt=os.urandom(16), n=16384, r=8, p=1)
# OR use bcrypt / argon2 libraries
```

---

### Issue 6 — B301: `pickle.loads()` on untrusted data
| Field | Detail |
|---|---|
| **Bandit ID** | B301 |
| **Severity** | Medium |
| **Confidence** | High |
| **Location** | `insecure.py`, Line 15 |

**Vulnerable Code:**
```python
data = input("Enter serialized object: ")
pickle.loads(data.encode())
```

**Why it's risky:**  
This is the most dangerous line in `insecure.py`. A crafted pickle payload can achieve **arbitrary code execution**. Example attack:
```python
import pickle, os
class Exploit(object):
    def __reduce__(self):
        return (os.system, ('whoami',))
payload = pickle.dumps(Exploit())
```
Sending this payload as input would execute `whoami` on the server.

**Remediation:**  
Never call `pickle.loads()` on data received from a user or network:
```python
# SECURE: use JSON or restrict deserialization to internal trusted data only
import json
safe_data = json.loads(user_input)
```

---

### Issue 7 — B311: Use of `random` module for unpredictable values
| Field | Detail |
|---|---|
| **Bandit ID** | B311 |
| **Severity** | Low |
| **Confidence** | High |
| **Location** | `insecure.py`, Line 17 |

**Vulnerable Code:**
```python
print(random.random())
```

**Why it's risky:**  
Python's `random` module uses the **Mersenne Twister** PRNG, which is **not cryptographically secure**. Its state can be predicted after observing enough outputs. Never use it for:
- Session tokens
- OTPs (One-Time Passwords)
- Cryptographic keys or nonces
- Salt generation

**Remediation:**
```python
import secrets   # cryptographically secure
token = secrets.token_hex(16)       # random 128-bit hex token
rand_int = secrets.randbelow(100)   # secure random integer
```

---

### Issues 8 & 9 — B605 / B607: `os.system()` with shell and partial path
| Field | Detail |
|---|---|
| **Bandit IDs** | B605, B607 |
| **Severity** | Low |
| **Confidence** | High |
| **Location** | `insecure.py`, Line 19 |

**Vulnerable Code:**
```python
os.system("ls")
```

**Why it's risky:**  
- **B605**: `os.system()` invokes the shell, same risks as `subprocess` with `shell=True`
- **B607**: `"ls"` is a partial path — if an attacker controls the `PATH` environment variable, they can substitute a malicious binary named `ls`

**Remediation:**
```python
# SECURE: use subprocess with full path and no shell
import subprocess
subprocess.run(["/bin/ls", "-la"], shell=False)
```

---

## Summary Table

| # | Bandit ID | Severity | Location | Vulnerability | Fix |
|---|---|---|---|---|---|
| 1 | B404 | Low | Line 1 | `subprocess` import | Use `shell=False` |
| 2 | B403 | Low | Line 3 | `pickle` import | Use `json` |
| 3 | B322 | High | Line 9 | `input()` feeding subprocess | Validate all input |
| 4 | B602 | **High** | Line 10 | `subprocess` with `shell=True` | `shell=False` + list args |
| 5 | B303 | Medium | Line 12 | MD5 hash | Use SHA-256 / scrypt |
| 6 | B301 | Medium | Line 15 | `pickle.loads()` on user data | Use `json.loads()` |
| 7 | B311 | Low | Line 17 | `random` for security use | Use `secrets` module |
| 8 | B605 | Low | Line 19 | `os.system()` with shell | Use `subprocess` |
| 9 | B607 | Low | Line 19 | Partial path `"ls"` | Use full path `/bin/ls` |

---

## Key Learning Outcomes

1. **Never trust user input** — validate, sanitize, and whitelist before use in any system call.
2. **MD5 and SHA1 are broken** — always use SHA-256 or above for integrity; use scrypt/bcrypt/argon2 for passwords.
3. **`pickle` is dangerous** — treat it like `eval()`. Never deserialize untrusted data.
4. **`shell=True` is a code smell** — it almost always indicates a potential injection vulnerability.
5. **Use `secrets` not `random`** — for anything security-related, `random` is the wrong tool.
6. **SAST tools like Bandit are a first line of defence** — not a complete solution, but an essential part of a secure development workflow.
