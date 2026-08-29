---
title: 模运算与快速幂
description: 用时钟算术和重复平方理解密码学的基本运算。
---

# 模运算与快速幂

## 先问一个问题

RSA 等密码系统需要计算像 $a^b\bmod n$ 这样指数极大的表达式。直接先算 $a^b$ 会产生不可承受的大整数，但模运算允许我们在每一步缩小结果。

## 同余

若两个整数除以 $n$ 的余数相同，记为：

$$a\equiv b\pmod n$$

同余在加法和乘法下保持成立：

$$((a\bmod n)(b\bmod n))\bmod n=(ab)\bmod n$$

这就是“时钟算术”的本质：12 点之后回到 0 点。

## 重复平方

指数的二进制表示使我们只需不断平方并按需相乘：

```python
def mod_pow(base, exponent, modulus):
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
    return result

print(mod_pow(7, 128, 13))
```

算法仅需 $O(\log b)$ 次循环，而不是 $O(b)$ 次乘法。

## 安全边界

这段代码用于学习，不应用于生产密码系统。真实密码实现还必须处理随机数、填充、常量时间操作、密钥生命周期和成熟库的审计问题。

## 练习

用 `pow(base, exponent, modulus)` 验证自己的实现；再实现扩展欧几里得算法，计算模逆元。
