"""
database.py — In-memory account store for ATM System

VULNERABILITY EMBEDDED:
  [VULN-3] Information Leakage via Error Messages
  - Full exception details (including internal account structure)
    are printed directly to the console on any error.

"""

# ──────────────────────────────────────────────────────────────────────────────
# [VULN-1] Hardcoded Credentials (B105 / B106)
# Account numbers and PINs are hardcoded directly in source code.
# An attacker who reads the source (or a compiled binary) immediately
# has full access to every account.
# ──────────────────────────────────────────────────────────────────────────────
import hashlib

# B106: hardcoded_password_funcarg — password values hardcoded as arguments
ADMIN_PASSWORD = "admin@123"      # B105: hardcoded_password_string
SECRET_KEY     = "atm_secret_99"  # B105: hardcoded_password_string

ACCOUNTS = {
    "1001234567": {
        "pin"    : "1234",          # HARDCODED PIN — B105
        "name"   : "Alice Kumar",
        "balance": 15000.00,
        # [VULN-1] Using MD5 to "verify" PIN — B303: insecure hash
        "pin_hash": hashlib.md5(b"1234").hexdigest(),
    },
    "1009876543": {
        "pin"    : "4321",          # HARDCODED PIN
        "name"   : "Bob Sharma",
        "balance": 8500.50,
        "pin_hash": hashlib.md5(b"4321").hexdigest(),
    },
}



def get_account(account_number: str) -> dict:
    """
    Return the account dict for the given account number.
    Raises KeyError if not found.

    [VULN-3] The raw KeyError propagates up and is printed in full,
    leaking internal data structure details to the user.
    """
    return ACCOUNTS[account_number]


def update_balance(account_number: str, new_balance: float) -> None:
    """Update the balance in the in-memory store."""
    ACCOUNTS[account_number]["balance"] = new_balance


def update_pin(account_number: str, new_pin: str) -> None:
    """Overwrite the PIN in the in-memory store."""
    ACCOUNTS[account_number]["pin"] = new_pin
