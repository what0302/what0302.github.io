from pathlib import Path
import os
import subprocess

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256


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


def decrypt_file(filename):

    encrypted = (
        TARGET_DIR /
        (filename + ".unt")
    )

    output = (
        TARGET_DIR /
        filename
    )

    if not encrypted.exists():

        print(
            f"[SKIP] {filename}: "
            "encrypted file missing"
        )

        return False

    if encrypted.is_symlink():

        print(
            f"[SKIP] {filename}: "
            "symlink rejected"
        )

        return False

    private_key = RSA.import_key(
        PRIVATE_KEY_FILE.read_bytes()
    )

    with encrypted.open(
        "rb"
    ) as f:

        magic = f.read(
            len(MAGIC)
        )

        if magic != MAGIC:

            raise ValueError(
                "Invalid UNT training file"
            )

        encrypted_key_length = (
            int.from_bytes(
                f.read(2),
                "big"
            )
        )

        if encrypted_key_length <= 0:

            raise ValueError(
                "Invalid encrypted key"
            )

        encrypted_aes_key = (
            f.read(
                encrypted_key_length
            )
        )

        nonce_length = (
            int.from_bytes(
                f.read(1),
                "big"
            )
        )

        nonce = f.read(
            nonce_length
        )

        tag_length = (
            int.from_bytes(
                f.read(1),
                "big"
            )
        )

        tag = f.read(
            tag_length
        )

        ciphertext = f.read()

    rsa_cipher = PKCS1_OAEP.new(
        private_key,
        hashAlgo=SHA256
    )

    aes_key = (
        rsa_cipher.decrypt(
            encrypted_aes_key
        )
    )

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

    temporary = (
        TARGET_DIR /
        (filename + ".recovering")
    )

    temporary.write_bytes(
        plaintext
    )

    # Atomic restore.
    os.replace(
        temporary,
        output
    )

    # Remove .unt only after verified recovery.
    encrypted.unlink()

    print(
        f"[RECOVERED] {filename}"
    )

    return True


def main():

    print()
    print(
        "=========================================="
    )

    print(
        " SECURITY TRAINING RECOVERY UTILITY"
    )

    print(
        "=========================================="
    )

    if not PRIVATE_KEY_FILE.exists():

        print(
            "[ERROR] Training private "
            "key not found"
        )

        return

    recovered = 0

    for filename in TARGET_FILES:

        try:

            if decrypt_file(
                filename
            ):

                recovered += 1

        except Exception as error:

            print(
                f"[FAILED] "
                f"{filename}: "
                f"{error}"
            )

    print()

    print(
        f"[+] Recovery completed: "
        f"{recovered}/"
        f"{len(TARGET_FILES)}"
    )

    print()

    if recovered == len(
        TARGET_FILES
    ):

        print(
            "[+] All demo files restored."
        )

    print(
        "[+] Safety backup remains:"
    )

    print(
        f"    {BACKUP_DIR}"
    )

    # Open the folder after recovery
    # so the restored filenames are visible.
    try:

        subprocess.Popen(
            [
                "xdg-open",
                str(TARGET_DIR)
            ]
        )

    except Exception:
        pass


if __name__ == "__main__":
    main()
