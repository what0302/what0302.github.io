from pathlib import Path
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256

PRIVATE_KEY = b"""-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAxgoOyqgZKaIJQHKw2nrJv9tL/c5MgoKgKehyyLtSXMuYZkeG
p2XJ7jrp0RXJqb9PAPZucCTIaM/JpfvwInWekdNmBU4dl/9po/UvEvxAGLEAlKOB
GhJWK7H7JLBDlW79CxAl0FtNRrBB1VZIqVbC/zmM9lHTrhGgjAZfqqzRFmO21q8+
l1QgFfZIKim68fzYa9QpjdsJp7tDcIS1kIP/s+NM7nfVBbFC2rGLr+XxIyXjYmND
Q/ra9c0uC8AFEbUIPJitPFlsi8VcYpM3ofN79poQJc2ggiTZAbEVUDaeJ6BPyTAc
Nv8Deogzh2+kPLB/3fAkKJAsVIU5948UGJyRVQIDAQABAoIBAFInS/mQAFhACtx8
d5c6xsTbQUv5r82YSL752dwhsUojf4Y2d8qrtDgqomKFSlIrtadtk2TcLXMld75u
pDB3YJ+X9cOPo0ExyG4mwS98C07y5o3CwkTBhJO90rRmlrLAByL2wOkNZyJC7hyF
HcF554yfIDXyvgCA+Xv9DOStqlNBsRuJNzzmiphY+fHUHEw878O/mug4Qxrz/yzg
KCUQa4efg3jIcDcsQwZy7tOGbET8+iECgCrrcZnOjSe3Ub28mvFq7UeuHT/ncB54
NHkmUak7LerJdjJVyyJeNTMVvTpZs9ZD8T83u0yycneQsFlfpsjCnxf13K7ILbpj
FnWIgyUCgYEA0v+i4/IqRKyNomDPD3/S6OTZl14nBYSA1BcC9TaEb8l7NcLmVf/4
MhFy43C4bh9dZR2SKmLJMgEhbEd+imZXtphbYzi0BGf4wWtaD3fUOpqDahW18IAX
bUdd33hZKd+boI1jaC46qXC4WcIkzubSQx8ZG5icintlKOafJfHAkDcCgYEA8Eba
nC5oW4o4Fc3kbbDYfo3K7ZA8tYKARjE9YTK3vR0CWzWWjX+yW/y0fWEv3iajzm36
kJNExSVLird0YRNRG+mBteZsego8rXD4930QALPUquJh5bOTzin4cQzI+Iz+O4uw
dYSlyBncD+Bc1CEqT096uigxvGCKuEswH1Yl7NMCgYBr8cxrwWBOcdij0dMcotBL
xYhsIAbmk7s0xfEFcjae2fzmrCcaqDFZrAOSyAASlok5Sb+VX6R+qIVo18qtE16c
U6WtRT0TY/2nNjyE3VD+Cj5g72p894sEpRYpVXCIM5VyteK9UalBNiGaCfC6yOuY
2zgFHjY3wpkmK5YP23YgUQKBgGHw38dt+0flDXuF06kKvxTHA4LWmoh6S4NRKu3l
2JOTsZQwQdAnzzJDzeaVqQdqxLauicZI4W1jCGng4eV4FEXGZwMYi/srFRS1yiZH
qjA/HV8SrEkPbB5LaWPbjEgUYMUw6ZrdmR35vIQUNoKZij+N7D7Zh3x79c+thk4f
tZHVAoGAMiKfyJPZ/cwCkA4pylrVgc/pJDpZQeLBFwi9Ts3hD2/1cACSZoGn6IIh
j5lWPcFz/BnaDdHJiA4CTBeoxQEgoGTvfATvz+i+Gs93oeVcBadBJOmtJ2XYFSA+
XmrXc4+OUxq1ZA01hxGOSpXvciRQ6zXLtLGpFIZ4T8LO6Zcac2E=
-----END RSA PRIVATE KEY-----"""

base = Path.home() / "Desktop" / "RansomDemo"
private = RSA.import_key(PRIVATE_KEY)
rsa = PKCS1_OAEP.new(private, hashAlgo=SHA256)
kl = private.size_in_bytes()

for p in (base / "critical_tk0667").rglob("*.unt"):
    d = p.read_bytes()
    key = rsa.decrypt(d[10:10 + kl])
    ns = d[10 + kl]
    nonce = d[11 + kl:11 + kl + ns]
    p.with_suffix("").write_bytes(AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt(d[27 + kl + ns:]))
    p.unlink()
    print("Restored:", p.with_suffix("").name)
