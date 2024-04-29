---
layout: post
title: "[개발일지] Virustotal 검색 자동화 툴"
tags: [개발일지, Virustotal, Python]
comments: true
---

바이러스토탈 검색 자동화 툴 개발과정

---
## (1) 개요
입사 후 여러 보안동향 보고서를 작성하게 되면, 여러 IoC들을 마주하게 된다. IoC란, Indicator of Compromise 의 약자로, 특정 침해사고를 분석하는데 사용되는 지표를 뜻한다.

여기엔 공격자의 IP 및 도메인, C&C 서버, 악성 MD 해시 등의 정보가 포함된다.

이 IoC 정보들을 보고서에 첨부하기 이전에 우리는 Virustotal을 이용해서 악성 정보의 reference를 제공해주어야 한다.

### 1. Virustotal이란,
Virustotal은 Ip, 도메인, 파일 해시값에 대해 검사를 제공하는 웹사이트이다. 최대 70가지 이상의 바이러스 검사 소프트웨어를 이용하여 검사를 진행한다. 조사한 IoC 데이터를 재확인하는데 이만한 도구가 없기에, 사이트에 접속하여 IoC의 악성 여부를 쉽게 파악할 수 있다.

주소 : virustotal.com

![스크린샷 2024-04-30 오전 3 02 23](https://github.com/what0302/what0302.github.io/assets/18510716/a6405e14-0ddd-4354-8be6-1ac5925d79ff)

## (2) 문제점 및 개발의 필요성
이러한 좋은 도구가 있음에도 불구하고 크나큰 문제가 있으니, 우리가 검색해야 할 IoC의 데이터가 너무나도 많다는 것이다. 

![image](https://github.com/what0302/what0302.github.io/assets/18510716/0762cb35-555c-43fb-87bf-5f0070d54401)

이는 보고서 하나에 들어가는 IoC 데이터 중 도메인에만 해당하는 것들을 가져온 것으로, 나머지 IP 및 해시값들을 검색해야 한다면 수동으로 몇번에 걸친 노동을 수행해야한다.

다행히 virustotal 정도 규모가 되는 도구들은 api를 지원해주기에, 이를 활용하여 내 손과 마음의 스트레스를 덜어주는 툴을 개발해보기로 했다.

## (3) 구상
우선 우리가 검색하는 데이터를 크게 세 가지로 분류해보았다. IP, 도메인, 파일 해시값. 각각에 해당하는 IoC 데이터를 텍스트 파일에 집어넣고, api를 이용해 자동으로 순차적으로 검색하도록 구상을 해보았다.

그리고 결과값을 csv 형태로 출력하도록 설정했고, 프로그래밍 실력 향상을 위해 tkinter을 이용해서 GUI도 만들어보았다.

프로그램을 만들던 도중, 하나의 api에서 소화 가능한 데이터의 양에 제한이 있음을 깨닫고, 두 개의 api key를 이용해 처리 데이터를 분산시켰다.

## (4) 제작
IP 검색, 도메인 검색, 파일 해시값 검색에 해당하는 코드이다.

### 1. IP 검색 코드
```python
import csv
import requests
import urllib3
import time
import socket
from tqdm import tqdm

API_KEY = ''  # API 키
IP_FILE = 'ip_list.txt'  # IP 주소 목록 파일
OUTPUT_FILE = 'output_ip.csv'  # 결과 출력 파일

    # 각 IP 주소에 대한 API 요청 수행
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['IP', 'Detected', 'Engines', 'URL'])

        seen_ips = set()  # 이미 검색된 IP 주소 추적

        # 진행 상태 표시를 위한 tqdm 사용
        with tqdm(total=len(ips)) as pbar:
            for i, ip in enumerate(ips):
                if ip in seen_ips:  # 이미 검색된 IP는 건너뛰기
                    continue
                
                # IP를 URL 형식으로 변환
                url = f'http://{ip}/'
                
                # VirusTotal API 요청 파라미터
                params = {'apikey': API_KEY, 'resource': url}
                response = requests.get('https://www.virustotal.com/vtapi/v2/url/report', params=params, verify=False)

                if response.status_code == 200:
                    data = response.json()
                    detected = data.get('positives', False)
                    engines = sorted([engine for engine in data.get('scans', {}).keys() if data['scans'][engine]['detected']])
                    url = f'https://www.virustotal.com/gui/ip-address/{ip}'  # 검색된 IP 주소의 VirusTotal 페이지 URL

                    writer.writerow([ip, detected, '|'.join(engines), url])
                else:
                    print(f"오류: {response.status_code} {response.reason}")
                
                seen_ips.add(ip)  # 현재 IP를 검색된 IP 목록에 추가
                
                # 다음 요청 전에 15초 대기, 1분에 4개 요청 제한 준수
                time.sleep(15)
                
                # 진행 상태 업데이트
                pbar.update(1)

```

내가 검색하고픈 IP 리스트를 ip_list.txt 파일에 넣은 후 코드를 실행하면, csv 파일에 [검색한 IP], [탐지 수], [탐지 엔진명], [virustotal 주소] 순으로 출력한다. 
이때, 192[.]168[.]255[.]255 처럼 난독화¹된 값도 그대로 넣어도 상관없다.

또한 프로그래밍 중 알게된건데, virustotal의 api 요청은 시간 당 제한 횟수가 정해져 있다. 그러므로 time.sleep 설정 없이 호출하게 되면 검색이 안되고 지나치는 경우가 생기기에 15초 대기를 설정해놨다.

[1] 이는 IP 주소 난독화 (IP Address Obfuscation)라고 하며, 아주 기본적인 난독화 방법 중 하나이다.

### 2. 도메인 검색 코드 
``` python
import csv
import requests
import urllib3
import time
import hashlib
from tqdm import tqdm


API_KEY = '' # API 키
URL_FILE = 'url_list.txt' # URL 목록이 저장된 파일
OUTPUT_FILE = 'output_url.csv' # 결과를 저장할 CSV 파일 이름

# SHA256 해시를 계산하는 함수
def get_sha256_hash(text):
    normalized_url = text.lower().replace('[', '').replace(']', '') # URL을 정규화한 후 해싱
    return hashlib.sha256(normalized_url.encode()).hexdigest()

# 파일에서 URL 읽기
with open(URL_FILE, 'r') as f:
    urls = [line.strip() for line in f]

# 각 URL에 대해 API 요청 수행
with open(OUTPUT_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['URL', 'Detected', 'Engines', 'Search_URL'])

    seen_urls = set() # 이미 본 URL을 추적하기 위한 집합
    with tqdm(total=len(urls)) as pbar: # 진행 상태 표시줄
        for i, url in enumerate(urls):
            if url in seen_urls: # 이미 본 URL은 건너뛰기
                continue
            
            params = {'apikey': API_KEY, 'resource': url}
            response = requests.get('https://www.virustotal.com/vtapi/v2/url/report', params=params, verify=False)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict): 
                    detected = data.get('positives', False)
                    engines = sorted([engine for engine in data.get('scans', {}).keys() if data['scans'][engine]['detected']])
                    search_url = f"https://www.virustotal.com/gui/url/{get_sha256_hash(url)}/detection"

                    writer.writerow([url, detected, '|'.join(engines), search_url])
                else:
                    print(f"오류: 예상치 못한 응답 형식 {data}")
            else:
                print(f"오류: {response.status_code} {response.reason}")
            
            seen_urls.add(url) # 현재 URL을 seen_urls에 추가
            
            time.sleep(15) # 다음 요청 전 15초 대기, 분당 4회 요청 제한
            
            # 진행 상태 표시줄 업데이트
            pbar.update(1)

```

### 3. 파일 해시값 검색 코드

```python
import csv
import requests
import urllib3
import time
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # SSL 인증서 경고 비활성화

API_KEY = '' # API 키
HASH_FILE = 'hash_list.txt' # 해시 값을 담은 파일 이름
OUTPUT_FILE = 'output_hash.csv' # 결과를 저장할 CSV 파일 이름

# 파일에서 해시 값을 읽기
with open(HASH_FILE, 'r') as f:
    hashes = [line.strip() for line in f] # 각 줄에서 해시 값을 읽어 리스트에 저장

# 각 해시 값에 대한 API 요청 수행
with open(OUTPUT_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['SHA256', 'MD5', 'SHA1', 'Type', 'Detected', 'Engines', 'URL']) 

    seen_hashes = set() # 이미 처리한 해시 값을 추적하기 위한 집합
    with tqdm(total=len(hashes)) as pbar: # 진행 상황을 표시하는 진행 바
        for i, hash_val in enumerate(hashes):
            if hash_val in seen_hashes: # 이미 처리된 해시 값은 건너뛰기
                continue
            
            params = {'apikey': API_KEY, 'resource': hash_val}
            response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params, verify=False)

            if response.status_code == 200:
                data = response.json()
                sha256 = data.get('sha256', '')
                md5 = data.get('md5', '')
                sha1 = data.get('sha1', '')
                file_type = data.get('type_description', '')
                detected = data.get('positives', False)
                engines = sorted([engine for engine in data.get('scans', {}).keys() if data['scans'][engine]['detected']])
                url = f'https://www.virustotal.com/gui/file/{hash_val}/detection' # 각 해시 값에 대한 검색 URL

                writer.writerow([sha256, md5, sha1, file_type, detected, '|'.join(engines), url])
            else:
                print(f"Error: {response.status_code} {response.reason}")
            
            seen_hashes.add(hash_val) # 현재 해시 값을 seen_hashes에 추가
            
            time.sleep(15) # 다음 요청 전 15초 대기, 분당 4회 요청 제한
            
            # 진행 바 업데이트
            pbar.update(1)

```

### 4. 코드 병합 및 GUI 생성
```python

```
