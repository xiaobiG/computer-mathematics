---
courseLevel: "2（推导与算法）"
prerequisites: "最大公约数、整除与同余"
estimatedMinutes: 50
experiment: "实现贝祖系数并验证模逆元存在条件"
title: 扩展欧几里得与模逆元：模运算中何时可以“除法”
description: 从贝祖等式推导模逆元，证明扩展欧几里得算法并处理逆元不存在的边界。
---

# 扩展欧几里得与模逆元：模运算中何时可以“除法”

## 文章元信息

- **建议阅读层级**：1–2 · 数论定义、递归算法与正确性
- **前置知识**：整除、余数、[模运算与快速幂](/number-theory-crypto/modular-arithmetic)
- **预计学习时间**：50 分钟
- **配套实验**：[密码学玩具箱](/projects/crypto-toybox)

## 学习目标

- 用贝祖等式判断模逆元是否存在；
- 实现扩展欧几里得算法并验证系数；
- 解释 RSA 与 CRT 中为什么需要互素条件。

## 从一个计算问题开始

普通算术中 $3x=1$ 的解是 $1/3$；模 7 下却有整数解 $x=5$，因为 $3\times5\equiv1\pmod7$。模 8 下 $2x\equiv1$ 则永远无解。程序怎样在不穷举所有 $x$ 的前提下判断并求解？

## 定义与推导

欧几里得算法利用 $\gcd(a,b)=\gcd(b,a\bmod b)$。更强的贝祖等式说存在整数 $x,y$ 使

$$ax+by=\gcd(a,b).$$

当 $\gcd(a,m)=1$，式子模 $m$ 后为 $ax\equiv1\pmod m$，因此 $x\bmod m$ 是 $a$ 的逆元。反之，若逆元存在，任何公因子都必须整除 1，所以互素也是必要条件。

## 算法实现与正确性

```python
from projects.crypto_toybox.main import (
    extended_gcd_trace,
    extended_gcd_trace_certificate,
    modular_inverse,
)

result, trace = extended_gcd_trace(240, 46)
gcd, x, y = result
assert gcd == 2 and 240 * x + 46 * y == gcd
assert [event.remainder for event in trace] == [10, 6, 4, 2, 0]
assert extended_gcd_trace_certificate(240, 46, result, trace)
assert modular_inverse(7, 26) == 15
assert (7 * modular_inverse(7, 26)) % 26 == 1
```

递归调用中的 $(x_1,y_1)$ 满足 $bx_1+(a\bmod b)y_1=g$。代入 $a\bmod b=a-\lfloor a/b\rfloor b$，整理得 $a y_1+b(x_1-\lfloor a/b\rfloor y_1)=g$，正是返回系数。`extended_gcd_trace` 公开每次除法的被除数、除数、商和余数；证书重放该链，检查每个余数确实满足 $0\le r<b$，终点为最大公约数，并独立核对 $ax+by=g$。篡改任一余数或贝祖系数都会使证书失败。每轮余数严格变小，时间为 $O(\log\min(a,b))$。

## 失败案例与工程边界

逆元不存在不是异常数值，而是代数事实：例如 $\gcd(2,8)=2$，所以 $2x\bmod8$ 永远为偶数。模数必须大于 1；负输入时应先规范化或明确 API 语义。密码代码不可据此自行构造协议，逆元计算还需考虑恒定时间和错误处理泄漏。

## 常见误区

- 模意义下的“除以 $a$”只在 $a$ 可逆时才合法。
- 逆元不是实数倒数，结果是一个同余类。
- RSA 中 $e$ 必须与 $\varphi(n)$ 互素，才能构造私钥指数 $d$。

## 练习

1. **基础**：用算法求 $11$ 在模 26 下的逆元。
2. **推导**：证明 $a$ 在模 $m$ 下可逆当且仅当 $\gcd(a,m)=1$。
3. **编码**：测试负 `value`、模数 1 和不可逆输入。
4. **开放**：解释有限域中为何每个非零元素都有逆元，而复合模数下不一定。

## 练习答案提示

1. 用扩展欧几里得先求 $11x+26y=1$，其中 $x$ 归一到 $0\ldots25$ 就是逆元；每轮余数必须严格变小。
2. 若有逆元则 $ax+my=1$，故 gcd 为 1；反向由贝祖等式取模即可构造逆元。
3. 先定义负值是规范化后接受还是拒绝；模数 1、gcd 非 1 都没有逆元，测试应检查异常契约而非偶然输出。
4. 域的非零元素对乘法构成群，故都有逆；复合模数中存在零因子，例如 $2\cdot4\equiv0\pmod8$，因而不能都可逆。

## 延伸与下一步

[中国剩余定理](/number-theory-crypto/chinese-remainder-theorem)用互素模数拆解同余系统；[RSA](/number-theory-crypto/rsa)正是用逆元条件构造 $ed\equiv1\pmod{\varphi(n)}$。
