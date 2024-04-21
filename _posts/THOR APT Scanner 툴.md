# THOR APT Scanner 툴을 활용한 침해 진단 업무
##### 원작자: 문광일 PM
##### 링크: [KOROMOON][KOROMOONlink]
[KOROMOONlink]: https://koromoon.blogspot.com/2022/09/thor-apt-scanner.html "Go KOROMOON"
##### 작성자: 김태현 사원
##### 작성일자: 2024년 4월 9일
</br>


## (1) THOR APT Scanner
- Nextron Systems 사에서 개발한 침해 진단 도구로 수천 개의 YARA 및 Sigma 규칙, IOC, 루트킷 및 이상 검사로 구성된 거대한 서명 세트를 통해 모든 종류의 위협을 검사하는 도구임.
- 홈페이지 링크 : https://www.nextron-systems.com/
- 아래와 같이 제품별로 기능이 분류되며 THOR 10은 기업용 제품으로 금액적으로 부담됨.
- 금액 부담없이 일반 기업체에서 침해 진단 업무에 사용할 경우 무료 THOR Lite 제품으로도 가능함.
- 보통 실서비스 서버에 웹쉘 파일이나 악의적인 도구 존재 여부에 대해 파일 검사 선에서 진단하면 됨.

</br><div align="center"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEheekMwbBM5SjT5kiE1M2-jmemMoeiGssaM__pZW5kgcuUCrFghQNEks1uxUx5vBFHt5Rs2pTQC2PlM-h_2xgsRN24yROMwt7v7bv3xBaFM7B2k-m7baVX8d_koPCBMWPV_mUVzOFFC4mYEOYZZG831HMfo9U3J3RI7Lqg-37YDrRLQQx6G9aqWUBaT/w640-h484/%EC%A0%9C%ED%92%88%EB%B3%84%20%EA%B8%B0%EB%8A%A5%20%EB%B6%84%EB%A5%98%ED%91%9C.png"></div>
<div align="center">&lt; 제품별 기능 분류표 &gt;</div></br>

- 참고로 백신 같은 경우 탐지/삭제하는 문제로 추후에 진단 시 보고나 포렌식 업무에 문제가 생길 수 있음.
- 또한, 리눅스 서버에서는 유료 백신을 설치할 경우, 서버당 라이센스 비용이 상당하며 실서비스에 구동할 경우, 오탐으로 인한 서비스 파일 삭제 등 문제가 발생할 수 있음.
- 리눅스 서버에 설치가 안되는 경우가 더러 있으며 THOR APT Scanner와 같이 상용 침해 진단 도구를 이용하여 업무에 활용함.

## (2) THOR 명령어
- THOR Lite 10.7.3 버전에서 명령어를 조사함.
- 방대한 관계로 아래 별첨을 참조 바람.

## (3) THOR Lite 제품 사용 예제
- THOR Lite 제품 다운로드 시 Nextron Systems 사 홈페이지에 가입을 해야 다운로드가 가능하며, 사용 라이센스 파일도 가입해야함.
- 사용 라이센스 기간은 1년이며 짧은 기간이 아니므로 큰 문제는 안됨.
- **참고로 사용 라이센스 파일은 THOR Lite 프로그램 디렉토리 안에 위치해야 사용이 가능함.**

</br><div align="center"> <img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjzQWZP2aAsAHJTbH3GIfHume4jCSbE05jezOMifdLI-pNZfALITnKnafWnYEYXFbwz88h1nQQDzycYOm7WRc9DA20NSacaSAiIQLCr3St5X2-Suf_1u3C_dxrSpIYCqkMnnlGX2krQNooqQSpTqFJPsn7BdQDUnFyGenxPXZtE30hxd99E14DJD14F/w640-h338/%EC%82%AC%EC%9A%A9%20%EB%9D%BC%EC%9D%B4%EC%84%BC%EC%8A%A4%20%ED%8C%8C%EC%9D%BC%20%EC%9C%84%EC%B9%98%20%ED%99%94%EB%A9%B4_%EA%B0%80%EA%B3%B5.png"></div>

<div align="center">&lt; 사용 라이센스 위치 화면 &gt;</div></br>

- **THOR Lite 제품은 포터블 형식으로 관리자 권한이나 root 권한으로 실행해야 하며 커맨드 라인에서 필요한 옵션만 사용하여 침해 진단함.**

- 그러나 모듈 중에서 Autoruns, Filescan, ProcessCheck만 가능하므로 파일 검사 선에서만 진단 가능함.

- 아래 명령어는 서버에서 안정적으로 구동하기 위해 CPU 20%를 넘기지 않고 우선순위는 매우 낮은 수준으로 특정 폴더만 파일 스캔하도록 하는 명령어 예제들임.
- 드라이브 전체도 검사가 가능하며, 테스트한 결과 윈도우 시스템 약 30만개 파일을 1시간 내로 검사 가능함.
- 최신 웹쉘 모음집 샘플을 대상으로 테스트한 결과, 약 90% 이상 탐지되는 것으로 확인됨.

`thor64-lite.exe -c 20 --verylowprio -a Filescan -p C:\Users\KOROMOON\Desktop\webshell-master`

`thor64-lite.exe -c 20 --verylowprio -a Filescan -p C:\\`

`sudo ./thor-lite-linux-64 -c 20 --verylowprio -a Filescan -p /`

</br><div align="center"> <img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgggCQA50NZLs3_X-BNJoSSGYcIJYTzCgpGzXdIUGsI-4t9E3oTgOaNkahdnhoRfmdqu6db2QZ3HJlD0U0AOBwxcob-zGPuHi0EKUTDxUKzDBGUmXLtE0nES0uZDpqB-HeI-BYCdEzEPZDTRmn9aMn05bVP2Eomsrk7khrRm0_QqkGMFGt_N6N0VHKt/w640-h274/%EC%9C%88%EB%8F%84%EC%9A%B0%20%EC%8B%9C%EC%8A%A4%ED%85%9C%20%EA%B2%80%EC%82%AC%20%ED%99%94%EB%A9%B4_%EA%B0%80%EA%B3%B5.png"></div>

<div align="center">&lt; 윈도우 시스템 실행 화면 &gt;</div></br>

</br><div align="center"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgPapZRHYG-S8K8I-YzdfhcuD9JRT2Oi7zJ5GUo5GyAOdjvy36Pcvo6X82q3LdUZxu4yfBR4ue23KyT3X-HE_HrUOdGzjSKaYC67U5npJO6L07m_LfskkDPK48ycX8P628EKA2kW6w1tYL7XINyA7oXv1qmFu_aqG9xBIp7omDQ-AMaFP1dyvC_U148/w640-h308/%EB%A6%AC%EB%88%85%EC%8A%A4%20%EC%8B%9C%EC%8A%A4%ED%85%9C%20%EA%B2%80%EC%82%AC%20%ED%99%94%EB%A9%B4_%EA%B0%80%EA%B3%B5.png"></div>
<div align="center">&lt; 리눅스 시스템 실행 화면 &gt</div></br>

- 제품에 기본적으로 제공하는 YARA 규칙으로도 상당수 탐지가 가능하며 아래 링크에서 고도화된 APT 관련 YARA 규칙을 추가할 수 있음. (주기적 업데이트 가능)
- APT 관련 YARA 규칙 다운로드 링크 : [https://github.com/Neo23x0/signature-base/tree/master/yara](https://github.com/Neo23x0/signature-base/tree/master/yara)

<details><summary>(4) 별첨. THOR 명령어</summary>
`>> thor64-lite.exe --version

  

THOR 10.7.3 (windows, amd64)

Build 11e6727 (2022-07-27 07:33:47)

YARA 4.2.2

PE-Sieve 0.3.3

OpenSSL 1.1.1l

Signature Database 2022/09/01-120047

  

  

>> thor64-lite.exe --fullhelp

  

   ###++++++   ________ ______  ___

   ###++++++  /_  __/ // / __ \/ _ \

   ###   +++   / / / _  / /_/ / , _/

   ###   +++  /_/ /_//_/\____/_/|_|  Lite

   ######+++ 

   ######+++  APT Scanner

  

  

01. 검사 옵션

  -t, --template string              해당 YAML 파일에서 기본 검사 매개변수를 처리함.

      --generate-config              주어진 매개변수에서 YAML 구성을 인쇄하고 종료함.

  -p, --path strings                 특정 파일 경로를 검사함. 이 옵션을 여러 번 지정하여 여러 경로를 정의함.

                                     비재귀 검사의 경우 경로에 ':NOWALK' 를 추가함. (기본값 : 시스템 드라이브만, 기본값 [])

      --allhds                       모든 로컬 하드 드라이브를 검사함. (Windows 시스템만 해당, 기본값 : 시스템 드라이브만)

      --alldrives                    네트워크 드라이브 및 ROM 드라이브를 포함한 모든 로컬 드라이브를 검사함. (기본값 : 시스템 드라이브만)

      --max_file_size uint           확인할 최대 파일 크기임. (더 큰 파일은 무시됨)

                                     이 제한을 늘리면 THOR 툴의 메모리 사용량이 증가함. (기본값 30MB)

      --max_file_size_intense uint   집중 검사를 위한 최대 파일 크기 (사용되지 않음, 기본값 200MB)

      --max_log_lines int            나머지 줄을 건너뛰기 전에 로그 파일을 체크인할 최대 줄 수임. (기본값 1,000,000)

      --max_process_size uint        확인할 최대 프로세스 크기임. (더 큰 프로세스는 무시됨, 기본값 2GB)

      --max_runtime int              최대 실행 시간임.

                                     지정된 시간이 지나면 THOR 툴이 중지됨.

                                     0 은 최대 런타임이 없음을 의미함. (기본값 168 시간)

      --nodoublecheck                다른 THOR 인스턴스가 실행 중인지 확인하지 마십시오.

                                     (예를 들어 여러 탑재 이미지가 단일 시스템에서 동시에 검사되는 Lab 사용 사례, Forensic Lab 라이센스가 필요함)

  -f, --epoch strings                시작 및 종료 날짜 쌍으로 기재하여 공격자 활동이 있는 날짜 범위를 지정함.

                                     이 날짜 사이에 생성/수정된 파일은 추가 점수를 받음. (지정된 시작 날짜 포함, 지정된 종료 날짜 제외)

                                     예제 : - f 2009-10-09 -f 2009-10-10 옵션 표시은 2009-10-09 공격 날짜를 표시함.

                                     (기본값 [])

      --epochscore int               공격자 활동이 있는 날에 생성/수정된 파일이 있을 경우 추가할 점수임.

                                     (--epoch 매개변수 참조, 기본값 35)

      --insecure                     TLS 호스트 확인을 건너뜀. (불안정함)

      --ca strings                   TLS 핸드쉐이크 중 호스트 인증서 확인을 위한 루트 CA 임. (기본값 [])

      --cross-platform               경로 구분자 플랫폼이 있는 IOC 를 독립적으로 적용함.

      --require-admin                관리자 권한 없이 THOR 를 실행하면 즉시 종료됨.

      --follow-symlinks              디렉토리를 가리키는 파일 검사 중에 심볼릭 링크가 발견되면 디렉토리를 검사함.

      --max-recursion-depth uint     검사할 아카이브의 최대 깊이임. (기본값 4)

      --max-nested-objects uint      검사할 아카이브당 최대 파일 수임. (기본값 10,000)

  

  

  

02. 검사 모듈

      --quick                      일부 감지 비용으로 검사 속도를 높이려면 여러 플래그를 활성화하십시오.

                                   이것은 다음과 같음 : --noeventlog --nofirewall --noprofiles --nowebdirscan --nologscan --noevtx --nohotfixes --nomft --lookback 3 --lookback-modules filescan

      --soft                       CPU 및 RAM 집약적인 모듈을 건더뛰고 실행 파일의 압축을 풀지 않고 DoublePulsar 백도어 검사를 수행하지 않으며 최대 CPU 사용량을 70% 로 낮추고 THOR 에 대해 낮은 우선 순위를 설정함.

                                   이 모드는 CPU 코어가 1개이거나 RAM이 1024 MB 미만인 시스템에서 자동으로 활성화됨.

                                   (CPU 및 RAM 집약적인 모듈 : 뮤텍스, 방화벽, 로그온, 네트워크 세션 및 공유, LSA 세션, 열린 파일, 호스트 파일)

      --intense                    soft 모드를 비활성화하고, 덤프 파일 분석, MFT 분석 및 시그마 규칙을 활성화하고, 관련성이 낮은 레지스트리 키를 건너뛰지 않고, 크기에 관계없이 프로세스를 검사하고, 달리 지정하지 않는 한 max_file_size 를 200 MB 로 설정함.

                                   경고 : 이 검사 모드는 시스템 안정성에 영향을 미치는 작업을 수행함. 위험을 감수하지 않는 한 라이브 검사에서 이 모드를 사용하지 마십시오.

      --diff                       각 모듈의 확인 시간을 모듈이 성공적으로 실행된 마지막 시간으로 설정하고 --global-lookback 을 활성화함. (--lookback 참조)

                                   사실상 이것은 마지막 검사 이후에 변경된 요소만 검사됨을 의미함. (ThorDB 가 활성화된 경우에만 작동)

      --lookback int               분석할 지난 날 수를 지정함.

                                   이 시점 이전의 이벤트 로그 항목은 무시됨.

                                   0 은 제한이 없음을 의미함. (기본값 0)

      --global-lookback            Lookback 을 지원하는 모든 모듈에 Lookback 을 적용함. (이벤트로그 뿐만 아니라)

                                   --lookback 및 --lookback-modules 도 참조하십시오.

                                   경고 : 타임스탬프 또는 이와 유사한 안티바이러스 회피 방법으로 인해 요소가 검사되지 않을 수 있음.

      --force-aptdir-lookback      FileScan 모듈의 모든 파일에 조회 응용 프로그램을 시행함.

                                   기본적으로 특히 위험에 처한 디렉토리는 Lookback 값을 무시함.

      --lookback-modules strings   주어진 모듈에 Lookback 을 적용함.

                                   --lookback 및 --modules 도 참조하십시오.

                                   경고 : 타임스탬프 또는 이와 유사한 안티바이러스 회피 방법으로 인해 요소가 검사되지 않을 수 있음.

                                   (기본값 [이벤트로그])

      --lab                        lab 검사 모드는 파일 시스템만 검사하고, 리소스 검사 및 quick 모드를 비활성화하고, intense 모드를 활성화하고, ThorDB 를 비활성하고, IOC 플랫폼을 독립적으로 적용하고, 모든 CPU 코어를 사용함.

                                   이 옵션은 기본적으로 모든 드라이브를 검색하지만 종종 -p 옵션과 함께 사용하여 단일 경로만 검색함.

                                   Forensic Lab 라이센스가 필요함.

      --virtual-map strings        다른 접두사를 사용하도록 찾은 파일 경로를 다시 작성하십시오.

                                   이는 파일의 현재 위치가 원래 위치와 일치하지 않아 참조가 오래되었을 수 있는 마운트된 이미지에 유용할 수 있음.

                                   원래 및 현재 경로를 --virtual-map path/to/current/location:path/to/original/location 으로 지정함.

                                   Windows 시스템에서는 드라이브 이름도 지원됨.

                                   F: 드라이브가 원래 C: 로 사용된 경우 --virtual-map F:C 를 지정함.

                                   Forensic Lab 라이센스가 필요함. (기본값 [])

  

  

03. 리소스 옵션

  -c, --cpulimit float        CPU 사용량을 지정한 설정값(백분율)으로 제한함.

                              최소값은 15%임. (기본값 90)

      --nocpulimit            cpulimit 검사를 비활성화함.

      --nosoft                soft 모드의 자동 활성화를 비활성화함. (--soft 참조)

      --norescontrol          시스템에 리소스가 부족한지 확인하지 마십시오.

                              리소스 부족으로 인해 취소된 검사를 시행하려면 이 옵션을 사용하십시오.

                              (주의해서 사용하세요!)

      --minmem uint           사용 가능한 실제 메모리 양이 지정된 값 아래로 떨어지면 실행 중인 검사을 취소함.

                              (단위 MB, 기본값 50)

      --lowprio               THOR 프로세스의 우선 순위를 더 낮은 수준으로 줄임.

      --verylowprio           THOR 프로세스의 우선 순위를 매우 낮은 수준으로 줄임.

      --nolowprio             soft 모드로 인해 THOR 프로세스의 우선 순위를 더 낮은 수준으로 낮추지 마십시오.

                              (--soft 참조)

      --nolockthread          C 라이브러리에 대한 호출을 주 스레드에 잠그지 마십시오.

                              (메모리 사용량을 희생시키면서 성능을 향상시킬 수 있음)

      --yara-stack-size int   YARA 스택에 대해 이수의 슬롯을 할당함. (기본값 16384)

                              이 제한을 늘리면 더 많은 메모리 오버헤드가 있지만 더 큰 규칙을 사용할 수 있음. (기본값 16384)

      --yara-timeout int      지정된 시간보다 오래 걸리는 YARA 검사를 취소함. (단위 초, 기본값 60)

      --threads uint16        지정된 수량의 THOR 스레드를 병렬로 실행함.

                              Forensic Lab 라이센스가 필요함.

      --bulk-size uint        지정된 수량의 요소를 함께 확인하십시오.

                              예를 들어 로그 라인 또는 레지스트리 항목 (기본값 20MB)

  

  

04. 특수 검사 모드

  -m, --image_file string          주어진 단일 메모리 이미지/덤프 파일만 검사함. (디스크 이미지에는 사용하지 않고 --lab 으로 마운트된 이미지를 검사함)

                                   Forensic Lab 라이센스가 필요함.

      --image-chunk-size uint      지정된 크기의 청크(chunk)로 이미지/덤프 파일을 검사함. (기본값 11MB)

  -r, --restore_directory string   DeepDive 동안 YARA 규칙에 일치하는 PE 파일을 지정된 폴더에 복원함.

      --restore_score int          주어진 값보다 높은 총 일치 점수를 가진 청크(chunk)만 복원함. (기본값 50)

      --dropzone                   특정 디렉토리에 드롭된 모든 파일을 관찰하고 검사함. (-p 옵션과 함께 전달되어야 함)

                                   리소스 검사 및 quick 모드를 비활성화하고 intense 모드를 활성화하고 ThorDB 를 비활성화하고 IOC 플랫폼을 독립적으로 적용함.

                                   Forensic Lab 라이센스가 필요함.

      --dropdelete                 검사 후 드롭 영역에 드롭된 모든 파일을 삭제함.

  

  

05. Thor Thunderstorm 서비스

      --thunderstorm                      특정 포트로 전송된 모든 파일을 감시하고 검사함. (--server-port 참조)

                                          리소스 확인 및 quick 모드를 비활성화하고 intense 모드를 활성화하고 ThorDB 를 비활성화하고 IOC 플랫폼을 독립적으로 적용함.

      --server-upload-dir string          THOR 가 업로드된 파일을 삭제하는 디렉토리의 경로임.

                                          이 경로가 존재하지 않으면 THOR 가 생성을 시도함.

                                          (기본값 : "C:\\Users\\[사용자명]\\AppData\\Local\\Temp\\thor-uploads")

      --server-host string                THOR 서버가 바인딩해야 하는 IP 주소임. (기본값 "127.0.0.1")

      --server-port uint16                THOR 서버가 바인딩해야 하는 TCP 포트임. (기본값 8080)

      --server-cert string                THOR 서버가 사용해야 하는 TLS 인증서임. 비워두면 TLS 가 사용되지 않음.

      --server-key string                 THOR 서버가 사용해야 하는 TLS 인증서의 개인키임. --server-cert 가 지정된 경우 필수임.

      --server-store-samples string       --server-upload-dir 로 지정된 폴더에 샘플을 영구적으로 저장할 지 여부를 설정함.

                                          모든 샘플을 저정하려면 "all" 을 지정하고 경고 또는 알림을 생성한 샘플만 저장하려면 "malicious" 를 지정함. (기본값 "none")

      --server-result-cache-size uint32   비동기 요청의 결과를 임시로 저장하는 데 사용되는 캐시의 크기임.

                                          0 으로 설정하면 캐시가 비활성화되고 비동기 결과가 저장되지 않음. (기본값 250,000)

      --pure-yara                         YARA 서명을 사용하여 파일만 검사함.

                                          (모든 프로그래밍 방식 검사, STIX, Sigma, IOC 및 대부분의 기능 및 모듈 비활성화)

      --sync-only-threads uint16          동기 요청을 위해 지정된 수량의 THOR 스레드를 예약함.

      --force-max-file-size               크기에도 불구하고 일반적으로 검사되는 레지스트리 하이브 또는 로그 파일과 같은 파일에도 최대 파일 크기를 적용함.

  

  

06. 라이센스 검색

      --asgard string           라이센스를 요청해야 하는 ASGARD 서버의 호스트 이름임.

                                (예 : asgard.my-company.internal)

      --asgard-token string     해당 토큰을 사용하여 asgard 서버 라이센스 API 로 인증함.

                                토큰은 ASGARD 의 '다운로드' 똔,ㄴ '라이센스' 섹션에서 찾을 수 있음.

                                ASGARD 2.5 이상이 필요함.

  -q, --license-path string     THOR 라이센스가 포함된 경로임. (기본값은 어플리케이션 디렉토리)

      --portal-key string       해당 API 키를 사용하여 portal.nextron-systems.com 에서 이 호스트에 대한 라이센스를 얻으십시오.

                                이 기능은 호스트 기반 서버/워크스테이션 계약에서만 지원됨.

      --portal-contracts ints   라이센스 생성을 위해 해당 계약을 사용하십시오.

                                계약이 지정되지 않은 경우 포털은 자체적으로 계약을 선택함.

                                --portal-key 참조하십시오. (기본값 [])

      --portal-nonewlic         포털의 기존 라이센스만 사용하십시오.

                                존재하지 않으면 종료함.

                                --portal-key 를 참조하십시오.

  

  

07. 활성 모듈

  

사용 가능한 모듈 : Filescan, Timestomp, DeepDive, EnvCheck, Hosts, LoggedIn, UserDir, Autoruns, Dropzone, Firewall, ProcessCheck, Rootkit, ServiceCheck, Thunderstorm, Users, AtJobs, DNSCache, EtwWatcher, Eventlog, Events, HotfixCheck, LSASessions, MFT, Mutex, NetworkSessions, NetworkShares, Pipes, RegistryChecks, SHIMCache, ScheduledTasks, WMIStartup

  

  -a, --module strings      다음 모듈만 활성화하십시오. (여러 모듈을 -a Module1 -a Module2 ... -a ModuleN 으로 지정, 기본값 [])

      --noprocs             프로세스를 분석하지 마십시오.

      --nofilesystem        파일 시스템을 검사하지 마십시오.

      --noreg               레지스트리를 분석하지 마십시오.

      --nousers             사용자 계정을 분석하지 마십시오.

      --nologons            현재 로그인한 사용자를 표시하지 마십시오.

      --noautoruns          자동 실행 요소를 분석하지 마십시오.

      --noeventlog          이벤트 로그를 분석하지 마십시오.

      --norootkits          루트킷을 검사하지 마십시오.

      --noevents            악성 이벤트를 검사하지 마십시오.

      --nodnscache          로컬 DNS 캐시를 분석하지 마십시오.

      --noenv               환경 변수를 분석하지 마십시오.

      --nohosts             호스트 파일을 분석하지 마십시오.

      --nomutex             악성 뮤텍스를 검사하지 마십시오.

      --notasks             예약된 작업을 검사하지 마십시오.

      --noservices          서비스를 분석하지 마십시오.

      --noprofiles          프로필 디렉토리를 분석하지 마십시오.

      --noatjobs            'at' 도구로 예약된 작업을 분석하지 마십시오.

      --nonetworksessions   네트워크 세션을 분석하지 마십시오.

      --nonetworkshares     네트워크 공유를 분석하지 마십시오.

      --noshimcache         SHIM 캐시 항목을 분석하지 마십시오.

      --nohotfixes          핫픽스(Hotfixes)를 분석하지 마십시오.

      --nowmistartup        WMI 를 사용하여 시작 요소를 분석하지 마십시오.

      --nofirewall          로컬 방화벽을 분석하지 마십시오.

      --nowmi               WMI 기능으로 모든 검사를 비활성화함.

      --nolsasessions       lsa 세션을 분석하지 마십시오.

      --nomft               드라이브의 MFT 를 분석하지 마십시오. (intense 모드가 아닌 경우 기본값)

      --mft                 드라이브의 MFT 를 분석함.

      --nopipes             명명된 파이프를 분석하지 마십시오.

      --noetwwatcher        THOR 런타임 동안 ETW 로그를 분석하지 마십시오.

      --nointegritycheck    Linux 에서 패키지 무결성에 대해 패키지 관리자에게 검사하지 마십시오.

      --timestomp           타임스탬프 감지를 활성화함.

      --notimestomp         타임스탬프 감지를 비활성화함.

  

  

08. 모듈 추가 기능

      --process ints              검사할 프로세스 ID 임.

                                  이 옵션을 여러 번 지정하여 여러 프로세스를 정의함.

                                  (기본값 : 모든 프로세스, 모듈 : Process Check, 기본값 [])

      --dump-procs                의심스럽거나 악의적인 프로세스에 대한 프로세스 덤프를 생성함. (모듈 : ProcessCheck)

      --max-procdumps uint        지정된 최대 수량의 프로세스 덤프를 만듬. (모듈 : ProcessCheck, 기본값 10)

      --procdump-dir string       지정된 디렉토리에 의심스러운 프로세스의 프로세스 덤프를 저장함. (모듈 : ProcessCheck, 기본값 : "%ProgramData%\\thor")

  -n, --eventlog-target strings   특정 이벤트 로그를 검사함.

                                  (예 : 'Security' 또는 'Microsoft-Windows-Sysmon/Operational', 모듈 : Eventlog, 기본값 [])

      --nodoublepulsar            DoublePulsar 백도어를 검사하지 마십시오. (모듈 : Rootkit)

      --full-registry             관련성이 낮은 레지스트리 하이브 키를 건너뛰지 마십시오. (모듈 : Registry)

      --noregwalk                 레지스트리 검사 중에 전체 레지스트리를 검사하지 마십시오.

      --showdeleted               MFT 에서 발견된 삭제된 파일을 'info' 메시지로 표시함.

      --allfiles                  일반적으로 관심이 없는 파일을 포함하여 모든 파일을 검사함.

                                  달리 지정하지 않는 한 --max_file_size 를 200 MB 로 설정함.

      --ads                       모든 파일에 대해 대체 데이터 스트림을 검사함.

  

  

09. 활성 기능

      --nothordb               검사 정보를 보관하기 위해 ThorDB 데이터베이스를 사용하거나 생성하지 마십시오.

      --sigma                  Sigma 서명으로 검사함. (지원 중단됨 : 기본적으로 활성화됨)

      --nosigma                Sigma 서명 비활성화함.

      --dumpscan               메모리 덤프를 검사함.

      --nologscan              로그 파일을 검사하지 마십시오. (.log 확장자 또는 위치로 식별됨)

      --noyara                 YARA 로 검사를 비활성화함.

      --nostix                 STIX 로 검사를 비활성화함.

      --noarchive              아카이브 내용을 검사하지 마십시오.

      --noc2                   알려진 C2 도메인에 대한 검사를 비활성화함.

      --noprochandles          프로세스 핸들을 분석하지 마십시오.

      --noprocconnections      프로세스 연결을 분석하지 마십시오.

      --noamcache              Amcache 파일을분석하지 마십시오.

      --noregistryhive         레지스트리 하이브 파일을 분석하지 마십시오.

      --noexedecompress        포터블(portable) 실행 파일의 압축을 풀고 검사하지 마십시오.

      --nowebdirscan           프로세스 핸들에서 발견된 웹 디렉토리를 분석하지 마십시오.

      --novulnerabilitycheck   시스템의 취약점을 분석하지 마십시오.

      --noprefetch             프리페치(prefetch) 디렉토리를 분석하지 마십시오.

      --nogroupsxml            groups.xml 을 분석하지 마십시오.

      --nowmipersistence       WMI 지속성을 검사하지 마십시오.

      --nolnk                  LNK 파일을 분석하지 마십시오.

      --noknowledgedb          Mac OS 에서 knowledge DB 를 검사하지 마십시오.

      --nower                  .wer 파일을 분석하지 마십시오.

      --noevtx                 EVTX 파일을 분석하지 마십시오.

      --noauthorizedkeys       authorized_keys 파일을 분석하지 마십시오.

      --noimphash              의심스런 EXE 파일의 해시값을 계산하지 마십시오. (Windows 시스템만 해당)

      --c2-in-memory           프로세스 메모리에 C2 IOC 를 적용함. (브라우저 및 기타 프로세스 메모리에서 많은 가용성을 기꺼이 허용하지 않는 한 권장하지 않음)

      --custom-c2-in-memory    프로세스 메모리에 사용자 지정 C2 IOC를 적용함.

      --noeml                  이메일 파서를 비활성화함.

  

  

10. 추가 기능

      --customonly            사용자 정의 서명만 사용 (모든 내부 THOR 서명 및 탐지 비활성화)

      --full-proc-integrity   프로세스 가장(impersonation) 탐지를 위해 --processintegrity 감도를 높임.

                              오탐을 일으킬 가능성이 높지만 실제 위협을 더 잘 탐지함.

      --processintegrity      PE-Sieve 를 실행하여 프로세스 무결성을 확인함. (Windows 시스템만 해당)

  

  

11. 출력 옵션

  -l, --logfile string                                    텍스트 출력을 위한 로그 파일 (기본값 ":hostname:_thor_:time:.txt")

      --htmlfile string                                   HTML 출력을 위한 로그 파일 (기본값 ":hostname:_thor_:time:.html")

      --nolog                                             텍스트 또는 HTML 로그 파일을 생성하지 마십시오.

      --nohtml                                            HTML 보고서 파일을 만들지 마십시오.

      --appendlog                                         덮어쓰기 대신 기존 로그에 텍스트 로그를 추가함.

      --keyval                                            키 값 쌍으로 텍스트 및 HTML 로그 파일의 형식을 지정하여 SIEM 시스템에서 필드 추출을 단순화함. (key='value')

      --json                                              json 보고서 파일을 생성함. (추천하지 않음 : 대신 --jsonfile 를 사용하십시오)

      --jsonfile string[=":hostname:_thor_:time:.json"]   JSON 출력에 대한 로그 파일임.

                                                          값을 지정하지 않으면 기본값은 :hostname:_thor_:time:.json 임.

  -o, --csvfile string                                    최소 점수가 있는 모든 파일에 대해 MD5, 파일 경로, 점수 를 포함하는 CSV 를 생성함. (기본값 ":hostname:_files_md5s.csv")

      --nocsv                                             언급된 모든 파일의 CSV 를 MD5 해시로 작성하지 마십시오. (--csvfile 참조)

      --csvstats                                          (추천하지 않음 : 대신 --stats-file 를 사용하십시오)

      --stats-file string[=":hostname:_stats.csv"]        Generate a CSV file containing the scan summary in a single line. If no value is specified, defaults to :hostname:_stats.csv.

  -e, --rebase-dir string                                 모든 출력 파일이 기록될 출력 디렉토리를 지정함. (기본값 : 현재 작업 디렉토리)

      --suppresspi                                        로컬 데이터 보호 정책을 준수하기 위해 로그 출력에서 모든 개인 정보를 표시하지 않음.

      --eventlog                                          Windows 응용 프로그램(application) 이벤트 로그에 기록함.

  -x, --min int                                           이 점수 이상의 파일만 보고하십시오. (기본값 40)

      --allreasons                                        결과가 위험한 것으로 간주되는 이유를 모두 표시하십시오. (기본값 : 상위 2개 이유만 표시됨)

      --printshim                                         출력에 모든 SHIM 캐시 항목을 'info' 레벨 메시지로 포함함.

      --printamcache                                      출력에 모든 AmCache 캐시 항목을 'info' 레벨 메시지로 포함함.

  -j, --overwrite-hostname string                         로컬 호스트명 값을 정적 값으로 재정의함.

                                                          (Lab 에서 장착된 이미지를 검사할 때 유용함. Forensic Lab 라이센스가 필요함. 기본값 "호스트명")

  -i, --scanid string                                     검사 식별자를 지정함. (검사 ID 를 필터링하는 데 유용하며 고유해야 함)

      --scanid-prefix string                              --scanid 또는 --noscanid가 지정되지 않은 경우 임의의 ID와 연결된 검사 ID의 접두사를 지정하십시오. (기본값 "S-")

      --noscanid                                          지정되지 않은 경우 검사 식별자를 자동으로 생성하지 마십시오.

      --silent                                            명령줄에 아무 것도 인쇄하지 마십시오.

      --cmdjson                                           명령줄 출력 형식을 JSON 으로 지정함.

      --cmdkeyval                                         명령줄 출력에 키-값 쌍을 사용함. (--keyval 참조)

      --encrypt                                           생성된 로그 파일과 MD5 csv 파일을 암호화함.

      --pubkey string                                     지정된 RSA 공개 키를 사용하여 로그 파일 및 csvfile을 암호화함. (--encrypt 참조)

                                                          --pubkey="<key>" 및 --pubkey="<file>" 모두 지원됨.

      --nocolor                                           색상이 지정된 명령줄 출력에 ANSI 이스케이프 시퀀스를 사용하지 마십시오.

      --genid                                             각 로그 메시지에 대한 고유 ID를 인쇄하십시오. 동일한 로그 메시지는 동일한 ID를 갖음.

      --print-rescontrol                                  체크 시 THOR 의 리소스 임계값 및 사용량을 인쇄함.

      --truncate int                                      최대 THOR 값당 길이임. (0 = 잘림 없음, 기본값 2048)

      --registry_depth_print int                          이보다 높은 깊이에서 레지스트리 키를 탐색할 때 정보(info) 메시지를 인쇄하지 마십시오. (기본값 1)

      --utc                                               현지 시간대 대신 UTC 로 타임스탬프를 인쇄함.

      --rfc3339                                           RFC3339 (YYYY-MM-DD'T'HH:mm:ss'Z') 형식으로 타임스탬프를 인쇄함.

      --reduced                                           감소된 출력 모드 - 경고, 경보 및 에러만 인쇄

      --printlicenses                                     모든 라이센스를 명령줄에 인쇄함. (기본값 : 10개의 라이센스만 인쇄됨)

      --local-syslog                                      THOR 이벤트를 로컬 syslog 에 인쇄함.

      --showall                                           해당 규칙이 이미 10번 이상 일치하더라도 인쇄 규칙이 일치함.

      --ascii                                             명령줄 및 로그 파일에 ASCII 가 아닌 문자를 인쇄하지 마십시오.

      --string-context uint                               YARA 일치에서 문자열을 인쇄할 때 일치를 둘러싼 지정한 많은 바이트를 포함하십시오. (기본값 50)

      --include-info-in-html                              

  

  

12. ThorDB

      --dbfile string   thor.db 파일의 위치임. (기본값 "%ProgramData%\\thor\\thor10.db")

      --resumeonly      새 검사을 시작하지 말고 중단된 검사만 완료하십시오.

                        중단된 검사이 없으면 아무 작업도 수행되지 않음.

      --resume          중단된 검사을 나중에 재개할 수 있도록 실행하는 동안 정보를 저장합니다.

이전 검사이 중단된 경우 새 검사을 시작하는 대신 다시 시작하십시오.

  

  

13. Syslog

  -s, --syslog strings        지정된 syslog 서버에 결과물을 씀.

                              형식 : server[:port[:syslogtype[:sockettype]]]

                              지원되는 syslog 유형 : DEFAULT/CEF/JSON/SYSLOGJSON/SYSLOGKV

                              지원되는 socket 유형 : UDP/TCP/TCPTLS

                              예제 : -s syslog1.dom.net, 

                                     -s arcsight.dom.net:514:CEF:UDP, 

                                     -s syslog2:4514:DEFAULT:TCP, 

                                     -s syslog3:514:JSON:TCPTLS

                                     (기본값 [])

      --rfc3164               긴 Syslog 메시지를 1024 바이트로 자름.

      --rfc5424               긴 Syslog 메시지를 2048 바이트로 자름.

      --rfc                   RFC 3164에 따라 엄격한 syslog를 사용하십시오.

                              (단순 호스트 이름, 단축 메시지)

      --maxsysloglength int   Syslog 메시지를 주어진 길이로 자름. (0 은 잘림 없음을 의미함, 기본값 2048)

      --cef_level int         CEF syslogs에 기록할 최소 심각도 수준을 정의함. (Debug=1, Info=3, Notice=4, Error=5, Warning=8, Alarm=10) (기본값 4)

  

  

14. 보고 및 조치

      --notice int              notice 생성되는 최소 점수임. (기본값 40)

      --warning int             warning 생성되는 최소 점수임. (기본값 60)

      --alert int               alert 생성되는 최소 점수임. (기본값 90)

      --action_command string   --action_level 점수보다 높은 점수를 가진 각 파일에 대해 지정된 명령어를 실행함.

      --action_args strings     --action_command를 통해 지정된 명령어에 전달할 인수임.

                                자리 표시자 %filename%, %filepath%, %file%, %ext%, %md5%, %score% 및 %date% 는 실행 시 대체됨. (기본값 [])

      --action_level int        지정된 점수 이상의 파일에 대해서만 --action_command 옵션의 명령어을 실행하십시오. (기본값 40)

      --nofserrors              파일 시스템 오류를 조용히 무시함.

  

  

15. THOR 원격

      --remote strings           대상 호스트 (호스트 집합에 대해 여러 --remote <host> 문 사용, 기본값 [])

      --remote-user string       사용자 이름 (지정하지 않으면 Windows 통합 인증이 사용됨)

      --remote-password string   원격 호스트에 대해 인증하는 데 사용할 암호임.

      --remote-prompt            원격 호스트에 대한 암호를 묻기

      --remote-debug             THOR Remote 의 디버그 모드

      --remote-dir string        지정된 원격 디렉토리에 THOR를 업로드하십시오. (기본값 "C:\\WINDOWS\\TEMP\\thor10-remote")

      --remote-workers int       동시 검사 수 (기본값 25)

      --remote-rate int          검사 시작 사이에 대기할 시간(초)임 (기본값 30)

  

  

16. 의심스러운 파일 자동 수집 (Bifrost)

      --bifrost2Server string   Bifrost 2 검역 서비스를 실행하는 서버임.

                                THOR는 모든 의심스러운 파일을 지정된 서버에 업로드함.

                                이 플래그는 ASGARD 2 에서 THOR 를 호출할 때만 사용할 수 있음.

      --bifrost2Score int       지정된 점수 이상의 모든 파일을 Bifrost 2 검역 서비스로 보냄.

                                이 플래그는 ASGARD 2 에서 THOR 를 호출할 때만 사용할 수 있음. (기본값 60)

  

  

17. 디버깅 및 정보

      --debug              디버깅 출력 표시

      --trace              추적 출력 표시

      --printall           확인된 모든 파일 인쇄 (noisy)

      --print-signatures   THOR 서명 및 IOC 표시 및 종료

      --version            서명 및 소프트웨어 버전 표시 및 종료

  -h, --help               가장 중요한 옵션에 대한 도움말 표시 및 종료

      --fullhelp           모든 옵션에 대한 도움말 표시 및 종료

  

  

18. 사용 예제

빠른 검사을 실행하고 출력 파일을 지정한 위치에 저장함.

thor64-lite.exe --quick -e path\to\outputfiledir

  

syslog 를 통해 파일 출력 및 로그 비활성화함.

thor64-lite.exe -s 10.1.5.14 --nohtml --nolog --nocsv

  

Windows 이벤트 로그의 지난 7일만 검사함.

thor64-lite.exe -a Eventlog --lookback 7

  

네트워크 공유에 로그인함.

thor64-lite.exe --nohtml --nocsv -l \\sys\rep\%COMPUTERNAME%_thor.txt

  

탑재된 이미지를 검사함.

thor64-lite.exe --lab -p G: --virtual-map G:C`
</details>
