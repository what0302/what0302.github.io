# CSCE 5550 — 백업 우선, 원래 경로 복호화 실습

이 버전은 Kali VM의 `~/Desktop/RansomDemo/critical_tk0667/` 안에 있는 PDF를 재귀적으로 읽고 AES-256-GCM 암호문 `.pdf.unt`를 **같은 폴더**에 자동 생성합니다. 실행 시작점은 `demo_encrypt.py`이며 기존 GitHub / Rubber Ducky 다운로드 흐름을 사용할 수 있습니다.

## 암호화 단계
- 원본 PDF를 `~/Desktop/RansomDemo/original_backup/critical_tk0667/`에 복사하고 SHA-256을 `original_backup/manifest.json`에 기록합니다.
- 별도 암호문 `.pdf.unt`를 각 PDF 옆에 생성합니다. **원본 PDF는 자동으로 이동하거나 삭제하지 않습니다.**
- `.unt`는 AES-256-GCM 암호문과 RSA-OAEP로 암호화된 AES 키를 포함합니다.

## 원래 위치로 복구를 보여주는 시연
1. 암호화가 끝난 후 `original_backup/`에 원본이 모두 있는지 확인합니다.
2. **사용자가 수동으로** `critical_tk0667`의 PDF 원본을 다른 격리 폴더로 옮기고, `.pdf.unt`만 남겨 둡니다. 이를 자동화하지 않았습니다. 복구할 수 있도록 외부 백업을 추가로 보관하세요.
3. GUI에서 4자리 복구 코드를 입력하면 공개 GitHub의 `recovery_code.txt`를 확인합니다.
4. 일치하면 `decrypt.py`와 실습 전용 개인키를 내려받아 `.unt`를 실제 AES-GCM으로 해독합니다. GCM 인증 태그, manifest SHA-256, 별도 원본 백업 SHA-256이 모두 일치해야 합니다.
5. 원본 PDF가 없는 경우 복호화한 내용으로 `critical_tk0667` **원래 경로에 PDF를 생성**합니다. PDF가 이미 있으면 덮어쓰지 않고 내용 일치 여부만 검증합니다.
6. `.unt`는 증거로 남습니다. 따라서 파일 원본을 자동 제거하는 랜섬웨어가 아닙니다.

## GitHub
`_posts`에 `demo_encrypt.py`, `encrypt.py`, `decrypt.py`, `recovery_code.txt`, `unt_mascot.png`를 업로드합니다. `recovery_private.pem`은 실습 전용이어야 하며 공개 저장소에 업로드하면 누구나 내려받을 수 있습니다. 키는 반드시 Kali의 `keys/public.pem`과 일치해야 합니다.

## 주의
- GUI는 ESC 키로 종료합니다.
- 암호화 전 VM 스냅샷을 저장하세요.
- 처음 실행 후 재실행하면 기존 manifest나 `.unt` 때문에 암호화를 중지하도록 설계했습니다.
- 이 버전은 문법 검증만 수행했으며 Kali에서 실제 전체 시연을 검증하지 않았습니다.
