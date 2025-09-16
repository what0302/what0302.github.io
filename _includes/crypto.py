import string

C_hex = "65 6c ce 6b c1 75 61 7e 53 66 c9 52 d8 6c 6a 53 6e 6e de 52 df 63 6d 7e 75 7f ce 64 d5 63 73"
C = bytes.fromhex(C_hex)
N = len(C)

PREFIX = b"ictf{"
LAST = ord("}")
ALPHA = (string.ascii_lowercase + string.digits + "_").encode()

def solve_for_period(L):
    cand = [set(range(256)) for _ in range(L)]
    # 접두사 제약
    for i,ch in enumerate(PREFIX):
        cand[i % L] &= {C[i] ^ ch}
    # 끝 '}'
    cand[(N-1) % L] &= {C[-1] ^ LAST}
    # 본문 제약
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
    # 후보 키 결정
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

found = []
for L in range(2, 17):
    sols = solve_for_period(L)
    if sols:
        for L, P in sols:
            found.append((L,P))
            print(f"[+] period={L} → {P.decode()}")

if not found:
    print("조건 만족하는 플래그 후보 없음")
