---
courseLevel: "1–2（核心概念与算法）"
prerequisites: "整除、余数与二进制"
estimatedMinutes: 50
experiment: "实现快速幂并统计乘法次数"
title: 模运算与快速幂：为什么大指数不必先算出来
description: 从同余封闭性推导重复平方，证明循环不变量并理解复杂度与侧信道边界。
---

# 模运算与快速幂：为什么大指数不必先算出来

## 文章元信息

- **建议阅读层级**：1–3 · 同余模型、算法证明与安全边界
- **前置知识**：整数除法、二进制表示、循环不变量
- **预计学习时间**：50 分钟
- **配套实验**：[密码学玩具箱](/projects/crypto-toybox)

## 学习目标

- 使用同余将大数运算约化为有限模数内运算；
- 用重复平方计算 $a^e\bmod n$ 并证明其不变量；
- 区分教学算法的复杂度正确性与生产密码实现的侧信道要求。

## 从一个计算问题开始

RSA 解密需要计算 $m^d\bmod n$，其中 $d$ 有数千位。若先计算 $m^d$，内存和时间都会耗尽；为何每一步先取模仍能保证最终余数完全相同？

## 定义与推导

若 $n$ 整除 $a-b$，记 $a\equiv b\pmod n$。同余在加法和乘法下封闭：

$$a\equiv b\pmod n\Rightarrow ac\equiv bc\pmod n.$$

因此 $((a\bmod n)(b\bmod n))\bmod n=(ab)\bmod n$。将指数写为二进制，$e=\sum_i e_i2^i$；依次平方得到 $a^{2^i}$，只有 $e_i=1$ 时乘入结果。指数每轮右移一位，循环次数为位数而非指数值。

## 算法实现与正确性

```python
def mod_pow(base, exponent, modulus):
    if modulus <= 1 or exponent < 0:
        raise ValueError("modulus must exceed 1 and exponent must be non-negative")
    result, base = 1, base % modulus
    while exponent:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
    return result


assert mod_pow(7, 128, 13) == pow(7, 128, 13)
```

不变量是：初始指数为 $E$ 时，$result\cdot base^{exponent}\equiv a^E\pmod n$。若最低位为 1，将一个 `base` 移到 `result`；平方 `base` 且指数右移保持等价。指数归零时不变量给出结果正确。时间为 $O(\log e)$ 次模乘，额外空间 $O(1)$（忽略大整数位数）。

## 失败案例与工程边界

普通实现的 `if exponent & 1` 和运行时间可能泄漏指数位；用于私钥时，攻击者可借计时、缓存或功耗推断秘密。生产密码只能使用经审计库中的常量时间实现，还需要安全随机数、填充、协议验证和密钥管理。负指数意味着模逆元，只有底数与模数互素时才有定义。

## 常见误区

- 模运算不能把除法随意分配：除法需要模逆元。
- $O(\log e)$ 不代表所有成本很小，大整数乘法随位数增长。
- `pow` 输出正确不证明自写密码系统安全。

## 练习

1. **基础**：手算 $3^{13}\bmod7$ 的平方链。
2. **推导**：用不变量证明最低位为 0 时循环仍保持等价。
3. **编码**：测试模数 1、负指数、底数为负和指数为 0。
4. **开放**：比较“平方—乘”与 Montgomery ladder 的控制流，说明后者为何更适合秘密指数。

## 延伸与下一步

[模逆元](/number-theory-crypto/extended-euclid)给出负指数/除法的合法条件；[RSA](/number-theory-crypto/rsa)将快速幂嵌入公钥协议，但必须额外处理填充与攻击面。
