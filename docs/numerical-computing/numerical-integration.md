---
courseLevel: "2（算法与误差）"
prerequisites: "积分、函数与求和"
estimatedMinutes: 45
experiment: "比较梯形法和 Simpson 法的误差阶"
title: 数值积分：从求和逼近面积
description: 用梯形法和 Simpson 法理解积分的离散近似。
---

# 数值积分：从求和逼近面积

当函数没有易用原函数、只有采样点或只可通过程序求值时，可将区间切分并求和。梯形法在每个小区间用直线逼近：

$$\int_a^b f(x)dx\approx\sum_i\frac{h}{2}(f(x_i)+f(x_{i+1}))$$

```python
def trapezoid(f, a, b, n):
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return h * total
```

Simpson 法在相邻小区间上用二次曲线逼近，函数足够光滑时通常精度更高，但要求分段数为偶数。

## 误差与边界

网格更细会减少截断误差，却增加函数调用和累计舍入误差。函数尖峰、间断或高频振荡时，应优先自适应切分而非盲目等距加点。

## 练习

用梯形法估算 $\int_0^\pi\sin x\,dx$，比较不同分段数下与精确值 2 的误差。
