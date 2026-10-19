# CSCE 5550 — Variant 1 key separation (safe copy-only demonstration)

## 변경 내용
- RSA 키는 Kali VM이 아닌 **Windows / 별도 실습 환경**에서 `keygen_offline.py`로 한 번 생성합니다.
- Kali 암호화 데모에는 **공개키 `public.pem`만** 전달합니다.
- 개인키 `private.pem`은 GitHub에 올리지 않고 Windows에 보관했다가, 복호화 시연 시에만 Kali VM에 수동으로 전달합니다.
- `encrypt.py`는 `critical_EUID` 안의 파일을 재귀 탐색하고, 원본을 변경하지 않고 `encrypted_output/`에 암호화된 복사본을 저장합니다.
- `decrypt.py`는 별도 제공된 `private.pem`으로 `recovered_output/`에 복원하고 SHA-256을 확인합니다.
- 따라서 강의안의 **공개키/개인키 역할 분리**를 보여주는 안전한 실습판입니다. 단, 키를 프로그램 안에 hardcode하라는 Variant 1의 세부 조건 및 원본 디렉터리 직접 암호화 조건을 그대로 구현한 것은 아닙니다.

## Windows 준비
1. Windows에 Python 및 `pycryptodomex` 설치: `py -m pip install pycryptodomex`
2. `py keygen_offline.py` 실행.
3. `keys_offline/public.pem`만 Kali VM의 `~/Desktop/RansomDemo/keys/public.pem`에 복사합니다.
4. `keys_offline/private.pem`은 Windows에 보관합니다. **GitHub, 공개 ZIP, 공개 저장소에 업로드하지 마세요.**

## Kali 준비
```bash
mkdir -p ~/Desktop/RansomDemo/keys
sudo apt install python3-pycryptodome python3-pil python3-pil.imagetk
```

Kali에서 이미 만들어진 공개키가 있는지 확인:
```bash
ls -lh ~/Desktop/RansomDemo/keys/public.pem
```

필요 시 `setup_lab.py`로 샘플 폴더를 만들 수 있으나 기본 폴더명은 `critical_EUID`입니다. 실제 학생 EUID를 쓰려면 `setup_lab.py`와 `encrypt.py`의 폴더명을 일치시키세요. 실제 PDF는 수동 배치하십시오.

## 시연
- 이전과 같은 GitHub 파일명인 `demo_encrypt.py`, `encrypt.py`, `decrypt.py`, `unt_mascot.png`, `recovery_code.txt`를 활용합니다.
- 기존 Rubber Ducky 스크립트의 GUI 시작 흐름은 유지하되, 이 버전의 암호화는 **원본을 보존하는 복사본 실습**입니다.
- 복호화 직전에만 Windows에 있는 `private.pem`을 Kali `~/Desktop/RansomDemo/keys/private.pem`으로 수동 복사하십시오.
- Kali `~/Desktop/RansomDemo/keys/private.pem`을 사전에 두지 않으면 복구 버튼이 실패하는 것이 정상입니다.
- 시연이 끝나면 Kali에 전달했던 개인키 복사본을 제거하고, VM 스냅샷으로 되돌리는 것을 권장합니다.

## 강의안과 차이
교수님 슬라이드 Variant 1은 encryptor 내 pk / decryptor 내 sk 하드코딩을 예시로 듭니다. 이 ZIP은 **개인키 비공개 유지 및 공격자 측 KeyGen 위치**만 우선 반영했습니다. 직접 원본을 잠그거나 USB로 파괴적 암호화를 자동 실행하는 구조는 포함하지 않습니다.
