from pathlib import Path
import os

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256


ROOT = Path.home() / "Desktop" / "RansomDemo"
TARGET_DIR = ROOT / "targets"
BACKUP_DIR = ROOT / ".safety_backup"
RUNTIME_DIR = ROOT / ".runtime"

PRIVATE_KEY_FILE = RUNTIME_DIR / "private.pem"

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
        f"{filename}.unt"
    )

    output = (
        TARGET_DIR /
        filename
    )

    if not encrypted.exists():
        print(
            f"[SKIP] {filename}: "
            "encrypted file not found"
        )
        return False

    if encrypted.is_symlink():
        print(
            f"[SKIP] {filename}: "
            "symbolic links are not allowed"
        )
        return False

    private_key = RSA.import_key(
        PRIVATE_KEY_FILE.read_bytes()
    )

    with encrypted.open("rb") as f:
        magic = f.read(
            len(MAGIC)
        )

        if magic != MAGIC:
            raise ValueError(
                "Invalid training file header"
            )

        wrapped_key_length = int.from_bytes(
            f.read(2),
            "big"
        )

        if wrapped_key_length <= 0:
            raise ValueError(
                "Invalid wrapped key length"
            )

        wrapped_key = f.read(
            wrapped_key_length
        )

        nonce_length = int.from_bytes(
            f.read(1),
            "big"
        )

        nonce = f.read(
            nonce_length
        )

        tag_length = int.from_bytes(
            f.read(1),
            "big"
        )

        tag = f.read(
            tag_length
        )

        ciphertext = f.read()

    rsa_cipher = PKCS1_OAEP.new(
        private_key,
        hashAlgo=SHA256
    )

    aes_key = rsa_cipher.decrypt(
        wrapped_key
    )

    aes_cipher = AES.new(
        aes_key,
        AES.MODE_GCM,
        nonce=nonce
    )

    # This both decrypts and verifies integrity.
    plaintext = aes_cipher.decrypt_and_verify(
        ciphertext,
        tag
    )

    temporary = output.with_suffix(
        output.suffix + ".recovering"
    )

    temporary.write_bytes(
        plaintext
    )

    os.replace(
        temporary,
        output
    )

    # Delete only the corresponding DEMO .unt file,
    # and only after successful authenticated decryption.
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
        " SECURITY AWARENESS TRAINING RECOVERY"
    )

    print(
        "=========================================="
    )

    if not PRIVATE_KEY_FILE.exists():
        print(
            "[ERROR] Training private key not found."
        )
        return

    recovered = 0

    for filename in TARGET_FILES:
        try:
            if decrypt_file(filename):
                recovered += 1

        except Exception as error:
            print(
                f"[FAILED] {filename}: {error}"
            )

    print()
    print(
        f"[+] Recovery completed: "
        f"{recovered}/{len(TARGET_FILES)} files"
    )

    print(
        "[+] Safety backups remain in:"
    )

    print(
        f"    {BACKUP_DIR}"
    )

    print()
    print(
        "Training simulation complete."
    )


if __name__ == "__main__":
    main()
