---
title: Jacobian、Hessian 与自动微分：梯度如何成为可计算的线性代数
description: 从局部线性化推导 Jacobian 与 Hessian，区分前向/反向自动微分，并用有限差分验证梯度实现。
courseLevel: "2–3（推导、算法与机器学习工程）"
prerequisites: "矩阵乘法、导数、链式法则与向量化"
estimatedMinutes: 65
experiment: "实现双变量函数梯度并用中心差分进行梯度检查"
---

# Jacobian、Hessian 与自动微分：梯度如何成为可计算的线性代数

## 学习目标

读完后，你能把标量导数推广为 Jacobian 与 Hessian；从局部线性模型解释 Jacobian-vector product；区分符号求导、数值微分与自动微分；并实现一个梯度检查器来验证优化代码。

## 从一个计算问题开始

标量函数 $f(x)$ 的导数是局部斜率。但模型往往是 $f:\mathbb{R}^n\to\mathbb{R}^m$：输入是一批特征，输出是一批预测。若逐个手写偏导，维度与广播规则很快让实现失控；若用有限差分，参数数百万时成本也不可接受。

线性代数给出语言：局部变化由矩阵乘法描述；自动微分把链式法则组织为可执行的计算图。

## 严格定义：局部线性模型

对可微映射 $f:\mathbb{R}^n\to\mathbb{R}^m$，Jacobian 是 $m\times n$ 矩阵

$$J_f(x)_{ij}=\frac{\partial f_i}{\partial x_j}(x).$$

小扰动 $\Delta x$ 下，

$$f(x+\Delta x)=f(x)+J_f(x)\Delta x+o(\|\Delta x\|).$$

因此 `J @ v` 是沿方向 $v$ 的一阶输出变化（JVP）；`J.T @ w` 是输出权重 $w$ 反传到输入的敏感度（VJP）。若损失 $L:\mathbb{R}^n\to\mathbb{R}$ 是标量，其梯度 $\nabla L$ 是 Jacobian 的转置写法。

Hessian 是标量损失的二阶导数矩阵：

$$H_L(x)_{ij}=\frac{\partial^2L}{\partial x_i\partial x_j}.$$

二阶泰勒模型为 $L(x+\Delta)\approx L(x)+\nabla L^T\Delta+\frac12\Delta^TH\Delta$。正定 Hessian 表示局部碗形，但神经网络常有非凸和奇异 Hessian，不能把牛顿法当作无条件保证。

## 链式法则就是矩阵乘法

若 $h=g\circ f$，则

$$J_h(x)=J_g(f(x))J_f(x).$$

这解释前向模式：把输入方向逐层乘 Jacobian，适合输入维度很小或只要一个 JVP。反向模式从标量损失的种子 $1$ 开始，逐层乘转置 Jacobian，适合输出维度为 $1$、参数很多的训练问题。反向传播不是近似，它在每个原子操作可微时给出机器精度下的链式法则结果。

## 可运行实验：解析梯度与数值检查

令 $L(x,y)=(xy+\sin x)^2$。设 $z=xy+\sin x$，则

$$\frac{\partial L}{\partial x}=2z(y+\cos x),\qquad\frac{\partial L}{\partial y}=2zx.$$

```python
from projects.linear_algebra_lab.forward_autodiff import demo_jvp_certificate
from projects.linear_algebra_lab.gradient_check import demo_loss, demo_loss_gradient, gradient_check

point = [0.4, -1.2]
direction = [0.3, -0.4]

# 前向模式在一次计算图遍历中给出 JVP；它应等于 grad(L)^T v。
assert demo_jvp_certificate(point, direction)["matches"]

# 中心差分只作为独立的、小规模梯度检查。
report = gradient_check(demo_loss, demo_loss_gradient, point)
assert all(item.absolute_error < 1e-6 for item in report)
```

`Dual(value, tangent)` 将一个数与沿指定方向的导数一起传播；加法与乘法分别执行链式法则和乘积法则。`demo_jvp_certificate` 将前向模式的结果与解析梯度点积比较，直接验证 $Jv=\nabla L^Tv$（标量损失时）。报告逐坐标记录解析值、数值值、绝对误差和尺度相关相对误差；测试还故意把第一个解析导数取反，确认只有该坐标的检查失败。中心差分用于**测试**而非训练：计算 $n$ 维梯度需约 $2n$ 次前向调用，步长还会遭受截断/舍入权衡。应只在小网络、小批量和固定随机种子下抽样检查若干参数。

## 算法与复杂度

完整 Jacobian 有 $mn$ 个元素，显式构造常常浪费。前向模式一次 JVP 的成本通常与一次前向计算同阶；反向模式一次 VJP 同样如此。训练标量损失时反向模式可在约常数倍前向成本内获得所有参数梯度，但需保存或重算中间值，形成时间—内存取舍。

二阶方法通常不显式形成 $n\times n$ Hessian；Hessian-vector product 可由两次自动微分得到，用于共轭梯度、曲率诊断或信赖域方法。

## 失败案例与工程边界

- **不可微操作**：`abs(0)`、`max` 的并列最大值、离散索引没有唯一普通导数；框架会选择子梯度或报错，必须理解定义。
- **原地修改与别名**：反向传播需要前向中间值；错误的原地写入会让梯度使用被覆盖的值。
- **随机性与状态**：dropout、随机采样、批归一化状态会让有限差分两侧不一致；梯度检查要固定随机源和状态。
- **数值溢出**：即使链式法则正确，`exp`、除零或极端尺度仍可产生 NaN；使用稳定损失和梯度裁剪。

## 常见误区

1. “自动微分就是数值微分。”错误：自动微分按链式法则算导数，不依赖小步长。
2. “反向传播直接算 Hessian。”错误：常规反传给的是标量损失的梯度；二阶信息要额外计算。
3. “梯度检查通过就没有 bug。”错误：它只能覆盖采样点，且错误可能被相互抵消。
4. “向量化只是更快的循环。”不止如此：它对应 Jacobian 的批量线性操作，并影响内存布局和数值归约顺序。

## 练习

1. **基础题**：写出 $f(x,y)=(x+y,xy)$ 的 Jacobian，并计算它在 $(2,3)$ 处乘方向 $(1,-1)$ 的结果。
2. **推导题**：从 $h=g\circ f$ 的分量链式法则推导 $J_h=J_gJ_f$。
3. **编码题**：给 `central_gradient` 加入相对误差检查；故意把 `analytic_gradient` 的一个符号写错，验证测试能捕获它。
4. **开放题**：比较前向模式和反向模式在“输入 3 维、输出 10 万维”与“输入 1 亿维、输出标量”两个问题上的选择。

## 练习答案提示

1. Jacobian 的第一行是 $(1,1)$、第二行是 $(y,x)$；在 $(2,3)$ 处乘 $(1,-1)$，逐行点积得到 JVP。
2. 先写分量形式 $\partial h_i/\partial x_j=\sum_k(\partial g_i/\partial f_k)(\partial f_k/\partial x_j)$，再识别矩阵乘法的行列指标顺序。
3. 相对误差分母需防止接近零，可与绝对误差联合；固定输入和步长后只翻转一个解析分量，断言该坐标失败而其余坐标仍通过。
4. 前向模式的成本随输入方向数增长，反向模式随输出方向数增长；因此前者适合少输入多输出，后者适合标量损失对大量参数求梯度。

## 延伸

可将 Jacobian 的局部线性模型与[数值微分](/numerical-computing/numerical-differentiation)的误差边界对照。继续学习 Gauss–Newton、Hessian-vector product 和计算图内存检查点；在工程实现中优先使用成熟自动微分框架，而不是手工维护大模型梯度。
