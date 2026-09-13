---
title: 张量形状与批处理：为什么 (3,) 不等于 (3, 1)
description: 用标量、向量、矩阵和行批次的可运行合同，解释形状、矩阵乘法与批量线性层的接口。
courseLevel: "0–1（数组契约与线性代数前置）"
prerequisites: "集合与数组形状、函数与 Python"
estimatedMinutes: 60
experiment: "重放逐元素向量加法与行批次线性层的形状和值"
---

# 张量形状与批处理：为什么 `(3,)` 不等于 `(3, 1)`

## 学习目标

你将能从具体值读出标量、向量、矩阵和批次的形状；区分一维向量 `(n,)` 与列矩阵 `(n,1)`；按行批次约定推导线性层 `X @ W + b` 的输入输出形状；并用可重放报告拒绝不兼容的维度。

## 直觉与严格定义：从“能跑”到“接口正确”

同样包含 3 个数字的 `[2,5,7]` 与 `[[2],[5],[7]]` 并不是同一个对象。前者有一个轴，形状为 `(3,)`；后者有两个轴，形状为 `(3,1)`。它们可能在某些数组库的广播规则下得到结果，但这不等于它们表达相同的数学对象。

本课程采用一个明确约定：样本按行堆叠。若一个批次有 $b$ 个样本、每个样本 $d$ 个特征，则 $X\in\mathbb R^{b\times d}$；线性层的权重 $W\in\mathbb R^{d\times o}$，偏置 $b\in\mathbb R^o$。为避免与批次数冲突，下面将偏置写作 $c$：

$$Y=XW+c,\qquad (b,d)@(d,o)+(o,)\longrightarrow(b,o).$$

右侧偏置并非“忽略形状”：它沿样本轴复制到每一行。这里把广播范围写进接口，不能把任意形状不匹配都归因于广播。

## 浏览器实验：追踪每一条轴

<TensorShapeExplorer />

切换三个操作并阅读每张输入卡上的形状。逐元素加法要求两个一维向量的形状完全相同；矩阵乘法要求左侧末轴与右侧倒数第二轴相同；批量线性层则保留批次数并把特征轴换成输出轴。

## 可运行实验：两种合同

```python
from projects.foundations_lab.tensor_shapes import (
    batch_linear_report,
    elementwise_add_report,
    square_batch_transpose_counterexample_report,
    tensor_shape,
    tensor_shapes_certificate,
)

assert tensor_shape(2.5) == []
assert tensor_shape([2, 5, 7]) == [3]
assert tensor_shape([[2], [5], [7]]) == [3, 1]

added = elementwise_add_report([2, 5, 7], [1, 1, 1])
assert added["output"] == {"values": [3, 6, 8], "shape": [3]}

inputs = {
    "batch": [[1, 2, 3], [4, 5, 6]],
    "weights": [[1, 0], [0, 1], [1, 1]],
    "bias": [10, 20],
}
report = batch_linear_report(**inputs)
assert report["output"]["shape"] == [2, 2]
assert report["output"]["values"] == [[14, 25], [20, 31]]
assert tensor_shapes_certificate("batch_linear", inputs, report)
```

运行：

```bash
python -m unittest projects.foundations_lab.test_tensor_shapes
```

教学合同只接受有限数字、非空一维向量和非空矩形二维矩阵。它拒绝锯齿行、逐元素加法的不同长度、`X` 与 `W` 的内层不相等，以及偏置宽度不等于输出宽度。证书每次重算数值和形状；篡改输出为 `[3,1]` 即使值仍是 `[3,6,8]` 也会失败。

## 形状仍相同的反例：方阵转置会交换轴的含义

仅检查形状还不够。若批次刚好是方阵，`X` 与 $X^\mathsf T$ 都是 `(2,2)`；后者甚至仍能和 `(2,2)` 权重相乘。此时“没有报错”不能说明样本轴仍是样本轴。

设两行分别是 Alice 和 Bob 的两个特征，取恒等权重和零偏置：

$$
X=\begin{bmatrix}1&2\\3&4\end{bmatrix},\qquad
X^\mathsf T=\begin{bmatrix}1&3\\2&4\end{bmatrix}.
$$

两种计算的输出形状都是 `(2,2)`，但前者的两行仍对应 `alice, bob`，后者的两行已经对应 `feature_0, feature_1`：每一行把原先来自不同样本的同一特征拼在了一起。数学上转置完全合法；错误发生在把它仍标成“样本批次”这一接口声明。

```python
counterexample_inputs = {
    "batch": [[1, 2], [3, 4]],
    "weights": [[1, 0], [0, 1]],
    "bias": [0, 0],
    "sample_labels": ["alice", "bob"],
}
counterexample = square_batch_transpose_counterexample_report(**counterexample_inputs)
assert counterexample["same_numeric_shape"]
assert counterexample["axis_semantics_changed"]
assert counterexample["normal"]["row_labels"] == ["alice", "bob"]
assert counterexample["transposed"]["row_labels"] == ["feature_0", "feature_1"]
assert tensor_shapes_certificate("square_batch_transpose_counterexample", counterexample_inputs, counterexample)
```

反例只接受方阵，因为只有在那里形状检查无法暴露转置；它强制每个原样本行有唯一标签，并把转置后的行标为特征。证书重放两个矩阵乘法、标签和轴角色，因而把转置结果伪称为 `["sample", "feature"]` 会失败。

## 推导：每个轴去哪了

对矩阵乘法，$X$ 的第 $i$ 行是第 $i$ 个样本，$W$ 的第 $j$ 列通向第 $j$ 个输出。输出元素是

$$Y_{ij}=\sum_{k=0}^{d-1}X_{ik}W_{kj}+c_j.$$

索引 $k$ 同时出现于两个输入，因求和被消去；$i$ 只来自 $X$，所以保留为样本轴；$j$ 只来自 $W$，所以保留为输出轴。这正给出 `(b,d) @ (d,o) -> (b,o)`。若 $d$ 不相同，连第 $k$ 项的配对都无法定义，不是“结果很差”，而是算式无定义。

逐元素加法没有求和轴：`[a_i] + [q_i] = [a_i + q_i]`，故两个长度都必须为 $n$，输出仍是 `(n,)`。`(3,)` 和 `(3,1)` 的轴数已经不同，不能把前者的单一索引直接当作后者的 `(行,列)` 索引。

## 正确性与复杂度

`tensor_shape` 先识别标量、再识别一维列表、最后验证所有矩阵行同宽；接受的二维对象因而有唯一的 `(行,列)` 形状。逐元素报告逐位置相加，长度合同使每一项都有唯一配对。批量报告直接按上述三重索引和计算，所以输出的第 `(i,j)` 项与定义相同；证书独立重建报告，绑定输入值、形状、约定和输出。

对 $X\in\mathbb R^{b\times d}$、$W\in\mathbb R^{d\times o}$，朴素计算为 $O(bdo)$ 时间，输出占 $O(bo)$ 空间。实际库会使用分块、SIMD 或 GPU；这些优化不改变轴的代数含义。

## 失败案例与工程边界

- **把列向量当一维向量。** `(3,1)` 不是 `(3,)`；先写清调用方需要的维数，再决定 `reshape` 或转置是否有数学理由。
- **只靠报错后转置。** `X.T @ W` 可能临时让内层相等，却会把样本轴变成特征轴；先标注每个轴的语义。
- **方阵让错误隐形。** 当批次数恰好等于特征数时，`X` 和 `X.T` 的形状相同；必须借助样本标签和轴角色判断转置是否仍符合接口。
- **把广播当修复工具。** 偏置 `(o,)` 在此约定中只沿批次轴扩展。更复杂的广播必须逐轴说明，不能默默接受。
- **把本合同当张量库。** 本页只到二维矩阵与行批次；dtype、步幅、自动微分、三维图像张量与生产性能属于后续主题。

## 常见误区

- **“形状相同就语义相同。”** 不一定。两个 `(2,3)` 可能一个是 2 个样本×3 特征，另一个是 2 行×3 列图像块；语义仍应随接口记录。
- **“偏置必须写成 `(1,o)`。”** 不必。本课程用 `(o,)`，并明确它只沿批次轴复制；不同框架可采用别的约定。
- **“标量形状是 `(1,)`。”** 不对；本合同将单个数记为零维 `()`，一元素向量才是 `(1,)`。
- **“矩阵乘法逐格相乘。”** 不对；`@` 消去内层轴。逐元素乘法通常是另一种操作。

## 练习

1. 若 `X` 的形状为 `(8, 4)`、`W` 为 `(4, 3)`、`c` 为 `(3,)`，写出 `X @ W + c` 的形状，并解释每条轴来源。
2. 比较 `(4,)`、`(4,1)`、`(1,4)` 的轴数、合法坐标和矩阵乘法角色。
3. 给出一组 `X:(2,3)` 和 `W:(4,2)`，说明为什么本合同拒绝它，而不是计算一个近似结果；再解释为何 `X:(2,2)` 的转置不能仅凭形状判断为安全。
4. 将一批 `b` 个 28×28 灰度图扁平为特征行，写出展平前后形状；说明此操作会丢失什么空间邻接语义。

## 练习答案提示

1. 输出为 `(8,3)`：8 保留样本，4 是被求和的特征轴，3 来自权重输出轴；偏置沿 8 行扩展。
2. 一维向量只有索引 `i`；列矩阵用 `(i,0)`；行矩阵用 `(0,j)`。后两者可参与矩阵乘法的位置不同。
3. 左末轴为 3、右倒数第二轴为 4；没有同一个求和索引集合，故 $XW$ 未定义。若都是 2，`X.T` 的乘法虽有定义，但行已经从样本变为特征，仍需检查轴角色。
4. 形状从 `(b,28,28)` 到 `(b,784)`；像素仍在，但二维邻接关系不再由形状表达。

## 延伸

[集合与数组形状](/foundations/sets-array-shapes)建立成员、坐标与矩形的最小合同；[矩阵乘法](/linear-algebra/matrix-multiplication)从线性变换进一步推导内层维度；[Jacobian、Hessian 与自动微分](/linear-algebra/jacobian-hessian-autodiff)会将这些形状推广到导数和反向传播。
