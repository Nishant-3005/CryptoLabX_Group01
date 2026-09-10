"""
kasiski_analysis.py -- Kasiski Examination for Vigenere Key Length Discovery
=============================================================================
Lab 6 | CryptoLabX Group 01 | 22CPP307

The Kasiski Examination (1863) finds repeated sequences in the ciphertext and
measures the distances between their occurrences. If the key length is m, then
any repeated plaintext fragment encrypted with the same key segment will produce
an identical ciphertext fragment. The distance between these repetitions will be
a multiple of m. By finding the GCD (or common factors) of all such distances,
we can determine the most likely key length.

Steps:
    1. find_repeated_patterns()  -- locate sequences appearing 2+ times
    2. calculate_distances()     -- compute gaps between repetitions
    3. find_factors()            -- factor each distance (likely multiples of key len)
    4. kasiski_analysis()        -- count factor frequencies; top count = key length
"""

from collections import Counter

# ANSI colour helpers
W = "\033[1m"
C = "\033[96m"
G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
X = "\033[0m"


# ─────────────────────────────────────────────────────────────────────────────
def find_repeated_patterns(ciphertext: str, min_length: int = 3) -> dict:
    """
    Scan ciphertext for repeated sequences of length >= min_length.

    For each starting position i and each length L in [min_length, min_length+2]:
        - Extract substring ciphertext[i : i+L]
        - Record position i for that substring
    Filter: keep only substrings that appear at 2 or more positions.

    Args:
        ciphertext : Clean uppercase ciphertext (no spaces)
        min_length : Minimum pattern length to consider (default 3)

    Returns:
        dict mapping pattern (str) -> list of starting positions (list[int])

    Example:
        {"QSV": [12, 78], "QSVH": [12, 78]}
    """
    n        = len(ciphertext)
    seen: dict[str, list[int]] = {}

    for i in range(n):
        for length in range(min_length, min_length + 3):   # 3, 4, 5
            if i + length > n:
                break
            pattern = ciphertext[i:i + length]
            if pattern not in seen:
                seen[pattern] = []
            seen[pattern].append(i)

    # Keep only patterns that appear at 2+ distinct positions
    repeated = {pat: positions for pat, positions in seen.items()
                if len(positions) >= 2}
    return repeated


# ─────────────────────────────────────────────────────────────────────────────
def calculate_distances(pattern_positions: dict) -> dict:
    """
    For each repeated pattern, compute the distance(s) between consecutive
    occurrences.

    Args:
        pattern_positions: dict returned by find_repeated_patterns()

    Returns:
        dict mapping pattern (str) -> list of distances (list[int])

    Example:
        {"QSV": [12, 78]} -> {"QSV": [66]}
        If 3 occurrences at [12, 78, 168]: -> {"QSV": [66, 90]}
    """
    distances: dict[str, list[int]] = {}
    for pattern, positions in pattern_positions.items():
        dists = []
        for j in range(1, len(positions)):
            dists.append(positions[j] - positions[j - 1])
        if dists:
            distances[pattern] = dists
    return distances


# ─────────────────────────────────────────────────────────────────────────────
def find_factors(n: int) -> list:
    """
    Find all factors of n that are > 1 and <= 20 (practical key length limit).

    Args:
        n: A positive integer (a distance between repeated patterns)

    Returns:
        Sorted list of integer factors of n in the range [2, 20]

    Example:
        find_factors(90) -> [2, 3, 5, 6, 9, 10, 15, 18]
        find_factors(66) -> [2, 3, 6, 11]  (11 > 20 excluded? No, 11<=20)
                         -> [2, 3, 6, 11]
    """
    return sorted([i for i in range(2, min(n + 1, 21)) if n % i == 0])


# ─────────────────────────────────────────────────────────────────────────────
def kasiski_analysis(ciphertext: str) -> list:
    """
    Full Kasiski examination pipeline.

    Steps:
        1. find_repeated_patterns(ciphertext)
        2. calculate_distances(patterns)
        3. For each distance, call find_factors()
        4. Aggregate factor frequencies with Counter
        5. Return factors sorted by frequency (descending)

    Prints a formatted analysis report as it runs.

    Args:
        ciphertext: Clean uppercase ciphertext

    Returns:
        list of tuples [(key_length, frequency_count), ...]
        sorted by frequency_count descending
    """
    print(f"\n{C}{'='*60}{X}")
    print(f"{W}  KASISKI EXAMINATION{X}")
    print(f"{C}{'='*60}{X}")
    print(f"  Ciphertext length : {len(ciphertext)} letters")

    # Step 1: Find repeated patterns
    patterns  = find_repeated_patterns(ciphertext, min_length=3)
    distances = calculate_distances(patterns)

    if not patterns:
        print(f"  {R}No repeated patterns found (ciphertext may be too short).{X}")
        return []

    print(f"\n{Y}  Repeated Patterns Found ({len(patterns)} total):{X}")
    print(f"  {'Pattern':<12} {'Positions':<30} {'Distances'}")
    print(f"  {'-'*60}")

    # Show top patterns by number of occurrences (most repeated first)
    top = sorted(patterns.items(), key=lambda kv: len(kv[1]), reverse=True)[:15]
    for pat, positions in top:
        dists = distances.get(pat, [])
        pos_str  = str(positions[:4]) + ("..." if len(positions) > 4 else "")
        dist_str = str(dists[:4])  + ("..." if len(dists) > 4 else "")
        print(f"  {pat:<12} {pos_str:<30} {dist_str}")

    # Step 3 & 4: Collect all distances, factor each, count
    factor_counter: Counter = Counter()
    all_distances = []

    for dists in distances.values():
        for d in dists:
            if d > 1:
                all_distances.append(d)
                for f in find_factors(d):
                    factor_counter[f] += 1

    print(f"\n{Y}  All Distances Collected: {sorted(set(all_distances))[:20]}{X}")
    print(f"\n{Y}  Factor Frequency Table (candidate key lengths):{X}")
    print(f"  {'Factor':<10} {'Frequency':<12} {'Bar'}")
    print(f"  {'-'*45}")

    factor_list = sorted(factor_counter.items(), key=lambda x: x[1], reverse=True)
    max_freq    = factor_list[0][1] if factor_list else 1

    for factor, freq in factor_list[:12]:
        bar    = "#" * int(freq / max_freq * 20)
        marker = f"  {G}<-- TOP{X}" if factor == factor_list[0][0] else ""
        print(f"  {factor:<10} {freq:<12} {bar}{marker}")

    # Step 5: Return sorted by frequency
    print(f"\n{G}  [+] Top candidate key lengths: "
          f"{[f for f, _ in factor_list[:5]]}{X}")
    print(f"{C}{'='*60}{X}\n")

    return factor_list
