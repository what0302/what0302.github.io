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
#
# This utility ONLY processes the five explicitly listed
# training files inside:
#
# ~/Desktop/RansomDemo/targets
#
# It does not recursively scan the filesystem.
# ============================================================


ROOT = (
    Path.home()
    / "Desktop"
    / "RansomDemo"
)

TARGET_DIR = (
    ROOT
    / "targets"
)

BACKUP_DIR = (
    ROOT
    / ".safety_backup"
)

RUNTIME_DIR = (
    ROOT
    / ".runtime"
)

LOG_FILE = (
    ROOT
    / "demo_log.txt"
)

CHECKSUM_FILE = (
    ROOT
    / "checksums.json"
)

PRIVATE_KEY_FILE = (
    RUNTIME_DIR
    / "private.pem"
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
# LOGGING
# ============================================================

def write_log(message):

    ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = (
        f"{timestamp} "
        f"{message}"
    )

    print(line)

    with LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            line + "\n"
        )


# ============================================================
# SHA-256
# ============================================================

def sha256_file(path):

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as f:

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


# ============================================================
# LOAD ORIGINAL CHECKSUMS
# ============================================================

def load_expected_checksums():

    if not CHECKSUM_FILE.exists():

        write_log(
            "[VERIFY-WARNING] "
            "checksums.json not found"
        )

        return {}

    try:

        checksums = json.loads(
            CHECKSUM_FILE.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(
            checksums,
            dict
        ):

            raise ValueError(
                "Checksum database is not a dictionary"
            )

        write_log(
            "[VERIFY] "
            "Original checksum database loaded"
        )

        return checksums

    except Exception as error:

        write_log(
            "[VERIFY-ERROR] "
            f"Could not load checksum database: {error}"
        )

        return {}


# ============================================================
# BASIC LAB VALIDATION
# ============================================================

def validate_environment():

    if not ROOT.exists():

        write_log(
            "[FATAL] "
            "RansomDemo directory does not exist"
        )

        return False

    if not TARGET_DIR.exists():

        write_log(
            "[FATAL] "
            "Training target directory does not exist"
        )

        return False

    if not PRIVATE_KEY_FILE.exists():

        write_log(
            "[FATAL] "
            "RSA private key not found"
        )

        return False

    return True


# ============================================================
# DECRYPT ONE DEMO FILE
# ============================================================

def decrypt_file(
    filename,
    expected_checksums
):

    encrypted = (
        TARGET_DIR
        / (filename + ".unt")
    )

    output = (
        TARGET_DIR
        / filename
    )

    temporary = (
        TARGET_DIR
        / (filename + ".recovering")
    )


    # --------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------

    if not encrypted.exists():

        write_log(
            "[SKIP] "
            f"{filename}.unt not found"
        )

        return False


    if encrypted.is_symlink():

        write_log(
            "[SKIP] "
            f"Symlink rejected: {filename}.unt"
        )

        return False


    if output.exists():

        write_log(
            "[WARNING] "
            f"Original filename already exists: {filename}"
        )

        return False


    # --------------------------------------------------------
    # Load RSA private key
    # --------------------------------------------------------

    private_key = RSA.import_key(
        PRIVATE_KEY_FILE.read_bytes()
    )


    # --------------------------------------------------------
    # Read .unt file
    # --------------------------------------------------------

    with encrypted.open(
        "rb"
    ) as f:

        # MAGIC HEADER
        magic = f.read(
            len(MAGIC)
        )

        if magic != MAGIC:

            raise ValueError(
                "Invalid UNT training file header"
            )


        # RSA encrypted AES key length
        encrypted_key_length_bytes = (
            f.read(2)
        )

        if len(
            encrypted_key_length_bytes
        ) != 2:

            raise ValueError(
                "Invalid encrypted AES key length field"
            )


        encrypted_key_length = (
            int.from_bytes(
                encrypted_key_length_bytes,
                "big"
            )
        )


        if encrypted_key_length <= 0:

            raise ValueError(
                "Invalid encrypted AES key length"
            )


        # RSA encrypted AES key
        encrypted_aes_key = (
            f.read(
                encrypted_key_length
            )
        )


        if len(
            encrypted_aes_key
        ) != encrypted_key_length:

            raise ValueError(
                "Incomplete encrypted AES key"
            )


        # AES-GCM nonce length
        nonce_length_bytes = (
            f.read(1)
        )


        if len(
            nonce_length_bytes
        ) != 1:

            raise ValueError(
                "Invalid nonce length field"
            )


        nonce_length = (
            int.from_bytes(
                nonce_length_bytes,
                "big"
            )
        )


        if nonce_length <= 0:

            raise ValueError(
                "Invalid AES-GCM nonce length"
            )


        # Nonce
        nonce = f.read(
            nonce_length
        )


        if len(nonce) != nonce_length:

            raise ValueError(
                "Incomplete AES-GCM nonce"
            )


        # Authentication tag length
        tag_length_bytes = (
            f.read(1)
        )


        if len(
            tag_length_bytes
        ) != 1:

            raise ValueError(
                "Invalid authentication tag length field"
            )


        tag_length = (
            int.from_bytes(
                tag_length_bytes,
                "big"
            )
        )


        if tag_length <= 0:

            raise ValueError(
                "Invalid AES-GCM authentication tag length"
            )


        # Authentication tag
        tag = f.read(
            tag_length
        )


        if len(tag) != tag_length:

            raise ValueError(
                "Incomplete AES-GCM authentication tag"
            )


        # Remaining bytes = ciphertext
        ciphertext = f.read()


    # --------------------------------------------------------
    # RSA-OAEP: recover AES key
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
    # Write temporary recovery file
    # --------------------------------------------------------

    temporary.write_bytes(
        plaintext
    )


    # --------------------------------------------------------
    # SHA-256 verification
    # --------------------------------------------------------

    recovered_hash = (
        sha256_file(
            temporary
        )
    )


    expected_hash = (
        expected_checksums.get(
            filename
        )
    )


    if expected_hash:

        if recovered_hash != expected_hash:

            if temporary.exists():

                temporary.unlink()

            write_log(
                "[HASH-MISMATCH] "
                f"{filename}"
            )

            raise ValueError(
                "Recovered SHA-256 does not "
                "match the original file"
            )


        write_log(
            "[HASH-MATCH] "
            f"{filename} "
            f"{recovered_hash}"
        )


    else:

        write_log(
            "[HASH-WARNING] "
            f"No original checksum available "
            f"for {filename}"
        )


    # --------------------------------------------------------
    # Restore original filename
    # --------------------------------------------------------

    os.replace(
        temporary,
        output
    )


    # --------------------------------------------------------
    # Remove .unt ONLY after successful:
    #
    # - RSA key recovery
    # - AES-GCM authentication
    # - AES decryption
    # - SHA verification (if baseline exists)
    # --------------------------------------------------------

    encrypted.unlink()


    write_log(
        "[RECOVERED] "
        f"{filename}.unt -> {filename}"
    )


    return True


# ============================================================
# VERIFY ALL RESTORED FILES
# ============================================================

def verify_all_files(
    expected_checksums
):

    verified = 0


    write_log(
        "[VERIFY] "
        "Starting final SHA-256 verification"
    )


    for filename in TARGET_FILES:

        restored = (
            TARGET_DIR
            / filename
        )


        if not restored.exists():

            write_log(
                "[VERIFY-FAILED] "
                f"{filename}: file missing"
            )

            continue


        if restored.is_symlink():

            write_log(
                "[VERIFY-FAILED] "
                f"{filename}: symlink rejected"
            )

            continue


        actual_hash = (
            sha256_file(
                restored
            )
        )


        expected_hash = (
            expected_checksums.get(
                filename
            )
        )


        if expected_hash:

            if actual_hash == expected_hash:

                verified += 1

                write_log(
                    "[VERIFY-PASS] "
                    f"{filename} "
                    f"{actual_hash}"
                )

            else:

                write_log(
                    "[VERIFY-FAILED] "
                    f"{filename}: SHA-256 mismatch"
                )

        else:

            write_log(
                "[VERIFY-WARNING] "
                f"{filename}: baseline unavailable"
            )


    return verified


# ============================================================
# CHECK REMAINING .UNT FILES
# ============================================================

def count_remaining_encrypted_files():

    remaining = 0

    for filename in TARGET_FILES:

        encrypted = (
            TARGET_DIR
            / (filename + ".unt")
        )

        if encrypted.exists():

            remaining += 1

    return remaining


# ============================================================
# OPEN TARGET DIRECTORY
# ============================================================

def open_target_folder():

    try:

        subprocess.Popen(
            [
                "xdg-open",
                str(TARGET_DIR)
            ]
        )

        write_log(
            "[GUI] "
            "Opened recovered files directory"
        )

    except Exception as error:

        write_log(
            "[GUI-WARNING] "
            f"Could not open file manager: {error}"
        )


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
        "=================================================="
    )

    write_log(
        "[RECOVERY-START] "
        "Recovery utility started"
    )


    # --------------------------------------------------------
    # Validate controlled lab
    # --------------------------------------------------------

    if not validate_environment():

        print()

        print(
            "Recovery environment validation failed."
        )

        return


    # --------------------------------------------------------
    # Load original hashes
    # --------------------------------------------------------

    expected_checksums = (
        load_expected_checksums()
    )


    # --------------------------------------------------------
    # Decrypt five explicitly defined files
    # --------------------------------------------------------

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
                "[RECOVERY-FAILED] "
                f"{filename}: {error}"
            )


    write_log(
        "[STATUS] "
        f"Files recovered: "
        f"{recovered}/"
        f"{len(TARGET_FILES)}"
    )


    # --------------------------------------------------------
    # Final SHA-256 validation
    # --------------------------------------------------------

    verified = (
        verify_all_files(
            expected_checksums
        )
    )


    write_log(
        "[STATUS] "
        f"SHA-256 verified: "
        f"{verified}/"
        f"{len(TARGET_FILES)}"
    )


    # --------------------------------------------------------
    # Check remaining .unt
    # --------------------------------------------------------

    remaining = (
        count_remaining_encrypted_files()
    )


    write_log(
        "[STATUS] "
        f"Remaining .unt files: {remaining}"
    )


    print()

    print(
        "=============================================="
    )


    if (
        recovered == len(TARGET_FILES)
        and
        verified == len(TARGET_FILES)
        and
        remaining == 0
    ):

        print(
            " RECOVERY SUCCESSFUL"
        )

        print()

        print(
            " 5 / 5 FILES RECOVERED"
        )

        print(
            " 5 / 5 SHA-256 VERIFIED"
        )

        print(
            " 0 ENCRYPTED FILES REMAIN"
        )


        write_log(
            "[SUCCESS] "
            "ALL FILES RECOVERED "
            "AND SHA-256 VERIFIED"
        )


    else:

        print(
            " RECOVERY INCOMPLETE"
        )

        print()

        print(
            f" Recovered: "
            f"{recovered}/"
            f"{len(TARGET_FILES)}"
        )

        print(
            f" Verified: "
            f"{verified}/"
            f"{len(TARGET_FILES)}"
        )

        print(
            f" Remaining .unt: "
            f"{remaining}"
        )


        write_log(
            "[WARNING] "
            "Recovery or verification "
            "was incomplete"
        )


    print(
        "=============================================="
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
        "Checksum database:"
    )

    print(
        CHECKSUM_FILE
    )

    print()


    print(
        "Log file:"
    )

    print(
        LOG_FILE
    )

    print()


    # --------------------------------------------------------
    # Automatically open restored files folder
    # --------------------------------------------------------

    open_target_folder()


    write_log(
        "[RECOVERY-END] "
        "Recovery utility finished"
    )


if __name__ == "__main__":

    main()
