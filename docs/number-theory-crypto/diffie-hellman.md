---
courseLevel: "2–3（协议与安全）"
prerequisites: "模幂、群论直觉与离散对数"
estimatedMinutes: 50
experiment: "用小参数模拟密钥协商与中间人攻击"
title: Diffie–Hellman 密钥交换
description: 理解双方如何在公开信道上协商同一秘密。
---

# Diffie–Hellman 密钥交换

双方公开选择大质数模数 $p$ 和生成元 $g$。Alice 选择私有指数 $a$，公开 $A=g^a\bmod p$；Bob 选择私有指数 $b$，公开 $B=g^b\bmod p$。

两人分别计算：

$$B^a\equiv(g^b)^a\equiv g^{ab}\equiv(g^a)^b\equiv A^b\pmod p$$

因此得到相同共享秘密，而窃听者只见 $g,p,A,B$。其安全性依赖离散对数问题的困难性。

## 它不自动验证身份

若没有签名、证书或其他认证机制，中间人可分别与双方协商不同秘密。这是“能保密”与“能确认对方身份”的重要区别。

## 工程边界

生产系统使用成熟协议和库，例如 TLS 中经过审计的椭圆曲线密钥交换；绝不使用教学参数或自行拼装协议。

## 练习

用小参数手算一次交换，验证双方结果相同；然后画出中间人攻击中三方交换的通信图。
