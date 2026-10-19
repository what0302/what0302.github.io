from pathlib import Path
import hashlib
import json
import shutil
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Random import get_random_bytes

BASE = Path.home() / 'Desktop' / 'RansomDemo'
SOURCE = BASE / 'critical_tk0667'
BACKUP = BASE / 'original_backup' / 'critical_tk0667'
RECOVERED = BASE / 'recovered_output' / 'critical_tk0667'
PUBLIC = BASE / 'keys' / 'public.pem'
PRIVATE = BASE / 'keys' / 'private.pem'
MANIFEST = BASE / 'original_backup' / 'manifest.json'


def files():
    if not SOURCE.is_dir() or SOURCE.is_symlink():
        raise RuntimeError('Training directory is missing')
    result = []
    for file in SOURCE.rglob('*.pdf'):
        if file.is_symlink() or not file.resolve().is_relative_to(SOURCE.resolve()):
            raise RuntimeError('Symlink or outside path is not allowed')
        if file.is_file():
            result.append(file)
    if not result:
        raise RuntimeError('No PDF files found')
    return sorted(result)


def encrypt_copies():
    if not PUBLIC.is_file():
        raise RuntimeError('Missing keys/public.pem')
    all_files = files()
    if any((path.with_name(path.name + '.unt')).exists() for path in all_files):
        raise RuntimeError('Encrypted copies already exist')
    BACKUP.mkdir(parents=True, exist_ok=True)
    pub = PKCS1_OAEP.new(RSA.import_key(PUBLIC.read_bytes()), hashAlgo=SHA256)
    manifest = []
    for path in all_files:
        relative = path.relative_to(SOURCE)
        copy = BACKUP / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        if copy.exists():
            raise RuntimeError('Backup already exists: ' + relative.as_posix())
        shutil.copy2(path, copy)
        if hashlib.sha256(copy.read_bytes()).digest() != hashlib.sha256(path.read_bytes()).digest():
            raise RuntimeError('Backup verification failed')
        manifest.append({'file': relative.as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    for path in all_files:
        plain = path.read_bytes()
        key = get_random_bytes(32)
        aes = AES.new(key, AES.MODE_GCM)
        cipher, tag = aes.encrypt_and_digest(plain)
        wrapped = pub.encrypt(key)
        blob = b'UNTDEMO2' + len(wrapped).to_bytes(2, 'big') + wrapped + bytes([len(aes.nonce)]) + aes.nonce + tag + cipher
        path.with_name(path.name + '.unt').write_bytes(blob)
    return len(all_files)


def recover_copies():
    if not PRIVATE.is_file():
        raise RuntimeError('Missing keys/private.pem; provide your test key locally')
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    rsa = PKCS1_OAEP.new(RSA.import_key(PRIVATE.read_bytes()), hashAlgo=SHA256)
    successes = 0
    for entry in manifest:
        relative = Path(entry['file'])
        if relative.is_absolute() or '..' in relative.parts or relative.suffix.lower() != '.pdf':
            raise RuntimeError('Invalid manifest entry')
        enc = SOURCE / relative.parent / (relative.name + '.unt')
        blob = enc.read_bytes()
        if blob[:8] != b'UNTDEMO2':
            raise RuntimeError('Invalid file format')
        pos = 8
        size = int.from_bytes(blob[pos:pos + 2], 'big')
        pos += 2
        key = rsa.decrypt(blob[pos:pos + size])
        pos += size
        nonce_size = blob[pos]
        pos += 1
        nonce = blob[pos:pos + nonce_size]
        pos += nonce_size
        tag = blob[pos:pos + 16]
        pos += 16
        plain = AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(blob[pos:], tag)
        if hashlib.sha256(plain).hexdigest() != entry['sha256']:
            raise RuntimeError('SHA-256 mismatch')
        dest = RECOVERED / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(plain)
        successes += 1
    return successes
