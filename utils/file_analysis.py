"""
utils/file_analysis.py
----------------------
Task 4: Reads a text file and computes statistical information.

Provides:
    - analyze_file(filepath) -> dict
    - display_analysis(stats, filepath)
"""

import os
from collections import Counter


def analyze_file(filepath: str) -> dict:
    """
    Read a text file and compute:
      - total characters (including whitespace)
      - total words
      - total lines
      - unique characters (set of all characters found)
      - letter frequency (only A-Z, case-insensitive, sorted by count desc)

    Returns a dictionary with all stats, or raises FileNotFoundError.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines  = content.splitlines()
    words  = content.split()
    chars  = list(content)

    # Only count alphabetic characters for letter frequency
    letters = [ch.upper() for ch in content if ch.isalpha()]
    freq    = Counter(letters)

    return {
        "filepath"       : filepath,
        "total_chars"    : len(chars),
        "total_words"    : len(words),
        "total_lines"    : len(lines),
        "unique_chars"   : sorted(set(chars)),        # includes spaces, punctuation
        "unique_char_count": len(set(chars)),
        "letter_freq"    : freq.most_common(),        # list of (letter, count) tuples
        "total_letters"  : len(letters),
    }


def display_analysis(stats: dict) -> None:
    """Pretty-print the analysis results to the terminal."""
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"
    LINE   = "-" * 60

    filename = os.path.basename(stats["filepath"])

    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  FILE ANALYSIS REPORT{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")
    print(f"  {BOLD}File:{RESET}              {filename}")
    print(f"  {BOLD}Total Characters:{RESET}  {stats['total_chars']}")
    print(f"  {BOLD}Total Words:{RESET}       {stats['total_words']}")
    print(f"  {BOLD}Total Lines:{RESET}       {stats['total_lines']}")
    print(f"  {BOLD}Unique Characters:{RESET} {stats['unique_char_count']}")
    print(f"{CYAN}{LINE}{RESET}")

    print(f"\n  {BOLD}{YELLOW}LETTER FREQUENCY (Top 10):{RESET}")
    print(f"  {'Letter':<8} {'Count':<8} {'Percentage':<10} Bar")
    print(f"  {'-'*50}")

    total = stats["total_letters"] or 1  # avoid division by zero
    for letter, count in stats["letter_freq"][:10]:
        pct     = (count / total) * 100
        bar_len = int(pct / 1.5)          # scale bar width
        bar     = f"{GREEN}{'#' * bar_len}{RESET}"
        print(f"  {letter:<8} {count:<8} {pct:<9.2f}%  {bar}")

    print(f"\n  {BOLD}Unique chars found:{RESET}")
    # Print unique chars in a readable grid (exclude newlines for display)
    display_chars = [
        repr(c)[1:-1] if c in ('\n', '\r', '\t') else c
        for c in stats["unique_chars"]
    ]
    row = "  "
    for ch in display_chars:
        row += f"{ch} "
        if len(row) > 55:
            print(row)
            row = "  "
    if row.strip():
        print(row)

    print(f"\n{CYAN}{'=' * 60}{RESET}\n")
