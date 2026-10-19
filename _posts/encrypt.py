from pathlib import Path
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes
import hashlib
import json

base = Path.home() / 'Desktop' / 'RansomDemo'
folders = [p for p in base.glob('critical_*') if p.is_dir() and not p.is_symlink()]
if len(folders) != 1:
    raise SystemExit('Create exactly one critical_EUID training folder')
source = folders[0]
output = base / 'encrypted_output'
key_file = base / 'keys' / 'public.pem'
if not key_file.is_file() or key_file.is_symlink():
    raise SystemExit('Missing keys/public.pem')
if output.exists():
    raise SystemExit('encrypted_output already exists; move it before rerunning')
files = [p for p in sorted(source.rglob('*')) if p.is_file() and not p.is_symlink()]
if not files:
    raise SystemExit('No training files found')
rsa = PKCS1_OAEP.new(RSA.import_key(key_file.read_bytes()), hashAlgo=SHA256)
items = []
for path in files:
    relative = path.relative_to(source)
    if not path.resolve().is_relative_to(source.resolve()):
        raise SystemExit('Invalid training file path')
    content = path.read_bytes()
    aes_key = get_random_bytes(32)
    aes = AES.new(aes_key, AES.MODE_GCM)
    encrypted, tag = aes.encrypt_and_digest(content)
    wrapped = rsa.encrypt(aes_key)
    dest = output / relative.parent / (relative.name + '.unt')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(len(wrapped).to_bytes(2, 'big') + wrapped + bytes([len(aes.nonce)]) + aes.nonce + tag + encrypted)
    items.append({'file':relative.as_posix(), 'sha256':hashlib.sha256(content).hexdigest()})
    print('Encrypted copy:', relative)
(output / 'manifest.json').write_text(json.dumps(items, indent=2), encoding='utf-8')
print('Completed:', len(items))
