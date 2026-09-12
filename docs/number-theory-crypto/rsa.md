---
courseLevel: "2–3（推导与安全工程）"
prerequisites: "模逆元、欧拉函数与快速幂"
estimatedMinutes: 65
experiment: "运行教学 RSA 并观察裸 RSA 的失败模式"
title: RSA：公开加密为何可行，以及裸 RSA 为何不安全
description: 从模逆元和欧拉定理推导 RSA 正确性，理解快速幂、填充与侧信道边界。
---

# RSA：公开加密为何可行，以及裸 RSA 为何不安全

## 文章元信息

- **建议阅读层级**：2–3 · 数论推导、算法与安全工程
- **前置知识**：[模运算与快速幂](/number-theory-crypto/modular-arithmetic)、[模逆元](/number-theory-crypto/extended-euclid)、互素与欧拉函数
- **预计学习时间**：65 分钟
- **配套实验**：[密码学玩具箱](/projects/crypto-toybox)

## 学习目标

读完后，你能根据互素指数构造教学 RSA 密钥；以欧拉定理与 CRT 推导包括非互素代表元的正确性；运行密钥前提与往返样例证书；并能解释裸 RSA 的确定性、可乘性和实现侧信道为何使它不能用于真实系统。

## 从一个计算问题开始

公开密钥 $(n,e)$ 允许任何人计算 $m^e\bmod n$。为什么只有持有私钥的人能还原 $m$？更重要的是：如果这个数学过程能运行，为什么真实系统仍然不能直接使用它加密一段消息？

## 直觉模型

RSA 把“反复乘幂”放入模 $n=pq$ 的世界。公开指数 $e$ 是一个可执行的变换；私钥指数 $d$ 被选择为它在指数意义上的逆变换。知道 $n$ 却不知道质因子，会使构造该逆变换所需的 $\varphi(n)$ 困难。

## 严格定义与构造

1. 选择不同质数 $p,q$，令 $n=pq$、$\varphi(n)=(p-1)(q-1)$；
2. 选择 $\gcd(e,\varphi(n))=1$；
3. 用扩展欧几里得求 $d$，使 $ed\equiv1\pmod{\varphi(n)}$；
4. 公钥为 $(n,e)$，私钥包含 $d$（实际实现也会保留 $p,q$ 作 CRT 优化）；
5. 教学中的整数消息满足 $0\le m<n$，加密 $c=m^e\bmod n$，解密 $m'=c^d\bmod n$。

## 分步推导：为何能解密

由模逆元定义，存在整数 $k$ 使 $ed=1+k\varphi(n)$。当 $m$ 与 $n$ 互素时，欧拉定理给出 $m^{\varphi(n)}\equiv1\pmod n$，于是

$$m^{ed}=m^{1+k\varphi(n)}=m(m^{\varphi(n)})^k\equiv m\pmod n.$$

对不与 $n$ 互素的消息，可分别在模 $p$、模 $q$ 下使用费马小定理，再由中国剩余定理合并，仍得到 $m^{ed}\equiv m\pmod n$。这就是 RSA 正确性；它不是“指数相除”，而是同余类中的指数关系。

## 手算一个完整例子

取 $p=5,q=11$，则 $n=55,\varphi(n)=40$。选择 $e=3$，因为 $3\times27=81\equiv1\pmod{40}$，故 $d=27$。对 $m=7$：

$$c=7^3\bmod55=13,\qquad m'=13^{27}\bmod55=7.$$

实际计算不应先构造 $13^{27}$，而应使用重复平方。

## 算法实现与复杂度

```python
from projects.crypto_toybox.main import (
    decrypt, encrypt, raw_rsa_properties, rsa_keypair_certificate,
    rsa_round_trip_certificate, rsa_round_trip_report, toy_rsa_keypair,
)

key = toy_rsa_keypair(5, 11, 3)
assert rsa_keypair_certificate(5, 11, key)["valid"]
assert encrypt(7, key) == 13
assert decrypt(13, key) == 7
assert raw_rsa_properties(2, 3, key) == {"deterministic": True, "multiplicative": True}

# 5、11、50 都不与 n=55 互素；仍须正确恢复。
report = rsa_round_trip_report([0, 5, 7, 11, 50], key)
assert report["all_recovered"]
assert report["non_coprime_messages"] == [0, 5, 11, 50]
assert rsa_round_trip_certificate(5, 11, key, report)["valid"]
```

运行 `python -m unittest projects.crypto_toybox.test_main`。`toy_rsa_keypair` 会先拒绝非质数因子和不满足 $1<e<\varphi(n)$、互素条件的指数，避免把证明前提静默留给调用者。`rsa_keypair_certificate(5, 11, key)` 则独立重算这些教学前提，并审计 $ed\bmod\varphi(n)=1$；篡改私钥指数会使证书失效。它要求传入 $p,q$，正是为了强调这不是可以安全暴露给真实系统的密钥检查方式。`rsa_round_trip_report` 还明确包含 $m=5,11,50$ 等与 $n$ 不互素的代表元；`rsa_round_trip_certificate` 会重新计算每条密文与解密值，并分别检查结果在模 $p$、模 $q$ 下与原消息相同。它把 CRT 覆盖的那部分正确性变成可篡改检测的有限样例审计。`raw_rsa_properties` 不产生攻击载荷或自制填充，它只核对同一明文总产生同一密文，以及 $E(m_1m_2\bmod n)=E(m_1)E(m_2)\bmod n$。这些为真的断言正是“数学可解密”并不足以构成安全加密的可执行证据。

重复平方需要 $O(\log e)$ 次模乘；大整数模乘本身有成本。真实 RSA 使用经过审计的库和 CRT 等优化，但优化也需要防止故障攻击与计时泄漏。

## 失败案例与工程边界

**裸 RSA 完全不能用于真实加密。** 它是确定性的、可乘的：攻击者可从 $c$ 构造与相关明文对应的密文，还可猜测小消息并验证。真实加密必须使用标准化、随机化的 RSA-OAEP；签名使用相应的 RSA-PSS，并由成熟库实现。密钥生成需要密码学安全随机数；私钥操作需考虑常量时间、故障注入、错误消息泄漏和密钥生命周期。现代系统也常优先使用椭圆曲线或混合加密。

## 常见误区

- $e,d$ 不是普通倒数，关系是模 $\varphi(n)$ 的乘法逆元。
- 安全性不来自“公式保密”，而来自大整数分解等计算难题和正确协议设计。
- 用小质数、固定随机数或 Python 教学代码“加密成功”不代表安全。

## 练习

1. **基础**：用 $p=3,q=11,e=3$ 求 $n,\varphi(n),d$，并验证一个消息的加解密。
2. **推导**：用中国剩余定理补全 $m$ 与 $n$ 不互素时的正确性论证。
3. **编码**：篡改 `rsa_round_trip_report` 中的一条密文或恢复消息，确认 `rsa_round_trip_certificate` 拒绝它；再为 `encrypt_toy` 添加负数、等于 $n$、大于 $n$ 的输入测试。
4. **开放**：查阅 OAEP 要解决的确定性/可塑性问题，并解释为何“自己实现填充”仍不安全。

## 练习答案提示

1. 先算 $n=33$、$\varphi(n)=20$，再解 $3d\equiv1\pmod{20}$；选择 $0\le m<n$ 的消息，并用重复平方核验两次模幂。
2. 分别证明 $m^{ed}\equiv m\pmod p$ 与 $\pmod q$：若对应素数整除 $m$，同余立即成立；否则用费马小定理，最后由 CRT 合并。
3. 明确教学 API 的消息域是 $0\le m<n$；证书需重新计算公钥幂、私钥幂和模 $p,q$ 的残余；三类越界输入都应断言拒绝方式一致，并保留一个边界内的正常回归用例。
4. OAEP 的随机编码阻止同明文得到同密文，并破坏裸 RSA 的直接可乘关系；安全性还依赖经过审计的参数、随机数和恒定时间实现，因此不能自行拼接填充。

## 延伸与下一步

[Diffie–Hellman](/number-theory-crypto/diffie-hellman)展示另一种基于离散对数的密钥协商；[哈希与密码存储](/number-theory-crypto/hashing-passwords)则强调真实安全系统通常比单个数学原语更依赖协议与实现边界。
