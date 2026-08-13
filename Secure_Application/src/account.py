"""
account.py — Core ATM Transactions

Core Functionalities Covered for authenticated users:
  - Balance Inquiry
  - Withdrawal
  - Deposit

VULNERABILITY EMBEDDED:
  [VULN-2] Improper Input Validation
  - Withdrawal and deposit amounts are not checked for:
      * Negative values        → allows "withdrawing" -500 to ADD funds
      * Zero                   → pointless transaction allowed
      * Non-numeric strings    → raises unhandled ValueError
      * Exceeding balance      → no overdraft protection enforced consistently

"""

import traceback
from database import get_account, update_balance


def balance_inquiry(account_number: str) -> None:
    """Display the current account balance."""
    account = get_account(account_number)
    print(f"\n  Account  : {account_number}")
    print(f"  Name     : {account['name']}")
    # [VULN-3] Printing full internal account dict leaks all fields
    print(f"  Balance  : Rs. {account['balance']:.2f}")


def withdraw(account_number: str, account: dict) -> None:
    """
    Process a cash withdrawal.

    [VULN-2] No input validation:
      - Negative amount accepted → effectively deposits money

    """
    print("\n  === WITHDRAWAL ===")
    raw = input("  Enter amount to withdraw: Rs. ").strip()

    try:
        # [VULN-2] No check: is raw numeric? is it > 0? is it <= balance?
        amount = float(raw)

        current_balance = account["balance"]

        # [VULN-2] Overdraft check is present but bypassable with a negative amount:
        #   e.g. withdraw(-500) passes this check and INCREASES balance
        if amount > current_balance:
            print(f"  [ERROR] Insufficient funds. Balance: Rs. {current_balance:.2f}")
            return

        new_balance = current_balance - amount
        update_balance(account_number, new_balance)
        account["balance"] = new_balance
        print(f"  Rs. {amount:.2f} dispensed. New Balance: Rs. {new_balance:.2f}")

    except Exception as e:
        # [VULN-3] Full traceback printed — leaks module paths, variable names
        print(f"  [ERROR] Transaction failed: {e}")
        print(traceback.format_exc())


def deposit(account_number: str, account: dict) -> None:
    """
    Process a cash deposit.

    [VULN-2] Same validation gaps as withdraw():
      - Negative deposit reduces the balance (effectively a withdrawal)
      - Zero deposit silently accepted
      - Non-numeric input causes full traceback (VULN-3)
    """
    print("\n  === DEPOSIT ===")
    raw = input("  Enter amount to deposit: Rs. ").strip()

    try:
        # [VULN-2] No positivity check, no upper limit
        amount = float(raw)

        new_balance = account["balance"] + amount
        update_balance(account_number, new_balance)
        account["balance"] = new_balance
        print(f"  Rs. {amount:.2f} deposited. New Balance: Rs. {new_balance:.2f}")

    except Exception as e:
        # [VULN-3] Full traceback
        print(f"  [ERROR] Transaction failed: {e}")
        print(traceback.format_exc())
