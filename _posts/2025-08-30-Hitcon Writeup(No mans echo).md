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
내용인 즉슨, 특정 내부 포트를 대상으로 TCP 연결을 시도하고, 연결된 포트로부터 받은 데이터를 조건에 따라 실행하는 일종의 포트 스캔 및 원격 코드 실행 취약점이 있는 서버임.

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

