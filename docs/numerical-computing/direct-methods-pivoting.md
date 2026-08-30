---
title: 直接法与选主元：残差、前向误差和算法稳定性
description: 以二阶高斯消元对比不选主元与部分选主元，区分算法造成的误差与病态问题造成的敏感性。
courseLevel: "2–3（数值线性代数与误差分析）"
prerequisites: "线性方程组、高斯消元、浮点数、条件数"
estimatedMinutes: 60
experiment: "重放不选主元和部分选主元的消元轨迹，比较残差、后向误差和前向误差"
---

# 直接法与选主元：残差、前向误差和算法稳定性

## 学习目标

读完后，你能推导高斯消元的前消元与回代步骤；说明部分选主元为何避开过小除数；在同一系统中比较不选主元和选主元的轨迹、残差与前向误差；并区分“算法不稳定”与“问题病态”这两种不同风险。

## 从一个计算问题开始

求解

$$
\begin{bmatrix}10^{-20}&1\\1&1\end{bmatrix}
\begin{bmatrix}x_1\\x_2\end{bmatrix}
=\begin{bmatrix}1\\2\end{bmatrix}.
$$

数学上解约为 $(1,1)$。若第一步直接用 $10^{-20}$ 作除数，消元因子约为 $10^{20}$；随后“2 减去 $10^{20}$”会在有限精度中丢失决定 $x_1$ 的有效数字。若先交换两行，以 1 为主元，计算就不会把微小数放到分母。

这不是“交换行让问题条件数变小”：行交换只改变算法的计算路径，原方程是否接近奇异仍由问题本身决定。

## 直觉与定义：从方程到消元算法

对第 $k$ 列选主元 $a_{pk}$，将该行交换到第 $k$ 行。对每一行 $i>k$，令

$$m_{ik}=\frac{a_{ik}}{a_{kk}},\qquad R_i\leftarrow R_i-m_{ik}R_k.$$

交换与“用一行减去另一行的倍数”在精确算术中不改变解集；完成后得到上三角系统 $Ux=c$，再自下而上回代：

$$x_i=\frac{c_i-\sum_{j=i+1}^n u_{ij}x_j}{u_{ii}}.$$

**部分选主元**在当前列尚未使用的行中选择绝对值最大的元素。它不能保证所有矩阵都绝对稳定，却是稠密消元中重要且低成本的默认防线；生产求解仍应使用经过审计的库和适合矩阵结构的分解。

## 可运行实验：两条轨迹

```python
from projects.floating_point_museum.direct_methods import (
    direct_method_comparison,
    direct_method_comparison_certificate,
)

matrix = [[1e-20, 1.0], [1.0, 1.0]]
right_side = [1.0, 2.0]
report = direct_method_comparison(matrix, right_side, [1.0, 1.0])

print(report["without_pivoting"]["relative_forward_error"])
print(report["partial_pivoting"]["relative_forward_error"])
assert report["certificate"]["partial_pivoting_used_a_swap"]
assert direct_method_comparison_certificate(matrix, right_side, [1.0, 1.0], report)
```

运行：

```bash
python -m unittest projects.floating_point_museum.test_direct_methods
```

实验记录每一步的主元行、是否交换、消元因子及增广矩阵。证书从原方程独立重放两种轨迹，因而篡改任一主元、因子、解、残差或结论都会失败。这里的 `reference_solution` 是教学用已知答案，专门让我们看见前向误差；真实业务通常没有真解，只能报告残差、后向误差与条件估计。

对这个例子，不选主元可得到很大的前向误差，且连原系统残差都可能不小；部分选主元同时得到小的后向误差与小的前向误差。这说明的是**算法路径**的差异。

## 残差、后向误差与前向误差

残差为 $r=b-A\hat x$。尺度化后向误差可写成

$$
\eta(\hat x)=\frac{\lVert r\rVert_\infty}
{\lVert A\rVert_\infty\lVert\hat x\rVert_\infty+\lVert b\rVert_\infty}.
$$

它问“$\hat x$ 是否精确解了一个很接近的方程”。若教学中知道真解 $x$，还可测前向误差

$$\frac{\lVert\hat x-x\rVert_\infty}{\lVert x\rVert_\infty}.$$

两者回答不同问题：本课的微小主元案例说明不稳定算法可能连后向误差都做不好；[条件数](/numerical-computing/condition-number)中的近奇异案例则说明即使后向误差小，原问题也可使前向误差很大。稳定算法不是条件数的替代品。

## 复杂度与工程边界

稠密 $n\times n$ 消元约为 $O(n^3)$ 时间、$O(n^2)$ 存储；交换主元行相对这一成本很小。稀疏矩阵中，消元会造成填充，主元策略还要考虑稀疏结构；对对称正定系统常使用 Cholesky 或[预条件共轭梯度](/numerical-computing/preconditioned-conjugate-gradient)，而不是把所有问题都塞进一般消元。

这个模块只处理 $2\times2$ 有限数矩阵，用于把每个浮点步骤完整展示。它拒绝零主元、错误形状和零范数参考解；不应将它当作生产求解器或把某次小残差理解为可靠性证明。

## 常见误区

- **“选主元修复病态。”** 错。它降低算法额外误差，不改变问题对输入扰动的敏感性。
- **“残差小就代表解接近真解。”** 错。病态问题可同时有小后向误差和大前向误差。
- **“任何交换行都一样。”** 错。部分选主元有明确规则：在当前列选择最大的可用绝对值。
- **“显式求逆再乘右端更通用。”** 错。它通常更慢、误差路径更长；应直接做分解和回代。

## 练习

1. **基础题**：手算例子不交换时第一步的消元因子，以及交换后第一步的因子。
2. **推导题**：说明行交换和 $R_i\leftarrow R_i-mR_k$ 为什么在精确算术中保持解集。
3. **编码题**：修改报告，额外记录每步主元绝对值与最大消元因子；为篡改一个因子的情况补测试。
4. **开放题**：在一个近奇异系统中同时运行部分选主元和条件数报告，设计一份不夸大可靠性的输出格式。

## 练习答案提示

1. 不交换时为 $1/10^{-20}=10^{20}$；交换后为 $10^{-20}$。比较的是数值放大，不是方程的解集。
2. 两操作对应可逆初等矩阵左乘；或直接验证每个满足旧方程的向量也满足新方程，反之亦然。
3. 保持报告的重放性：记录必须由增广矩阵重算，证书不能只比较最终解。
4. 同时报主元轨迹、尺度化残差、条件估计、输入不确定性和“前向误差未知/受条件数限制”的说明；不因一次残差小就宣布准确。

## 延伸

[线性代数中的高斯消元](/linear-algebra/gaussian-elimination)从代数角度建立行变换；[LU 分解与主元选择](/linear-algebra/lu-factorization-pivoting)将消元组织成分解；[条件数](/numerical-computing/condition-number)继续解释为什么稳定算法仍会遇到不可靠的病态问题。
