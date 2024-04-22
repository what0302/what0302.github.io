---
layout: post
title: "Web-Development 로그인 페이지 실습"
tags: [웹개발, HTML, CSS, PHP, 실습]
comments: true
---

HTML, CSS, PHP 를 이용한 간단한 로그인 페이지 구축

---

## (1) login.php

<br>

```php
<link rel="stylesheet" href="style.css">

<?php
session_start(); // 세션 시작

// 간단한 사용자 데이터
$users = [
    "admin" => "admin1234"
];

// 로그인 처리
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    if (isset($users[$username]) && $users[$username] == $password) {
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $username;
        header("Location: welcome.php"); // 로그인 성공 시 welcome.php로 리다이렉트
        exit();
    } else {
        $error = "잘못된 사용자 이름 또는 비밀번호입니다.";
    }
}
?>

<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>로그인</title>
</head>
<body>
    <?php if (isset($error)): ?>
        <p><?php echo $error; ?></p>
    <?php endif; ?>
    <form class="box"  method="post">
        사용자 이름: <input type="text" name="username" placeholder="ID"><br>
        비밀번호: <input type="password" name="password" placeholder="Password"><br>
        <button type="submit">Sign in</button>
    </form>
	<div class="sign-up-box">
    <i class="material-icons">create</i>
  </div>
</body>
</html>

```

<br>

## (2) welcome.php

<br>

```php
<?php
session_start();

// 로그인 여부 확인
if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true) {
    header("Location: login.php"); // 로그인되지 않은 경우 로그인 페이지로 리다이렉트
    exit();
}
?>

<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>환영합니다</title>
</head>
<body>
    <h2>환영합니다, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
    <p><a href="logout.php">로그아웃</a></p>
</body>
</html>

```
<br>

## (3) logut.php

<br>

```php
<?php
session_start();
session_destroy(); // 세션 종료
header("Location: login.php"); // 로그인 페이지로 리다이렉트
exit();

```

<br>

## (4) style.css

<br>

```css
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
:root {
  --padding: 60px;
}
.box {
  position: relative;
  margin: 50px auto;
  width: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: var(--padding);
  background-color: #c4dfff;
  border-radius: 7px;
}

.box input,
.box button {
  padding: 15px;
  font-size: 1.2em;
  border: none;
}
.box input {
  margin-bottom: 25px;
}
.box button {
  background-color: #ffe4c4;
  color: #547fb2;
  border-radius: 4px;
}

.sign-up-box {
  position: absolute;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: #86acd9;
  display: flex;
  justify-content: center;
  align-items: center;
  top: var(--padding);
  right: -35px;
  cursor: pointer;
  transition: all 500ms ease-in-out;
}
.sign-up-box i {
  font-size: 1.9em;
  color: #fff;
}

/*.active*/

.sign-up-box.active {
  top: 0;
  bottom: 0;
  right: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  padding: 30px;
  cursor: default;
  border-radius: 7px;
}

.sign-up-box.active input,
.sign-up-box.active button {
  padding: 15px;
  font-size: 1.2em;
  border: none;
  margin: 0;
}
.sign-up-box.active input {
  margin-bottom: 10px;
}

.sign-up-box.active > span {
  position: absolute;
  width: 30px;
  height: 30px;
  background-color: #fff;
  border-radius: 50%;
  top: 5px;
  right: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #547fb2;
  font-weight: 700;
  cursor: pointer;
}

```

<br>


## (5) 결과
### 1. 로그인 페이지
<img width="500" alt="스크린샷 2024-04-22 오후 3 21 34" src="https://github.com/what0302/what0302.github.io/assets/18510716/610d0910-ec4c-4f9f-9cf3-a543bb850c35">

<br>

### 2. 로그인 실패 문구
<img width="500" alt="스크린샷 2024-04-22 오후 3 21 55" src="https://github.com/what0302/what0302.github.io/assets/18510716/21e7d165-e37f-45b2-8501-165c5f5ae2ab">

<br>

### 3. 로그인 성공 문구
<img width="500" alt="스크린샷 2024-04-22 오후 3 22 21" src="https://github.com/what0302/what0302.github.io/assets/18510716/1e3f536b-5db6-4c09-addb-2cf416f84ec8">

<br>

<img width="593" alt="스크린샷 2024-04-22 오후 3 22 11" src="https://github.com/what0302/what0302.github.io/assets/18510716/8c5a010c-cb75-415b-a1cc-5c69b8ee1642">
