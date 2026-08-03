"""
main.py — CryptoLabX Toolkit Entry Point
==========================================
Cryptography Laboratory (22CPP307) | Group 01

Task 3 : Menu-driven CLI  (Encrypt / Decrypt / Attack / Analyze / Exit)
Task 4 : File analysis    (via utils/file_analysis.py)
Task 5 : Action logging   (via utils/logger.py)
"""

import os
import glob

from utils.file_analysis import analyze_file, display_analysis
from utils.logger import log_action, log_session_start, show_log

# ─── ANSI colour helpers ────────────────────────────────────────────────────
R   = "\033[0m"       # reset
B   = "\033[1m"       # bold
CYN = "\033[96m"      # cyan
GRN = "\033[92m"      # green
YLW = "\033[93m"      # yellow
RED = "\033[91m"      # red
MGT = "\033[95m"      # magenta


# ─── Banner ─────────────────────────────────────────────────────────────────
_BANNER_ART = (
    "  =====================================================\n"
    "   ____ ____  __ __ ____ ____  ____  __     __   ___ \n"
    "  / ___|  _ \\ \\ V  V /  _ \\_   _|/ __ \\ |    \\ \\ / /\n"
    " | |   | |_) | \\ /\\ /| |_) || | | |  | | |    > V < \n"
    " | |___|  _ <  |  |  ||  __/ | | | |  | | |___|  |  \n"
    "  \\____|_| \\_\\ |__|__||_|    |_|  \\____/|_____|__|  \n"
    "\n"
    "   Cryptography Laboratory Toolkit | Group 01 | 22CPP307\n"
    "  =====================================================\n"
)
BANNER = f"\n{CYN}{B}{_BANNER_ART}{R}\n"


# ─── Menu ────────────────────────────────────────────────────────────────────
def print_menu() -> None:
    print(f"\n{CYN}{'='*52}{R}")
    print(f"{B}   CRYPTOLABX -- MAIN MENU{R}")
    print(f"{CYN}{'-'*52}{R}")
    print(f"   {GRN}[1]{R}  Encrypt     {YLW}(Coming Soon){R}")
    print(f"   {GRN}[2]{R}  Decrypt     {YLW}(Coming Soon){R}")
    print(f"   {GRN}[3]{R}  Attack      {YLW}(Coming Soon){R}")
    print(f"   {GRN}[4]{R}  Analyze File")
    print(f"   {GRN}[5]{R}  View Log")
    print(f"   {RED}[0]{R}  Exit")
    print(f"{CYN}{'═'*52}{R}")


# ─── Analyze sub-menu ────────────────────────────────────────────────────────
def get_dataset_files() -> list[str]:
    """Return a sorted list of .txt files in the datasets/ folder."""
    base    = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(base, "datasets", "*.txt")
    return sorted(glob.glob(pattern))


def handle_analyze() -> None:
    """Let the user pick a file from datasets/ and display its analysis."""
    files = get_dataset_files()
    if not files:
        print(f"\n  {RED}No .txt files found in datasets/ folder.{R}")
        return

    print(f"\n{YLW}  Available files in datasets/:{R}")
    for i, path in enumerate(files, start=1):
        print(f"  {GRN}[{i}]{R}  {os.path.basename(path)}")
    print(f"  {RED}[0]{R}  Back to main menu")

    choice = input(f"\n  {B}Select file number:{R} ").strip()
    if choice == "0":
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
        print(f"  {RED}Invalid selection.{R}")
        return

    filepath = files[int(choice) - 1]
    try:
        stats = analyze_file(filepath)
        display_analysis(stats)
        log_action("ANALYZE", os.path.basename(filepath))
    except FileNotFoundError:
        print(f"  {RED}File not found: {filepath}{R}")
    except Exception as e:
        print(f"  {RED}Error reading file: {e}{R}")


# ─── Coming-soon handler ─────────────────────────────────────────────────────
def coming_soon(feature: str) -> None:
    print(f"\n  {YLW}+------------------------------------------+{R}")
    print(f"  {YLW}|  {MGT}{B}{feature:<40}{R}{YLW}|{R}")
    print(f"  {YLW}|  This module is under development.       |{R}")
    print(f"  {YLW}|  Check back in future lab sessions!      |{R}")
    print(f"  {YLW}+------------------------------------------+{R}")
    log_action(feature.upper().replace(" ", "_"))


# ─── Main loop ───────────────────────────────────────────────────────────────
def main() -> None:
    # Enable ANSI on Windows terminals
    os.system("")

    print(BANNER)
    log_session_start()

    while True:
        print_menu()
        choice = input(f"\n  {B}Enter your choice:{R} ").strip()

        if choice == "1":
            coming_soon("Encrypt")

        elif choice == "2":
            coming_soon("Decrypt")

        elif choice == "3":
            coming_soon("Attack")

        elif choice == "4":
            handle_analyze()

        elif choice == "5":
            show_log()
            log_action("VIEW_LOG")

        elif choice == "0":
            log_action("EXIT")
            print(f"\n  {CYN}Thank you for using CryptoLabX. Goodbye!{R}\n")
            break

        else:
            print(f"\n  {RED}Invalid choice. Please enter 0–5.{R}")


if __name__ == "__main__":
    main()
