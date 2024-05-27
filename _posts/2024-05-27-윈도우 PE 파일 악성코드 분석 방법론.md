# 윈도우 PE 파일 악성코드 분석 방법론
##### 작성자 : 김평일 대리, 김태현 사원
##### 작성일자 : 2024년 5월 23일
</br></br>

## (1) PE 파일 개요
### 1-1 PE 파일이란?

PE(Portable Executable)파일은 윈도우 실행파일이라고 부르며 윈도우 OS에서 사용되는 실행파일 형식을 의미함. 즉, 윈도우 운영체제에서 우리가 만들고 사용하는 파일이 다른 윈도우 운영체제의 PC로 옮겨져도 실행이 가능하도록 만들어 놓은 포맷 혹은 파일을 PE 포맷, PE 파일이라고 부르는 것임.

대표적으로 exe파일이 있음. 우리가 웹사이트에서 exe 파일을 다운받으면 윈도우를 사용하는 모든 컴퓨터에서 이 파일을 실행시킬 수 있음.

### 1-2 PE 파일 종류

PE파일의 종류는 총 4개의 계열이 있으며 다음과 같음
- 실행 계열 : EXE, SCR
- 드라이버계열 : SYS, VXD
- 라이브러리 계열 : DLL, OCX, CPL, DRV
- 오브젝트 계열 : OBJ

### 1-3 PE 파일 생성 과정

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/7dbc05af-5659-4678-939d-ee58e351cf14)

PE파일의 생성 과정은 다음과 같음.

1. 소스코드 작성
2. 바이너리로 변경(컴파일)
3. 필요한 라이브러리 연결(링킹)
4. exe 파일로 빌드(빌드)

이때 가장 중요한 부분은 PE 헤더임. PE 파일을 빌드 할 때, **파일 실행 시 필요한 정보들을 약속된 규약에 맞춰 PE 파일의 헤더에 기입함.** 운영체제는 PE 파일의 헤더 정보를 보고 해당 프로그램을 실행시킴.

**한마디로, PE 포맷은 윈도우 로더가 실행 가능한 코드를 관리하는데 필요한 정보를 캡슐화한 데이터 구조체임.**

### 1-4 PE 파일 구조

PE 파일은 다음과 같으 구성되어 있음.
- Header + Section<br><br>
Header란 실행 파일의 성격과 특징을 나타내며(프로그램 구동 정보 등등),
Section은 구체적이고 세부적인 기능을 나타냄(코드, 전역변수 등등).

위 구조를 자세히 표현하면 아래와 같음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/3443a383-3dd2-4617-8e29-fcf74c6960bf)


## (2) PE 파일 정적분석
### 2-1 정적분석

정적분석(Static Analysis)이란, 악성코드를 직접 실행하지 않고 그 자체가 가지고 있는 속성들을 통해 악의적인 여부를 진단하는 방법으로, 실행했을 때 실행 파일의 행위는 확인이 불가능하나 속성은 파악이 가능함.

파일, 파이너리 코드, 문자열, 파일의 헤더, 리소스 등을 조사하여 악성 코드를 식별함.

## (3) PE 파일 정적분석 도구

### 3-1 DIE

DIE는 Detect It Easy의 줄임말로, 어셈블리 패턴과 PE 헤더의 IAT를 분석하여 사용된 컴파일러를 추정하는 프로그램임. 난독화 솔루션을 사용했을 때에도 어떤 난독화 프로그램을 사용했는지 표시됨.

*IAT란, Import Address Table로 PE 파일이 사용하는 외부 API 함수의 주소들을 배열 형태로 저장해놓은 영역을 의미함.

*PE파일 종류
실행 계열 - EXE, SCR
라이브러리 계열 - DLL, OCX, CPL, DRV
드라이브 계열 - SYS, VXD
오브젝트 계열 - OBJ

다운로드 링크 : https://github.com/horsicq/DIE-engine/releases

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/b42a4adc-2d9c-4e00-860c-241919631676)

다음과 같이 분석이 가능함. 컴파일러와 프레임워크 추정 결과 C++ MFC를 사용한 프로그램임을 알 수 있음.

DIE로는 어떤 언어로 작성되었는지를 주로 확인하고, 나머지는 아래에서 설명할 Pestudio를 사용하여 분석함.

### 3-2 Pestudio

Pestudio는 사용자가 실행파일, 특히 Windows 운영 체제에서 실행되는 파일에 대한 자세한 분석을 제공하는 도구임. 파일의 속성, 파일의 특성, 잠재적 위험에 대한 정보, 멀웨어 감염 및 기타 악성 활동을 포함한 보안 위험을 탐지하도록 설계됨. 다음과 같은 분석 기능을 제공함.

- 파일 서명 인식
- 하드 코딩된 URL 및 IP 주소 인식
- 메타데이터 수집
- 문자열 수집
- Virustotal 결과 검색

다운로드 링크 : https://www.winitor.com/

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/373a3a63-7aad-45f4-92c7-2885b3ec4237)

Pestudio에 악성코드를 올린 첫 화면이며, 파일 고유의 해시값과 파일 크기, 파일 종류 등을 표시해줌.
first-bytes-hex의 4D 5A는 MZ 파일의 16진수 시그니처 문자열을 뜻하며, 이는 .exe 파일에 사용되는 형식임.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/b9b038c7-63ec-4b73-b0fa-f36adb15a525)

또한 파일의 엔트로피도 나오는데, 엔트로피 값을 통해 악성 코드의 난독화 여부를 파악할 수 있음. 엔트로피는 0-8 범위로 측정되며, 값이 7에서 8에 가까울수록 난독화가 되어 있다고 보면 됨. 난독화가 되어 있지 않으면 3-5점대임.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/a944f37c-b5ee-4f0f-8f41-8b88f83e0839)

메뉴의 indicators 항목에선 파일 내부의 정보를 위험도 순으로 정렬해줌. 여기선 IP주소와 도메인 패턴의 위험도를 가장 높게 평가하였음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/3302b96b-c13f-4c89-8ee0-787a09092d66)

import 메뉴에선 네트워크 소켓 관련 함수를 확인할 수 있음. 이를 통해 악성코드가 특정 IP와 C&C서버와의 통신을 할 것이라는 분석이 가능함

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/97f0a672-72a2-4bf3-b636-932a0f9730a0)

virustotal 메뉴에선 파일의 해시값을 virustotal에 조회하여 악성 여부를 판단할 수 있음. Virustotal에 등록된 안티 바이러스 제품들에 의해 검사된 결과의 요약본을 확인할 수 있음. 제품에 의해 탐지가 되었을 경우 'positiv'열에 표시됨.

다만 이때 주의해야 할 점은, MD5 및 SHA 해시값은 파일을 조금만 수정하더라도 얼마든지 변경되기 때문에, 악성코드 유사성 해시인 imphash와 ssdeep 또한 고려해야함. imphash는 IAT기반으로 생성되는 해시값이며, ssdeep는 바이너리 블록을 기반으로 생성된 해시값임.

더 자세하게 설명하면, ssdeep은 Fuzzy hash를 사용하여 파일의 유사도를 측정할 수 있도록 개발된 프로그램임. 파일 내부의 데이터를 일정 변경하여 원본과 비교하면 유사도가 % 형태로 출력이 가능함. 이 방식을 이용하여 미리 추출한 파일의 해시값을 한 파일의 딕셔너리로 사용을 하고, 그 딕셔너리를 통해 유사한 파일을 찾는 방식으로 악성 코드를 검출할 수 있음. 

Imphash는  import hash의 줄임말로, PE파일에서 import 된 라이브러리와 API의 목록을 해시화 한 값임. PE파일, 즉 윈도우 실행 파일은 소프트웨어의 동작을 위해 함수, API 등이 들어 있는 DLL을 import 시켜 사용하는데, 그때 사용하는 API 등의 실행 순서를 통해 어떤 방식으로 프로그램이 구동되는지 파악할 수 있음. PE파일 내에는 특정 순서를 가지는 라이브러리와 API의 이름을 기술 해 둔 테이블이 있는데, 이를 IAT(Import Address Table)이 있는데, 이를 기반으로 생성한 해시값이 imphash임. 

기존의 MD5 및 SHA 해시 기반 탐지는, 해시값이 정확히 일치하는 파일에 대해서만 탐지가 가능함. 그래서 파일 내부에 하드코딩된 악성 IP 및 C&C 서버가 바뀌는 경우 해시값이 변경되기에 탐지하지 못함. 그러나 ssdeep과 imphash값은 이러한 정보들이 변경 및 변조되어도 파일의 전체 유사성과 동작하는 방식으로 탐지하기에 악성코드 여부를 효과적으로 파악할 수 있음.

### 3-3 Hashtab

Hashtab은 파일의 해시값 확인을 위해 설치하는 서브 프로그램이다. 이를 설치하면 윈도우의 속성 탭에 "파일 해시" 항목이 추가되어 해시값을 쉽게 확인할 수 있다.

다운로드 링크 : https://www.majorgeeks.com/files/details/hashtab.html

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/dae20a70-b669-4f16-9ea4-5f718f015159)

## (4) PE 파일 동적분석
### 4-1 동적분석
동적분석(Dynamic Analysis)이란, 악성코드를 직접 시스템에 실행시킨 후 변화를 모니터링하여 행동 패턴을 분석하는 방법을 의미함. 실제 악성코드가 실행되기 때문에 가상환경에서 테스트하여 분석할 필요가 있음.

프로세스 -> 파일 -> 레지스트리 -> 네트워크 순으로 확인하며, 시스템의 변화가 악성코드의 원인인지 정확히 파악하기 위해 반복확인 과정이 필요함.

## (5) PE 파일 동적분석 도구

### 5-1 Sysmon

Sysmon은 System Monitoring의 줄임말로, 윈도우의 로그를 분석하는데 가장 일반적으로 사용되는 추가 도구 중 하나임. Sysmon을 사용하면 코드 동작과 네트워크 트래픽을 추적하여 악성 활동을 탐지할 수 있음

Sysmon은 현재 마이크로소프트가 소유하고 있는 패키지의 일부이며 별도의 다운로드와 다음과 같은 설치 과정을 거쳐주어야 함

다운로드 링크 : https://learn.microsoft.com/ko-kr/sysinternals/downloads/sysmon

`Sysmon.exe -i -n -h sha256`
- -i : Sysmon을 설치하라는 명령어
- -n : 네트워크 연결 모니터링을 활성화하는 옵션
- -h sha256 : 파일 생성 및 이미지 로딩 이벤트를 로깅할 때 sha256 알고리즘을 사용할 것을 지정

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/704f5832-6973-424a-8556-67b809818766)

Sysmon 활용 방법임. (1)"이벤트 뷰어"를 오픈한 후 "응용 프로그램 및 서비스 로그 - Microsoft - Sysmon" 항목을 찾아서 "Operational" 항목을 클릭함.

Operational 항목을 선택하면 우측에 (2)날짜와 시간 순으로 Sysmon이 기록한 로그 정보가 표시되며, 특정 로그를 선택할 경우 하단의 (3)일반 항목에 세부 정보가 출력됨.

참고로, 이벤트 ID 별 상황은 다음과 같음.

(중요)<br>
ID 1 : Process Create - 프로세스 생성 시 발생<br>
ID 3 : Network Connection - 네트워크 연결 시 발생<br>
ID 5 : Process Terminate - 프로세스 종료 시 발생


### 5-2 Regshot

Regshot은 레지스트리의 스냅샷을 신속하게 촬영한 다음, 시스템 변경을 수행하거나 새 소프트웨어 제품을 설치한 후 수행되는 두 번째 스냅샷과 비교할 수 있는 오픈소스 레지스트리 비교 유틸리티임.

악성코드의 동적분석 시 활용되며, 악성 행위가 실행되기 전에 스냅샷을 찍고, 악성 행위가 실행된 후의 스냅샷을 찍어 이를 비교해 레지스트리의 수정 정보를 확인함.

다운로드 링크 : https://sourceforge.net/projects/regshot/

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/56c93c58-035f-4bd9-bc48-020df1cd3aea)

Regshot을 실행하고, 1st shot과 2nd shot을 각각 클릭해서 레지스트리 파일을 두개 생성함. 이후 Compare을 클릭하여 변경된 부분을 확인

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/f121bb72-a86e-4c89-948a-665912e98d8e)


### 5-3 Procmon

Procmon은 Process Monitor의 줄임말로, 프로세스의 분석과 디버깅을 하기 위해 레지스트리, 파일, 프로세스, 네트워크 동작 등을 **실시간으로 캡처하는 프로그램임**

다운로드 링크 : https://learn.microsoft.com/ko-kr/sysinternals/downloads/procmon

프로세스들 중, 검색하고자 하는 특정 프로세스만 필터링 할 수 있음

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/4207b45c-293d-4ca2-bbe6-66318905fd02)

디폴드 필터를 모두 삭제 후

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/b41c9e59-8794-4fea-8270-58a9b538b2a2)

모니터링 대상 프로세스의 이름을 입력함.

Process Name 선택, is 선택, (대상 프로세스) 입력, Include 선택, Add 클릭

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/1b93558c-336b-4e76-8659-34776f389e80)

이후 수집한 로그를 외부로 내보내기하여 세부적인 분석을 수행할 수 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/89b30301-3bf2-4224-8281-ec5f76558b14)

또한, AutoScroll 버튼을 활성화하여 새로운 이벤트를 실시간으로 확인할 수 있으며, tool - process tree - include subtree를 활성화하여 트리 구조를 확인할 수 있음.

필터 규칙 : Column 이름(PID, Operation 등) 동일한 경우 여러 규칙들이 OR Column 이름(PID, Operation 등) 다른 경우 여러 규칙들이 AND -> Operation 기준으로 필터링 ==> WriteFile, RegSetValue, SetBasicInfomationFil

### 5-4 Autoruns

Autoruns는 msconfig.exe의 확장된 도구로, 윈도우 시스템이 부팅 후 자동으로 시작되는 서비스 또는 프로그램 등을 모니터링 할 수 있는 도구임.
특정 악성코드의 경우 cmd.exe를 자동으로 실행시켜 프로세스를 유지하기에 이를 탐지하고 조치할 수 있음.

악성코드가 지속성을 위해 자동으로 실행할 때, 악성코드는 description이 이상하거나 publisher이 없음. 프로세스가 자동으로 실행되지 않아야 하는 상황에서 인증되지 않은 프로세스가 식별된다면 악성일 가능성이 높음.

악성코드가 실행되지 않은 환경에서 save 후, 악성코드를 실행 했을 때와 비교분석을 진행함.

다운로드 링크 : https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/a3dedf6a-ec43-49c0-a6b6-6c6d9e2022bc)

다음과 같이 활성화된 프로세스 목록을 확인할 수 있음

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/eb5bd167-af3a-4aba-95a5-b2596656faf4)

상단 option의 Hide Microsoft Entries 옵션을 통해 마이크로소프트의 기본 프로세스를 숨길 수 있음. 이는 악성코드를 분석하는데 있어 복잡함을 덜기 위함임. 검색되는 항목 중 게시자가 Microsoft Corporation이면 숨김 처리가 됨.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/3805f490-c627-4a41-8109-d7db8014b5bf)

그러나 프로그램 게시자는 얼마든지 임의로 수정이 가능함. 그러므로 options - scan options - verify code signatures를 활성화하여 디지털 서명을 검증하는 작업을 진행할 수 있음.




### 5-5 Procexp

Procexp는 Process Exploer의 줄임말로, 윈도우 시스템 모니터링 유틸리티임. 실행중인 프로세스 목록 및 트리를 확인할 수 있음. 이를 통해 프로세스가 점유하고 있는 자원들을 한 눈에 볼 수 있으며, 프로세스가 동작하는 경로, 라이브러리, 레지스트리를 확인할 수 있음.

악성코드 분석 시 프로세스 확인을 위해 작업관리자보다 Procexp를 더 쓰는 편임. 가장 주요하게 모니터링하는 부분은 프로세스의 부모 자식 관계임.

다운로드 링크 : https://learn.microsoft.com/ko-kr/sysinternals/downloads/process-explorer

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/7b5252a8-4f56-4252-9156-bb73f6547760)

프로그램을 실행했을 때 기본적으로 확인할 수 있는 화면으로 현재 실행 중인 프로세스를 모니터링할 수 있음. GUI 화면으로 프로세스 트리를 확인할 수 있어 구조를 쉽게 파악할 수 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/950db592-f38b-4e30-b60e-0fdcc55c50c4)

해당 프로세스를 클릭하여 프로세스 핸들, DLL(라이브러리), 쓰레드 정보도 확인할 수 있음. 비정상 프로세스를 분석하는데 있어 중요한 정보들임.

추가로, view - scroll to new process를 활성화라여 새로운 프로세스 실행 시 자동으로 해당 프로세스를 따라가도록 설정할 수 있음.






















