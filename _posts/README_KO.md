# CSCE5550 자동 암호화 복사본 실습

## 목적
Rubber Ducky로 Kali VM에서 `demo_encrypt.py` 실행 → GitHub에서 `encrypt.py` 받음 → `critical_tk0667`의 PDF를 재귀적으로 암호화해 **같은 폴더에 `.pdf.unt` 생성** → UNT GUI 표시 → GitHub 4자리 코드 확인 → `decrypt.py`와 실습 전용 개인키 다운로드 → `recovered_output`에 PDF 복원하고 SHA-256 검증.

원본 PDF는 삭제·수정하지 않습니다. `original_backup/critical_tk0667`에 추가로 백업합니다. 실습 VM에서만 사용하세요.

## GitHub에 넣을 파일
`what0302.github.io/_posts/`에 `demo_encrypt.py`, `encrypt.py`, `decrypt.py`, `recovery_code.txt`, `recovery_private.pem`, `unt_mascot.png`를 올립니다. `payload_ducky.txt`는 DuckyScript 참고 파일입니다.

GitHub에 공개한 `recovery_private.pem`과 4자리 숫자는 누구나 볼 수 있습니다. **실습 전용 RSA 키만 사용**하고 실제 보안 인증으로 간주하지 마세요.

## Windows에서 처음 한 번
`py -m pip install pycryptodomex` 실행 후 `py keygen_offline.py`를 실행합니다. `keys_offline/public.pem`과 `keys_offline/recovery_private.pem`을 생성합니다. 기존 키를 덮어쓰지 않습니다.

- `public.pem`: Kali `/home/kali/Desktop/RansomDemo/keys/public.pem`에 복사
- `recovery_private.pem`: GitHub `_posts/`에 올림
- `keygen_offline.py`: GitHub에 올릴 필요 없음

공개키와 개인키는 **같은 실행에서 생성한 한 쌍**이어야 합니다.

## Kali 준비
```
sudo apt update
sudo apt install -y python3-pycryptodomex python3-pil python3-pil.imagetk
mkdir -p ~/Desktop/RansomDemo/keys
python3 -c "from Cryptodome.Cipher import AES; print('AES OK')"
```

대상 PDF들은 `/home/kali/Desktop/RansomDemo/critical_tk0667/` 아래에 둡니다. 하위 `folder1`, `folder2`, `folder3`의 PDF도 처리됩니다. 대상 폴더 외부의 파일은 처리하지 않습니다. `original_backup`과 `.runtime`은 대상 밖에 있습니다.

## 자동 실행과 복구
- `payload_ducky.txt`를 Hak5 Payload Studio에서 컴파일하여 **본인이 관리하는 Kali VM**에서만 실행하세요.
- GitHub에서 `demo_encrypt.py`를 받고 실행하면, `encrypt.py`를 자동 다운로드하여 암호화 복사본부터 생성합니다.
- 암호화 후 PDF 원본은 그대로 남고 `filename.pdf.unt`가 같은 폴더에 생성됩니다.
- 성공하면 GUI의 `RECOVER FILES`에 `recovery_code.txt`의 4자리 숫자를 입력합니다.
- 코드가 일치하면 `recovery_private.pem`, `decrypt.py`를 다운로드해 복호화하고 `recovered_output/critical_tk0667/`에 결과를 저장합니다.

## 예상 구조
```
RansomDemo/
  critical_tk0667/
    project.pdf
    project.pdf.unt
    folder1/
      lecture.pdf
      lecture.pdf.unt
    folder2/
    folder3/
  original_backup/
    manifest.json
    critical_tk0667/
      project.pdf
      folder1/...
  recovered_output/
    critical_tk0667/
      project.pdf
      folder1/...
  keys/
    public.pem
  .runtime/
    encrypt.py
    decrypt.py
    recovery_private.pem
```

## 반복 실습
프로그램은 기존 `.unt` 또는 기존 manifest를 무조건 덮어쓰지 않습니다. 반복 실습 전 VM 스냅샷을 복원하거나 실습 생성물(`.unt`, `original_backup`, `recovered_output`)을 별도로 보관한 뒤 새 환경에서 실행하세요. **원본 PDF를 지우지 마세요.**

## 과제 기준
PDF 내용에 실제 AES-256-GCM + RSA-OAEP 암호화를 적용합니다. 다만 `.unt`는 복사 암호문이며 원본 PDF를 삭제하거나 잠그지 않습니다. 강의안의 실파일 접근 불가 시연과는 차이가 있습니다. 최종 과제에서는 적절한 주석, Monitoring/Detection/Mitigation도 별도 필요합니다.
