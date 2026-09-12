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

报告的两组 `*_normal_equation_residual` 都是 $A^Tr$：它们接近零，才说明相应路径确实达到最小二乘的一阶最优性条件。`least_squares_report_certificate` 会独立重算报告，同时分别检查两条路径的驻点条件与“报告的残差范数确由报告中的系数产生”；篡改一项指标即被拒绝。`least_squares_normal_equations` 有意调用带选主元的方程求解器，便于核对推导；`least_squares_qr` 以改进 Gram–Schmidt 得到 $A=QR$，计算 $Q^Tb$ 后对上三角 $R$ 回代，才是默认应选的数值路径。运行 `python -m unittest projects.linear_algebra_lab.test_main` 可验证小例解、两条路径的一致性、正交残差、秩亏列和宽矩阵边界。

构造正规方程或 QR 的密集成本都约为 $O(mn^2)$；随后求解 $n\times n$ 系统为 $O(n^3)$。QR 避免了正规方程将条件数近似平方的额外放大。

## 正确性证据与数值选择

对列满秩的 $A$，凸二次目标只有一个驻点；$A^Tr=0$ 因而既是正规方程的残差，也是最小解的证书。示例报告同时检查正规方程与 QR 的该证书，并报告两组系数的距离。这个小而良态的例子中两条路径应相同；若特征近似共线，二者的数值结果可能开始分离，这正是应该选择 QR 或 SVD 的信号，而不是把差异平均掉。

若列秩亏，$A^\mathsf TA$ 不可逆，最小二乘解通常不唯一；但最小残差的投影 $A\hat x$ 仍唯一。教学 QR 代码会显式拒绝这种输入，避免悄悄返回依赖列顺序的结果。SVD 则可通过丢弃零奇异值选择其中范数最小的解；这是一条额外的解选择规则，不能从正规方程本身自动得到。

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

`exact` 的 $b$ 在 $A$ 的列空间中，所以验收应是 $Ax=b$。`projected` 只改变最后一次观测，已不在同一条直线模型的列空间中；此时正确不变量不再是零残差，而是 $A^Tr\approx0$ 且残差被保留。第三个输入把两列写成同一方向，诊断拒绝假装 QR 能给出唯一坐标：即便目标可达，仍须先选择最小范数、稀疏性或其他额外规则。

修改这些行之前，先用自然语言写下“每个特征允许怎样改变输出”和“我希望验收精确等式还是投影正交性”。如果你的模型只有一行、两列，诊断会标为欠定，而不是擅自把某个坐标设为零。这是从投影概念迁移到建模选择的关键一步。

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

正规方程把小奇异方向的尺度平方，因而这个例子在 `1e-12` 的消元容差下先拒绝 $A^TA$；QR 路径仍产生一个满足 $A^Tr\approx0$ 的浮点驻点。然而两条几乎重复的列让系数已偏离精确值：残差小、驻点条件成立，都不能恢复丢失的可辨识性。这个实验不证明 QR 总是更准确，也不将这份改进 Gram–Schmidt 教学代码当作生产实现；它只说明应报告列共线、缩放和系数敏感性，并在需要最小范数或秩判定时交给成熟的 pivoted QR/SVD 库。

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
