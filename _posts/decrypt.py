from pathlib import Path
import hashlib
import json
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256

base = Path.home() / 'Desktop' / 'RansomDemo'
encrypted_dir = base / 'encrypted_output'
output = base / 'recovered_output'
key_file = base / 'keys' / 'private.pem'

if not encrypted_dir.is_dir() or encrypted_dir.is_symlink() or not key_file.is_file():
    raise SystemExit('Encrypted copies or offline private key not found. Provide private.pem only during recovery demo.')
if output.exists():
    raise SystemExit('recovered_output already exists. Move it before another run.')

items = json.loads((encrypted_dir / 'manifest.json').read_text(encoding='utf-8'))
private_key = RSA.import_key(key_file.read_bytes())
rsa = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
verified = 0

# Restore copies and check their SHA-256 values.
for item in items:
    relative = Path(item['file'])
    if relative.is_absolute() or '..' in relative.parts:
        raise SystemExit('Invalid path in manifest')
    original = encrypted_dir / relative.parent / (relative.name + '.unt')
    if original.is_symlink():
        raise SystemExit('Symlink is not allowed')
    data = original.read_bytes()
    key_size = int.from_bytes(data[:2], 'big')
    if key_size != private_key.size_in_bytes():
        raise SystemExit('Invalid encrypted key length')
    pos = 2
    wrapped_key = data[pos:pos + key_size]
    pos += key_size
    nonce_len = data[pos]
    pos += 1
    nonce = data[pos:pos + nonce_len]
    pos += nonce_len
    tag = data[pos:pos + 16]
    encrypted = data[pos + 16:]

    aes_key = rsa.decrypt(wrapped_key)
    plaintext = AES.new(aes_key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(encrypted, tag)
    digest = hashlib.sha256(plaintext).hexdigest()
    if digest != item['sha256']:
        raise SystemExit('SHA-256 mismatch: ' + str(relative))

    result = output / relative
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_bytes(plaintext)
    verified += 1
    print('Recovered and verified:', relative)

print('SHA-256 verified:', verified, '/', len(items))
