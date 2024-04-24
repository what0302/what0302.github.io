# Linux 웹쉘 탐지
##### 작성자: 김태현 사원
##### 작성일자: 2024년 4월 24일
</br>


## (1) 개요
2024년 4월 18일자로 금융보안원 인텔리전스 보고서 페이지에 금융정보 탈취 공격에 대한 심층 분석 보고서가 기재됨.
<br><br>
금융보안원 보고서 링크 : <br>
https://www.fsec.or.kr/bbs/detail?menuNo=244&bbsNo=11451
<br><br>
2022년 9월, 금융보안원은 특정 쇼핑몰 웹사이트에 삽입된 신용카드 정보를 탈취하는 피싱 결제페이지를 분석하게 되면서, 신용카드 정보를 노리는 새로운 위협 그룹 EvilQueen을 식별하였고, 이들이 국내를 대상으로 수행한 오퍼레이션에 대해 상세 추적하였음.<br><br>
이에 대한 결과로, 자체 개발한 프로그램을 통해 5천여개 온라인 쇼핑몰을 분석하여 피싱페이지가 삽입된 50여개의 쇼핑몰을 발견하였음.<br><br>
![스크린샷 2024-04-24 오전 11 38 18](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/165347210/3c49f0c2-16c5-4759-b980-0ba346e83363)
<br><br>
일부 피싱 결제페이지가 삽입된 쇼핑몰의 웹서버를 분석한 결과, SQL 인젝션 공격 이후 관리자 페이지 로그인 및 웹쉘 업로드 등의 공격 절차가 확인되었음.
<br><br>
업로드된 웹쉘은 기본적으로 파일 목록 확인, 파일 업로드, 명령어 전송, 리버스 연결 등의 다양한 기능이 존재함. 이러한 기능을 통해 공격 조직은 피해 시스템에 대한 제어권을 획득하고, 원격에서 해당 시스템에 지속적으로 접근하여 악성 행위를 수행한 것으로 확인됨.
<br><br>
![스크린샷 2024-04-24 오전 11 42 48](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/165347210/75a560f3-bd0a-416d-87b1-496e63163f34)
<br><br>

## (2) 대응
국내 중·소규모 쇼핑몰 해킹을 통한 카드정보 탈취 및 부정결제 사고를 심층 분석한 결과, 다음과 같은 피싱 결제페이지 관련 악성파일을 탐지하였음. @별첨 참조
<br><br>
리눅스 운영체제의 경우 성능 혹은 인식 문제로 백신 설치가 미흡한 경우가 많으므로 침해사고 발생 시 피해가 겉잡을 수 없이 커질 수 있음.
<br><br>
이에 빠르게 대응하고자, 쉘 스크립트를 구동하여 웹 페이지 디렉토리 내에 악성 md5 해시값을 가진 파일이 있는지 탐지할 예정임
<br><br>
```sh
#!/bin/bash

# 탐지할 디렉토리 지정
TARGET_DIRECTORY="/target_directory"

# 악성 파일의 MD5 해시값 목록
# 예시: MD5_VALUES=("e4d909c290d0fb1ca068ffaddf22cbd0" "another-md5-value")
MD5_VALUES=("md5-value-1" "md5-value-2" "md5-value-3")

# 타겟 디렉토리 안의 모든 파일에 대해 반복
find "$TARGET_DIRECTORY" -type f | while read -r file
do
  # 파일의 MD5 해시값 계산
  FILE_MD5=$(md5sum "$file" | awk '{ print $1 }')

  # 계산된 해시값이 악성 파일의 해시값 목록에 있는지 확인
  for md5 in "${MD5_VALUES[@]}"; do
    if [[ "$FILE_MD5" == "$md5" ]]; then
      echo "악성 파일 탐지: $file"
    fi
  done
done
```
<br><br>
다음은 리눅스 환경에서 실행할 수 있는 쉘 스크립트임. 이 스크립트는 특정 디렉토리(/target_directory) 안에 있는 모든 파일에 대해 MD5 해시값을 계산하고, 미리 정의된 악성 파일의 MD5 해시값 목록과 비교하여 일치하는 경우 해당 파일의 경로를 출력함. 다음과 같은 설정을 추가해야함.
<br><br>
1. TARGET_DIRECTORY 변수에 탐지할 디렉토리 경로를 정확히 설정
2. MD5_VALUES 배열에 탐지하고자 하는 악성 파일의 MD5 해시값을 정확히 입력
3. 터미널에서 chmod +x detect_malware.sh 명령을 사용하여 실행 권한을 부여
<br><br>
## (3) IoC
bc_ok.php 25347d0ee959565fd9ce485862af6248<br>
bc.php 917158fa1936c565bc93cec4c5179707<br>
bc1.php 2f512e7616f9a0133497128a9005cdd3<br>
bc2.php 5695841722af3215f1ab7561258f204c<br>
checkCardBin.php f142ae7c54373f6b4ece9d17c9232108<br>
checkRedirectApprvJson.php 054c491eee6cae3bf46ac0c0a2b47ac7<br>
error.php 10312d1ae949278b2781fb87cd147fdf<br>
hanacard_ok.php 715005a6e399c30d251e9cb3fc7a663d<br>
hanacard.php ddb90059d1da9301debf19138c4471a1<br>
hanacard1_step1.php 5fbd8a73abdb01b3cb2a05bfcbef66ba<br>
hanacard1.php e1963c50761bb84cae73d301f3f2161a<br>
hanacard2.php 45c5d7ad6303a795bf826164c9f4e180<br>
huaka.php ddb90059d1da9301debf19138c4471a1<br>
huaka1.php e1963c50761bb84cae73d301f3f2161a<br>
index.php a783c4a6884edd50300f37fd0ef1399d<br>
kb_ok.php a2508341c1bd0e61b20a843532a0b8bf<br>
kb_step1.php e6bae1ac3e26d0c118c035a5971f5b0b<br>
kb.php 265cb23461586ba0aa77c49e81edefcb<br>
kb1.php 265cb23461586ba0aa77c49e81edefcb<br>
le_ok.php 3b0b36a24651d56fd20186d46519ec38<br>
le.php 3e6a0a60eb1008daeaaedd7595daa64e<br>
le1.php 8854bd5253e64f12e1285b7fd2f5de84<br>
mobileGW.php 0cc2d6de3087739390a927def5e9dc25<br>
nh_ok.php 4245c1dcb245bef467f2b3978c9340da<br>
nh_step1.php 3564a42d9b83d576143d5bd6a0180788<br>
nh.php 717b588702d93f4960a52d17b9deaf41<br>
nh1.php 717b588702d93f4960a52d17b9deaf41<br>
payerror.php 25d873eb92db4f042f6dd1967a1f3c61<br>
phone.php 4cc4f118bb74a8c574b78a9713f7a8c4<br>
phonecc.php 05818725779729b0686e162e8eb4ac5e<br>
phonekb.php feccfcafa89f043fc2dfc2940311d64c<br>
shanxing_ok.php edc3c05fbc54e2c11352c44fb3f1105c<br>
shanxing_step1.php cd17268789ed546433ced0837cb2aed8<br>
shanxing_step2.php c5fcd025824288e8db29a5d7e675c7cc<br>
shanxing.php db695b7fdd9e72bba89107511f14d1b9<br>
shanxing1_step1.php b2a6100d093bed2176aa824739be32c1<br>
shanxing1.php 24a76d92f7685eaa9dfe153de64f8b8d<br>
test.php 59e352a18f2c520b148402ffd7d8c940<br>
top.php 4755f840c1576385f70c9cf3714e0102<br>
xandai_ok.php 9a3fcd518852760557358a87ef61bcac<br>
xandai_step1.php f6fea5c5ec6e1ae815c5d63058c4087a<br>
xandai.php e1ea7559e525aea6963502e4d158c038<br>
xandai1.php e1ea7559e525aea6963502e4d158c038<br>
xinghan_ok.php 9d42602cbde6abdff209161a4b00e08a<br>
xinghan_step1.php fc5af8616572a1519985ea90fae29cb9<br>
xinghan.php 32af3fa8db98729ba98ecb4a9895fa03<br>
xinghan1.php 20f2318737364e3cfa665d08e40b8d4c<br>
