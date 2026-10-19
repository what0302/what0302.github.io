from pathlib import Path
from Cryptodome.PublicKey import RSA

folder = Path(__file__).resolve().parent / "keys_offline"
folder.mkdir(exist_ok=True)
public = folder / "public.pem"
private = folder / "recovery_private.pem"
if public.exists() or private.exists():
    raise SystemExit("Key files already exist. Do not overwrite existing keys")
key = RSA.generate(2048)
public.write_bytes(key.publickey().export_key())
private.write_bytes(key.export_key())
print("Created", public, "and", private)
