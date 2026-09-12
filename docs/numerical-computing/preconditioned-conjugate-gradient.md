---
title: 预条件共轭梯度法：为什么缩放能让迭代更快
description: 从 SPD 二次型与共轭方向推导对角预条件 CG，重放每一步残差并识别非正定、停止与条件数边界。
courseLevel: "2–3（数值线性代数与工程）"
prerequisites: "矩阵乘法、内积、残差、迭代线性方程组与条件数"
estimatedMinutes: 80
experiment: "在同一 SPD 系统比较无预条件与 Jacobi CG 的轨迹、残差和步数"
---

# 预条件共轭梯度法：为什么缩放能让迭代更快

## 学习目标

读完后，你能说明 CG 只适用于对称正定（SPD）系统；从残差和 $A$-共轭方向写出一步更新；解释 Jacobi 对角预条件改变的是什么；并用可重放轨迹审计残差、曲率与停止条件。

## 从“残差在降，为什么还很慢”开始

稀疏 SPD 系统常来自网格、最小二乘正规方程或平滑问题。Jacobi 虽然只需逐行更新，但病态或尺度不均时可能需要很多轮。CG 不逐坐标修正，而是在一组不重复破坏彼此进展的方向上最小化二次能量；预条件器再把尺度差异先缩小。

## 定义与推导

对对称正定 $A$，解 $Ax=b$ 等价于最小化

$$q(x)=\tfrac12x^TAx-b^Tx,$$

因为 $\nabla q(x)=Ax-b=-r$，其中 $r=b-Ax$ 是残差。给定搜索方向 $p_k$，令 $x_{k+1}=x_k+\alpha_kp_k$。令该直线方向导数为零，得到

$$\alpha_k=\frac{r_k^Tz_k}{p_k^TAp_k},\qquad z_k=M^{-1}r_k.$$

这里 $M$ 是预条件器。Jacobi 取 $M=\mathrm{diag}(A)$，故只需逐分量除以对角元。再令

$$\beta_k=\frac{r_{k+1}^Tz_{k+1}}{r_k^Tz_k},\qquad p_{k+1}=z_{k+1}+\beta_kp_k,$$

便使新方向保持 $A$-共轭。SPD 前提保证 $p_k^TAp_k>0$；若实现发现非正曲率，不能把它当作“正常收敛”。

## 同一问题的两种尺度：为什么 Jacobi 有时少走很多步

“Jacobi 更快”不是无条件事实，必须固定矩阵、右端、残差阈值和每步成本后再比较。考虑

$$A=\mathrm{diag}(1,100,10000),\qquad b=(1,1,1)^T.$$

它是 SPD，但三个坐标的尺度相差四个数量级。无预条件时，初始方向就是 $r_0=b$；CG 需要分别消化三个不同特征值，在精确算术中最多三步。Jacobi 取 $M=\mathrm{diag}(A)=A$，于是预条件后的算子 $M^{-1}A=I$，所有方向拥有同一特征值；从 $x_0=0$ 出发，第一步就得到

$$z_0=M^{-1}r_0=(1,0.01,0.0001)^T,\qquad \alpha_0=1,\qquad x_1=z_0=A^{-1}b.$$

这不是“Jacobi 总能把条件数变成 1”：它只在矩阵恰好对角时完全消去尺度差；有较大非对角耦合时仍需看谱分布、预条件应用成本和实际残差。

## 可运行实验：在同一输入比较轨迹

```python
from projects.floating_point_museum.preconditioned_cg import (
    pcg_trace_certificate, preconditioned_conjugate_gradient,
)

A = [[1.0, 0.0, 0.0], [0.0, 100.0, 0.0], [0.0, 0.0, 10_000.0]]
b = [1.0, 1.0, 1.0]
plain_solution, plain_trace = preconditioned_conjugate_gradient(A, b, preconditioner="identity")
jacobi_solution, jacobi_trace = preconditioned_conjugate_gradient(A, b, preconditioner="jacobi")

assert len(plain_trace) == 3
assert len(jacobi_trace) == 1
assert all(abs(left - right) < 1e-10 for left, right in zip(plain_solution, jacobi_solution))
assert pcg_trace_certificate(A, b, jacobi_solution, jacobi_trace, preconditioner="jacobi")["valid"]
```

运行 `python -m unittest projects.floating_point_museum.test_preconditioned_cg`。`preconditioner="identity"` 公开了普通 CG 基线，`"jacobi"` 只做对角缩放；两条轨迹均记录 $\alpha$、$\beta$、近似解、残差范数和 $r^Tz$，证书必须以相同预条件选择重放，否则比较没有意义。它能拒绝伪造的步长或“看似很小”的残差。稠密矩阵每轮为 $O(n^2)$，稀疏实现则主要为一次矩阵—向量乘，接近 $O(\mathrm{nnz}(A))$；Jacobi 还需 $O(n)$ 次逐对角元除法，真实选择应比较总耗时而不是只看迭代数。

## 正确性、停止与工程边界

每步精确最小化当前 Krylov 子空间中的二次能量；在精确算术中，$n$ 维 SPD 系统至多 $n$ 步结束。浮点中正交性会损失，所以实践以残差阈值、最大迭代数和问题尺度共同决定停止。小残差仍须结合条件数解释前向误差；预条件器改善的是谱分布与迭代速度，不会自动修复原问题病态或错误建模。

Jacobi 预条件器最便宜，却无法处理零/负对角，也未必显著聚集特征值。只有当较少迭代节省的矩阵—向量乘成本超过预条件应用和构造成本时，“更少步”才可能成为“更快”。真实大规模求解应评估不完全 Cholesky、多重网格或领域专用预条件器，并采用成熟稀疏库。

## 失败案例与常见误区

- **非对称矩阵**：CG 的共轭推导失效，教学实现会拒绝它；改用 GMRES、BiCGSTAB 等合适方法。
- **非正定曲率**：$p^TAp\le0$ 表示 SPD 前提不能在当前方向成立，不能继续除法。
- **把 $M^{-1}$ 显式求出来**：预条件应通过廉价“解 $Mz=r$”应用，通常不构造逆矩阵。
- **“两步收敛”可泛化**：小例维度低且精确；浮点、谱簇和容差会改变真实步数。

## 练习

1. **基础题**：对 $A=\mathrm{diag}(4,9)$ 和 $b=(4,18)^T$ 写出 Jacobi 预条件后的 $z_0$、$\alpha_0$ 与 $x_1$；解释为何它一步得到精确解。
2. **推导题**：沿 $x+\alpha p$ 对 $q$ 求导，推出 $\alpha$ 的分子和分母；指出此处哪一步需要 $p^TAp>0$。
3. **比较题**：将示例矩阵的中间对角元从 100 改为 10，预测两种方法的精确步数是否改变，并解释“谱不同但仍有三个不同特征值”与停止阈值的关系。
4. **编码题**：篡改一条 `CgEvent.alpha`，确认以相同 `preconditioner` 的 `pcg_trace_certificate` 拒绝它；再测试非对称输入和未知预条件名称。
5. **开放题**：为一个稀疏 PDE 系统比较无预条件、Jacobi 与多重网格的报告指标，并说明为何不能只比较迭代次数。

## 练习答案提示

1. $z_0=(1,2)^T=A^{-1}b$；此时 $p_0=z_0$、$\alpha_0=1$，故 $x_1=A^{-1}b$。这是对角矩阵的特殊情形。
2. 令 $p^T(A(x+\alpha p)-b)=0$，再用 $r=b-Ax$ 整理即可；分母为零或负时不能得到最小化步长。
3. 两种对角矩阵都有三个不同特征值，精确算术下普通 CG 仍至多需三步，而 Jacobi 仍使预条件算子为单位阵、一步结束；有限精度/阈值下实际计数仍可能不同。
4. 证书会以指定的预条件选择完整重算事件；非对称检查和未知名称拒绝是输入/CG 前提，不是性能优化。
5. 同时报时间、矩阵—向量次数、预条件成本、残差、前向误差估计与内存；不同硬件下“轮数少”未必更快。

## 延伸

[迭代解线性方程组](/numerical-computing/iterative-linear-systems)给出驻定迭代与残差证据；[条件数](/numerical-computing/condition-number)解释残差与解误差为何不同；[最小二乘](/linear-algebra/least-squares)展示正规方程为何可能放大条件数。下一步可研究 Krylov 子空间、Lanczos 与不完全分解。
