# CSCE 5550 실습용 GitHub + Rubber Ducky 데모

현재 버전은 **원본을 암호화하거나 삭제하지 않고**, 지정한 프로젝트 폴더를 재귀적으로 읽어서 별도 폴더에 암호화 복사본을 만듭니다. 실제 공격 프로그램이 아닌 안전한 교육용 시뮬레이션입니다.

## 구성
- `setup_lab.py`: `~/Desktop/RansomDemo/critical_EUID` 안에 테스트 폴더와 파일 생성 (최종 제출 때 `EUID`를 실제 값으로 바꾸고 교수님이 지정한 문서 사용)
- `keygen.py`: RSA 키를 `~/Desktop/RansomDemo/keys/`에 생성
- `encrypt.py`: 대상 폴더 파일을 재귀적으로 읽어 `encrypted_output`에 `.unt` 암호화 복사본 생성, SHA-256 기록
- `decrypt.py`: `recovered_output`에 복구하여 SHA-256 비교
- `demo_encrypt.py`: GitHub에서 `encrypt.py`를 다운로드해 실행하고 마스코트/카운트다운/복구 GUI 제공
- `recovery_code.txt`: 예시 복구 코드 (공개 저장소 파일이므로 실제 보안 비밀 아님)
- `unt_mascot.png`: UNT 이미지
- `payload_ducky.txt`: 본인 Kali VM에서만 사용하는 키보드 입력 자동화 예시

## 먼저 Kali에서 준비
```
sudo apt install python3-pycryptodomex python3-pil python3-pil.imagetk
mkdir -p ~/Desktop/RansomDemo
```

`setup_lab.py`와 `keygen.py`를 Kali의 `~/Desktop/RansomDemo/` 안에 복사하거나 GitHub에서 내려받은 뒤 **직접 실행**:
```
python3 ~/Desktop/RansomDemo/setup_lab.py
python3 ~/Desktop/RansomDemo/keygen.py
```

## GitHub 업로드
이 폴더에서 `demo_encrypt.py`, `encrypt.py`, `decrypt.py`, `unt_mascot.png`, `recovery_code.txt` 파일을 본인 저장소의 `_posts/`에 업로드. 위 코드의 URL은 `what0302/what0302.github.io/master`를 기준으로 작성됨.

`setup_lab.py`, `keygen.py`는 별도로 준비하는 초기 세팅 단계이며, 매 실행 때 실행하지 않음.

## 실행
1. VM 스냅샷을 생성하고 본인이 소유한 Kali 게스트 VM을 전면에 둠.
2. `payload_ducky.txt`를 Hak5 Payload Studio로 컴파일하여 사용.
3. GitHub의 프로그램을 가져와 `encrypted_output`에 암호문 복사본을 생성하고 GUI 표시.
4. `VIEW ENCRYPTED COPIES`에서 `.unt` 확인.
5. 복구 코드 입력 → GitHub `decrypt.py` 다운로드 후 `recovered_output` 생성 및 SHA-256 검증.

## 반복 실습
`encrypted_output` 및 `recovered_output`을 **확인한 다음 별도로 보관하거나 삭제**하고 다시 시연하세요. 원본 `critical_EUID` 폴더는 그대로 남습니다. 키 파일은 분실하면 안 됩니다.

## 과제에서 추가로 필요한 것
- 실제 EUID 및 과제 지정 문서/폴더를 사용해야 함.
- 이 버전은 암호문 복사본을 생성하므로 교수님이 명시한 '원본 대상 디렉터리 직접 암호화' 시나리오와 차이가 있음.
- Monitoring / Detection / Mitigation은 현재 포함하지 않았음.
- 최종 제출에 필요한 README, 주석, 라이브러리 링크, 작동 검증, 보고서, 발표 영상 별도 준비.
