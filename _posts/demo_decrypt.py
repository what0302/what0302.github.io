from pathlib import Path
from datetime import datetime
import hashlib
import json
import os
import subprocess

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256


# ============================================================
# CONTROLLED SECURITY TRAINING RECOVERY UTILITY
# ============================================================

ROOT = Path.home() / "Desktop" / "RansomDemo"

TARGET_DIR = ROOT / "targets"
BACKUP_DIR = ROOT / ".safety_backup"
RUNTIME_DIR = ROOT / ".runtime"

LOG_FILE = ROOT / "demo_log.txt"
CHECKSUM_FILE = ROOT / "checksums.json"

PRIVATE_KEY_FILE = (
    RUNTIME_DIR / "private.pem"
)

TARGET_FILES = [
    "personal_notes.txt",
    "employees.csv",
    "config.json",
    "project_plan.md",
    "application.log",
]

MAGIC = b"UNTDEMO1"


# ============================================================
# UTILITIES
# ============================================================

def write_log(message):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = f"{timestamp} {message}"

    print(line)

    ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    with LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            line + "\n"
        )


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:

        while True:

            chunk = f.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def load_expected_checksums():
    if not CHECKSUM_FILE.exists():

        write_log(
            "[VERIFY-WARNING] "
            "Checksum database missing"
        )

        return {}

    try:

        data = json.loads(
            CHECKSUM_FILE.read_text(
                encoding="utf-8"
            )
        )

        return data

    except Exception as error:

        write_log(
            f"[VERIFY-ERROR] "
            f"Could not read checksum database: {error}"
        )

        return {}


# ============================================================
# DECRYPT ONE FILE
# ============================================================

def decrypt_file(
    filename,
    expected_checksums
):
    encrypted = (
        TARGET_DIR /
        (filename + ".unt")
    )

    output = (
        TARGET_DIR /
        filename
    )

    if not encrypted.exists():

        write_log(
            f"[SKIP] "
            f"{filename}.unt not found"
        )

        return False

    if encrypted.is_symlink():

        write_log(
            f"[SKIP] "
            f"Symlink rejected: {filename}.unt"
        )

        return False

    private_key = RSA.import_key(
        PRIVATE_KEY_FILE.read_bytes()
    )

    with encrypted.open(
        "rb"
    ) as f:

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        magic = f.read(
            len(MAGIC)
        )

        if magic != MAGIC:

            raise ValueError(
                "Invalid UNT training file header"
            )

        # ----------------------------------------------------
        # Wrapped AES key
        # ----------------------------------------------------

        encrypted_key_length = (
            int.from_bytes(
                f.read(2),
                "big"
            )
        )

        if encrypted_key_length <= 0:

            raise ValueError(
                "Invalid encrypted AES key length"
            )

        encrypted_aes_key = f.read(
            encrypted_key_length
        )

        # ----------------------------------------------------
        # Nonce
        # ----------------------------------------------------

        nonce_length = (
            int.from_bytes(
                f.read(1),
                "big"
            )
        )

        if nonce_length <= 0:

            raise ValueError(
                "Invalid AES-GCM nonce"
            )

        nonce = f.read(
            nonce_length
        )

        # ----------------------------------------------------
        # Authentication tag
        # ----------------------------------------------------

        tag_length = (
            int.from_bytes(
                f.read(1),
                "big"
            )
        )

        if tag_length <= 0:

            raise ValueError(
                "Invalid AES-GCM authentication tag"
            )

        tag = f.read(
            tag_length
        )

        ciphertext = f.read()

    # --------------------------------------------------------
    # Recover AES key using RSA private key
    # --------------------------------------------------------

    rsa_cipher = PKCS1_OAEP.new(
        private_key,
        hashAlgo=SHA256
    )

    aes_key = rsa_cipher.decrypt(
        encrypted_aes_key
    )

    # --------------------------------------------------------
    # AES-GCM authenticated decryption
    # --------------------------------------------------------

    aes_cipher = AES.new(
        aes_key,
        AES.MODE_GCM,
        nonce=nonce
    )

    plaintext = (
        aes_cipher.decrypt_and_verify(
            ciphertext,
            tag
        )
    )

    # --------------------------------------------------------
    # Write to temporary file first
    # --------------------------------------------------------

    temporary = TARGET_DIR / (
        filename + ".recovering"
    )

    temporary.write_bytes(
        plaintext
    )

    # --------------------------------------------------------
    # SHA-256 verification
    # --------------------------------------------------------

    recovered_hash = sha256_file(
        temporary
    )

    expected_hash = (
        expected_checksums.get(
            filename
        )
    )

    if expected_hash:

        if recovered_hash != expected_hash:

            temporary.unlink(
                missing_ok=True
            )

            write_log(
                f"[HASH-MISMATCH] "
                f"{filename}"
            )

            raise ValueError(
                "Recovered file SHA-256 "
                "does not match original"
            )

        write_log(
            f"[HASH-MATCH] "
            f"{filename} {recovered_hash}"
        )

    else:

        write_log(
            f"[HASH-WARNING] "
            f"No original hash available for {filename}"
        )

    # --------------------------------------------------------
    # Only now restore the visible file
    # --------------------------------------------------------

    os.replace(
        temporary,
        output
    )

    # Delete encrypted version only after:
    #
    # 1. RSA unwrap succeeded
    # 2. AES-GCM authentication succeeded
    # 3. SHA-256 verification succeeded
    #
    encrypted.unlink()

    write_log(
        f"[RECOVERED] "
        f"{filename}.unt -> {filename}"
    )

    return True


# ============================================================
# FINAL VERIFICATION
# ============================================================

def verify_all_files(
    expected_checksums
):
    matched = 0

    write_log(
        "[VERIFY] Starting final SHA-256 verification"
    )

    for filename in TARGET_FILES:

        restored = (
            TARGET_DIR /
            filename
        )

        if not restored.exists():

            write_log(
                f"[VERIFY-FAILED] "
                f"{filename}: missing"
            )

            continue

        actual = sha256_file(
            restored
        )

        expected = (
            expected_checksums.get(
                filename
            )
        )

        if expected and actual == expected:

            matched += 1

            write_log(
                f"[VERIFY-PASS] "
                f"{filename} {actual}"
            )

        elif expected:

            write_log(
                f"[VERIFY-FAILED] "
                f"{filename}: SHA-256 mismatch"
            )

        else:

            write_log(
                f"[VERIFY-WARNING] "
                f"{filename}: baseline unavailable"
            )

    return matched


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print(
        "=============================================="
    )

    print(
        " SECURITY AWARENESS TRAINING RECOVERY"
    )

    print(
        "=============================================="
    )

    print()

    write_log(
        "[RECOVERY-START] Recovery utility started"
    )

    if not PRIVATE_KEY_FILE.exists():

        write_log(
            "[FATAL] RSA private key not found"
        )

        print(
            "Training private key not found."
        )

        return

    expected_checksums = (
        load_expected_checksums()
    )

    recovered = 0

    for filename in TARGET_FILES:

        try:

            if decrypt_file(
                filename,
                expected_checksums
            ):

                recovered += 1

        except Exception as error:

            write_log(
                f"[RECOVERY-FAILED] "
                f"{filename}: {error}"
            )

    print()

    write_log(
        f"[STATUS] Files recovered: "
        f"{recovered}/{len(TARGET_FILES)}"
    )

    verified = verify_all_files(
        expected_checksums
    )

    print()

    write_log(
        f"[STATUS] SHA-256 verified: "
        f"{verified}/{len(TARGET_FILES)}"
    )

    if (
        recovered == len(TARGET_FILES)
        and
        verified == len(TARGET_FILES)
    ):

        write_log(
            "[SUCCESS] "
            "ALL FILES RECOVERED AND SHA-256 VERIFIED"
        )

        print()
        print(
            "=============================================="
        )

        print(
            " RECOVERY SUCCESSFUL"
        )

        print(
            " 5 / 5 FILES RECOVERED"
        )

        print(
            " 5 / 5 SHA-256 VERIFIED"
        )

        print(
            "=============================================="
        )

    else:

        write_log(
            "[WARNING] "
            "Recovery or verification was incomplete"
        )

    print()

    print(
        "Safety backup:"
    )

    print(
        BACKUP_DIR
    )

    print()

    print(
        "Log file:"
    )

    print(
        LOG_FILE
    )

    # Open the folder so the restored
    # files can be visually inspected.
    try:

        subprocess.Popen(
            [
                "xdg-open",
                str(TARGET_DIR)
            ]
        )

    except Exception as error:

        write_log(
            f"[GUI-WARNING] "
            f"Could not open file manager: {error}"
        )

    write_log(
        "[RECOVERY-END] Recovery utility finished"
    )


if __name__ == "__main__":
    main()
