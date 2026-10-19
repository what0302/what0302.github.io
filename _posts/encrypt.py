from pathlib import Path
import hashlib
import json
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes

base = Path.home() / 'Desktop' / 'RansomDemo'
source = base / 'critical_EUID'
output = base / 'encrypted_output'
public_file = base / 'keys' / 'public.pem'

if not source.is_dir() or source.is_symlink():
    raise SystemExit('Training folder missing or invalid')
if not public_file.is_file():
    raise SystemExit('Missing public.pem. Copy only the public key to Kali keys folder.')
if output.exists():
    raise SystemExit('encrypted_output already exists. Move it before another run.')

public_key = RSA.import_key(public_file.read_bytes())
rsa = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
items = []

# Only make encrypted copies. Original training files are not changed.
for path in sorted(source.rglob('*')):
    if not path.is_file() or path.is_symlink():
        continue
    relative = path.relative_to(source)
    plaintext = path.read_bytes()
    aes_key = get_random_bytes(32)
    aes = AES.new(aes_key, AES.MODE_GCM)
    encrypted, tag = aes.encrypt_and_digest(plaintext)
    wrapped_key = rsa.encrypt(aes_key)

    result = output / relative.parent / (path.name + '.unt')
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_bytes(
        len(wrapped_key).to_bytes(2, 'big') + wrapped_key +
        len(aes.nonce).to_bytes(1, 'big') + aes.nonce +
        tag + encrypted
    )
    items.append({'file': relative.as_posix(), 'sha256': hashlib.sha256(plaintext).hexdigest()})
    print('Encrypted copy:', relative)

(output / 'manifest.json').write_text(json.dumps(items, indent=2), encoding='utf-8')
print('Completed:', len(items), 'files')
