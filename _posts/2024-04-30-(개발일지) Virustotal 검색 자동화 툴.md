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
