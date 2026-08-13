# Lab 3 — ATM System: Complete Technical Explanation
## CryptoLabX Group 01 | 22CPP307 Cryptography Laboratory

---

## 1. Assignment Context

**Group Number:** 01  
**Application Assigned:** ATM System (Group No. % 10 = 1)  
**SAST Tool:** Bandit  
**Language:** Python 3  
**Location in repo:** `Secure_Application/`

The objective of Lab 3 is to build a **small, intentionally vulnerable application** that demonstrates real-world security flaws, then scan it with a SAST tool (Bandit) to detect and document those flaws. The key distinction is that this is **not** meant to be a production-quality system — it is a controlled environment for learning how vulnerabilities look in code and how automated tools detect them.

---

## 2. Application Overview — ATM System

The ATM system simulates the core operations of a real Automated Teller Machine. It is a **console-based, menu-driven Python application** with no GUI, no database, and no network — purely in-memory and interactive via `input()`.

### Five Core Functionalities

| # | Functionality | Module | Entry Function |
|---|---|---|---|
| 1 | **Login** | `auth.py` | `login()` |
| 2 | **Balance Inquiry** | `account.py` | `balance_inquiry()` |
| 3 | **Withdrawal** | `account.py` | `withdraw()` |
| 4 | **Deposit** | `account.py` | `deposit()` |
| 5 | **PIN Change** | `auth.py` | `change_pin()` |

### Three Deliberate Vulnerabilities

| # | Vulnerability | Category | Bandit Rule | Severity |
|---|---|---|---|---|
| VULN-1 | Hardcoded credentials (passwords in source) | CWE-259 | B105 | Low |
| VULN-1b | MD5 used for PIN hashing | CWE-327 | B324 | **High** |
| VULN-2 | Improper input validation (no bounds on amounts) | CWE-20 | Logic flaw | — |
| VULN-3 | Information leakage via error messages (full tracebacks) | CWE-209 | — | Logic flaw |

---

## 3. Project Structure

```
Secure_Application/
├── src/
│   ├── atm.py          Entry point — main loop, banner, menu dispatch
│   ├── auth.py         Login & PIN change logic
│   ├── account.py      Balance inquiry, withdrawal, deposit
│   └── database.py     In-memory account store (hardcoded accounts)
├── sast/
│   └── bandit_report_lab3.txt    Raw Bandit scan output
├── reports/            (for written analysis reports)
└── screenshots/        (for demo screenshots)
```

**Why modular?** Each Python file has exactly one responsibility (Single Responsibility Principle). This makes it easy to:
- Swap in a real database later (only `database.py` changes)
- Add encryption to auth (only `auth.py` changes)
- Test each module independently

---

## 4. Module-by-Module Explanation

---

### 4.1 `database.py` — Account Store

**Purpose:** Acts as a stand-in for a real database. Stores account data in a Python dictionary in memory. Data is lost when the program exits.

**Key data structure:**
```python
ACCOUNTS = {
    "1001234567": {
        "pin"     : "1234",
        "name"    : "Alice Kumar",
        "balance" : 15000.00,
        "pin_hash": hashlib.md5(b"1234").hexdigest(),
    },
    ...
}
```

**Key functions:**

| Function | Parameters | Returns | What it does |
|---|---|---|---|
| `get_account(account_number)` | `str` | `dict` | Looks up account by key; raises `KeyError` if not found |
| `update_balance(account_number, new_balance)` | `str, float` | `None` | Overwrites the balance field in the dict |
| `update_pin(account_number, new_pin)` | `str, str` | `None` | Overwrites the pin field in the dict |

**Vulnerabilities embedded here:**

- **VULN-1 (B105):** `ADMIN_PASSWORD = "admin@123"` and `SECRET_KEY = "atm_secret_99"` are hardcoded string literals. Bandit detects variable names containing `password` or `secret` and flags them. In production, these would come from environment variables (`os.environ.get("ADMIN_PASSWORD")`).

- **VULN-1b (B324):** `hashlib.md5(b"1234").hexdigest()` — MD5 is a cryptographically broken hash function since 2004. For PIN/password verification, you must use a slow, salted hash like `bcrypt`, `scrypt`, or `argon2`. Bandit flags this as High severity.

- **VULN-3 (setup):** `get_account()` raises a raw `KeyError` without catching it. When this propagates to `auth.py`, the full traceback (including the internal dict key that was looked up) is printed to the user's terminal.

---

### 4.2 `auth.py` — Authentication & PIN Management

**Purpose:** Handles the two security-critical operations: verifying identity (login) and changing the PIN.

**Key functions:**

#### `login() → tuple[str, dict] | tuple[None, None]`

```
1. Print login prompt
2. Read account_number from input
3. Read pin from input
4. Call get_account(account_number)
   ├── If account not found → KeyError raised
   │    └── VULN-3: Full traceback printed to terminal
   └── If found:
       ├── Compare account["pin"] == pin  ← VULN-1: plain text comparison
       ├── Match → return (account_number, account_dict)
       └── No match → print error, return (None, None)
```

**Returns:** A tuple. On success: `(account_number_str, account_dict)`. On failure: `(None, None)`. The caller (`atm.py`) checks whether the returned account is `None` to decide whether to allow session entry.

**Vulnerability detail — VULN-3 in `login()`:**
```python
except Exception as e:
    print(f"\n  [ERROR] Login failed: {e}")
    print(traceback.format_exc())   # ← prints full stack trace to terminal
```
A real system should only show: `"Invalid account number or PIN."` The traceback reveals internal module paths, variable names, and the exact key that was searched — giving an attacker a map of the internal data structure.

---

#### `change_pin(account_number, account) → None`

```
1. Prompt for current PIN → compare to account["pin"]
2. If mismatch → print error, return
3. Prompt for new_pin and confirm_pin
4. VULN-2: NO validation performed on new_pin:
   - Length not checked (could be 1 character)
   - Not checked to be numeric
   - No complexity policy
5. If new_pin == confirm_pin → call update_pin()
6. VULN-3: Print the new PIN in the confirmation message
```

**The double-leak in step 6:**
```python
print(f"  PIN successfully changed to: {new_pin}")
```
This echoes the secret back to the screen — a shoulder-surfer or CCTV camera could capture it.

---

### 4.3 `account.py` — Transactions

**Purpose:** Implements the three financial operations. This is where VULN-2 (improper input validation) is most visible.

**Key functions:**

#### `balance_inquiry(account_number) → None`

The simplest function. Fetches the account and prints `name`, `account_number`, and `balance`. No vulnerability here beyond the general VULN-3 risk from `get_account()`.

---

#### `withdraw(account_number, account) → None`

```
1. Read raw string from input
2. VULN-2: float(raw) — no check if raw is numeric
   - "abc" → ValueError → full traceback printed (VULN-3)
3. amount = float(raw)
4. Check: amount > current_balance → "Insufficient funds"
   - VULN-2: amount = -500 passes this check (−500 < 15000 is True)
   - Subtracting -500 from balance ADDS 500 (money creation bug)
5. new_balance = current_balance - amount
6. update_balance() and print confirmation
```

**The negative-amount exploit (VULN-2 demo):**
```
Enter amount to withdraw: Rs. -500
→ Check: -500 > 15000? NO → passes
→ new_balance = 15000 - (-500) = 15500
→ "Rs. -500.00 dispensed. New Balance: Rs. 15500.00"
```
The user "withdrew" a negative amount and their balance **increased** by Rs. 500.

---

#### `deposit(account_number, account) → None`

Mirrors `withdraw()`. Same VULN-2 gaps:
- Negative deposit **reduces** the balance (essentially a stealth withdrawal)
- No upper limit on deposit amount
- Non-numeric input causes full traceback

---

### 4.4 `atm.py` — Entry Point & Main Loop

**Purpose:** The orchestrator. Ties all modules together. Handles the outer session loop, login flow, and menu dispatch.

**Program flow:**

```
START
  │
  ├── print_banner()          Print ASCII art header
  │
  └── OUTER LOOP (per card insertion):
        │
        ├── Prompt: ENTER to login, Q to quit
        │
        └── LOGIN LOOP (up to 3 attempts):
              │
              ├── login() → (account_number, account)
              │     ├── Success → break login loop
              │     └── Failure → attempts++
              │
              ├── 3 failures → "Card blocked" → continue outer loop
              │
              └── INNER MENU LOOP (authenticated session):
                    │
                    ├── [1] balance_inquiry(account_number)
                    ├── [2] withdraw(account_number, account)
                    ├── [3] deposit(account_number, account)
                    ├── [4] change_pin(account_number, account)
                    ├── [0] break → "Logged out"
                    └── [?] "Invalid option"
```

**Key design decisions:**
- `account` dict is passed by reference in Python, so balance updates in `account.py` are immediately reflected across the session without re-fetching from the store.
- The 3-attempt lockout is session-level only — restarting the program resets it (another VULN-2 gap).
- `os.system("")` is called at startup to enable ANSI colour codes on Windows terminals. This is flagged by Bandit B605/B607 but is harmless here (empty string is passed).

---

## 5. Bandit SAST Scan Results

**Command used:**
```bash
py -3 -m bandit -r Secure_Application/src/
```

**Results summary:**

| Rule | Severity | Confidence | Location | Issue |
|---|---|---|---|---|
| B605 | Low | High | `atm.py:40` | `os.system("")` — shell process |
| B607 | Low | High | `atm.py:40` | Partial executable path |
| B105 | Low | Medium | `database.py:26` | `ADMIN_PASSWORD = "admin@123"` hardcoded |
| B105 | Low | Medium | `database.py:27` | `SECRET_KEY = "atm_secret_99"` hardcoded |
| B324 | **High** | High | `database.py:35` | `hashlib.md5()` — weak hash |
| B324 | **High** | High | `database.py:41` | `hashlib.md5()` — weak hash |

**Total: 2 High | 0 Medium | 4 Low | 6 issues**

Note: VULN-2 (improper input validation) and VULN-3 (information leakage via traceback) are **logic-level vulnerabilities** — they are design flaws, not pattern-based, so Bandit does not detect them. This is a key teaching point: SAST tools catch known patterns, but manual code review is still essential for logic flaws.

---

## 6. Vulnerabilities — Deep Dive

### VULN-1: Hardcoded Credentials (CWE-259)

**What it is:** Embedding passwords, PINs, or secrets directly in source code.

**Why it's dangerous:** Source code is often:
- Stored in version control (GitHub, GitLab) — accessible to anyone with repo access
- Reverse-engineered from compiled binaries
- Leaked in stack traces, logs, or error messages

**Bandit detection:** B105 (`hardcoded_password_string`) — triggers when a variable whose name contains "password", "secret", "key", "passwd", or "token" is assigned a string literal.

**Secure fix:**
```python
import os
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")  # from environment
# or use python-dotenv to load from a .env file
```

---

### VULN-2: Improper Input Validation (CWE-20)

**What it is:** Accepting user input without checking that it is within valid bounds, type, and range.

**Why it's dangerous:** In financial systems, unvalidated numeric input can lead to:
- **Negative withdrawal** → balance increase (money creation)
- **Overflow** → unexpected behaviour for very large numbers
- **Type errors** → crashes that leak internal state

**Bandit detection:** None — this is a logic flaw, not a code pattern.

**Secure fix:**
```python
def get_positive_amount(prompt: str) -> float:
    raw = input(prompt).strip()
    if not raw.isdigit():
        raise ValueError("Amount must be a positive integer.")
    amount = int(raw)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return float(amount)
```

---

### VULN-3: Information Leakage via Error Messages (CWE-209)

**What it is:** Displaying internal system details (file paths, variable names, stack traces, database keys) in user-facing error messages.

**Why it's dangerous:**
- Reveals the internal architecture to an attacker
- Stack traces show exact file names and line numbers — helps targeted exploitation
- Printing the new PIN on screen is a shoulder-surfing risk

**Bandit detection:** None — logic flaw.

**Secure fix:**
```python
import logging

logging.basicConfig(filename="atm_errors.log", level=logging.ERROR)

try:
    account = get_account(account_number)
except KeyError as e:
    logging.error(f"Account lookup failed: {e}", exc_info=True)  # log internally
    print("  [ERROR] Invalid account number or PIN.")             # generic to user
```

---

## 7. Test Accounts

| Account Number | PIN | Account Holder | Balance |
|---|---|---|---|
| `1001234567` | `1234` | Alice Kumar | Rs. 15,000.00 |
| `1009876543` | `4321` | Bob Sharma | Rs. 8,500.50 |

---

## 8. How to Run

```bash
# Navigate to src directory
cd Secure_Application/src

# Run the application
py -3 atm.py

# OR from project root
py -3 Secure_Application/src/atm.py
```

---

## 9. How to Re-run the SAST Scan

```bash
# From project root
py -3 -m bandit -r Secure_Application/src/

# Save to file
py -3 -m bandit -r Secure_Application/src/ -o Secure_Application/sast/bandit_report_lab3.txt -f txt
```

---

*CryptoLabX Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 | MNIT Jaipur*
