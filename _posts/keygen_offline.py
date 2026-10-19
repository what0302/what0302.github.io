from pathlib import Path
from Cryptodome.PublicKey import RSA

keys = Path(__file__).resolve().parent / "keys_offline"
keys.mkdir(exist_ok=True)
public = keys / "public.pem"
private = keys / "private.pem"

if public.exists() or private.exists():
    raise SystemExit("Keys already exist. Files were not changed.")

key = RSA.generate(2048)
public.write_bytes(key.publickey().export_key())
private.write_bytes(key.export_key())
print("Created public.pem and private.pem in:", keys)
print("Keep private.pem offline and do not commit it to GitHub.")
