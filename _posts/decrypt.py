from pathlib import Path
import hashlib
import json
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256

base = Path.home() / "Desktop" / "RansomDemo"
source = base / "critical_tk0667"
keyfile = base / ".runtime" / "recovery_private.pem"
items = json.loads((base / "original_backup" / "manifest.json").read_text(encoding="utf-8"))
private = RSA.import_key(keyfile.read_bytes())
rsa = PKCS1_OAEP.new(private, hashAlgo=SHA256)
key_len = private.size_in_bytes()

results = []
name = "?"
try:
    for item in items:
        name = Path(item["file"])
        if name.is_absolute() or ".." in name.parts or name.suffix.lower() != ".pdf":
            raise ValueError("invalid file path")
        encrypted = source / name.parent / (name.name + ".unt")
        if encrypted.is_symlink() or not encrypted.is_file() or not encrypted.resolve().is_relative_to(source.resolve()):
            raise ValueError("missing or unsafe encrypted file")
        data = encrypted.read_bytes()
        if not data.startswith(b"UNTDEMO2") or int.from_bytes(data[8:10], "big") != key_len:
            raise ValueError("invalid encrypted format")
        pos = 10 + key_len
        aes_key = rsa.decrypt(data[10:pos])
        nonce_size = data[pos]
        nonce = data[pos + 1:pos + 1 + nonce_size]
        pos += 1 + nonce_size
        tag = data[pos:pos + 16]
        plaintext = AES.new(aes_key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(data[pos + 16:], tag)
        if hashlib.sha256(plaintext).hexdigest() != item["sha256"]:
            raise ValueError("SHA-256 mismatch")
        results.append((name, plaintext))
except (ValueError, IndexError, KeyError) as e:
    raise SystemExit(f"Decryption failed: {name} ({e})")

for name, plaintext in results:
    dest = source / name
    if dest.is_symlink():
        raise SystemExit("Symlink not allowed: " + str(name))
    if dest.exists():
        if dest.read_bytes() != plaintext:
            raise SystemExit("Existing original differs. No overwrite: " + str(name))
        print("Verified existing original:", name)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(plaintext)
        print("Restored from .unt:", name)
print("All verified:", len(results))
