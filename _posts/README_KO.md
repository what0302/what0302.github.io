# CSCE 5550 Copy-only Ransomware Recovery Demonstration

이 패키지는 원본 PDF를 변경하거나 삭제하지 않는 **실습용 암호화 복사본** 프로젝트입니다. 실습 전에 VMware 스냅샷을 권장합니다.

## 파일 구성

- `demo_encrypt.py`: GitHub에서 `encrypt.py`를 가져와 실행하고 작은 화면에도 맞는 UNT GUI를 표시합니다.
- `encrypt.py`: `~/Desktop/RansomDemo/critical_*` 안의 하위 폴더를 읽어 `encrypted_output`에 `.unt` 암호화 복사본을 만듭니다. 원본 보존.
- `decrypt.py`: `encrypted_output` 암호문을 `recovered_output`에 복구하고 SHA-256을 확인합니다.
- `keygen_offline.py`: Windows에서 RSA 키 쌍 생성. 같은 폴더 아래 `keys_offline/`에 저장됩니다.
- `recovery_private.pem`: `keygen_offline.py`가 만드는 **실습용 개인키 복사본**으로, 사용자 선택에 따라 공개 GitHub에 배포하는 데모용입니다. 실제 비밀키를 이 방식으로 공개하지 마세요.
- `recovery_code.txt`: 4자리 GUI 데모 코드. 초기 예시 1234. 공개된 텍스트이므로 실제 인증 보안은 없습니다.
- `payload_ducky.txt`: 기존 Kali VM에서 사용했던 DuckyScript 실행 흐름.

## Windows 준비

1. Python 설치 및 `py -m pip install pycryptodomex`.
2. `py keygen_offline.py` 1회 실행.
3. 생성된 `keys_offline/public.pem`만 Kali VM `~/Desktop/RansomDemo/keys/public.pem`로 옮깁니다.
4. GitHub `what0302/what0302.github.io`의 `_posts`에 `demo_encrypt.py`, `encrypt.py`, `decrypt.py`, `recovery_code.txt`, `unt_mascot.png`를 업로드합니다.
5. **공개 데모키에 한해** `keys_offline/recovery_private.pem`도 `_posts/recovery_private.pem`로 업로드합니다. 개인키가 공개되어 누구든지 복호화할 수 있습니다. 실습 이외에는 사용하지 마세요.
6. `payload_ducky.txt` 내용은 Hak5 Payload Studio에서 컴파일해 사용합니다.

## Kali 사전 준비

```
sudo apt update
sudo apt install -y python3-pycryptodomex python3-pil python3-pil.imagetk
mkdir -p ~/Desktop/RansomDemo/keys
python3 -c "from Cryptodome.Cipher import AES; from PIL import ImageTk; print('OK')"
```

대상 폴더를 정확히 하나만 만드세요. 예시: `~/Desktop/RansomDemo/critical_tk0667/` 아래에 PDF 및 `folder1`, `folder2`, `folder3`을 만듭니다. 루트에는 과제 설명 PDF도 복사합니다. *EUID 값은 반드시 강의 기준으로 확인하세요.* 다른 `critical_*` 폴더가 있으면 동작하지 않게 했습니다.

## 실행 및 복구

1. Windows에서 GitHub로 최신 파일 push.
2. Kali에서 기존 Ducky 실행 또는 `python3 ~/Desktop/RansomDemo/demo_encrypt.py`.
3. 암호화 결과: `~/Desktop/RansomDemo/encrypted_output`; 원본 `critical_*`는 그대로입니다.
4. GUI에 `recovery_code.txt`와 같은 4자리 코드 입력.
5. GUI가 `recovery_private.pem` 및 `decrypt.py`를 다운로드해 복호화하고, `~/Desktop/RansomDemo/recovered_output`에 복구합니다.
6. 다시 실행할 때는 기존 `encrypted_output`, `recovered_output`을 별도 위치로 옮긴 후 시작하세요. 덮어쓰기를 방지합니다.

## 기존 실습 파일

`~/Desktop/RansomDemo/.runtime/private.pem`은 과거 데모 키일 수 있어 새로운 공개키와 섞지 마세요. `keys_offline/private.pem`을 GitHub에 올리지 않고 `recovery_private.pem` 사본을 올리는 이유는 데모 용도와 실제 보관용을 구분하기 위한 것입니다. **두 파일 내용은 동일해서 둘 다 실제로는 공개됩니다.** 공개 배포 키는 절대 다른 목적으로 쓰지 마세요.

## 과제 루브릭 관련

강의의 Variant 1은 RSA 공개키와 개인키를 각 프로그램에 포함하는 구조를 보여줍니다. 이 버전은 학습 편의를 위해 `public.pem`과 GitHub에서 다운로드되는 개인키 파일을 분리했습니다. 또한 원본을 암호화해 잠그는 대신 암호화 복사본을 만드므로 해당 항목의 실제 구현과 동일하다고 주장하면 안 됩니다. 발표 전에 교수님 승인 또는 추가 구현이 필요합니다.
