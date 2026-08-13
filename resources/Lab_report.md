# Laboratory Notebook
## Course: Cryptography Laboratory (22CPP307)
## Group: 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)

---
---

# LAB 1 — Python Foundations for Cryptography

---

## Aim

To set up a structured Python project for a cryptography toolkit (CryptoLabX) with a menu-driven command-line interface, file analysis capability, and a persistent session logging mechanism.

---

## Brief Theory

Python is a high-level, interpreted programming language widely used in cryptography research due to its simplicity and rich library ecosystem. A **CLI (Command-Line Interface)** is a text-based interface where the user interacts with the program by typing commands. **Modular programming** involves dividing a program into independent, reusable modules — each responsible for one specific function.

**File analysis** in the context of cryptography is the foundation of frequency analysis — a classical attack technique where the statistical distribution of letters in a ciphertext is compared against known language letter frequencies to deduce the cipher key. **Logging** is the practice of recording runtime events with timestamps, enabling traceability and auditing of user actions. Together, these components form the core infrastructure of a cryptographic toolkit that will support cipher implementations in future labs.

---

## Algorithm / Flowchart

### Task 3 — Menu-Driven CLI (main.py)

```
START
  │
  ├─► Print ASCII Banner
  ├─► log_session_start()
  │
  └─► LOOP:
        │
        ├─► print_menu()
        ├─► Read user input
        │
        ├─[1] Encrypt      → coming_soon() → log_action("ENCRYPT")
        ├─[2] Decrypt      → coming_soon() → log_action("DECRYPT")
        ├─[3] Attack       → coming_soon() → log_action("ATTACK")
        ├─[4] Analyze File → handle_analyze() → log_action("ANALYZE", filename)
        ├─[5] View Log     → show_log() → log_action("VIEW_LOG")
        ├─[0] Exit         → log_action("EXIT") → BREAK
        └─[?] Invalid      → Print error → continue loop
```

### Task 4 — File Analysis (utils/file_analysis.py)

```
INPUT: filepath (string)
  │
  ├─► Open file → read full content
  ├─► Count: total characters, words, lines
  ├─► Extract all alphabetic chars → convert to UPPERCASE
  ├─► Counter(letters) → get frequency of each A-Z letter
  ├─► Sort by count (descending) → most_common()
  └─► Return dict { total_chars, total_words, total_lines,
                    unique_chars, unique_char_count,
                    letter_freq, total_letters }

display_analysis(stats):
  ├─► Print file summary table
  ├─► Print Top-10 letter frequency bar chart
  └─► Print unique character set
```

### Task 5 — Logger (utils/logger.py)

```
log_session_start():
  └─► Append "=== SESSION STARTED [timestamp] ===" to outputs/cryptolabx.log

log_action(action, detail=""):
  └─► Append "[YYYY-MM-DD HH:MM:SS]  ACTION: <action>  |  DETAIL: <detail>"

show_log():
  └─► Read last 20 lines of cryptolabx.log → print to terminal
```

---

## Important Commands

```bash
# Run the toolkit
python main.py

# Project structure
python -m py_compile main.py          # Syntax check
python -m py_compile utils/file_analysis.py
python -m py_compile utils/logger.py

# Git operations (Lab 1 setup)
git init
git add .
git commit -m "init: initialized CryptoLabX project"
git push origin main
```

---

## Observations

| Task | Observation |
|------|-------------|
| Task 1 | Git repository successfully initialized. `.gitignore` configured to exclude `__pycache__/`, `*.pyc`, `outputs/` (log files) |
| Task 2 | 5 plaintext dataset files (`data1.txt` – `data5.txt`) added to `datasets/`. Files contain varying English text suitable for frequency analysis |
| Task 3 | CLI menu renders correctly with ANSI colours (cyan, green, yellow, red) on both Linux and Windows terminals. `os.system("")` required on Windows to enable ANSI |
| Task 4 | Analyzed `data1.txt` — most frequent letter was **E** (~12.3%), consistent with standard English letter frequency distribution. Top-10 bar chart rendered correctly |
| Task 5 | Log file auto-created at `outputs/cryptolabx.log` on first run. Each action timestamped correctly. Session separator visible in log |
| Menu flow | Invalid input (e.g., `"abc"`) handled gracefully — error message printed, loop continues without crashing |
| Modules | `utils/` package imported successfully via `__init__.py`. Separation of concerns confirmed — `main.py` contains no analysis or logging logic directly |

---
---

# LAB 2 — Static Application Security Testing (SAST) Using Bandit

---

## Aim

To gain hands-on experience with Static Application Security Testing (SAST) by installing and configuring the **Bandit** tool (assigned to Group 1), creating an intentionally insecure Python program, performing a static security scan, and analysing and documenting the detected vulnerabilities.

---

## Brief Theory

**Static Application Security Testing (SAST)** is a method of analysing source code for security vulnerabilities *without executing* the program. SAST tools scan the source code, bytecode, or binary to identify patterns associated with known vulnerability classes. **Bandit** is a widely-used open-source SAST tool developed by the Python Security team (PyCQA). It processes Python source files using an Abstract Syntax Tree (AST) and applies a set of test plugins (each identified by a rule ID such as B301, B602) to detect insecure coding practices.

Common vulnerability categories detectable by Bandit include: shell injection via `subprocess.call(shell=True)`, use of weak hash functions (MD5, SHA1), unsafe deserialization using `pickle`, use of non-cryptographic random generators, and hardcoded credentials. Each finding is rated by **Severity** (Low/Medium/High) and **Confidence** (Low/Medium/High), giving developers a priority-ranked list of security issues to remediate.

---

## Algorithm / Flowchart

### SAST Process with Bandit

```
START
  │
  ├─► Install Bandit
  │     └─► sudo apt install bandit
  │
  ├─► Create insecure test program (insecure.py)
  │     └─► Include intentional vulnerabilities:
  │           • Hardcoded password
  │           • subprocess with shell=True
  │           • hashlib.md5() (weak hash)
  │           • pickle.loads() (unsafe deserialization)
  │           • random.random() (non-crypto RNG)
  │           • os.system() (shell execution)
  │
  ├─► Run Bandit scan
  │     └─► bandit insecure.py -o bandit_report.txt -f txt
  │
  ├─► Analyse each finding:
  │     For each issue:
  │     ├─► Note: Rule ID, Severity, Confidence
  │     ├─► Identify: file, line number, code snippet
  │     ├─► Understand: why it is a vulnerability
  │     └─► Suggest: remediation / secure alternative
  │
  ├─► Save terminal session log
  │     └─► script sast_lab_log.txt ... exit
  │
  └─► Save command history
        └─► history > command_history.txt

END
```

---

## Important Commands

```bash
# System update
sudo apt update

# Install Bandit
sudo apt install -y bandit

# Verify installation
bandit --version

# Start terminal session logging
script sast_lab_log.txt

# Create working directory
mkdir -p ~/CryptographyLab/Lab2_Bandit
cd ~/CryptographyLab/Lab2_Bandit

# Run Bandit scan on test file
bandit insecure.py

# Run scan and save report to file
bandit insecure.py -o bandit_report.txt -f txt

# End terminal session log
exit

# Save command history
history > command_history.txt
```

---

## Observations

### System & Tool Info

| Field | Detail |
|-------|--------|
| OS | Ubuntu 24.04 LTS (Noble Numbat) |
| Bandit Version | 1.6.2 |
| Installation Method | `sudo apt install bandit` |
| Total Dependencies Installed | 10 packages |
| Problems Encountered | None |

### Test Program Summary (`insecure.py` — 13 lines of code)

| Line | Vulnerability Introduced |
|------|--------------------------|
| 1 | `import subprocess` — flagged by B404 |
| 3 | `import pickle` — flagged by B403 |
| 7 | `password = "admin123"` — hardcoded credential |
| 9–10 | `subprocess.call(command, shell=True)` — shell injection (B602) |
| 12 | `hashlib.md5(b"hello")` — weak hash function (B303) |
| 14–15 | `pickle.loads(data.encode())` — unsafe deserialization (B301) |
| 17 | `random.random()` — non-crypto PRNG (B311) |
| 19 | `os.system("ls")` — shell execution (B605, B607) |

### Bandit Scan Results Summary

| Rule ID | Severity | Confidence | Vulnerability |
|---------|----------|------------|--------------|
| B404 | Low | High | `import subprocess` flagged |
| B403 | Low | High | `import pickle` flagged |
| B322 | High | High | `input()` — Python 2 eval risk |
| B602 | High | High | `subprocess.call(shell=True)` — shell injection |
| B303 | Medium | High | `hashlib.md5()` — insecure hash |
| B322 | High | High | Second `input()` — Python 2 eval risk |
| B301 | Medium | High | `pickle.loads()` — unsafe deserialization |
| B311 | Low | High | `random.random()` — not cryptographically secure |
| B605 | Low | High | `os.system()` — shell process start |
| B607 | Low | High | `os.system("ls")` — partial executable path |

**Totals: 3 High | 2 Medium | 5 Low | All 10 at High Confidence**

### Key Findings & Remediations

| Finding | Why Dangerous | Secure Alternative |
|---------|--------------|-------------------|
| `subprocess.call(shell=True)` | Allows arbitrary OS command injection if input is user-controlled | Use `subprocess.run(["cmd", "arg"])` with `shell=False` |
| `hashlib.md5()` | MD5 is cryptographically broken; vulnerable to collision attacks | Use `hashlib.sha256()` or `hashlib.sha3_256()` |
| `pickle.loads()` | Deserialization of untrusted data can execute arbitrary code | Use `json.loads()` for safe data exchange |
| `random.random()` | Predictable; not suitable for keys, tokens, or nonces | Use `secrets.token_bytes()` or `os.urandom()` |
| `password = "admin123"` | Hardcoded credentials are exposed in source control | Use environment variables or a secrets manager |

---
---

# LAB 3 — Developing a Vulnerable Application & SAST Analysis

---

## Aim

To design and implement a deliberately vulnerable Python application (ATM System) with a modular architecture, embed three specific vulnerability categories, and perform Static Application Security Testing (SAST) using Bandit to detect and document the identified security flaws.

---

## Brief Theory

In Lab 3, the approach shifts from *scanning existing code* (Lab 2) to *deliberately designing vulnerabilities* into a structured application. This is a common technique in security education known as **Capture-the-Flag (CTF) style vulnerable app development** — building apps like DVWA (Damn Vulnerable Web App) or WebGoat.

**Hardcoded Credentials (CWE-259):** Storing passwords, PINs, or API keys directly in source code is one of the most common real-world vulnerabilities. Source code is frequently checked into version control systems (Git), which may be public or accessed by multiple team members. Any secret in source code should be considered compromised.

**Improper Input Validation (CWE-20):** Every value received from an external source (user input, files, network) must be validated before use. Failure to validate: data type, range (min/max), sign (positive/negative), and length leads to logic bugs, crashes, and exploitable conditions. In financial software, a negative withdrawal amount that bypasses a simple `> balance` guard can increase the user's balance — a money-creation bug.

**Information Leakage via Error Messages (CWE-209):** Full exception tracebacks, internal variable names, file paths, and data structure keys exposed in user-facing messages give an attacker a precise map of the application's internals. The principle of **least information disclosure** dictates that error messages to end-users must be generic, while detailed logs are stored server-side only.

**Modular Design Principle:** The application is split into four files, each with a single responsibility — `database.py` (data), `auth.py` (identity), `account.py` (transactions), `atm.py` (orchestration). This mirrors the **Separation of Concerns** architectural pattern and makes the code easier to review, test, and patch.

---

## Algorithm / Flowchart

### ATM System — Main Program Flow

```
START (atm.py)
  │
  ├─► print_banner()
  │
  └─► OUTER LOOP:
        │
        ├─► Prompt: ENTER to login / Q to quit
        │
        └─► LOGIN LOOP (max 3 attempts):
              │
              ├─► auth.login()
              │     ├─► Read account_number, pin
              │     ├─► database.get_account(account_number)
              │     │     ├── Found → compare pin (plain text) [VULN-1]
              │     │     └── Not found → print full traceback [VULN-3]
              │     └─► Return (account_number, account) or (None, None)
              │
              ├─► 3 failures → "Card blocked" → outer loop
              │
              └─► MENU LOOP (authenticated):
                    │
                    ├─[1] account.balance_inquiry()
                    ├─[2] account.withdraw()
                    │       ├─► Read amount (no validation) [VULN-2]
                    │       ├─► Negative check: amount > balance only
                    │       └─► Update balance (negative amount allowed)
                    ├─[3] account.deposit()
                    │       └─► Same gaps as withdraw [VULN-2]
                    ├─[4] auth.change_pin()
                    │       ├─► No PIN complexity check [VULN-2]
                    │       └─► Print new PIN to screen [VULN-3]
                    └─[0] Logout → outer loop
```

---

## Important Commands

```bash
# Run the ATM application
py -3 Secure_Application/src/atm.py

# Run Bandit SAST scan on source
py -3 -m bandit -r Secure_Application/src/

# Save Bandit report to file
py -3 -m bandit -r Secure_Application/src/ -o Secure_Application/sast/bandit_report_lab3.txt -f txt

# Test accounts
Account: 1001234567  PIN: 1234   (Alice Kumar,  Rs. 15,000)
Account: 1009876543  PIN: 4321   (Bob Sharma,   Rs.  8,500)

# Demonstrate VULN-2 (negative withdrawal)
# At "Enter amount to withdraw:" type: -500
# Observe balance INCREASES by 500

# Demonstrate VULN-3 (traceback leakage)
# At "Enter Account Number:" type: 0000000000
# Observe full Python traceback printed to terminal
```

---

## Observations

### Application Structure

| File | Lines | Responsibility |
|---|---|---|
| `atm.py` | ~100 | Entry point, banner, menu loop, session management |
| `auth.py` | ~80 | Login, PIN comparison, PIN change |
| `account.py` | ~90 | Balance inquiry, withdrawal, deposit |
| `database.py` | ~66 | In-memory account store, CRUD functions |

### Bandit Scan Results

| Rule | Severity | Confidence | Location | Vulnerability |
|---|---|---|---|---|
| B605 | Low | High | `atm.py:40` | `os.system("")` — shell process start |
| B607 | Low | High | `atm.py:40` | Partial executable path |
| B105 | Low | Medium | `database.py:26` | `ADMIN_PASSWORD = "admin@123"` hardcoded |
| B105 | Low | Medium | `database.py:27` | `SECRET_KEY = "atm_secret_99"` hardcoded |
| B324 | **High** | High | `database.py:35` | `hashlib.md5()` — insecure hash for PIN |
| B324 | **High** | High | `database.py:41` | `hashlib.md5()` — insecure hash for PIN |

**Total: 2 High | 0 Medium | 4 Low**

### Vulnerability Demonstration Results

| Vulnerability | Test Input | Expected (Secure) Behaviour | Actual (Insecure) Behaviour |
|---|---|---|---|
| VULN-1 (Hardcoded creds) | Open `database.py` in editor | Credentials not visible in source | PINs `1234`, `4321` visible as plain strings |
| VULN-2 (Bad validation) | Withdraw `-500` | "Invalid amount. Must be positive." | Balance increases by Rs. 500 |
| VULN-2 (Bad validation) | Deposit `abc` | "Invalid amount. Enter a number." | Full `ValueError` traceback printed |
| VULN-3 (Info leakage) | Login with `0000000000` | "Invalid account or PIN." | Full traceback with key `0000000000` printed |
| VULN-3 (Info leakage) | Change PIN to `5678` | No confirmation of PIN value | "PIN successfully changed to: 5678" printed |

### SAST Limitation Observed

Bandit detected 6 issues — all pattern-based (hardcoded strings, MD5 use, `os.system`). It did **not** detect:
- VULN-2 (negative amounts) — this is a business logic flaw, not a code pattern
- VULN-3 (traceback leakage) — printing `traceback.format_exc()` is not inherently flagged

**Key insight:** SAST tools are powerful for pattern matching but cannot replace manual code review for logic vulnerabilities.

---

*Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505) | 22CPP307 Cryptography Laboratory | MNIT Jaipur*

