# 🔐 CryptoLabX — Cryptography Laboratory Toolkit

> **Course:** Cryptography Laboratory (22CPP307)
> **Group:** 01
> **Lab:** Lab Assignment 1 — Python Foundations for Cryptography

---

## 👥 Group Members

| Name | Roll Number | GitHub |
|------|-------------|--------|
| Nishant | 2024UCP1773 | [@Nishant-3005](https://github.com/Nishant-3005) |
| Lokesh Saini | 2024UCP1505 | — |

---

## 📌 Project Overview

**CryptoLabX** is a Python-based command-line toolkit built as part of the Cryptography Laboratory course. The project serves as a growing foundation for implementing and exploring classical and modern cryptographic algorithms throughout the semester.

Lab 1 focuses on setting up the core infrastructure of the toolkit — a structured Python project with a menu-driven interface, file analysis capabilities, and persistent session logging — before actual cipher implementations begin in subsequent labs.

---

## ✅ Tasks Completed (Lab 1)

### Task 1 — Project Initialization & Repository Setup
- Initialized a Python project repository on GitHub under the name `CryptoLabX_Group01`
- Set up standard project structure with `main.py`, `utils/`, `datasets/`, and `resources/` directories
- Configured `.gitignore` to exclude `__pycache__`, virtual environments (`venv/`, `.env`), log outputs, and OS-specific files
- Both collaborators linked to the shared repository

### Task 2 — Dataset Preparation
- Populated the `datasets/` folder with **5 sample plaintext files** (`data1.txt` through `data5.txt`)
- These files serve as input corpus for frequency analysis and future cipher experiments
- All files are plain UTF-8 encoded text

### Task 3 — Menu-Driven CLI Interface (`main.py`)
- Built a fully functional **interactive command-line interface** with an ASCII art banner
- Menu options implemented:

  | Option | Feature | Status |
  |--------|---------|--------|
  | `[1]` | Encrypt | 🔜 Coming Soon |
  | `[2]` | Decrypt | 🔜 Coming Soon |
  | `[3]` | Attack (Cryptanalysis) | 🔜 Coming Soon |
  | `[4]` | Analyze File | ✅ Implemented |
  | `[5]` | View Session Log | ✅ Implemented |
  | `[0]` | Exit | ✅ Implemented |

- Uses ANSI colour codes for a rich terminal experience (cyan, green, yellow, red, magenta)
- Input validation with clear error messages for invalid choices

### Task 4 — File Analysis Module (`utils/file_analysis.py`)
Implements `analyze_file()` and `display_analysis()` functions that compute:

- **Total characters** (including whitespace and punctuation)
- **Total words** and **total lines**
- **Unique character set** across the entire file
- **Letter frequency analysis** — counts occurrences of each A–Z letter (case-insensitive)
- **Top-10 frequency bar chart** rendered in the terminal with percentage breakdown

This module forms the foundation for **frequency analysis attacks** on classical ciphers (Caesar, Vigenère, etc.) in upcoming labs.

### Task 5 — Session Logger (`utils/logger.py`)
Implements a persistent logging system:

- Automatically creates an `outputs/` directory and `cryptolabx.log` file on first run
- Every menu action (Encrypt, Decrypt, Analyze, Exit, etc.) is **timestamped and appended** to the log
- A session separator (`SESSION STARTED [timestamp]`) is written at program startup
- The **View Log** menu option (`[5]`) displays the last 20 log entries in the terminal
- Log format: `[YYYY-MM-DD HH:MM:SS]  ACTION: <action>  |  DETAIL: <optional detail>`

---

## 📁 Project Structure

```
CryptoLabX_Group01/
│
├── main.py                  # Entry point — CLI menu & main loop
│
├── utils/
│   ├── __init__.py          # Package initializer
│   ├── file_analysis.py     # Task 4: Text statistics & letter frequency
│   └── logger.py            # Task 5: Timestamped action logger
│
├── datasets/
│   ├── data1.txt            # Sample plaintext corpus (5 files)
│   ├── data2.txt
│   ├── data3.txt
│   ├── data4.txt
│   └── data5.txt
│
├── resources/               # Lab assignment PDFs & reference material
├── outputs/                 # Auto-generated: cryptolabx.log (gitignored)
├── requirements.txt         # Dependency list (stdlib only for Lab 1)
├── .gitignore               # Git exclusions
└── README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python **3.10+** (uses `list[str]` type hints)
- No external packages required for Lab 1 — uses Python standard library only (`os`, `glob`, `collections`, `datetime`)

### Run the Toolkit

```bash
# Clone the repository
git clone https://github.com/Nishant-3005/CryptoLabX_Group01.git
cd CryptoLabX_Group01

# Run the CLI
python main.py
```

---

## 📦 Dependencies

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| *(stdlib only)* | — | `os`, `glob`, `collections`, `datetime` | ✅ Used |
| `numpy` | ≥1.26.0 | Matrix operations for modern ciphers | 🔜 Planned |
| `sympy` | ≥1.12 | Number theory, modular arithmetic | 🔜 Planned |
| `pycryptodome` | ≥3.20.0 | Reference AES/RSA implementations | 🔜 Planned |
| `matplotlib` | ≥3.8.0 | Frequency analysis plots | 🔜 Planned |

---

## 🔭 Upcoming (Future Labs)

- [ ] **Caesar Cipher** — Encrypt / Decrypt / Brute-force attack
- [ ] **Vigenère Cipher** — Polyalphabetic encryption & Kasiski attack
- [ ] **Rail Fence & Columnar Transposition** ciphers
- [ ] **Frequency Analysis** — Visual plots using matplotlib
- [ ] **Modular Arithmetic Utilities** — GCD, extended Euclidean, modular inverse
- [ ] **AES / RSA** — Modern cipher reference via pycryptodome

---

## 📝 Lab Progress Log

| Lab | Tasks | Contributor | Status |
|-----|-------|-------------|--------|
| Lab 1 | Project init, datasets, CLI menu, file analysis, logger | Nishant (2024UCP1773) | ✅ Done |
| Lab 2 | Caesar & Vigenère cipher implementation | — | 🔜 Upcoming |
| Lab 3 | Cryptanalysis / attack modules | — | 🔜 Upcoming |

---

*CryptoLabX — Group 01 | 22CPP307 Cryptography Laboratory*
