"""
statistical_tests.py -- Comprehensive Statistical Testing Suite for Randomness
==============================================================================
Lab 9 | CryptoLabX Group 01 | 22CPP307

Implements statistical randomness tests compliant with NIST SP 800-22 and
standard cryptographic randomness evaluation criteria:
    1. Monobit Frequency Test (bit-level 0 vs 1 distribution)
    2. Byte Frequency Distribution & Chi-Square (chi^2) Goodness-of-Fit Test
    3. Runs Test (oscillation & transition analysis)
    4. Serial Correlation / Autocorrelation (Lag-1 and Lag-k dependence)
    5. Shannon Entropy Calculation (information density per byte)
    6. Monte Carlo Estimation of Pi (spatial uniformity in 2D unit square)
"""

import math
import os
import struct
import sys
import time
from collections import Counter


def monobit_test(data: bytes) -> dict:
    """
    NIST SP 800-22 Frequency (Monobit) Test.

    Tests whether the number of ones and zeros in the sequence are
    approximately equal, as expected for a truly random sequence.

    Args:
        data: raw bytes to test

    Returns:
        dict with total_bits, ones_count, zeros_count, proportion,
        statistic, p_value, and passed (bool).
    """
    total_bytes = len(data)
    total_bits = total_bytes * 8

    # Fast bit counting using bin().count()
    ones_count = sum(bin(b).count('1') for b in data)
    zeros_count = total_bits - ones_count

    # S_n is sum of X_i where X_i = +1 for bit 1, -1 for bit 0
    s_n = abs(ones_count - zeros_count)
    s_obs = s_n / math.sqrt(total_bits)

    # p-value = erfc(s_obs / sqrt(2))
    p_value = math.erfc(s_obs / math.sqrt(2))
    passed = p_value >= 0.01

    return {
        "test_name": "Monobit Frequency Test",
        "total_bits": total_bits,
        "ones_count": ones_count,
        "zeros_count": zeros_count,
        "proportion_ones": ones_count / total_bits,
        "statistic": s_obs,
        "p_value": p_value,
        "passed": passed
    }


def byte_frequency_test(data: bytes) -> dict:
    """
    Byte-Frequency Distribution and Chi-Square Goodness-of-Fit Test.

    Evaluates whether each of the 256 possible byte values (0..255)
    occurs with equal probability (1/256).

    Args:
        data: raw bytes to test

    Returns:
        dict with counts, expected, chi2_statistic, degrees_of_freedom,
        p_value, and passed (bool).
    """
    total_bytes = len(data)
    expected_count = total_bytes / 256.0

    counts = [0] * 256
    for b in data:
        counts[b] += 1

    # Chi-square statistic: sum((observed - expected)^2 / expected)
    chi2_stat = sum(((c - expected_count) ** 2) / expected_count for c in counts)
    df = 255

    # Wilson-Hilferty transformation approximation for Chi-Square p-value
    # Z = ((chi2/df)^(1/3) - (1 - 2/(9*df))) / sqrt(2/(9*df))
    w = 2.0 / (9.0 * df)
    z = (((chi2_stat / df) ** (1.0 / 3.0)) - (1.0 - w)) / math.sqrt(w)
    # p-value is upper tail: P(Z > z) = 0.5 * erfc(z / sqrt(2))
    p_value = 0.5 * math.erfc(z / math.sqrt(2))
    p_value = max(0.0, min(1.0, p_value))

    # Typical acceptable chi2 range for df=255 at alpha=0.01 is [198.5, 319.4]
    passed = 0.01 <= p_value <= 0.99

    return {
        "test_name": "Byte Frequency Chi-Square Test",
        "total_bytes": total_bytes,
        "expected_per_byte": expected_count,
        "min_byte_count": min(counts),
        "max_byte_count": max(counts),
        "chi2_statistic": chi2_stat,
        "degrees_of_freedom": df,
        "p_value": p_value,
        "passed": passed,
        "byte_counts": counts
    }


def runs_test(data: bytes) -> dict:
    """
    NIST SP 800-22 Runs Test.

    Evaluates whether the number of runs of consecutive ones and zeros
    oscillates as expected for a random sequence.

    Args:
        data: raw bytes to test

    Returns:
        dict with total_runs, p_value, and passed (bool).
    """
    total_bytes = len(data)
    total_bits = total_bytes * 8

    # Fast bit stream representation or iterative run counting
    ones = sum(bin(b).count('1') for b in data)
    pi = ones / total_bits

    # Pre-test condition from NIST SP 800-22
    if abs(pi - 0.5) >= (2.0 / math.sqrt(total_bits)):
        return {
            "test_name": "Runs Test",
            "total_runs": 0,
            "statistic": 0.0,
            "p_value": 0.0,
            "passed": False,
            "reason": "Failed pre-test: proportion of ones deviates significantly from 0.5"
        }

    # Count runs (transitions between bits)
    # A run starts at bit 0 and increments every time bit[i] != bit[i-1]
    transitions = 0
    prev_bit = (data[0] >> 7) & 1
    for byte in data:
        for shift in range(7, -1, -1):
            bit = (byte >> shift) & 1
            if bit != prev_bit:
                transitions += 1
                prev_bit = bit

    v_n = transitions + 1  # Total runs = transitions + 1

    # Theoretical expected runs and standard deviation
    expected_runs = 2.0 * total_bits * pi * (1.0 - pi) + 1.0
    denom = 2.0 * math.sqrt(2.0 * total_bits) * pi * (1.0 - pi)

    if denom == 0:
        p_value = 0.0
    else:
        statistic = abs(v_n - expected_runs) / denom
        p_value = math.erfc(statistic)

    passed = p_value >= 0.01

    return {
        "test_name": "Runs Test",
        "total_runs": v_n,
        "expected_runs": expected_runs,
        "p_value": p_value,
        "passed": passed
    }


def autocorrelation_test(data: bytes, max_lag: int = 10) -> dict:
    """
    Serial Correlation (Autocorrelation) Test.

    Computes correlation coefficient r_k between byte X_i and byte X_{i+k}
    for lags k = 1..max_lag. For independent white noise, r_k ~ N(0, 1/N).

    Args:
        data: raw bytes to test
        max_lag: maximum lag to compute (default: 10)

    Returns:
        dict with lag coefficients, 95% confidence bounds, and passed (bool).
    """
    n = len(data)
    mean = sum(data) / n

    # Variance denominator: sum((x_i - mean)^2)
    var_sum = sum((b - mean) ** 2 for b in data)
    if var_sum == 0:
        return {"test_name": "Autocorrelation", "passed": False, "correlations": {}}

    correlations = {}
    passed_all = True
    # 99% confidence threshold: 2.576 / sqrt(N) for multi-lag hypothesis testing
    bound_99 = 2.576 / math.sqrt(n)
    bound_95 = 1.96 / math.sqrt(n)

    for k in range(1, max_lag + 1):
        cov_sum = sum((data[i] - mean) * (data[i + k] - mean) for i in range(n - k))
        r_k = cov_sum / var_sum
        correlations[k] = r_k
        if abs(r_k) > bound_99:
            passed_all = False

    return {
        "test_name": "Serial Autocorrelation Test",
        "lag_1_correlation": correlations.get(1, 0.0),
        "correlations": correlations,
        "confidence_bound_95": bound_95,
        "confidence_bound_99": bound_99,
        "passed": passed_all
    }


def shannon_entropy(data: bytes) -> dict:
    """
    Calculates Shannon Entropy in bits per byte.

    Formula: H(X) = - sum(p_i * log2(p_i))
    Theoretical maximum for 256 byte outcomes is log2(256) = 8.000000 bits/byte.

    Args:
        data: raw bytes to test

    Returns:
        dict with entropy, max_entropy, and ratio.
    """
    n = len(data)
    counts = Counter(data)

    entropy = 0.0
    for count in counts.values():
        p = count / n
        if p > 0:
            entropy -= p * math.log2(p)

    return {
        "test_name": "Shannon Entropy",
        "entropy": entropy,
        "max_entropy": 8.0,
        "entropy_deficit": 8.0 - entropy,
        "passed": entropy >= 7.9990  # Extremely close to theoretical 8.0
    }


def monte_carlo_pi(data: bytes) -> dict:
    """
    Monte Carlo Estimation of Pi.

    Treats successive 2-byte pairs as (x, y) coordinates normalized to [0, 1).
    Counts fraction of points inside quarter circle: x^2 + y^2 <= 1.0.
    Approximates pi ~ 4 * (inside / total_points).

    Args:
        data: raw bytes to test

    Returns:
        dict with estimated_pi, true_pi, absolute_error, and percentage_error.
    """
    # Use 2 bytes for x and 2 bytes for y -> 4 bytes per 2D point
    num_points = len(data) // 4
    if num_points == 0:
        return {"test_name": "Monte Carlo Pi", "passed": False}

    inside = 0
    # Process in chunks of 4 bytes
    for i in range(0, num_points * 4, 4):
        # 16-bit unsigned integers: 0..65535
        x = (data[i] << 8 | data[i + 1]) / 65535.0
        y = (data[i + 2] << 8 | data[i + 3]) / 65535.0
        if (x * x + y * y) <= 1.0:
            inside += 1

    pi_estimate = 4.0 * (inside / num_points)
    true_pi = math.pi
    abs_err = abs(pi_estimate - true_pi)
    pct_err = (abs_err / true_pi) * 100.0

    # For ~262,144 points, standard error is ~ 4 * sqrt(p*(1-p)/N) ~ 0.003
    passed = pct_err <= 0.5  # Error within 0.5%

    return {
        "test_name": "Monte Carlo Pi Estimation",
        "total_points": num_points,
        "points_inside": inside,
        "estimated_pi": pi_estimate,
        "true_pi": true_pi,
        "absolute_error": abs_err,
        "percentage_error": pct_err,
        "passed": passed
    }


def evaluate_dataset(filepath: str) -> dict:
    """
    Runs the full statistical randomness test suite on a binary file.

    Args:
        filepath: path to .bin file

    Returns:
        comprehensive dictionary containing all test results.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "rb") as f:
        data = f.read()

    file_size = len(data)

    t0 = time.time()
    monobit = monobit_test(data)
    byte_freq = byte_frequency_test(data)
    runs = runs_test(data)
    autocorr = autocorrelation_test(data, max_lag=10)
    entropy = shannon_entropy(data)
    mc_pi = monte_carlo_pi(data)
    total_time = time.time() - t0

    all_passed = (
        monobit["passed"] and
        byte_freq["passed"] and
        runs["passed"] and
        autocorr["passed"] and
        entropy["passed"] and
        mc_pi["passed"]
    )

    return {
        "filepath": filepath,
        "filename": os.path.basename(filepath),
        "file_size_bytes": file_size,
        "execution_time_seconds": total_time,
        "all_passed": all_passed,
        "monobit": monobit,
        "byte_frequency": byte_freq,
        "runs": runs,
        "autocorrelation": autocorr,
        "entropy": entropy,
        "monte_carlo_pi": mc_pi
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python statistical_tests.py <path_to_binary_file>")
        sys.exit(1)

    target_file = sys.argv[1]
    res = evaluate_dataset(target_file)

    print("=" * 72)
    print(f"Randomness Evaluation Results: {res['filename']}")
    print(f"File Size: {res['file_size_bytes']:,} bytes | Tested in {res['execution_time_seconds']:.3f}s")
    print("=" * 72)
    print(f"[*] Monobit Proportion (1s) : {res['monobit']['proportion_ones']:.6f} | p-val: {res['monobit']['p_value']:.4f} [{'PASS' if res['monobit']['passed'] else 'FAIL'}]")
    print(f"[*] Chi-Square (df=255)     : {res['byte_frequency']['chi2_statistic']:.2f} | p-val: {res['byte_frequency']['p_value']:.4f} [{'PASS' if res['byte_frequency']['passed'] else 'FAIL'}]")
    print(f"[*] Runs Test Total Runs    : {res['runs']['total_runs']:,} | p-val: {res['runs']['p_value']:.4f} [{'PASS' if res['runs']['passed'] else 'FAIL'}]")
    print(f"[*] Shannon Entropy         : {res['entropy']['entropy']:.6f} / 8.000000 bits/byte [{'PASS' if res['entropy']['passed'] else 'FAIL'}]")
    print(f"[*] Autocorrelation (Lag-1) : {res['autocorrelation']['lag_1_correlation']:+.6f} (99% Bound: +/-{res['autocorrelation']['confidence_bound_99']:.6f}) [{'PASS' if res['autocorrelation']['passed'] else 'FAIL'}]")
    print(f"[*] Monte Carlo Pi Estimate : {res['monte_carlo_pi']['estimated_pi']:.5f} (Error: {res['monte_carlo_pi']['percentage_error']:.3f}%) [{'PASS' if res['monte_carlo_pi']['passed'] else 'FAIL'}]")
    print("-" * 72)
    print(f"OVERALL EVALUATION STATUS   : [{'PASS - STATISTICALLY RANDOM' if res['all_passed'] else 'FAIL'}]")
    print("=" * 72)
