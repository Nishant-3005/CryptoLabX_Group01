# Bandit SAST Tool — Installation Record
## CryptoLabX Group 01 | Lab 2 | 22CPP307

---

## 1. System Information

| Field              | Details                          |
|--------------------|----------------------------------|
| Operating System   | Ubuntu 24.04 LTS (Noble Numbat)  |
| Kernel             | Linux (WSL2 / Native Ubuntu)     |
| Shell              | bash                             |
| Python Version     | Python 3.12 (system default)     |
| SAST Tool Assigned | Bandit (Group 1)                 |
| Bandit Version     | 1.6.2                            |

---

## 2. Installation Procedure

### Step 1 — Update package lists
```bash
sudo apt update
```
Ensures the latest package index is fetched before installation.

### Step 2 — Install Bandit via apt
```bash
sudo apt install -y bandit
```
This installs Bandit and all its Python dependencies automatically.

### Step 3 — Verify installation
```bash
bandit --version
```
Expected output: `bandit 1.6.2`

---

## 3. Dependencies Installed

The following packages were automatically installed as dependencies of Bandit:

| Package                      | Version    | Purpose                                      |
|------------------------------|------------|----------------------------------------------|
| `bandit`                     | 1.6.2      | SAST tool (main package)                     |
| `python3-bandit`             | 1.6.2      | Python 3 library component of Bandit         |
| `python3-git`                | 3.1.37     | Git repository interaction (for repo scans)  |
| `python3-gitdb`              | 4.0.11     | Git object database layer                    |
| `python3-smmap`              | 6.0.0      | Sliding memory map for git object access     |
| `python3-stevedore`          | 5.1.0      | Plugin loading mechanism used by Bandit      |
| `python3-pbr`                | 5.11.1     | Python Build Reasonableness (stevedore dep)  |
| `python3-more-itertools`     | 10.2.0     | Extended itertools (Bandit utility dep)      |
| `python3-importlib-metadata` | 4.12.0     | Package metadata access                      |
| `python3-zipp`               | 1.0.0      | Zip file path abstraction                    |

**Total new packages installed:** 10
**Additional disk space used:** ~2.3 MB

---

## 4. Working Directory Setup

```bash
mkdir -p ~/CryptographyLab/Lab2_Bandit
cd ~/CryptographyLab/Lab2_Bandit
```

---

## 5. Terminal Session Logging

As instructed, the full terminal session was captured using the `script` command:

```bash
script sast_lab_log.txt
```
*(All subsequent commands were recorded automatically)*

When finished:
```bash
exit
```

Shell history was also saved separately:
```bash
history > command_history.txt
```

---

## 6. Problems Encountered & Resolutions

| Problem | Resolution |
|---------|------------|
| None encountered during installation | Installation completed cleanly on first attempt |
| `sudo apt install bandit` prompted for password | Entered sudo password — standard behavior |
| Confirmation prompt `[Y/n]` during install | Entered `Y` to proceed |

---

## 7. Post-Installation Verification

After installation, Bandit was verified working by running it against the test program:

```bash
bandit insecure.py -o bandit_report.txt -f txt
```

Output confirmed: **10 issues detected** across 13 lines of code.

---

*Documented by: Lokesh Saini (2024UCP1505) | 2026-08-06*
