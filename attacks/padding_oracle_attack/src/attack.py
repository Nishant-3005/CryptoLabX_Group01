"""
attack.py -- Padding Oracle Attack: Byte-by-byte Plaintext Recovery
====================================================================
Lab 7 | CryptoLabX Group 01 | 22CPP307

This module implements the core padding oracle attack.
It does NOT import or use the AES key directly.
It only calls oracle.query() which returns True/False.

Algorithm overview:
    For each ciphertext block C_i (attacked using previous block C_{i-1}):
        For each byte position j from 15 down to 0:
            pad_value = 16 - j
            Set already-known bytes in crafted block to produce pad_value
            Brute-force byte j: try all 256 values
            When oracle says valid -> deduce intermediate value
            Compute plaintext byte = intermediate XOR original previous block byte

Mathematical basis:
    I_i[j] = AES_K_inv(C_i)[j]              (intermediate value, fixed but unknown)
    P_i[j] = I_i[j] XOR C_{i-1}[j]          (original plaintext)
    P'_i[j] = I_i[j] XOR C'_{i-1}[j]        (plaintext with modified prev block)

    When oracle accepts: P'_i[j] = pad_value
    Therefore:  I_i[j]  = pad_value XOR C'_{i-1}[j]
                P_i[j]  = I_i[j] XOR C_{i-1}[j]
"""

BLOCK_SIZE = 16

# ANSI colour helpers
W = "\033[1m"; C_CLR = "\033[96m"; G = "\033[92m"
Y = "\033[93m"; R = "\033[91m"; X = "\033[0m"


def split_blocks(data: bytes) -> list:
    """
    Split data into BLOCK_SIZE (16-byte) blocks.

    Args:
        data: bytes whose length is a multiple of BLOCK_SIZE
    Returns:
        list of bytes objects, each 16 bytes long
    """
    return [data[i:i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]


def attack_block(prev_block: bytes, target_block: bytes, oracle) -> bytes:
    """
    Recover the plaintext of target_block using the padding oracle.

    Args:
        prev_block   : The ciphertext block immediately before target_block
                       (or IV if target_block is the first ciphertext block)
        target_block : The 16-byte ciphertext block to attack
        oracle       : Object with .query(iv_and_ct: bytes) -> bool method

    Returns:
        16-byte plaintext of target_block

    Algorithm:
        For byte_pos from 15 down to 0:
            pad_value = 16 - byte_pos
            Build crafted_prev where known bytes produce pad_value
            Brute-force crafted_prev[byte_pos] over 0..255
            When oracle accepts -> intermediate[byte_pos] = pad_value XOR guess
            plaintext[byte_pos] = intermediate[byte_pos] XOR prev_block[byte_pos]
    """
    intermediate = bytearray(BLOCK_SIZE)
    plaintext = bytearray(BLOCK_SIZE)

    for byte_pos in range(BLOCK_SIZE - 1, -1, -1):
        pad_value = BLOCK_SIZE - byte_pos   # 0x01, 0x02, ..., 0x10

        # Build crafted previous block
        crafted = bytearray(BLOCK_SIZE)

        # Set already-recovered positions to produce correct padding
        for k in range(byte_pos + 1, BLOCK_SIZE):
            crafted[k] = intermediate[k] ^ pad_value

        found = False
        for guess in range(256):
            crafted[byte_pos] = guess

            # Query oracle with: [crafted_prev (as IV) | target_block (as CT)]
            test_data = bytes(crafted) + bytes(target_block)

            if oracle.query(test_data):
                # Edge case for last byte: verify it's truly 0x01 padding
                # and not a coincidental multi-byte valid padding
                if byte_pos == BLOCK_SIZE - 1:
                    # Flip the byte before to check if padding is still valid
                    verify = bytearray(crafted)
                    verify[byte_pos - 1] ^= 0x01
                    if not oracle.query(bytes(verify) + bytes(target_block)):
                        continue  # false positive — this was multi-byte padding

                intermediate[byte_pos] = pad_value ^ guess
                plaintext[byte_pos] = intermediate[byte_pos] ^ prev_block[byte_pos]
                found = True
                break

        if not found:
            print(f"  {R}[!] Failed to recover byte at position {byte_pos}{X}")
            plaintext[byte_pos] = ord('?')

    return bytes(plaintext)


def padding_oracle_attack(iv: bytes, ciphertext: bytes, oracle) -> bytes:
    """
    Full padding oracle attack: recover all plaintext from ciphertext.

    The attack works by treating each pair of adjacent blocks
    (prev_block, target_block) as a 2-block message and attacking
    the target block by manipulating the previous block and querying
    the oracle.

    Args:
        iv         : 16-byte initialization vector
        ciphertext : The encrypted data (must be a multiple of 16 bytes)
        oracle     : Padding oracle object with .query(data) -> bool method

    Returns:
        Recovered plaintext with PKCS#7 padding stripped

    The function prints detailed progress as each block is recovered.
    """
    blocks = split_blocks(ciphertext)
    all_blocks = [iv] + blocks

    recovered = b""
    total_blocks = len(blocks)

    print(f"\n{C_CLR}{'=' * 60}{X}")
    print(f"{W}  PADDING ORACLE ATTACK{X}")
    print(f"{C_CLR}{'=' * 60}{X}")
    print(f"  Ciphertext blocks : {total_blocks}")
    print(f"  Bytes to recover  : {total_blocks * BLOCK_SIZE}")

    for i in range(1, len(all_blocks)):
        prev_block = all_blocks[i - 1]
        target_block = all_blocks[i]

        block_start_queries = oracle.query_count
        block_pt = attack_block(prev_block, target_block, oracle)
        block_queries = oracle.query_count - block_start_queries

        recovered += block_pt

        print(f"\n{Y}  Block {i}/{total_blocks}:{X}")
        print(f"  Oracle queries : {block_queries}")
        print(f"  Recovered hex  : {block_pt.hex()}")
        try:
            text_repr = block_pt.decode('utf-8', errors='replace')
            # Replace non-printable chars for display
            display = ""
            for ch in text_repr:
                if ch.isprintable() or ch in ('\n', '\r', '\t'):
                    display += ch
                else:
                    display += f"\\x{ord(ch):02x}"
            print(f"  Recovered text : {display}")
        except Exception:
            print(f"  Recovered text : (non-printable)")

    # Strip PKCS#7 padding from recovered plaintext
    pad_len = recovered[-1]
    if 1 <= pad_len <= BLOCK_SIZE and all(b == pad_len for b in recovered[-pad_len:]):
        print(f"\n  {G}Stripping {pad_len} bytes of PKCS#7 padding{X}")
        recovered = recovered[:-pad_len]
    else:
        print(f"\n  {Y}Warning: final block padding looks unusual (pad byte = {pad_len:#04x}){X}")

    print(f"\n{G}{W}  Attack complete!{X}")
    print(f"  Total oracle queries : {oracle.query_count}")
    print(f"  Recovered plaintext  : {recovered.decode('utf-8', errors='replace')}")
    print(f"{C_CLR}{'=' * 60}{X}\n")

    return recovered
