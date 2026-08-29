---
title: 椭圆曲线密码学预备：有限域上的点为什么能相加
description: 从有限域短 Weierstrass 曲线推导点加与 double-and-add，解释群结构、离散对数假设和教学实现的安全边界。
courseLevel: "2–3（代数结构、算法与密码工程边界）"
prerequisites: "模逆元、有限域、群论直觉与快速幂"
estimatedMinutes: 70
experiment: "在小素域上实现点加、无穷远点和 double-and-add 标量乘法"
---

# 椭圆曲线密码学预备：有限域上的点为什么能相加

## 学习目标

读完后，你能说明有限域短 Weierstrass 曲线的定义；按公式计算点加、倍点与无穷远点；实现 $kP$ 的 double-and-add；解释椭圆曲线离散对数问题的角色；并识别小参数、未验证点、非恒定时间和自制协议为何不能用于真实安全系统。

## 从密钥大小的疑问开始

ECC 构造一个群，但元素是有限域上曲线的点。在合适参数下，它能以较短的公开参数达到同类离散对数安全目标。重点不在“曲线看起来复杂”，而在于群运算高效、反向求标量困难，以及参数和实现经过长期公开审查。

本文只建立数学预备。下文的小曲线和 Python 代码故意可枚举，完全不安全。

## 严格定义：曲线、域与无穷远点

取奇素数 $p$，有限域为 $\mathbb F_p$，所有运算按 $p$ 取模。短 Weierstrass 形式为

$$E: y^2=x^3+ax+b\pmod p.$$

要求判别式不为零：

$$4a^3+27b^2\not\equiv0\pmod p.$$

否则曲线有奇点，割线—切线规则不能给出所需群。点集由满足方程的 $(x,y)$ 和额外符号 $\mathcal O$ 构成；$\mathcal O$ 是无穷远点和加法单位元。若 $P=(x,y)$，则

$$-P=(x,-y\bmod p),\qquad P+(-P)=\mathcal O.$$

## 分步推导：从斜率到点加

给定不同且不互逆的点 $P=(x_1,y_1),Q=(x_2,y_2)$，割线斜率是

$$\lambda=(y_2-y_1)(x_2-x_1)^{-1}\pmod p.$$

代入直线至曲线方程，比较三次多项式根的和可得

$$x_3=\lambda^2-x_1-x_2\pmod p,
\qquad y_3=\lambda(x_1-x_3)-y_1\pmod p.$$

当 $P=Q$ 时，切线公式为

$$\lambda=(3x_1^2+a)(2y_1)^{-1}\pmod p.$$

若 $y_1=0$，分母为零；这正好是 $P=-P$，结果应为 $\mathcal O$，不是去求零的逆元。模数是素数且点在曲线上，才保证上述逆元和群定理的前提。

## 可运行实验：小域上的点群

玩具箱实现了 $y^2=x^3+2x+2\pmod {17}$：

```python
from projects.crypto_toybox.elliptic_curve import ToyCurve

curve = ToyCurve(p=17, a=2, b=2)
G = (5, 1)
assert curve.add(G, (5, 16)) is None
assert curve.scalar_multiply(2, G) == (6, 3)
assert curve.scalar_multiply(7, G) == (0, 6)

result, trace = curve.scalar_multiply_trace(7, G)
assert curve.scalar_multiply_trace_certificate(7, G, result, trace)
```

```bash
python -m unittest projects.crypto_toybox.test_elliptic_curve
```

`scalar_multiply(k, P)` 与快速幂同构：扫描 $k$ 的二进制位，当前点倍增，位为 1 则累加。`scalar_multiply_trace` 记录每轮的低位、累计点、倍点和剩余标量；独立证书会重放每一步，并拒绝被篡改的轨迹。若 $k$ 有 $\lfloor\log_2 k\rfloor+1$ 位，点加次数为 $O(\log k)$。测试验证单位元、逆元、倍点、重复加法与 double-and-add 的一致性，并拒绝奇点、合数模数、曲线外点和负标量。

## 从标量乘法到离散对数假设

给定基点 $G$ 和标量 $k$，计算 $Q=kG$ 很快。ECDLP 反过来问：给定 $G,Q$，求 $k$。在标准选择的曲线和大子群中，没有已知的通用高效算法；ECDH、ECDSA 等依赖这一类假设和额外协议细节。

这不是“公式自动提供安全”。安全还取决于子群阶、私钥生成、点验证、协议认证、nonce 管理、恒定时间实现、编码与抗侧信道设计。这里 $p=17$ 可立即枚举，故只用于检查代数。

## 正确性、复杂度与工程边界

非奇异曲线上的群律是代数定理；实现的每次 `add` 先验证曲线成员，保证公式输入满足前提。double-and-add 的循环不变量是：已处理低位的累加结果与当前倍点共同表示原 $kP$；每次位移和倍增保持该关系，因此结束时得到 $kP$。轨迹证书逐轮重放这一更新，因此能发现一次有限运行中篡改的位、累计点、倍点或剩余标量；它仍不是群律证明，也不会把教学代码变成安全实现。

但 Python 大整数、分支和模逆元的运行时间可能泄漏秘密标量。实现没有协因子/子群检查、标准点编码、安全随机数或恒定时间保证；不可用于 ECDH、签名、加密、钱包或任何真实秘密。

## 失败案例与常见误区

- **合数模数**：非零元素不都可逆，不能把环误当有限域。
- **奇异曲线**：判别式为零时不满足所需群结构。
- **曲线外点/小子群输入**：真实协议若不验证输入，可能泄漏私钥信息。
- **复用签名 nonce**：可直接破坏某些签名方案的私钥，与点加公式正确无关。
- **“短密钥所以更安全”**：安全性来自标准曲线和已知攻击成本，不来自代码短或图形复杂。

## 练习

1. **基础题**：在模 $17$ 下验证 $(5,1)$ 与 $(5,16)$ 都在曲线上，并计算它们的和。
2. **推导题**：从直线与三次方程的根和，推导 $x_3=\lambda^2-x_1-x_2$。
3. **编码题**：列举小曲线全部点，验证每次 `add(P, Q)` 的结果仍在曲线上或为 `None`。
4. **开放题**：为一个真实 ECDH 集成列出必须交给成熟库处理的项目，并说明各自防范什么攻击。

## 延伸

[有限域、群与离散对数直觉](/number-theory-crypto/finite-fields-groups)提供抽象群语言；[Diffie–Hellman](/number-theory-crypto/diffie-hellman)解释密钥交换的认证问题；[密码学玩具箱](/projects/crypto-toybox)收录本课实验。继续学习时优先查阅标准与成熟库文档：point validation、cofactor clearing、constant-time arithmetic、RFC 7748 与协议安全证明。
