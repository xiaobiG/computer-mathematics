---
title: 项目：密码学玩具箱
description: 用快速幂、模逆元与小参数 RSA 串起数论课程的教学实现。
---

# 项目：密码学玩具箱

## 安全声明

本项目**仅用于教学**。它使用很小的固定参数，缺少标准填充、认证、密钥生成、常量时间操作和安全随机数；绝不可用于保护真实数据、密码、身份或网络通信。

## 目标

实现并测试三块数学积木：模幂、扩展欧几里得算法和教学 RSA。重点是看到这些函数在加密、解密流程中如何连接，而非尝试自制密码系统。

## 数学连接

- [模运算与快速幂](/number-theory-crypto/modular-arithmetic)
- [最大公约数与模逆元](/number-theory-crypto/extended-euclid)
- [RSA](/number-theory-crypto/rsa)
- [中国剩余定理](/number-theory-crypto/chinese-remainder-theorem)

## 运行

```bash
python projects/crypto_toybox/main.py
python -m unittest projects.crypto_toybox.test_main
```

## 实验问题

1. 修改明文 $m$，验证 `decrypt(encrypt(m)) == m`；
2. 用扩展欧几里得算法验证公开指数和私钥指数互为模逆元；
3. 思考：为什么知道 $n=pq$ 但不知道 $p,q$ 会使计算私钥变困难？

## 从这里走向真实系统

真实应用必须使用平台或经审计库实现 TLS、签名和密码存储。学习代码有价值，但“能运行”绝不等于“安全”。
