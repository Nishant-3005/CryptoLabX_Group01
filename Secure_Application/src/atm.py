"""
atm.py — ATM System Entry Point
================================
Lab 3 | Secure Application | CryptoLabX Group 01
Course: Cryptography Laboratory (22CPP307)

Application : ATM System (Group 1 — Group No. % 10 = 1)
SAST Tool   : Bandit
Language    : Python 3

Core Functionalities:
  1. Login                (auth.login)
  2. Balance Inquiry      (account.balance_inquiry)
  3. Withdrawal           (account.withdraw)
  4. Deposit              (account.deposit)
  5. PIN Change           (auth.change_pin)

Deliberate Vulnerabilities (for SAST demonstration):
  VULN-1  Hardcoded Credentials    (database.py — B105/B106)
  VULN-2  Improper Input Validation (account.py — no bounds checks)
  VULN-3  Information Leakage via Error Messages (auth.py, account.py)

Run:
  python atm.py
"""

from auth    import login, change_pin
from account import balance_inquiry, withdraw, deposit

# ─── ANSI helpers (basic, no external deps) ──────────────────────────────────
C = "\033[96m"   # cyan
G = "\033[92m"   # green
Y = "\033[93m"   # yellow
R = "\033[91m"   # red
W = "\033[1m"    # bold
X = "\033[0m"    # reset


def print_banner() -> None:
    import os; os.system("")   # enable ANSI on Windows
    print(f"""
{C}{W}
  ================================================
    ___  _____  __  __   ____  _   _  _  _
   / _ \|_   _||  \/  | / ___|| | | || \| |
  | | | | | |  | |\/| || |    | |_| ||  ` |
  | |_| | | |  | |  | || |___ |  _  || |\  |
   \__\_\ |_|  |_|  |_| \____||_| |_||_| \_|

        Automated Teller Machine System
        CryptoLabX Group 01 | Lab 3
  ================================================
{X}""")


def print_menu() -> None:
    print(f"""
{C}  --------------------------------{X}
  {W}[1]{X}  Balance Inquiry
  {W}[2]{X}  Withdraw Cash
  {W}[3]{X}  Deposit Cash
  {W}[4]{X}  Change PIN
  {W}[0]{X}  {R}Logout{X}
{C}  --------------------------------{X}""")


def main() -> None:
    print_banner()

    MAX_LOGIN_ATTEMPTS = 3   # [VULN-2] limit exists but is bypassable by restarting

    while True:
        print(f"\n{Y}  Insert card / Enter credentials to begin.{X}")
        print(f"  {W}[Q]{X} Quit application\n")
        choice = input("  Press ENTER to login, Q to quit: ").strip().upper()
        if choice == "Q":
            print(f"\n  {G}Thank you for using CryptoLabX ATM. Goodbye!{X}\n")
            break

        # ── Login ────────────────────────────────────────────────────────────
        attempts = 0
        account_number, account = None, None

        while attempts < MAX_LOGIN_ATTEMPTS:
            account_number, account = login()
            if account:
                break
            attempts += 1
            remaining = MAX_LOGIN_ATTEMPTS - attempts
            if remaining > 0:
                print(f"  {Y}Attempts remaining: {remaining}{X}")

        if not account:
            print(f"\n  {R}Card blocked after {MAX_LOGIN_ATTEMPTS} failed attempts.{X}")
            continue

        # ── Authenticated session ─────────────────────────────────────────────
        while True:
            print_menu()
            option = input("  Select option: ").strip()

            if option == "1":
                balance_inquiry(account_number)
            elif option == "2":
                withdraw(account_number, account)
            elif option == "3":
                deposit(account_number, account)
            elif option == "4":
                change_pin(account_number, account)
            elif option == "0":
                print(f"\n  {G}Logged out successfully. Please collect your card.{X}")
                break
            else:
                print(f"  {R}Invalid option. Please select 0-4.{X}")


if __name__ == "__main__":
    main()
