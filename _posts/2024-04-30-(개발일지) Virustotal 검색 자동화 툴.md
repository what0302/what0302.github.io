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
