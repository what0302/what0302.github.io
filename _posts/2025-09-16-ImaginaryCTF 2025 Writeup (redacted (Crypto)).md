[crypto.py](https://github.com/user-attachments/files/22363968/crypto.py)---
layout: post
title: "ImaginaryCTF 2025 Writeup (redacted (Crypto))"
tags: [정보보안, CTF]
comments: true
---

ImaginaryCTF 2025 Writeup 입니다

--- 

## (1) 문제 
<img width="959" height="413" alt="redacted" src="https://github.com/user-attachments/assets/4b4b528a-676b-4b42-8848-a00c8fef562f" />

Cyberchef에서 XOR Key와 Input에 특정 문자열을 입력한 형태임. Output을 보고 Input을 맞추는 Crypto 문제임

## (2) 풀이

### 2-1. 풀이 개요

ictf{...} 문자열을 각각 입력한 것으로 추측할 수 있음.

문제 이미지에서 보이는 key 오른쪽의 hex는 key를 어떤식으로 해석할지 선택하는 부분임. XOR에서 key와 input이 동일하면 00 00 00 .. 이 출력되는데, 이 경우 key를 hex로 해석하기 때문에 다른 결과가 나옴. 

Scheme에 Standard는 반복키 XOR(repeating-key XOR)에 해당됨.

### 2-2. 풀이 접근

주어진 hex C= "65 6c ce 6b c1 75 61 7e 53 66 c9 52 d8 6c 6a 53 6e 6e de 52 df 63 6d 7e 75 7f ce 64 d5 63 73" 와 ictf{...} 플래그 형식을 이용해서 길이가 L인 반복키라고 가정하고 평문과 L을 찾으면 됨

```python
C_hex = "65 6c ce 6b c1 75 61 7e 53 66 c9 52 d8 6c 6a 53 6e 6e de 52 df 63 6d 7e 75 7f ce 64 d5 63 73"
C = bytes.fromhex(C_hex)
N = len(C)

PREFIX = b"ictf{"
LAST = ord("}")
```
- 평문의 시작은 "ictf{" 로 고정, 끝은 "}"로 고정

```python
def solve_for_period(L):
    cand = [set(range(256)) for _ in range(L)]
```

- cand[r]에 평문 단어에 해당하는 각 위치에 들어갈 바이트를 0부터 255까지 허용

```python
for i,ch in enumerate(PREFIX):
        cand[i % L] &= {C[i] ^ ch}
    cand[(N-1) % L] &= {C[-1] ^ LAST}
    for i in range(N):
        if i < len(PREFIX) or i == N-1:
            continue
        r = i % L
        allowed = set()
        for k in cand[r]:
            if (C[i] ^ k) in ALPHA:
                allowed.add(k)
        cand[r] = allowed
        if not cand[r]:
            return []
```

- 평문의 첫 바이트는 i에 해당하므로 이를 고정
- 같은 방식으로 마지막 }도 고정
- 이후 키 바이트 k에 대해 k를 적용했을 때 그 위치에 들어가는 평문 문자들이 허용 문자(ALPHA)에 들어가는지 확인하고, 조건을 만족하는 k만 남김. ictf{...} 형식을 만족하므로, 대문자 소문자 - 등 읽을 수 있는 문자에 해당되는지 파악하기 위함임

```python
from itertools import product
sols = []
for ks in product(*[list(c) for c in cand]):
    Kphase = bytes(ks)
    Kfull = bytes(Kphase[i % L] for i in range(N))
    P = bytes(ci ^ ki for ci,ki in zip(C,Kfull))
    if P.startswith(PREFIX) and P.endswith(b"}"):
        body = P[len(PREFIX):-1]
        if all(ch in ALPHA for ch in body):
            sols.append((L, P))
return sols
```

- 후보 키들의 모든 조합을 brute force
- 각 키로 전체 길이의 키 스트림 kfull을 만들고 p = C ⊕ kfull를 계산
- 해당 조건에 만족하는 후보를 모두 출력

전체 코드
