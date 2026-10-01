"""
main.py -- Padding Oracle Attack: Full Demonstration
=====================================================
Lab 7 | CryptoLabX Group 01 | 22CPP307

Workflow:
    1. Generate a random AES-128 key (kept secret -- never passed to attack)
    2. Encrypt a plaintext message using AES-CBC
    3. Create a padding oracle (has key internally, attack cannot see it)
    4. Run the padding oracle attack on the ciphertext
    5. Display recovered plaintext, query count, and verification
    6. Save results to outputs/results.txt

Usage:
    cd attacks/padding_oracle_attack/src
    python main.py
"""

import os
import sys
import datetime

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aes_cbc import (
    generate_key, aes_cbc_encrypt, aes_cbc_decrypt,
    pkcs7_pad, BLOCK_SIZE
)
from padding_oracle import PaddingOracle
from attack import padding_oracle_attack, split_blocks

# ANSI colours
W = "\033[1m"; C = "\033[96m"; G = "\033[92m"
Y = "\033[93m"; R = "\033[91m"; M = "\033[95m"; X = "\033[0m"

_OUTPUTS_PATH = os.path.join(_SRC, "..", "outputs", "results.txt")

# ── The plaintext to encrypt (attacker does NOT know this) ──────────────────

PLAINTEXT = (
    b"The Padding Oracle Attack demonstrates that even strong ciphers "
    b"like AES can be broken if the system leaks padding validity."
)


def banner() -> None:
    """Print the coloured lab banner."""
    os.system("")  # enable ANSI on Windows
    print(f"""
{C}{W}
  ============================================================
   Padding Oracle Attack -- AES-CBC Cryptanalysis
   CryptoLabX | Lab 7 | Group 01 | 22CPP307
  ============================================================
{X}""")


def print_hex_blocks(data: bytes, label: str = "", indent: int = 4) -> None:
    """Print data as hex in 16-byte blocks with optional label."""
    blocks = [data[i:i+BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]
    prefix = " " * indent
    if label:
        print(f"{prefix}{Y}{label}:{X}")
    for i, block in enumerate(blocks):
        print(f"{prefix}  Block {i}: {block.hex()}")


def demonstrate_attack() -> tuple:
    """
    Run the full padding oracle attack demonstration.

    Returns:
        (recovered_plaintext, oracle_query_count, verified)
    """
    # ── Step 1: Generate secret key ─────────────────────────────────────────
    print(f"{Y}Step 1: Generating secret AES-128 key...{X}")
    key = generate_key(16)
    print(f"  Key generated (hidden from attacker)")
    print(f"  Key hex: {M}[REDACTED -- not available to attack]{X}")

    # ── Step 2: Encrypt the plaintext ───────────────────────────────────────
    print(f"\n{Y}Step 2: Encrypting plaintext with AES-CBC...{X}")
    iv, ciphertext = aes_cbc_encrypt(PLAINTEXT, key)

    num_blocks = len(ciphertext) // BLOCK_SIZE
    padded = pkcs7_pad(PLAINTEXT)

    print(f"  Plaintext     : {PLAINTEXT.decode()}")
    print(f"  Plaintext len : {len(PLAINTEXT)} bytes")
    print(f"  Padded len    : {len(padded)} bytes ({num_blocks} blocks)")
    print(f"  IV            : {iv.hex()}")
    print_hex_blocks(ciphertext, "Ciphertext")

    # ── Step 3: Create the padding oracle ───────────────────────────────────
    print(f"\n{Y}Step 3: Creating padding oracle...{X}")
    oracle = PaddingOracle(key)
    print(f"  Oracle created (key locked inside, not accessible)")
    print(f"  Oracle interface: oracle.query(iv + ct) -> True/False")

    # Quick sanity check
    legit = oracle.query(iv + ciphertext)
    print(f"  Sanity check (legit ciphertext): {G}{legit}{X}")
    oracle.reset_count()  # don't count sanity checks

    # ── Step 4: Run the attack ──────────────────────────────────────────────
    print(f"\n{Y}Step 4: Running Padding Oracle Attack...{X}")
    print(f"  The attack will recover plaintext byte-by-byte")
    print(f"  using ONLY the oracle (no key access)")

    recovered = padding_oracle_attack(iv, ciphertext, oracle)
    total_queries = oracle.query_count

    # ── Step 5: Verify ──────────────────────────────────────────────────────
    print(f"{Y}Step 5: Verifying result...{X}")
    verified = (recovered == PLAINTEXT)

    print(f"\n{C}{'=' * 60}{X}")
    print(f"{W}  VERIFICATION{X}")
    print(f"{C}{'=' * 60}{X}")
    print(f"  Original plaintext : {PLAINTEXT.decode()}")
    print(f"  Recovered plaintext: {recovered.decode('utf-8', errors='replace')}")
    print(f"  Match              : ", end="")
    if verified:
        print(f"{G}{W}PASS -- Plaintext recovered correctly!{X}")
    else:
        print(f"{R}{W}FAIL -- Mismatch detected{X}")
    print(f"  Total oracle queries: {total_queries}")
    print(f"  Bytes recovered     : {len(recovered)}")
    print(f"{C}{'=' * 60}{X}")

    # ── Step 6: Analysis ────────────────────────────────────────────────────
    print(f"\n{Y}Step 6: Attack Analysis{X}")
    print(f"\n  {W}Why modifying the previous ciphertext block works:{X}")
    print(f"  In CBC decryption: P_i = AES_K_inv(C_i) XOR C_{{i-1}}")
    print(f"  The intermediate value I_i = AES_K_inv(C_i) is fixed.")
    print(f"  By changing C_{{i-1}} to C', we control P'_i = I_i XOR C'")
    print(f"  When oracle says 'valid padding', we deduce I_i,")
    print(f"  then compute P_i = I_i XOR original_C_{{i-1}}")

    print(f"\n  {W}Query statistics:{X}")
    print(f"  Total queries     : {total_queries}")
    print(f"  Ciphertext blocks : {num_blocks}")
    print(f"  Queries per block : ~{total_queries // num_blocks}")
    print(f"  Theoretical max   : {256 * 16 * num_blocks} (256 x 16 x {num_blocks})")
    print(f"  Efficiency        : {total_queries / (256 * 16 * num_blocks) * 100:.1f}%")

    return recovered, total_queries, verified


def save_results(recovered: bytes, query_count: int, verified: bool) -> None:
    """Save results to outputs/results.txt."""
    os.makedirs(os.path.dirname(_OUTPUTS_PATH), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    num_blocks = (len(PLAINTEXT) + BLOCK_SIZE) // BLOCK_SIZE  # approx

    with open(_OUTPUTS_PATH, "w", encoding="utf-8") as f:
        f.write("Padding Oracle Attack -- Results\n")
        f.write("CryptoLabX Group 01 | Lab 7 | 22CPP307\n")
        f.write(f"Run timestamp: {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Original plaintext  : {PLAINTEXT.decode()}\n")
        f.write(f"Plaintext length    : {len(PLAINTEXT)} bytes\n")
        f.write(f"Ciphertext blocks   : {num_blocks}\n\n")
        f.write(f"Recovered plaintext : {recovered.decode('utf-8', errors='replace')}\n")
        f.write(f"Match               : {'PASS' if verified else 'FAIL'}\n\n")
        f.write(f"Total oracle queries: {query_count}\n")
        f.write(f"Queries per block   : ~{query_count // max(num_blocks, 1)}\n")
        f.write(f"Theoretical max     : {256 * 16 * num_blocks}\n\n")
        f.write("Attack Explanation:\n")
        f.write("  In CBC decryption, P_i = AES_inv(C_i) XOR C_{i-1}.\n")
        f.write("  By modifying C_{i-1} and checking if the oracle accepts\n")
        f.write("  the padding, we can deduce the intermediate value I_i\n")
        f.write("  byte-by-byte, then XOR with the real C_{i-1} to get P_i.\n\n")
        f.write("Prevention:\n")
        f.write("  1. Use authenticated encryption (AES-GCM) instead of AES-CBC\n")
        f.write("  2. Apply Encrypt-then-MAC (HMAC verified before decryption)\n")
        f.write("  3. Return generic errors -- never reveal padding validity\n\n")
        f.write("Group 01 | Nishant (2024UCP1773) | Lokesh Saini (2024UCP1505)\n")

    print(f"\n  {G}Results saved -> {os.path.relpath(_OUTPUTS_PATH)}{X}")


def main() -> None:
    banner()
    recovered, query_count, verified = demonstrate_attack()
    print(f"\n{Y}Step 7: Saving results...{X}")
    save_results(recovered, query_count, verified)
    print(f"\n  {G}{W}Done!{X}")


if __name__ == "__main__":
    main()
