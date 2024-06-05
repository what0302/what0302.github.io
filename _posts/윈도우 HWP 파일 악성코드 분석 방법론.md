# 윈도우 문서형 악성코드 분석 방법론
##### 작성자 : 김평일 대리, 정한울 대리, 김태현 사원, 강하늘 사원
##### 작성일자 : 2024년 6월 1일
</br></br>


##  HWP 파일

### 1. 한글 파일 악성코드 개요

HWP 한글 문서형 악성코드는 문서 파일 열람 시 악성코드에 감염되는 유형으로, 주로 한글 프로그램을 사용하는 공공기관이나 가상화폐 관련 기업 등의 대상을 공격하는 타깃형 공격이 2010년 이후부터 꾸준히 발생함.

악성 HWP 문서의 상당수가 EPS를 이용하여 악성 행위를 수행함. 

`EPS란?
Encapulated PostScript의 약자로, Adobe에서 만든 PostScript 언어를 이용하여 그래픽 이미지를 표현하는 파일임. 이를 이용하여 각종 고화질 벡터 이미지를 표현할 수 있어, HWP에서는 EPS 이미지를 포함하거나 볼 수 있는 기능이 존재함.`

EPS에서 사용한 CVE-2017-8291 취약점은 고스트스크립트(Ghostscript) 인터프리터가 '.eqproc' 함수에서 매개변수 타입 유효성을 검증하지 않아 피연산자 스택의 메모리가 변조됨. 즉, 악의적인 PostScript 파일로 스택을 변조함으로써 임의 코드를 실행할 수 있는 것임.

2017년 02월 23일에 한글과컴퓨터에서 EPS 파일 처리 과정의 취약점을 조치하여 최신 업데이트가 적용된 HWP는 EPS를 이용한 악성코드가 동작하지 않음. 하지만 여전히 예전 버전을 사용하는 사용자, 관공서가 많이 때문에 해당 악성코드는 꾸준히 배포되고 있음.

### 2. 한글 파일 구조

한글 2002부터 한글 2018까지 출시된 한글 프로그램은 기본적으로 5.0버전의 한글 문서 파일 형식으로 한글 파일(.hwp)를 생성함.

한글 문서 파일 형식 5.0은 OLE(Object Linking and Embedding) 파일을 기반으로 하여 여러 개의 Storage와 Stream으로 구성되어 있음.

`OLE(Object Linking and Embedding) : Microsoft가 개발한 기술로, 문서와 기타 객체에 연결과 삽입을 도와주는 연결 규약임. 여기서 정보 객체를 OLE Object라고 하며 OLE Object에는 문서, 동영상, 소리, 그림, 수식, 표 등을 하나의 Object로 포함함. 쉽게 설명하면 사진 문서를 올릴 때 문서에 포함된 사진 데이터는 하나의 Object가 됨.
`

또한, 파일 크기를 최소화하기 위해 압축 기능을 사용하는데, 그림 관련 데이터를 포함한 일부 스트림은 파일의 크기를 줄이기 위해 zlib로 압축해서 저장하는 방식을 사용함.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/8dd58bcd-01f5-4623-8b1a-a0d26ba535c2)

하나의 스트림에는 일반적인 바이너리나 레코드 구조로 데이터가 저장되고, 스트림에 따라 압축 및 암호화되기도 함. 위 표에서 바이너리 데이터를 의미하는 BinData라는 스토리지가 존재하는데, 여기에 그림 또는 OLE Object가 zlib으로 압축되어 저장됨.

이처럼 한글 문서에 그림 파일을 삽입할 수 있으며 삽입 가능한 파일 포맷중에 EPS 파일이 포함되어 있음. 그리고 **한글 파일에 포함된 EPS 파일은 BinData 스토리지에 각각의 스트림으로 zlib으로 압축되어 저장됨.**

### 3. EPS 파일 로드 과정

EPS(Encapsulated PostScript) 파일은 포스트스크립트 프로그래밍 언어로 작성된 규격화된 파일로, 단일 그래픽 이미지를 표현함. 이러한 EPS 파일을 화면에 표현하기 위해 인터프리터가 필요하며 한글 프로그램에는 인터프리터인 고스트스크립트(GhostScript)를 내장하고 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/096a6703-890b-45f1-a220-02f817b587f5)

기본적으로 위와 같이 4개의 파일로 구성되어 있으며, 인터프리팅 기능을 하는 핵심 파일은 gsdll32.dll 라이브러리임. 이외에 실행 파일들은 라이브러리 함수를 호출하는 역할을 하며 한컴에서 제작한 gbb.exe 파일을 제외하면 모두 공개된 고스트스크립트 소스로 컴파일된 파일임.
- gbb.exe : 한컴에서 제작한 포스트스크립트 인터프리터로 gsdll32.dll 로드해서 동작함
- gsdll32.dll : 고스트스크립트 인터프리터 핵심 라이브러리
- gswin32.exe : 고스트스크립트 인터프리터 GUI 버전으로 gsdll32.dll 로드해서 동작
- gswind32c.exe : 고스트스크립트 인터프리터 커맨드 버전으로 gsdll32.dll 로드해서 동작

#### 3-1) 프로세스

한글 프로그램은 문서를 읽는 과정에서 EPS 이미지가 포함된 페이지가 로드될 때 이를 화면에 표현하기 위해 고스트스크립트 인터프리터인 gbb.exe 파일고 gswind32c.exe 파일이 순차적으로 실행됨. **즉, Hwp.exe 프로세스는 Child Process로 gbb.exe와 gswin32c.exe 프로세스를 실행할 때 표현 대상인 EPS 파일을 실행 인자로 전달하여 그래픽 이미지를 화면에 표시하는 것임.**

위에서 설명했듯이 EPS파일(스트림)은 BinData Storage에 .zlib으로 압축되어 저장되어 있기 때문에, **Hwp.exe 프로세스는 먼저 .zlib 압축을 풀어 임시 파일을 생성하고, 생성된 임시 파일을 고스트스크립트 인터프리터가 처리할 수 있도록 생성된 임시 파일경로를 인자로 전달함.**

추가로, EPS 파일이 문서의 첫 번째가 아닌 다른 페이지에 삽입된 경우 해당 페이지가 화면에 로드될 때 고스트스크립트가 실행되어 동작하지만, 실제 악성 한글 파일의 대부분은 문서를 열자마자 악의적인 기능이 동작하도록 첫 번째 페이지에 삽입되어 있음.

#### 3-2) 요약

Hwp.exe 프로세스가 EPS 파일을 처리할 때 .zlib으로 압축되어 있는 EPS파일(스트림)을 압축해제하고 임시 파일을 만들어 해당 파일 경로를 인자로 고스트스크립트 인터프리터인 gbb.exe, gswin32c.exe 프로세스를 호출하면서 전달하며, 두 프로세스는 취약점이 존재하는 gsdll32.dll 라이브러리를 로드하여 사용함. 이때, Type Confusion 취약점이 발생하는 .eqproc 함수를 사용하게 됨.
<br>
<br>

##  한글 파일 악성코드 상세 분석

sample2_xup0zGn.hwp에 대한 상세 분석 프로세스임<br><br>
`파일 정보`<br><br>

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/8f899c4d-e7f5-4b78-92b1-cd922b59d5ab)

해당 한글 악성코드는 도널드 트럼프 미국 대통령과 김정은 북한 국무위원장이 2019년 2월 27-28일 베트남 하노이에서 가졌던 2차 북미 정상회담 결과에 대한 특별좌담회 문서파일을 미끼로 사용하였음.<br>
<br>

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/a60b9831-b0aa-4504-9d54-a382e16e0ee0)

해당 악성코드 또한 EPS를 이용한 악성행위를 수행함.

### 1. 행위 분석

한글 문서를 실행시키면 쉘코드가 바로 실행됨. Procmon 프로그램의 Process Tree 기능을 이용하여 현재 한글문서 하위에 실행되는 프로세스들을 확인할 수 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/2376412a-af83-41f0-8912-0589f5567fad)

EPS 파일을 포함한 한글 문서가 이미지를 로드할 때, OLE 구조상 EPS 파일은 임시파일 형태로 BinData 폴더에 생성됨. 한글 프로세스는 생성된 임시 파일을 인터프리터가 전달받아 처리하도록 gbb.exe 프로세스와 gswin32c.exe 프로세스에 임시 파일 경로를 인자로 전달하여 실행됨.

따라서 위 사진과 같이 한글 프로세스 하위에 2개의 gbb.exe, gswin32c.exe 프로세스가 실행되고 있는 것을 확인할 수 있음. 하지만 각 프로세스의 하위에서 iexplore.exe가 injection 되어 있음. 이는 사용자의 눈에 보이지 않게 동작하며, 실제 악성행위는 해당 iexplorer.exe 내부에서 일어날 것으로 유추됨.

### 2. 악성코드 추출(EPS - PostScript)

한글 문서 내부에 들어 있는 EPS 파일을 추출하기 위해 '누리랩'에서 개발한 HWp2Scan 프로그램을 이용함. 이를 통해 한글 문서의 취약점을 확인할 수 있으며 EPS 파일을 추출할 수 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/f07df3f9-7abd-403c-bde3-f3773162f5d5)

취약점 검사 기능을 이용하면 현재 검사하고 있는 한글 문서에 존재하는 취약점을 확인할 수 있음. 현재 검사하고 있는 문서에선 취약점이 발견되고 있지 않은데, 이는 악성 PostScript 파일은 콛가 암호화되어 검사 로직에서 확인되지 않기 때문임.

우선 BinData 안에 있는 BIN003.eps 파일을 추출함. 참고로 BinData 폴더는 압축된 상태이므로 추출 옵션 중 'Save a Hex(Decompress)'을 이용해야함.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/82aebe58-a90e-437a-8a3f-f12c45197911)

인코딩된 PostScript 파일을 Sublime Text로 확인한 결과임. 첫 번째 라인의 꺽쇄 다음으로 시작하는 이어지는 문자열이 쉘코드임. 해당 PostScript를 실행시키면 XOR연산을 통해 인코딩된 쉘코드가 복호화되고 실행됨.

복호화된 쉘코드를 얻기 위해 12라인의 exec를 print로 변경하여 헥사값을 얻어낼 수 있음. 이렇게 하면 따로 PostScript의 문법을 몰라도 원하는 복호화 결과를 얻을 수 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/4ea32377-abcd-4ea0-b7bc-caf641f108da)

코드를 수정하고 mal.eps로 새로 저장함.

### 3. PostScript 실행

PostScript는 GhostScript를 이용하여 실행시킬 수 있음.

다운로드 링크 : https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/tag/gs926

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/9416403c-9a06-405b-9cc9-8dae73a4a867)

PosrtScript의 마지막 exec 부분을 print로 변경하여 복호화된 코드가 출력됨. 출력 결과를 확인해보면 다음과 같음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/2a70aa69-0ba0-4b41-b65e-9b0c3508f634)

복호화된 코드는 9090..으로 시작하며, 이는 쉘코드의 nop 영역임을 유추할 수 있음. 따라서 해당 쉘코드로 추정되는 놈을 실행시켜봐야함.

### 4. Shellcode 분석

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/1c13ffd5-0918-4462-a598-534ec64340ab)

Shellcode2EXE를 이용하여 쉘코드를 exe로 변환시키면 다음과 같음

추출한 실제 쉘코드는 암호화되어 있으며, XOR로 복호화가 진행되고 jmp로 이동하여 실제 동작이 진행됨. C&C 서버는 현재 닫혀 있으므로 Any Run Sandbox를 이용해 추가 정보를 확인해야함.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/cfd0da78-037d-4788-939e-e038ef4f6b10)

쉘코드 내부에서 " http[:]//itoassn[.]mireene[.]co[.]kr" 주소로 Request를 보내는 것을 확인할 수 있음. 자세한 주소는 디버거를 통해 확인할 수 있으며 다음과 같음 " http[://]itoassn[.]mireene[.]co[.]kr/shop/shop/mail/com/mun/down[.]php ".

해당 서버에서 추가적인 악성코드를 요청하게 되고, 이는 VBE라는 파일을 다운로드 받게 함. 해당 파일은 여러번 인코딩된 URL을 포함하고 이를 디코딩하여 난독화된 VBS 코드를 얻을 수 있고, 이를 해제하여 코드 원본을 확인할 수 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/783eac54-a3ed-4784-a19a-4f788a09428a)

난독화된 VBS 코드와

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/96d32f27-5ad0-4fdd-90d0-165031261307)

난독화가 해제된 VBS 코드

### 5. 정리

sample2_xup0zGn.hwp는 CVE-2017-8291 취약점을 이용하여 공격하는 다운로더형 악성코드로, 파일 실행 시 내부에 있는 EPS파일에서 쉘코드가 실행.

쉘코드가 실행되면 " http[://]itoassn[.]mireene[.]co[.]kr/shop/shop/mail/com/mun/down[.]php"에서 추가로 악성코드를 다운받도록 구성되어 있음.
