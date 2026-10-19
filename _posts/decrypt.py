from pathlib import Path
import hashlib
import json
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256

base = Path.home() / "Desktop" / "RansomDemo"
source = base / "critical_tk0667"
backup = base / "original_backup"
output = base / "recovered_output" / "critical_tk0667"
keyfile = base / ".runtime" / "recovery_private.pem"
items = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
private = RSA.import_key(keyfile.read_bytes())
rsa = PKCS1_OAEP.new(private, hashAlgo=SHA256)

results = []
for item in items:
    name = Path(item["file"])
    if name.is_absolute() or ".." in name.parts or name.suffix.lower() != ".pdf":
        raise SystemExit("Invalid file name in manifest")
    encrypted = source / name.parent / (name.name + ".unt")
    if encrypted.is_symlink() or not encrypted.resolve().is_relative_to(source.resolve()):
        raise SystemExit("Unsafe encrypted file")
    data = encrypted.read_bytes()
    if not data.startswith(b"UNTDEMO2"):
        raise SystemExit("Invalid encrypted file")
    pos = 8
    length = int.from_bytes(data[pos:pos + 2], "big")
    pos += 2
    if length != private.size_in_bytes():
        raise SystemExit("Wrong encrypted key format")
    aes_key = rsa.decrypt(data[pos:pos + length])
    pos += length
    nonce_size = data[pos]
    pos += 1
    nonce = data[pos:pos + nonce_size]
    pos += nonce_size
    tag = data[pos:pos + 16]
    plaintext = AES.new(aes_key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(data[pos + 16:], tag)
    if hashlib.sha256(plaintext).hexdigest() != item["sha256"]:
        raise SystemExit("SHA-256 mismatch: " + str(name))
    results.append((name, plaintext))

for name, plaintext in results:
    restored = output / name
    restored.parent.mkdir(parents=True, exist_ok=True)
    restored.write_bytes(plaintext)
    print("Recovered:", name)
print("Verified:", len(results), "PDFs")
