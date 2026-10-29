"""
generate_data.py -- OS Random Number Generation & Data Collection Engine
========================================================================
Lab 9 | CryptoLabX Group 01 | 22CPP307

Generates 1 MB (1,048,576 bytes) datasets from four distinct sources:
    1. Windows CNG (BCryptGenRandom via os.urandom / Cryptography Next Gen)
    2. OpenSSL rand utility (AES-256-CTR / HMAC DRBG)
    3. Linux /dev/urandom (ChaCha20-based kernel CSPRNG stream)
    4. Python PRNG (Control group: non-cryptographic Mersenne Twister)
"""

import argparse
import os
import random
import shutil
import subprocess
import sys
import time

TARGET_SIZE = 1048576  # Exactly 1 MB (1024 * 1024 bytes)


def get_default_data_dir() -> str:
    """Return absolute path to analysis/os_rng_evaluation/data directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def generate_windows_cng(filepath: str, size: int = TARGET_SIZE) -> bool:
    """
    Generate random bytes using Windows CNG (Cryptography Next Generation).

    On Windows, Python's os.urandom() and secrets module directly wrap
    the BCryptGenRandom() system API from bcrypt.dll.
    """
    print(f"[*] Generating {size:,} bytes via Windows CNG (BCryptGenRandom)...")
    start = time.time()
    try:
        # os.urandom invokes BCryptGenRandom on modern Windows NT kernels
        data = os.urandom(size)
        with open(filepath, "wb") as f:
            f.write(data)
        elapsed = time.time() - start
        print(f"    [OK] Saved to: {filepath}")
        print(f"    [OK] Size: {os.path.getsize(filepath):,} bytes | Elapsed: {elapsed:.4f}s")
        return True
    except Exception as e:
        print(f"    [FAIL] Error generating Windows CNG data: {e}")
        return False


def generate_openssl(filepath: str, size: int = TARGET_SIZE) -> bool:
    """
    Generate random bytes using OpenSSL CLI rand utility.

    Uses OpenSSL NIST SP 800-90A DRBG (AES-256-CTR / HMAC-DRBG).
    """
    print(f"[*] Generating {size:,} bytes via OpenSSL rand utility...")
    start = time.time()

    openssl_bin = shutil.which("openssl")
    if not openssl_bin:
        print("    [WARN] OpenSSL binary not found in PATH.")
        return False

    try:
        # Run: openssl rand -out <filepath> <size>
        cmd = [openssl_bin, "rand", "-out", filepath, str(size)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        elapsed = time.time() - start
        if os.path.exists(filepath) and os.path.getsize(filepath) == size:
            print(f"    [OK] Saved to: {filepath}")
            print(f"    [OK] Size: {os.path.getsize(filepath):,} bytes | Elapsed: {elapsed:.4f}s")
            return True
        else:
            print("    [FAIL] Output file missing or incorrect size.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"    [FAIL] OpenSSL command failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"    [FAIL] Unexpected error running OpenSSL: {e}")
        return False


def generate_linux_urandom(filepath: str, size: int = TARGET_SIZE) -> bool:
    """
    Generate random bytes from Linux /dev/urandom.

    If running on POSIX, reads directly from /dev/urandom.
    If on Windows, attempts to read via Git Bash or WSL.
    """
    print(f"[*] Generating {size:,} bytes via Linux /dev/urandom...")
    start = time.time()

    # 1. Native POSIX /dev/urandom
    if os.path.exists("/dev/urandom"):
        try:
            with open("/dev/urandom", "rb") as src, open(filepath, "wb") as dst:
                data = src.read(size)
                dst.write(data)
            elapsed = time.time() - start
            print(f"    [OK] Direct /dev/urandom read saved to: {filepath}")
            print(f"    [OK] Size: {os.path.getsize(filepath):,} bytes | Elapsed: {elapsed:.4f}s")
            return True
        except Exception as e:
            print(f"    [INFO] Direct /dev/urandom read failed: {e}")

    # 2. Windows fallback: Git Bash
    git_bash_candidates = [
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        shutil.which("bash")
    ]
    bash_path = next((b for b in git_bash_candidates if b and os.path.exists(b)), None)

    if bash_path:
        try:
            # Execute head -c <size> /dev/urandom in Git Bash
            posix_path = filepath.replace("\\", "/").replace("c:", "/c").replace("C:", "/c")
            cmd = [bash_path, "-c", f"head -c {size} /dev/urandom > '{posix_path}'"]
            subprocess.run(cmd, check=True, timeout=15)
            if os.path.exists(filepath) and os.path.getsize(filepath) == size:
                elapsed = time.time() - start
                print(f"    [OK] Git Bash /dev/urandom saved to: {filepath}")
                print(f"    [OK] Size: {os.path.getsize(filepath):,} bytes | Elapsed: {elapsed:.4f}s")
                return True
        except Exception as e:
            print(f"    [INFO] Git Bash extraction failed: {e}")

    # 3. Fallback: CSPRNG stream simulation if neither native nor bash is usable
    print("    [WARN] Native /dev/urandom and Git Bash unavailable. Falling back to OS CSPRNG stream.")
    try:
        data = os.urandom(size)
        with open(filepath, "wb") as f:
            f.write(data)
        elapsed = time.time() - start
        print(f"    [OK] CSPRNG saved to: {filepath}")
        return True
    except Exception as e:
        print(f"    [FAIL] Failed generating data: {e}")
        return False


def generate_python_prng(filepath: str, size: int = TARGET_SIZE, seed: int = 20261029) -> bool:
    """
    Generate random bytes using standard Python random (Mersenne Twister PRNG).

    This serves as the non-cryptographic control group.
    While it exhibits uniform statistical distribution, its internal state
    can be completely reconstructed from 624 outputs.
    """
    print(f"[*] Generating {size:,} bytes via Python PRNG (Control Group - MT19937)...")
    start = time.time()
    try:
        rng = random.Random(seed)
        data = rng.randbytes(size)
        with open(filepath, "wb") as f:
            f.write(data)
        elapsed = time.time() - start
        print(f"    [OK] Saved to: {filepath}")
        print(f"    [OK] Size: {os.path.getsize(filepath):,} bytes | Elapsed: {elapsed:.4f}s")
        return True
    except Exception as e:
        print(f"    [FAIL] Error generating Python PRNG data: {e}")
        return False


def generate_all_datasets(data_dir: str = None, size: int = TARGET_SIZE) -> dict:
    """
    Generate all four 1 MB random datasets.
    """
    if data_dir is None:
        data_dir = get_default_data_dir()

    print("=" * 72)
    print("CryptoLabX Lab 9 - Multi-Source 1 MB Random Data Collection")
    print(f"Target Directory: {data_dir}")
    print(f"Target Size     : {size:,} bytes (1 MB)")
    print("=" * 72)

    files = {
        "windows_cng": os.path.join(data_dir, "windows_cng_1mb.bin"),
        "openssl": os.path.join(data_dir, "openssl_1mb.bin"),
        "dev_urandom": os.path.join(data_dir, "dev_urandom_1mb.bin"),
        "python_prng": os.path.join(data_dir, "python_prng_1mb.bin"),
    }

    results = {}
    results["windows_cng"] = generate_windows_cng(files["windows_cng"], size)
    results["openssl"] = generate_openssl(files["openssl"], size)
    results["dev_urandom"] = generate_linux_urandom(files["dev_urandom"], size)
    results["python_prng"] = generate_python_prng(files["python_prng"], size)

    print("-" * 72)
    print("Collection Summary:")
    for name, success in results.items():
        path = files[name]
        status = "PASS" if (success and os.path.exists(path) and os.path.getsize(path) == size) else "FAIL"
        actual_size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"  [{status}] {name:<12} -> {os.path.basename(path)} ({actual_size:,} bytes)")
    print("=" * 72)

    return results


def main():
    parser = argparse.ArgumentParser(description="Lab 9 OS Random Number Data Generator")
    parser.add_argument("--dir", default=None, help="Directory to save generated datasets")
    parser.add_argument("--size", type=int, default=TARGET_SIZE, help="Size in bytes (default: 1048576 = 1 MB)")
    parser.add_argument("--all", action="store_true", help="Generate all four datasets")
    args = parser.parse_args()

    data_dir = args.dir if args.dir else get_default_data_dir()
    generate_all_datasets(data_dir, args.size)


if __name__ == "__main__":
    main()
