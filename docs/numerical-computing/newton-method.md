---
title: 牛顿法：用切线快速逼近方程的根
description: 理解迭代公式、收敛条件与失败案例。
---

# 牛顿法：用切线快速逼近方程的根

## 从切线得到迭代

求 $f(x)=0$ 的根。当前猜测为 $x_k$ 时，用切线近似曲线：

$$f(x)\approx f(x_k)+f'(x_k)(x-x_k)$$

令近似值为零，得到：

$$x_{k+1}=x_k-\frac{f(x_k)}{f'(x_k)}$$

在根附近、导数不为零且函数足够光滑时，它常具有很快的二次收敛。

```python
def newton(f, df, x, tolerance=1e-10, max_steps=50):
    for _ in range(max_steps):
        y, slope = f(x), df(x)
        if abs(slope) < 1e-14:
            raise ValueError('导数过小，切线不可靠')
        next_x = x - y / slope
        if abs(next_x - x) <= tolerance:
            return next_x
        x = next_x
    raise RuntimeError('未在限定步数内收敛')
```

## 失败也很重要

初值太远时，切线可能跳到错误区域；导数接近零时，步长会异常大；某些函数甚至会在几个点之间循环。数值算法必须带有迭代上限、导数检查和收敛判据。

## 练习

用牛顿法计算 $\sqrt{2}$，再尝试 $f(x)=x^{1/3}$ 且初值接近 0，观察导数问题。
