---
title: 项目：密码学玩具箱
description: 用快速幂、模逆元、小参数 RSA、教学签名验签与有限域椭圆曲线串起数论课程的教学实现。
---

# 项目：密码学玩具箱

## 安全声明

本项目**仅用于教学**。它使用很小的固定参数，缺少标准填充、认证、密钥生成、常量时间操作和安全随机数；绝不可用于保护真实数据、密码、身份或网络通信。

## 目标

实现并测试八块数学积木：带逐位不变量证书的教学模幂、扩展欧几里得算法、通用中国剩余合并、带质因子前提/模逆元证书和 CRT 样例审计的教学 RSA、教学签名验签等式、有限域乘法群与小参数 DH 转录、带可重放 double-and-add 轨迹证书的有限域椭圆曲线点群和标准库 HMAC 验证。重点是看到这些函数在加密、验签、密钥协商、标量乘法或消息认证中如何连接，而非尝试自制密码系统。

## 数学连接

- [模运算与快速幂](/number-theory-crypto/modular-arithmetic)
- [最大公约数与模逆元](/number-theory-crypto/extended-euclid)
- [RSA](/number-theory-crypto/rsa)
- [数字签名](/number-theory-crypto/digital-signatures)
- [Diffie–Hellman 密钥交换](/number-theory-crypto/diffie-hellman)
- [中国剩余定理](/number-theory-crypto/chinese-remainder-theorem)
- [椭圆曲线密码学预备](/number-theory-crypto/elliptic-curve-prelude)
- [消息认证码](/number-theory-crypto/message-authentication-codes)

## 运行

```bash
python projects/crypto_toybox/main.py
python -m unittest projects.crypto_toybox.test_main
python -m unittest projects.crypto_toybox.test_primality
python -m unittest projects.crypto_toybox.test_password_storage
python -m unittest projects.crypto_toybox.test_diffie_hellman
python -m unittest projects.crypto_toybox.test_elliptic_curve
python -m unittest projects.crypto_toybox.test_message_auth
python -m unittest projects.crypto_toybox.test_signatures
```

## 实验问题

1. 修改明文 $m$，使用 `rsa_round_trip_report` 同时验证互素与不互素代表元的 `decrypt(encrypt(m)) == m`；
2. 运行 `mod_pow_trace`，核对每轮低位、`result` 和平方后的 `base`；说明这份可读轨迹为何不能用于秘密指数；
3. 用 `rsa_keypair_certificate(p, q, key)` 验证公开指数和私钥指数互为模逆元，并篡改一个指数观察证书失效；
4. 思考：为什么知道 $n=pq$ 但不知道 $p,q$ 会使计算私钥变困难？
5. 在小素域上验证 $P+(-P)=\mathcal O$，并解释为何这不构成真实椭圆曲线密码实现。
6. 对比诚实 DH 和中间人转录：前者的两端共享值相同，后者中攻击者分别与两端匹配而两端并未建立同一秘密。
7. 对 Carmichael 数 561 运行 `miller_rabin_report`，重放某个合数见证者的平方链，并说明为何无见证者不构成素数证明。
8. 用同一密码创建两条含不同盐的教学记录，确认派生值不同；再用错误密码尝试迁移成本参数，确认不会生成新记录。
9. 记录 `scalar_multiply_trace(7, G)`，篡改其中一轮剩余标量或累计点，并验证轨迹证书拒绝它；解释为何公开该轨迹本身就不适合秘密标量。

## 从这里走向真实系统

真实应用必须使用平台或经审计库实现 TLS、签名和密码存储。学习代码有价值，但“能运行”绝不等于“安全”。
