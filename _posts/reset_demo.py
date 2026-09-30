from pathlib import Path
import shutil
from datetime import datetime


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

TARGET_FILES = [
    "personal_notes.txt",
    "employees.csv",
    "config.json",
    "project_plan.md",
    "application.log",
]


def log(message):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = (
        f"{timestamp} "
        f"[RESET] {message}"
    )

    print(line)

    ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    with LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            line + "\n"
        )


def main():

    TARGET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print(
        "======================================"
    )

    print(
        " RANSOM DEMO RESET"
    )

    print(
        "======================================"
    )

    restored = 0

    for filename in TARGET_FILES:

        original = (
            TARGET_DIR /
            filename
        )

        encrypted = (
            TARGET_DIR /
            (filename + ".unt")
        )

        backup = (
            BACKUP_DIR /
            filename
        )

        if encrypted.exists():
            encrypted.unlink()

            log(
                f"Removed {encrypted.name}"
            )

        if backup.exists():

            shutil.copy2(
                backup,
                original
            )

            restored += 1

            log(
                f"Restored {filename}"
            )

        elif original.exists():

            log(
                f"{filename} already present"
            )

        else:

            log(
                f"WARNING: backup missing for "
                f"{filename}"
            )

    if RUNTIME_DIR.exists():

        shutil.rmtree(
            RUNTIME_DIR
        )

        log(
            "Runtime directory cleared"
        )

    if CHECKSUM_FILE.exists():

        CHECKSUM_FILE.unlink()

        log(
            "Old checksum database cleared"
        )

    print()
    print(
        f"[+] Restored: "
        f"{restored}/"
        f"{len(TARGET_FILES)}"
    )

    print(
        "[+] Demo ready for another run."
    )

    print()


if __name__ == "__main__":
    main()
