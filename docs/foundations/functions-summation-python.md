---
courseLevel: "0（预备知识）"
prerequisites: "初中代数与 Python 基础语法"
estimatedMinutes: 45
experiment: "将平方和的 sigma 记号、循环枚举和闭式公式放在同一份可测试报告中"
title: 符号、函数、求和与 Python：把数学对象变成可运行契约
description: 从函数的定义域、复合与有限求和出发，建立五大专题共享的代码—符号对应关系。
---

# 符号、函数、求和与 Python：把数学对象变成可运行契约

## 问题场景

看到 $\sum_{i=1}^n i^2$ 时，代码该从 0 还是 1 开始？`range(1, n + 1)` 与 `range(n)` 为什么不同？很多算法错误不是公式不会，而是数学区间、数组索引与函数输入约束没有对齐。

## 学习目标

完成本课后，你能说明函数的定义域与值域；把复合 $g\circ f$ 和半开区间写成 Python；将有限求和翻译为循环；并用闭式公式与边界样例审计实现。

## 直觉与严格定义

函数 $f:A\to B$ 对每个 $x\in A$ 指定唯一输出 $f(x)\in B$。代码中的类型、输入检查和异常策略就是定义域的一部分。复合先算 $f$ 再算 $g$：

$$ (g\circ f)(x)=g(f(x)). $$

有限求和

$$\sum_{i=a}^{b-1}t(i)=t(a)+t(a+1)+\cdots+t(b-1)$$

恰好对应 Python 的 `range(a, b)`；它包含起点、不包含终点。空区间 $a=b$ 的和定义为 0，这使得循环和递推的边界统一。

## 分步推导：平方和的两种计算路径

以 $S_n=\sum_{i=1}^{n}i^2$ 为例，闭式是

$$S_n=\frac{n(n+1)(2n+1)}6.$$ 

本课不把这个公式当作神谕：一条路径按定义逐项累加，另一条使用闭式；在小整数上二者相等是代码与符号是否对齐的可检查证据。形式证明可由归纳法完成：验证 $n=0$，再比较 $S_{n+1}=S_n+(n+1)^2$ 与闭式的差。

## 算法实现：把索引约定写成 API

```python
from projects.foundations_lab.summation import (
    finite_sum,
    sum_of_squares_certificate,
    sum_of_squares_report,
)

assert finite_sum(lambda i: i * i, 1, 4) == 14.0  # 1^2 + 2^2 + 3^2
report = sum_of_squares_report(10)
assert report["certificate"]["enumeration_matches_closed_form"]
assert sum_of_squares_certificate(10, report)["valid"]
assert sum_of_squares_report(0)["certificate"]["empty_sum_is_zero"]
```

运行 `python -m unittest projects.foundations_lab.test_summation`。`finite_sum` 明确采用半开区间 `[start, stop)` 并拒绝倒置区间、非有限项；报告把枚举和闭式放在一起。`sum_of_squares_certificate` 会重新运行两条路径并检查 `n=0` 的空和边界，因此篡改枚举和或闭式不能通过。枚举时间为 $O(n)$、额外空间为 $O(1)$，闭式为 $O(1)$；大数组中应先理解这一语义，再使用 NumPy 的向量化归约，而不是把索引错误加速。

## 正确性、边界与常见误区

循环不变量是：处理完索引 `i` 前，`total` 等于 $\sum_{k=a}^{i-1}t(k)$。初始化为空和 0；每轮加入 `t(i)` 后不变量保持；循环结束 `i=b`，得到定义中的总和。

- `range(a, b)` 不包含 `b`；将数学的 $1\ldots n$ 写成代码时常需 `range(1, n+1)`。
- 空和不是错误；它是递归基例和过滤后归约的重要约定。
- 函数的“能调用”不代表定义域正确；NaN、维度不符或倒置区间应有明确契约。

## 练习

1. **基础**：写出 `range(2, 5)` 对应的求和下标与结果 $\sum i$。
2. **推导**：用归纳法证明平方和闭式从 $n$ 到 $n+1$ 的步骤。
3. **编码**：篡改平方和报告中的枚举值或闭式，确认 `sum_of_squares_certificate` 拒绝；再实现 $\sum_{i=0}^{n-1}(2i+1)$ 并用 $n^2$ 验证。
4. **开放**：比较 Python 循环与 NumPy `sum` 的语义、浮点累加顺序和性能边界。

## 练习答案提示

1. `range(2, 5)` 给出 $2,3,4$；先写清半开区间，再做求和，避免把 5 误算进去。
2. 基例代入 $n=0$（或题目约定的起点）；归纳步将 $S_{n+1}$ 写成 $S_n+(n+1)^2$，代入假设后通分化简。
3. 先让证书重算 `[1,n+1)` 与闭式，再用 `range(n)` 枚举 $0$ 到 $n-1$，并覆盖 $n=0$；比较枚举值与 $n*n$，不要只测试一个正整数。
4. 先确认两者处理的轴、空数组和数据类型是否相同；性能比较要包含数组创建成本，数值比较要注意归约顺序可能不同。

## 延伸

[命题逻辑、量词与归纳法](/discrete-math/logic-induction-proofs)给出这里归纳证明的语言；[向量与点积](/linear-algebra/vectors-dot-product)将求和推广到向量；[误差传播](/numerical-computing/error-propagation)说明浮点求和为何还需考虑数值稳定性。
