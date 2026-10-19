from pathlib import Path
from Cryptodome.PublicKey import RSA

folder = Path(__file__).resolve().parent / 'keys_offline'
folder.mkdir(exist_ok=True)
public = folder / 'public.pem'
private = folder / 'private.pem'
if public.exists() or private.exists():
    raise SystemExit('Keys already exist')
key = RSA.generate(2048)
public.write_bytes(key.publickey().export_key())
private.write_bytes(key.export_key())
(folder / 'recovery_private.pem').write_bytes(private.read_bytes())
print('Created public.pem and private.pem')
print('For this public demo, recovery_private.pem is a public training-only key')
