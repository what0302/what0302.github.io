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

### 1. probe 파라미터로 입력 받기

```php 
$probe = (int)@$_GET['probe'];
```
- GET 파라미터 'probe'에서 숫자 값을 받아 정수형으로 변환하고 내부 포트 범위 시작 번호로 사용함

### 2. 포트 범위 생성 및 무작위로 섞기

```php
$range = range($probe, $probe + 42);
shuffle($range);
```

- probe부터 probe+42까지 총 43개의 연속 포트 번호 배열 생성
- 배열을 무작위로 섞는 과정임

### 3. 각 포트에 대해 TCP 연결 시도

```php
foreach ($range as $k => $port) {
    $target = sprintf("tcp://%s:%d", $_SERVER['SERVER_ADDR'], $port);
    $fp = @stream_socket_client($target, $errno, $errstr, 1);
    if (!$fp) continue;
```
- 서버 자신의 내부 IP 주소(```$_SERVER['SERVER_ADDR']```)와 포트 번호를 조합하여 TCP 주소 생성
- ```stream_socket_client```로 최대 1초 동안 해당 포트에 TCP 연결 시도, 실패하면 다음 포트 탐색

### 4. 연결 성공 시 데이터 송수신 처리

```php
    stream_set_timeout($fp, 1);
    fwrite($fp, file_get_contents("php://input"));
    $data = fgets($fp);
```
- 연결된 소켓에 대해 읽기 타임아웃 1초 설정
- 현재 HTTP 요청의 바디(raw POST 데이터) 전체를 해당 TCP 연결에 사용함

### 5. 받은 데이터가 있을 때 데이터 처리

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
- JSON 객체 안에 ```signal``` 속성이 있고 값이 "Arrival"이면
- ```logoram``` 속성 앖을 PHP 코드로 간주해 ```eval()``` 함수로 실행함. 이때 임의코드 실행 취약점이 발생
- 소켓 닫고 스크립트 종료

### 6. 위 조건이 없으면 다음 포트를 계속 탐색
- 조건이 만족되지 않거나 연결 실패 시 다음 포트 탐색

### 7. 마지막으로 현재 소스 코드 화면에 출력
```php
highlight_file(__FILE__);
```
- 직접 접근했을 때 이 PHP 파일의 소스가 하이라이팅된 상태로 표시됨

### 문제 요약
> 사용자가 probe 값으로 지정한 포트부터 43개의 포트를 무작위로 내부 IP에서 TCP 연결을 시도하고, POST 요청의 본문을 해당 포트에 보내고, 연결된 곳에서 JSON 형태의 응답이 signal="Arrival" 일 경우 eval로 전달된 PHP 코드를 실행함으로써 내부 시스템에 원격으로 코드를 실행할 수 있도록 설계되어 있는 구조임


## (2) 풀이
- 웹사이트에 직접 연결을 시도하면 부하가 발생함으로 도커 이미지를 생성해서 풀이를 진행함.
``` no-mans-echo_chall-76a916a81207254228c87f29b3364225471f9bad.tar.gz ```
문제 파일 다운로드함. 압축 해제 후 해당 폴더로 진입해서 
``` docker build -t no-mans-echo .``` 
도커 이미지를 빌드함. 
- 이후 도커 컨테이너 실행 및 포트 매핑 ```docker run -d -p 8080:8080 --name no-mans-echo no-mans-echo```

<img width="592" height="460" alt="스크린샷 2025-08-30 오후 11 17 57" src="https://github.com/user-attachments/assets/1476fff4-7de4-4970-adc7-544180efcfa3" />

도커 이미지 빌드가 제대로 되었다면 `http://localhost:8080/`로 접근했을 때 index.php가 정상 출력됨
