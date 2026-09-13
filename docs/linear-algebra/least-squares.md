---
courseLevel: "2–3（推导与工程）"
prerequisites: "投影、转置与线性方程组"
estimatedMinutes: 75
experiment: "自行构造 A、b，诊断精确可达、投影与秩亏路径"
title: 最小二乘：没有精确解怎么办
description: 从正交投影推导正规方程，并理解 QR 与 SVD 的数值边界。
---

# 最小二乘：没有精确解怎么办

## 学习目标

- 将拟合问题写为最小化残差 $\lVert Ax-b\rVert^2$；
- 从正交投影推导正规方程；
- 从任务叙述自行构造 $A,b$，并区分精确可达、投影逼近与秩亏/欠定模型；
- 知道何时不应直接求解 $A^TAx=A^Tb$。

## 从一个计算问题开始

测得点 $(0,1),(1,2),(2,2)$ 不在同一直线上。程序不该要求一条恰好经过所有点的直线，而应寻找总体误差最小的直线。

## 定义与推导

令 $A$ 的列为可用特征方向，$A\hat x$ 是对 $b$ 的近似。最优残差 $r=b-A\hat x$ 必与每个列方向正交：

$$A^T(b-A\hat x)=0\quad\Longrightarrow\quad A^TA\hat x=A^Tb.$$

这不是“先求逆”的许可，而是投影的代数描述。若 $A$ 列满秩，理论解为 $(A^TA)^{-1}A^Tb$；实现中通常解方程，而不显式求逆。

把目标函数写成

$$
F(x)=\frac12\lVert Ax-b\rVert_2^2.
$$

沿任意方向 $h$ 扰动一小步 $t$，展开二次项的一次部分：

$$
F(x+th)=F(x)+t\,h^\mathsf T A^\mathsf T(Ax-b)+O(t^2).
$$

极小点不能沿任何 $h$ 再下降，所以 $A^\mathsf T(A\hat x-b)=0$。使用 $r=b-A\hat x$ 就得到 $A^\mathsf Tr=0$：残差与列空间正交，$A\hat x$ 正是 $b$ 在列空间上的投影。

## 手算一个完整例子

拟合 $y=ax+c$ 时，令 $A=\begin{bmatrix}0&1\\1&1\\2&1\end{bmatrix}$、$b=(1,2,2)^T$。先计算 $A^TA=\begin{bmatrix}5&3\\3&3\end{bmatrix}$ 与 $A^Tb=(6,5)^T$，再解二元系统即可得到最小二乘直线。残差不必为零，但它与 $A$ 的两列都正交。

解为 $\hat x=(a,c)^T=(1/2,7/6)^T$，预测值为 $(7/6,5/3,13/6)^T$，因而

$$
r=b-A\hat x=(-1/6,\;1/3,\;-1/6)^T.
$$

直接检查两条正交条件：$[0,1,2]r=0$ 与 $[1,1,1]r=0$。这比只看到“残差长度变小”更强：它验证了所有可用线性特征方向上都没有一阶改进空间。

## QR 路径为何避免正规方程

对列满秩矩阵作薄 QR 分解 $A=QR$，其中 $Q^\mathsf TQ=I$，$R$ 为可逆上三角矩阵。将 $b$ 分成列空间投影和正交余量：

$$
b=QQ^\mathsf Tb+(I-QQ^\mathsf T)b.
$$

两项正交，因此

$$
\lVert QRx-b\rVert_2^2
=\lVert Rx-Q^\mathsf Tb\rVert_2^2
+\lVert(I-QQ^\mathsf T)b\rVert_2^2.
$$

第二项不依赖 $x$，所以只需回代 $R\hat x=Q^\mathsf Tb$；没有必要形成 $A^\mathsf TA$。若 $A$ 的奇异值是 $\sigma_i$，则 $A^\mathsf TA$ 的特征值是 $\sigma_i^2$，所以在 2-范数下

$$
\kappa_2(A^\mathsf TA)=\frac{\sigma_{\max}^2}{\sigma_{\min}^2}=\kappa_2(A)^2.
$$

这就是近似共线时正规方程更脆弱的数学原因，而不仅仅是“库文档建议使用 QR”。

## 把公式实现为代码

实验室提供一条用于对照推导的正规方程路径，以及不显式形成 $A^TA$ 的 QR 路径：

```python
from projects.linear_algebra_lab.main import (
    least_squares_comparison_report,
    least_squares_report_certificate,
)

A = [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]]
report = least_squares_comparison_report(A, [1.0, 2.0, 2.0])

assert report["solution_distance"] < 1e-12
assert max(abs(value) for value in report["normal_normal_equation_residual"]) < 1e-12
assert max(abs(value) for value in report["qr_normal_equation_residual"]) < 1e-12
assert least_squares_report_certificate(A, [1.0, 2.0, 2.0], report)["valid"]
```

两组 `*_normal_equation_residual` 都是 $A^Tr$；证书重算系数、残差范数与驻点条件。正规方程路径只用于核对推导；改进 Gram–Schmidt 的 QR 路径才是本实验的默认选择。项目测试还覆盖秩亏与宽矩阵边界。

构造正规方程或 QR 的密集成本都约为 $O(mn^2)$；随后求解 $n\times n$ 系统为 $O(n^3)$。QR 避免了正规方程将条件数近似平方的额外放大。

## 正确性证据与数值选择

列满秩时凸二次目标只有一个驻点，故 $A^Tr=0$ 即为最小解证据。良态例中两条路径应相同；近共线时的差异是改用 QR/SVD 的信号。

列秩亏时 $A^\mathsf TA$ 不可逆，投影 $A\hat x$ 仍唯一而系数通常不唯一；教学 QR 会拒绝它。SVD 的最小范数解是一条额外规则，不能从正规方程自动得到。

## 构造实验：先从任务写出 $A,b$，再选择验收不变量

前面的示例已经给出设计矩阵；真实任务首先要由你决定每一行是一次观测、每一列是哪一个可调特征、目标向量又代表什么。下面的诊断函数不替你建模，但会把你构造的输入放回列空间语言中：

```python
from projects.linear_algebra_lab.main import diagnose_least_squares_case

# 直线 y = ax + c；三行是 x=0,1,2 的观测，列是斜率和截距。
A = [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]]

exact = diagnose_least_squares_case(A, [1.0, 2.0, 3.0])
projected = diagnose_least_squares_case(A, [1.0, 2.0, 4.0])
rank_deficient = diagnose_least_squares_case(
    [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]], [1.0, 2.0, 4.0],
)

assert exact["fit_path"] == "exact_full_rank_solution"
assert projected["fit_path"] == "qr_projection_for_unreachable_target"
assert rank_deficient["fit_path"] == "rank_revealing_qr_or_svd_required"
```

`exact` 验收 $Ax=b$；只改末次观测后的 `projected` 则保留非零残差并验收 $A^Tr\approx0$。重复列或宽矩阵必须先声明最小范数、稀疏性等规则，不能由 QR 擅自选坐标。

## 反例：QR 能继续计算，不代表系数已经可信

将第二列写成几乎等于第一列的扰动。下面的数据仍然列满秩，精确系数为 $(1,1)$，但区别只有 $10^{-7}$：

```python
from projects.linear_algebra_lab.main import least_squares_normal_equations, least_squares_qr

delta = 1e-7
A = [[1.0, 1.0], [1.0, 1.0 + delta], [1.0, 1.0 - delta]]
b = [2.0, 2.0 + delta, 2.0 - delta]

try:
    least_squares_normal_equations(A, b)
except ValueError:
    print("A^T A 的主元已落入教学容差")

x_qr, r_qr = least_squares_qr(A, b)
print(x_qr)  # 在 binary64 教学实现中约为 [1.0555, 0.9445]
assert max(abs(sum(A[i][j] * r_qr[i] for i in range(3))) for j in range(2)) < 1e-12
```

正规方程在 `1e-12` 容差下先拒绝 $A^TA$；QR 仍给出 $A^Tr\approx0$，但系数已偏离 $(1,1)$。小残差不能恢复可辨识性；生产环境应报告共线与缩放，并交给 pivoted QR/SVD。

## 岭正则化：不是“更稳地解原来的题”，而是换了题目

对 $A=[(1,1),(2,2),(3,3)]^T,b=(1,2,4)^T$，普通最小二乘只能确定系数之和。岭回归改写目标为 $\lVert Ax-b\rVert_2^2+\lambda\lVert x\rVert_2^2$（$\lambda>0$），其条件是 $(A^TA+\lambda I)x=A^Tb$。因此秩亏时也唯一；唯一性来自“偏好小系数”，不是数据辨识了重复特征。

```python
from projects.linear_algebra_lab.main import ridge_regularization_report

A = [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]]
report = ridge_regularization_report(A, [1.0, 2.0, 4.0], regularization=1.0)

assert report["solution"] == [17 / 29, 17 / 29]
assert max(abs(value) for value in report["regularized_gradient"]) < 1e-12
assert min(abs(value) for value in report["data_gradient"]) > 1e-3
```

岭解的原数据梯度不为零，正由 $\lambda x$ 抵消：这是不同目标，不是同一问题的数值修复。`regularization` 是模型选择；生产中使用 QR/SVD 型 ridge 实现。

## 失败案例与工程边界

正规方程会近似平方条件数，近似共线的特征可能使小误差被放大。生产数值代码优先用带选主元的 QR 或 SVD；特征尺度相差很大时先标准化。最小二乘最小化平方误差，对离群点敏感，鲁棒回归是另一种目标。

## 常见误区

- “最小二乘”不保证每个点误差最小，只保证平方和最小。
- 不要显式计算矩阵逆。
- 残差与 $b$ 不必正交，而是与列空间正交。

## 练习

1. **基础**：完成例子中的二元系统并验证两个正交条件。
2. **推导**：由 $A=QR$ 和 $Q^TQ=I$ 推导 $R\hat x=Q^Tb$。
3. **编码**：给 `least_squares_qr` 增加一组带截距的线性拟合测试，并检查 $A^Tr$。
4. **构造**：从“用常数项和时间斜率解释三次温度观测”自行写出 $A,b$；再只改一个观测，使诊断从精确路径转为投影路径。分别写出两种情况下应验收的数学不变量。
5. **开放**：构造一个重复特征或欠定模型，说明为何不能从“残差很小”直接得到唯一系数；再用 QR/SVD 库函数与正规方程比较病态输入的残差与前向误差。

## 练习答案提示

1. 将 $A\hat x-b$ 逐分量写出，再分别点乘 $A$ 的两列；目标是 $A^Tr=0$，不是 $r=0$。
2. 左乘 $Q^T$，并使用 $Q^TQ=I$ 消去 $Q$；只在 $R$ 可逆时直接回代。
3. 截距列应全为 1；除断言系数外，断言正规方程残差每个分量接近零。
4. 每行对应一次观测，斜率列写观测时间、截距列写 1；精确时验收 $Ax=b$，不精确时保留非零 $r=b-Ax$ 并验收 $A^Tr\approx0$。
5. 两列相同意味着存在不改变预测的零空间方向；需要额外解选择规则。使用同一数据和尺度报告两种残差、系数距离与前向误差；病态时“较小残差”不单独决定解更可信。

## 下一步

投影选择的是一个子空间；[特征值与 PCA](/linear-algebra/eigenvalues-pca)将寻找最值得保留的子空间方向。
