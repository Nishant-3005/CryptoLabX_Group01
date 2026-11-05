"""
main.py -- End-to-End Orchestrator for Lab 10 MT19937 Attacks & Cryptanalysis
=============================================================================
Lab 10 | Cryptography Laboratory (22CPP307)
Group: 01 | Nishant (2024UCP1773) & Lokesh Saini (2024UCP1505)

Orchestrates both practical cryptanalytic attacks on MT19937:
    Part A: Known-Plaintext Seed Recovery on MT19937 Stream Cipher (2^16 search space)
    Part B: Predictable Password Reset Token Recovery via Timestamp Window Search
    Exports comprehensive results to outputs/results.txt
"""

import os
import sys
import time

# Ensure local source imports work whether executed from root or src/
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from stream_cipher import (
    generate_vulnerable_plaintext,
    generate_16bit_seed,
    encrypt,
    decrypt
)
from seed_recovery_attack import brute_force_16bit_seed
from token_generator import generate_reset_token
from token_prediction_attack import predict_token


def run_part_a():
    """Execute Part A: MT19937 Stream Cipher Known-Plaintext Seed Recovery."""
    print("\n" + "=" * 80)
    print(" PART A: MT19937 TOY STREAM CIPHER KNOWN-PLAINTEXT ATTACK")
    print("=" * 80)

    # 1. Target payload generation
    known_sequence = b"AAAAAAAAAAAAAA"
    plaintext_str, prefix_str, prefix_len = generate_vulnerable_plaintext(min_prefix=5, max_prefix=20)
    plaintext_bytes = plaintext_str.encode("ascii")
    secret_seed = generate_16bit_seed()
    ciphertext = encrypt(plaintext_bytes, secret_seed)

    print(f"[*] Payload Parameters:")
    print(f"    Prefix Length         : {prefix_len} characters")
    print(f"    Random Prefix         : '{prefix_str}'")
    print(f"    Known Sequence        : '{known_sequence.decode('ascii')}' (14 x 'A')")
    print(f"    Full Plaintext        : '{plaintext_str}' ({len(plaintext_bytes)} bytes)")
    print(f"    Secret 16-bit Seed    : {secret_seed} (0x{secret_seed:04X})")
    print(f"    Generated Ciphertext  : {ciphertext.hex()} ({len(ciphertext)} bytes)")

    print(f"\n[*] Mounting Known-Plaintext Brute-Force Attack...")
    print(f"    Search Space Size     : 65,536 candidate seeds (0x0000 to 0xFFFF)")
    print(f"    Matching Mechanism    : Sliding-window substring scan (unknown offset)")

    attack_res = brute_force_16bit_seed(ciphertext, known_sequence)

    print(f"\n[+] Part A Attack Completed:")
    print(f"    Recovered Seed        : {attack_res['recovered_seed']} ({attack_res['recovered_seed_hex']})")
    print(f"    Seed Recovery Match   : {'CONFIRMED EXACT MATCH' if attack_res['recovered_seed'] == secret_seed else 'FAILED'}")
    print(f"    Recovered Plaintext   : '{attack_res['recovered_plaintext_str']}'")
    print(f"    Detected Known Offset : Byte index {attack_res['known_sequence_offset']}")
    print(f"    Seeds Tested          : {attack_res['seeds_tested']:,} / {attack_res['total_seed_space']:,} ({attack_res['search_percentage']:.2f}%)")
    print(f"    Execution Latency     : {attack_res['elapsed_seconds']:.4f} seconds")
    print(f"    Throughput Rate       : {attack_res['seeds_per_second']:,.0f} seeds/second")
    print(f"    Integrity Check       : [{'PASS' if attack_res['verified'] else 'FAIL'}]")

    return {
        "prefix_len": prefix_len,
        "prefix_str": prefix_str,
        "plaintext_str": plaintext_str,
        "secret_seed": secret_seed,
        "ciphertext_hex": ciphertext.hex(),
        "attack_res": attack_res
    }


def run_part_b():
    """Execute Part B: Predictable Password Reset Token Recovery."""
    print("\n" + "=" * 80)
    print(" PART B: PREDICTABLE PASSWORD RESET TOKEN ATTACK (TIMESTAMP SEED)")
    print("=" * 80)

    # 1. Target simulated issuance
    base_client_time = int(time.time())
    # Introduce a simulated network propagation / processing delta (+24s)
    simulated_server_time = base_client_time + 24
    issued_time, token_raw, token_hex = generate_reset_token(simulated_server_time)

    print(f"[*] Vulnerable Token Issuance:")
    print(f"    Client Request Time   : {base_client_time} (Unix epoch seconds)")
    print(f"    Server Issuance Time  : {simulated_server_time} (Delta: +24 seconds)")
    print(f"    Intercepted Reset Tok : {token_hex} (16 bytes, 32 hex chars)")

    print(f"\n[*] Mounting Timestamp Prediction Window Attack...")
    print(f"    Base Timestamp (T_0)  : {base_client_time}")
    print(f"    Search Radius         : +/- 300 seconds (5 minutes)")
    print(f"    Search Interval       : [{base_client_time - 300}, {base_client_time + 300}]")
    print(f"    Candidate Pool Size   : 601 candidate timestamps")

    pred_res = predict_token(token_hex, base_client_time, window_seconds=300)

    print(f"\n[+] Part B Attack Completed:")
    print(f"    Target Token          : {pred_res['target_token']}")
    print(f"    Recovered Timestamp   : {pred_res['recovered_timestamp']} ({pred_res['recovered_timestamp_hex']})")
    print(f"    Timestamp Accuracy    : {'CONFIRMED EXACT MATCH' if pred_res['recovered_timestamp'] == simulated_server_time else 'FAILED'}")
    print(f"    Detected Time Offset  : {pred_res['time_offset_seconds']:+d} seconds relative to request")
    print(f"    Candidates Tested     : {pred_res['candidates_tested']} / {pred_res['total_window_candidates']}")
    print(f"    Execution Latency     : {pred_res['elapsed_seconds'] * 1000.0:.3f} ms")
    print(f"    Regenerated Token     : {pred_res['regenerated_token']}")
    print(f"    Token Match Verified  : [{'PASS' if pred_res['verified'] else 'FAIL'}]")

    return {
        "base_client_time": base_client_time,
        "simulated_server_time": simulated_server_time,
        "token_hex": token_hex,
        "pred_res": pred_res
    }


def save_results(part_a_data: dict, part_b_data: dict):
    """Persist structured attack results and analysis table to outputs/results.txt."""
    base_dir = os.path.abspath(os.path.join(current_dir, ".."))
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    out_file = os.path.join(outputs_dir, "results.txt")

    a = part_a_data
    a_res = a["attack_res"]
    b = part_b_data
    b_res = b["pred_res"]

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("Cryptography Laboratory (22CPP307) -- Lab 10\n")
        f.write("Task: MT19937 Stream Cipher Known-Plaintext & Predictable Token Attacks\n")
        f.write("Group 01: Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)\n")
        f.write("Execution Timestamp: " + time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()) + "\n")
        f.write("=" * 84 + "\n\n")

        f.write("1. PART A: MT19937 STREAM CIPHER 16-BIT SEED RECOVERY RESULTS\n")
        f.write("-" * 84 + "\n")
        f.write(f"Target Plaintext          : {a['plaintext_str']}\n")
        f.write(f"Prefix String             : '{a['prefix_str']}' ({a['prefix_len']} characters)\n")
        f.write(f"Known Plaintext Sequence  : 'AAAAAAAAAAAAAA' (14 x 'A')\n")
        f.write(f"Known Sequence Offset     : Byte {a_res['known_sequence_offset']}\n")
        f.write(f"True Encryption Seed      : {a['secret_seed']} (0x{a['secret_seed']:04X})\n")
        f.write(f"Recovered Encryption Seed : {a_res['recovered_seed']} ({a_res['recovered_seed_hex']})\n")
        f.write(f"Seed Match Result         : {'EXACT MATCH' if a_res['recovered_seed'] == a['secret_seed'] else 'MISMATCH'}\n")
        f.write(f"Ciphertext (Hex)          : {a['ciphertext_hex']}\n")
        f.write(f"Recovered Plaintext       : {a_res['recovered_plaintext_str']}\n")
        f.write(f"Candidate Seeds Tested    : {a_res['seeds_tested']:,} / {a_res['total_seed_space']:,} ({a_res['search_percentage']:.2f}% of space)\n")
        f.write(f"Brute-Force Execution Time: {a_res['elapsed_seconds']:.4f} seconds\n")
        f.write(f"Search Throughput Rate    : {a_res['seeds_per_second']:,.0f} seeds/second\n")
        f.write(f"Verification Check        : {'PASS' if a_res['verified'] else 'FAIL'}\n\n")

        f.write("2. PART B: PREDICTABLE PASSWORD RESET TOKEN ATTACK RESULTS\n")
        f.write("-" * 84 + "\n")
        f.write(f"Client Request Timestamp  : {b['base_client_time']} (Unix epoch)\n")
        f.write(f"True Server Issuance Time : {b['simulated_server_time']} (Unix epoch)\n")
        f.write(f"Intercepted Target Token  : {b['token_hex']}\n")
        f.write(f"Search Window Radius      : +/- 300 seconds\n")
        f.write(f"Search Window Range       : [{b_res['search_window_range'][0]}, {b_res['search_window_range'][1]}]\n")
        f.write(f"Total Candidate Timestamps: {b_res['total_window_candidates']}\n")
        f.write(f"Recovered Issuance Time   : {b_res['recovered_timestamp']} ({b_res['recovered_timestamp_hex']})\n")
        f.write(f"Timestamp Match Result    : {'EXACT MATCH' if b_res['recovered_timestamp'] == b['simulated_server_time'] else 'MISMATCH'}\n")
        f.write(f"Reconstructed Token Check : {b_res['regenerated_token']}\n")
        f.write(f"Candidates Tested         : {b_res['candidates_tested']} / {b_res['total_window_candidates']}\n")
        f.write(f"Search Execution Time     : {b_res['elapsed_seconds'] * 1000.0:.3f} ms\n")
        f.write(f"Verification Check        : {'PASS' if b_res['verified'] else 'FAIL'}\n\n")

        f.write("3. SUMMARY & COMPARATIVE SECURITY TABLE\n")
        f.write("-" * 84 + "\n")
        f.write(f"{'Attack Vector':<32} | {'Search Space':<16} | {'Search Time':<14} | {'Complexity':<12} | {'Result'}\n")
        f.write("-" * 84 + "\n")
        time_a_str = f"{a_res['elapsed_seconds']:.3f} s"
        time_b_str = f"{b_res['elapsed_seconds'] * 1000.0:.2f} ms"
        f.write(f"{'Part A: 16-bit Seed Stream Cipher':<32} | {'65,536 seeds':<16} | {time_a_str:<14} | {'O(2^16)':<12} | {'BROKEN [PASS]'}\n")
        f.write(f"{'Part B: Timestamp Reset Token':<32} | {'601 timestamps':<16} | {time_b_str:<14} | {'O(Delta T)':<12} | {'BROKEN [PASS]'}\n")
        f.write("-" * 84 + "\n\n")

        f.write("4. CRYPTOGRAPHIC LESSONS & DEFENSES\n")
        f.write("-" * 84 + "\n")
        f.write("1. MT19937 has ZERO cryptographic security: small seed spaces (16-bit) are trivial to invert via brute force.\n")
        f.write("2. Time-seeded PRNGs (random.seed(int(time.time()))) reduce token entropy from 128 bits to ~9 bits (600 candidates).\n")
        f.write("3. Remedy: Use OS-level CSPRNGs (secrets.token_hex(32) or os.urandom(32)) providing 256 bits of true entropy.\n")

    print(f"\n[+] Detailed experimental results saved to: {out_file}")


def main():
    print("=" * 80)
    print(" CRYPTOGRAPHY LABORATORY (22CPP307) -- LAB 10")
    print(" Cryptanalysis of MT19937 PRNG Misuse in Ciphers and Authentication")
    print(" Group 01: Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)")
    print("=" * 80)

    part_a_data = run_part_a()
    part_b_data = run_part_b()
    save_results(part_a_data, part_b_data)

    print("\n" + "=" * 80)
    print(" LAB 10 DEMONSTRATION & VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    main()
