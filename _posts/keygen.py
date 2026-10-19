from pathlib import Path
from Cryptodome.PublicKey import RSA

base = Path.home() / 'Desktop' / 'RansomDemo'
keys = base / 'keys'
keys.mkdir(parents=True, exist_ok=True)
public = keys / 'public.pem'
private = keys / 'private.pem'

if public.exists() or private.exists():
    print('Keys already exist. No keys were replaced.')
else:
    key = RSA.generate(2048)
    public.write_bytes(key.publickey().export_key())
    private.write_bytes(key.export_key())
    private.chmod(0o600)
    print('New key pair created in:', keys)
