# CSCE 5550 Fall 2026 — Ransomware Project
**Student ID:** tk0667

## Environment

| Item | Value |
|------|-------|
| OS | Kali Linux 2024.x (guest VM, VirtualBox or VMware) |
| Python | 3.9 or higher |
| Privilege | `sudo` required for vaccine.py (fanotify needs CAP_SYS_ADMIN) |

## Dependencies

Install the required library on the Kali VM:

```bash
pip install pycryptodome
```

Standard library modules used (no install needed): `ctypes`, `os`, `sqlite3`, `select`, `signal`, `struct`, `sys`, `time`, `tkinter`, `pathlib`

## Directory Structure

Before running, create the target directory on the Kali VM:

```
~/Desktop/RansomDemo/
└── critical_tk0667/
    ├── folder1/   ← place homework/lab PDFs here
    ├── folder2/
    └── folder3/
```

```bash
mkdir -p ~/Desktop/RansomDemo/critical_tk0667/folder1
mkdir -p ~/Desktop/RansomDemo/critical_tk0667/folder2
mkdir -p ~/Desktop/RansomDemo/critical_tk0667/folder3
```

## Files

| File | Description |
|------|-------------|
| `demo_encrypt.py` | Infection entry point — downloads and runs `encrypt.py` from GitHub, then launches the ransom GUI |
| `encrypt.py` | Ransomware payload — AES-256-GCM + RSA-OAEP hybrid encryption, targets `critical_tk0667/` |
| `decrypt.py` | Recovery component — RSA-OAEP decrypts per-file AES key, restores original files |
| `vaccine.py` | Defense — fanotify-based monitor that blocks and kills any process opening protected files |
| `payload_ducky.txt` | USB Rubber Ducky script for the infection demo |
| `recovery_code.txt` | 4-digit ransom recovery code (hosted on GitHub) |
| `keygen_offline.py` | Offline RSA key pair generator (for reference; keys are pre-embedded in scripts) |

## Running the Demo

### Step 1 — Infection

```bash
python3 demo_encrypt.py
```

This simulates the infection: downloads and runs the ransomware payload, then displays the ransom GUI.

### Step 2 — Verify Encryption

Check that files in `~/Desktop/RansomDemo/critical_tk0667/` have been renamed to `.unt`.

### Step 3 — Decryption (recovery)

Enter recovery code `1234` in the GUI, or run directly:

```bash
python3 decrypt.py
```

### Step 4 — Deploy Vaccine (monitoring/detection/mitigation)

Restore files first (Step 3), then:

```bash
sudo python3 vaccine.py
```

The vaccine monitors `critical_tk0667/` using Linux `fanotify`. Any process other than the vaccine itself that attempts to open a protected file is immediately denied (`EACCES`) and killed (`SIGKILL`). All incidents are logged to `~/Desktop/RansomDemo/vaccine_log.db` (SQLite).

### Step 5 — Confirm Vaccine Blocks Encryption

With the vaccine running, re-run the ransomware:

```bash
python3 demo_encrypt.py
```

Expected result: 0 files encrypted. The vaccine terminal shows `[!] BLOCKED` entries.

## Incident Log

The vaccine writes to a SQLite database at `~/Desktop/RansomDemo/vaccine_log.db`:

```bash
sqlite3 ~/Desktop/RansomDemo/vaccine_log.db \
  "SELECT timestamp, pid, action, filename FROM incidents;"
```

## Notes

- Run the demo inside a VM snapshot. Revert before each test run.
- The RSA key pair is pre-embedded in `encrypt.py` / `decrypt.py` for demo purposes.
- `recovery_private.pem` is the matching RSA private key (included for grading reference only).
- Third-party library: [PyCryptodome](https://pycryptodome.readthedocs.io/)
