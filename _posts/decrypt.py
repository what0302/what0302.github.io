from pathlib import Path
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
import hashlib
import json

base = Path.home() / 'Desktop' / 'RansomDemo'
encrypted_dir = base / 'encrypted_output'
output = base / 'recovered_output'
key_file = base / '.runtime' / 'recovery_private.pem'
if not encrypted_dir.is_dir() or not key_file.is_file():
    raise SystemExit('Encrypted copies or recovery key missing')
if output.exists():
    raise SystemExit('recovered_output exists; move it before rerunning')
items = json.loads((encrypted_dir / 'manifest.json').read_text(encoding='utf-8'))
private = RSA.import_key(key_file.read_bytes())
rsa = PKCS1_OAEP.new(private, hashAlgo=SHA256)
results = []
for item in items:
    name = Path(item['file'])
    if name.is_absolute() or '..' in name.parts or name.parts[0].startswith('.'):
        raise SystemExit('Unsafe manifest entry')
    source = encrypted_dir / name.parent / (name.name + '.unt')
    if source.is_symlink() or not source.resolve().is_relative_to(encrypted_dir.resolve()):
        raise SystemExit('Unsafe encrypted path')
    data = source.read_bytes()
    length = int.from_bytes(data[:2], 'big')
    if length != private.size_in_bytes():
        raise SystemExit('Invalid encrypted key')
    offset = 2
    wrapped = data[offset:offset+length]
    offset += length
    nonce_size = data[offset]
    offset += 1
    nonce = data[offset:offset+nonce_size]
    offset += nonce_size
    tag = data[offset:offset+16]
    cipher = data[offset+16:]
    aes_key = rsa.decrypt(wrapped)
    clear = AES.new(aes_key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(cipher, tag)
    if hashlib.sha256(clear).hexdigest() != item['sha256']:
        raise SystemExit('Checksum mismatch: ' + str(name))
    results.append((name, clear))
for name, clear in results:
    dest = output / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(clear)
    print('Verified:', name)
print('Recovered:', len(results), 'files')
