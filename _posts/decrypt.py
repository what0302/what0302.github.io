from pathlib import Path
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256

base = Path.home() / "Desktop" / "RansomDemo"
source = base / "critical_tk0667"
keyfile = base / ".runtime" / "recovery_private.pem"
private = RSA.import_key(keyfile.read_bytes())
rsa = PKCS1_OAEP.new(private, hashAlgo=SHA256)
key_len = private.size_in_bytes()

files = sorted(source.rglob("*.unt"))

for p in files:
    data = p.read_bytes()
    pos = 10 + key_len
    aes_key = rsa.decrypt(data[10:pos])
    nonce_size = data[pos]
    nonce = data[pos + 1:pos + 1 + nonce_size]
    pos += 1 + nonce_size + 16
    plaintext = AES.new(aes_key, AES.MODE_GCM, nonce=nonce).decrypt(data[pos:])
    dest = p.with_suffix("")
    dest.write_bytes(plaintext)
    p.unlink()
    print("Restored:", dest.name)
