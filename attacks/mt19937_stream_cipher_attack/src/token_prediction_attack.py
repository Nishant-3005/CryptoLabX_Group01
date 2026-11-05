"""
token_prediction_attack.py -- Predictable Reset Token Cracker Engine
====================================================================
Lab 10 | CryptoLabX Group 01 | 22CPP307

Mounts an exhaustive search attack against timestamp-seeded reset tokens:
    1. Assumes attacker intercepted or observed a 16-byte hex token
    2. Attacker establishes base observation timestamp T_approx
    3. Evaluates search window: [T_approx - window_seconds, T_approx + window_seconds]
    4. For default window = 300 seconds, search space is 601 candidates
    5. Recovers exact issuance timestamp and regenerates token for verification
"""

import random
import time
import sys
from token_generator import generate_reset_token


def predict_token(
    target_hex_token: str,
    base_timestamp: int,
    window_seconds: int = 300,
    callback=None
) -> dict:
    """
    Search candidate timestamps in [base_timestamp - window_seconds, base_timestamp + window_seconds].
    Generates the corresponding 16-byte token for each candidate seed and compares with target.

    Args:
        target_hex_token: Intercepted token string in hex (32 hex characters).
        base_timestamp: Approximate epoch timestamp (seconds) when request was triggered.
        window_seconds: Search radius in seconds (default: 300 -> +/- 5 minutes).
        callback: Optional callback for search progress tracking.

    Returns:
        dict: Attack metrics, recovered timestamp, candidates tested, and verification.
    """
    start_time = time.time()
    normalized_target = target_hex_token.lower().strip()

    t_start = base_timestamp - window_seconds
    t_end = base_timestamp + window_seconds
    total_candidates = (t_end - t_start) + 1

    candidates_tested = 0
    recovered_timestamp = None

    for candidate_t in range(t_start, t_end + 1):
        candidates_tested += 1

        # Periodic progress notification
        if callback and candidates_tested % 100 == 0:
            callback(candidates_tested, total_candidates)

        # Generate candidate token
        rng = random.Random(candidate_t)
        candidate_bytes = bytes(rng.getrandbits(8) for _ in range(16))
        candidate_hex = candidate_bytes.hex()

        if candidate_hex == normalized_target:
            recovered_timestamp = candidate_t
            break

    elapsed = time.time() - start_time

    if recovered_timestamp is not None:
        # Verify by regenerating token with recovered timestamp
        _, verify_bytes, verify_hex = generate_reset_token(recovered_timestamp)
        verified = (verify_hex == normalized_target)

        return {
            "recovered_timestamp": recovered_timestamp,
            "recovered_timestamp_hex": f"0x{recovered_timestamp:08X}",
            "base_timestamp": base_timestamp,
            "time_offset_seconds": recovered_timestamp - base_timestamp,
            "candidates_tested": candidates_tested,
            "total_window_candidates": total_candidates,
            "search_window_range": (t_start, t_end),
            "elapsed_seconds": elapsed,
            "target_token": normalized_target,
            "regenerated_token": verify_hex,
            "verified": verified,
        }
    else:
        return {
            "recovered_timestamp": None,
            "recovered_timestamp_hex": None,
            "base_timestamp": base_timestamp,
            "time_offset_seconds": None,
            "candidates_tested": candidates_tested,
            "total_window_candidates": total_candidates,
            "search_window_range": (t_start, t_end),
            "elapsed_seconds": elapsed,
            "target_token": normalized_target,
            "regenerated_token": None,
            "verified": False,
        }


if __name__ == "__main__":
    print("=" * 72)
    print("CryptoLabX Lab 10 - Part B: Predictable Token Attack Demo")
    print("=" * 72)

    # 1. Simulate target web server generating token
    current_time = int(time.time())
    # Introduce realistic network / queue latency (e.g. 35 seconds delta)
    simulated_server_time = current_time + 35
    _, target_raw, target_hex = generate_reset_token(simulated_server_time)

    print("\n[+] Victim Action (Password Reset Requested):")
    print(f"    Observed Intercepted Token : {target_hex}")
    print(f"    True Server Timestamp      : {simulated_server_time}")

    print("\n[*] Attacker Perspective:")
    print(f"    Attacker Client Time (T_0) : {current_time}")
    print(f"    Search Interval Window     : [{current_time - 300}, {current_time + 300}] (+/- 300s)")
    print(f"    Total Candidate Timestamps : 601 candidates")
    print("    Running token prediction search...")

    res = predict_token(target_hex, current_time, window_seconds=300)

    print("\n[*] Token Prediction Results:")
    print("-" * 72)
    print(f"    Target Token               : {res['target_token']}")
    print(f"    Recovered Timestamp        : {res['recovered_timestamp']} ({res['recovered_timestamp_hex']})")
    print(f"    True Match Confirmed       : {'YES' if res['recovered_timestamp'] == simulated_server_time else 'NO'}")
    print(f"    Latency / Offset from T_0  : {res['time_offset_seconds']:+d} seconds")
    print(f"    Candidates Tested          : {res['candidates_tested']} / {res['total_window_candidates']}")
    print(f"    Search Execution Time      : {res['elapsed_seconds'] * 1000.0:.3f} ms")
    print(f"    Regenerated Token (Check)  : {res['regenerated_token']}")
    print(f"    Attack Verification        : [{'PASS' if res['verified'] else 'FAIL'}]")
    print("=" * 72)
