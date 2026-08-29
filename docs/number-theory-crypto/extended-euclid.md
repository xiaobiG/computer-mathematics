---
title: 最大公约数与模逆元
description: 用扩展欧几里得算法解出模运算中的除法。
---

# 最大公约数与模逆元

## 从辗转相除到线性组合

欧几里得算法不断使用：

$$\gcd(a,b)=\gcd(b,a\bmod b)$$

扩展欧几里得算法进一步寻找整数 $x,y$，使：

$$ax+by=\gcd(a,b)$$

当 $\gcd(a,m)=1$ 时，上式模 $m$ 后得到 $ax\equiv1\pmod m$，因此 $x$ 就是 $a$ 的模逆元。

```python
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def inverse_mod(a, m):
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError('逆元不存在')
    return x % m
```

## 模运算中的“除法”

模 $m$ 下不能直接除以 $a$；只有当 $a$ 与 $m$ 互素时，才可乘以逆元 $a^{-1}$。这是 RSA 密钥构造与许多有限域算法的基础。

## 练习

计算 $7$ 在模 $26$ 下的逆元，并验证两者乘积除以 26 的余数为 1。
