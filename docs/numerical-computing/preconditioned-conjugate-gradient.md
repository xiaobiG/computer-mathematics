---
title: 预条件共轭梯度法：为什么缩放能让迭代更快
description: 从 SPD 二次型与共轭方向推导对角预条件 CG，重放每一步残差并识别非正定、停止与条件数边界。
courseLevel: "2–3（数值线性代数与工程）"
prerequisites: "矩阵乘法、内积、残差、迭代线性方程组与条件数"
estimatedMinutes: 65
experiment: "重放对角预条件共轭梯度轨迹，并拒绝被篡改的搜索步"
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

这里 $M$ 是预条件器。Jacobi 取 $M=\operatorname{diag}(A)$，故只需逐分量除以对角元。再令

$$\beta_k=\frac{r_{k+1}^Tz_{k+1}}{r_k^Tz_k},\qquad p_{k+1}=z_{k+1}+\beta_kp_k,$$

便使新方向保持 $A$-共轭。SPD 前提保证 $p_k^TAp_k>0$；若实现发现非正曲率，不能把它当作“正常收敛”。

## 可运行实验：重放 Krylov 轨迹

```python
from projects.floating_point_museum.preconditioned_cg import (
    pcg_trace_certificate, preconditioned_conjugate_gradient,
)

A = [[4.0, 1.0], [1.0, 3.0]]
b = [1.0, 2.0]
solution, trace = preconditioned_conjugate_gradient(A, b)
assert abs(solution[0] - 1 / 11) < 1e-10
assert abs(solution[1] - 7 / 11) < 1e-10
assert pcg_trace_certificate(A, b, solution, trace)["valid"]
```

运行 `python -m unittest projects.floating_point_museum.test_preconditioned_cg`。轨迹记录 $\alpha$、$\beta$、近似解、残差范数和 $r^Tz$；证书从输入重新执行迭代，故可拒绝伪造的步长或“看似很小”的残差。稠密矩阵每轮为 $O(n^2)$，稀疏实现则主要为一次矩阵—向量乘，接近 $O(\operatorname{nnz}(A))$。

## 正确性、停止与工程边界

每步精确最小化当前 Krylov 子空间中的二次能量；在精确算术中，$n$ 维 SPD 系统至多 $n$ 步结束。浮点中正交性会损失，所以实践以残差阈值、最大迭代数和问题尺度共同决定停止。小残差仍须结合条件数解释前向误差；预条件器改善的是谱分布与迭代速度，不会自动修复原问题病态或错误建模。

Jacobi 预条件器最便宜，却无法处理零/负对角，也未必显著聚集特征值。真实大规模求解应评估不完全 Cholesky、多重网格或领域专用预条件器，并采用成熟稀疏库。

## 失败案例与常见误区

- **非对称矩阵**：CG 的共轭推导失效，教学实现会拒绝它；改用 GMRES、BiCGSTAB 等合适方法。
- **非正定曲率**：$p^TAp\le0$ 表示 SPD 前提不能在当前方向成立，不能继续除法。
- **把 $M^{-1}$ 显式求出来**：预条件应通过廉价“解 $Mz=r$”应用，通常不构造逆矩阵。
- **“两步收敛”可泛化**：小例维度低且精确；浮点、谱簇和容差会改变真实步数。

## 练习

1. **基础题**：对 $A=\operatorname{diag}(4,9)$ 写出 Jacobi 预条件后的 $z$ 与残差关系。
2. **推导题**：沿 $x+\alpha p$ 对 $q$ 求导，推出 $\alpha$ 的分子和分母。
3. **编码题**：篡改一条 `CgEvent.alpha`，确认 `pcg_trace_certificate` 拒绝它；再测试非对称输入。
4. **开放题**：为一个稀疏 PDE 系统比较无预条件、Jacobi 与多重网格的报告指标，并说明为何不能只比较迭代次数。

## 练习答案提示

1. 对角预条件逐项为 $z_i=r_i/a_{ii}$；它按坐标尺度重标残差。
2. 令 $p^T(A(x+\alpha p)-b)=0$，再用 $r=b-Ax$ 整理即可。
3. 证书会完整重算事件；非对称检查是 CG 前提，而不是性能优化。
4. 同时报时间、矩阵—向量次数、预条件成本、残差、前向误差估计与内存；不同硬件下“轮数少”未必更快。

## 延伸

[迭代解线性方程组](/numerical-computing/iterative-linear-systems)给出驻定迭代与残差证据；[条件数](/numerical-computing/condition-number)解释残差与解误差为何不同；[最小二乘](/linear-algebra/least-squares)展示正规方程为何可能放大条件数。下一步可研究 Krylov 子空间、Lanczos 与不完全分解。
