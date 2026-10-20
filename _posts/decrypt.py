from pathlib import Path
import json
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256

base = Path.home() / "Desktop" / "RansomDemo"
source = base / "critical_tk0667"
items = json.loads((base / "original_backup" / "manifest.json").read_text(encoding="utf-8"))
private = RSA.import_key((base / ".runtime" / "recovery_private.pem").read_bytes())
rsa = PKCS1_OAEP.new(private, hashAlgo=SHA256)
key_len = private.size_in_bytes()

for item in items:
    name = item["file"]
    data = (source / (name + ".unt")).read_bytes()
    pos = 10 + key_len
    aes_key = rsa.decrypt(data[10:pos])
    nonce_size = data[pos]
    nonce = data[pos + 1:pos + 1 + nonce_size]
    pos += 1 + nonce_size + 16
    plaintext = AES.new(aes_key, AES.MODE_GCM, nonce=nonce).decrypt(data[pos:])
    (source / name).write_bytes(plaintext)
    print("Restored:", name)
