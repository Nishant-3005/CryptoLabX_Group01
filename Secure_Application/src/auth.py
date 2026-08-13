"""
auth.py — Authentication & PIN Management

  - Login
  - PIN Change

VULNERABILITY EMBEDDED:
  [VULN-1] Hardcoded Credentials
  - PINs are compared against values hardcoded in database.py.
  - No hashing.

  [VULN-3] Information Leakage via Error Messages
  - On login failure the full exception object is printed,
    revealing internal account structure to the attacker.
"""

import traceback
from database import get_account, update_pin


def login() -> tuple[str, dict] | tuple[None, None]:
    """
    Prompt for account number and PIN.
    Returns (account_number, account_dict) on success, (None, None) on failure.

    """
    print("\n  === ATM LOGIN ===")
    account_number = input("  Enter Account Number: ").strip()
    pin            = input("  Enter PIN          : ").strip()

    try:
        account = get_account(account_number)

        if account["pin"] == pin:
            print(f"\n  Welcome, {account['name']}!")
            return account_number, account
        else:
            print("\n  [ERROR] Incorrect PIN.")
            return None, None

    except Exception as e:
        # [VULN-3] Full exception + traceback printed to console
        # Leaks internal key structure: "1001234567", "pin", "balance", etc.
        print(f"\n  [ERROR] Login failed: {e}")
        print(traceback.format_exc())
        return None, None


def change_pin(account_number: str, account: dict) -> None:
    """
    Allow the authenticated user to change their PIN.

    [VULN-2] No complexity rules enforced — PIN can be "0", "aaaa", etc.
    [VULN-1] New PIN stored in plain text immediately.
    """
    print("\n  === CHANGE PIN ===")
    current = input("  Enter current PIN : ").strip()

    if current != account["pin"]:
        print("  [ERROR] Current PIN is incorrect.")
        return

    new_pin     = input("  Enter new PIN     : ").strip()
    confirm_pin = input("  Confirm new PIN   : ").strip()

    # [VULN-2] No length check, no digit-only check, no complexity policy
    if new_pin != confirm_pin:
        print("  [ERROR] PINs do not match.")
        return

    update_pin(account_number, new_pin)
    # [VULN-3] Leaks the new PIN value back in the confirmation message
    print(f"  PIN successfully changed to: {new_pin}")
