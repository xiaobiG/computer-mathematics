---
courseLevel: "2–3（工程数值可靠性）"
prerequisites: "浮点数表示、绝对误差与相对误差"
estimatedMinutes: 55
experiment: "为浮点比较写属性测试，并用固定随机种子复现实验失败样本"
title: 浮点比较、容差与属性测试
description: 将误差模型变成 API 契约：设计尺度相关容差、残差检查和可复现的性质测试。
---

# 浮点比较、容差与属性测试

> 数值代码最危险的测试往往是 `result == expected`：它在本应相等的结果上误报失败，也可能在错误被粗糙容差掩盖时误报成功。可靠的测试先说明“允许怎样的误差”，再用不依赖单一答案的性质寻找反例。

## 学习目标

完成本课后，你可以：

- 从绝对与相对误差构造尺度相关的近似比较；
- 为零附近、极大数、NaN、无穷和不同量纲设计明确策略；
- 区分“数值相近”“残差小”和“算法正确”三种断言；
- 用固定种子、性质和缩小反例构造可复现数值测试；
- 识别过宽容差、不可复现实验和相关输入造成的假安全感。

## 从一个脆弱断言开始

在二进制浮点中，`0.1 + 0.2` 的存储值通常不等于字面量 `0.3`。把所有测试改成 `abs(a - b) < 1e-6` 看似解决问题，却会制造新的错误：

- 比较 \(10^{12}\) 量级的长度时，\(10^{-6}\) 小得没有意义；
- 比较 \(10^{-15}\) 附近的物理量时，固定容差反而过宽；
- 把米和毫米混用，数值“接近”并不代表量纲正确；
- NaN 与任何值比较都为假，悄悄通过或失败都不是好策略。

容差不是一个神奇常数，而是接口契约的一部分：它必须说明参考尺度、误差来源与失败后的含义。

## 近似相等的数学模型

常用规则是同时允许绝对和相对误差：

\[
|a-b|\le \max(\varepsilon_{abs},\;\varepsilon_{rel}\max(|a|,|b|)).
\]

绝对容差处理零附近；相对容差随数值尺度变化。选择较大者不是随意宽松，而是在“真值接近零”和“真值远离零”两种误差模型之间切换。

例如计算结果是通过 \(k\) 次浮点运算得到，机器精度为 \(u\)，若算法的前向误差分析给出约 \(Cku\)，可以据此设置相对容差的数量级；若传感器本身精度为 0.01 mm，绝对容差应来自测量规格，而非机器精度。测试代码不能替代误差分析，但应把分析结果固定成可审阅的参数。

## 算法实现：一个可审计的比较函数

```python
from projects.floating_point_museum.comparison import (
    close_enough,
    comparison_certificate,
    comparison_report,
)

assert close_enough(0.1 + 0.2, 0.3)
assert close_enough(1_000_000_000.0 + 0.5, 1_000_000_000.0, rel_tol=1e-9)
assert not close_enough(1.0, 1.1, abs_tol=1e-12, rel_tol=1e-9)
assert not close_enough(float("nan"), float("nan"))

report = comparison_report(1e12, 1e12 + 1.0, abs_tol=1e-6, rel_tol=1e-9)
assert report["close"]
assert report["threshold"] == 1000.000000001
assert comparison_certificate(report)["valid"]
```

`comparison_report` 显示差值、尺度相关阈值和最终判断，`comparison_certificate` 从四个输入字段重新计算契约，因此篡改阈值或 `close` 结论都会被拒绝。第二个断言的容差是否合理，取决于应用：对金融余额，0.5 的偏差也许绝不能接受；对粗略仿真，它可能可接受。函数提供机制，不替调用者决定语义。

## 残差、前向误差与测试预言

对线性系统 \(Ax=b\)，候选解 \(\hat x\) 的残差是

\[
r=b-A\hat x.
\]

测试 `\|r\|` 小是在检查“\(\hat x\) 是否近似满足输入方程”，却不是检查 `\hat x` 是否接近真解。由条件数可知，病态问题可以有很小的残差和很大的前向误差。好的测试策略分层：

1. 对已知小型真解的良态问题，检查前向误差；
2. 对真实大型问题，检查缩放后的残差和后向误差；
3. 对变换或分解，检查结构性质，例如 \(Q^TQ\approx I\)、\(PA\approx LU\)；
4. 对随机数据，检查不变量和统计性质，而不把一次运行的数字当真理。

这避免了“测试通过，所以算法正确”的逻辑跳跃：数值测试只能增加证据，正确性仍依赖适用前提与证明。

## 性质测试：生成许多输入，而不是手写几个例子

示例测试擅长记录已知 bug；性质测试检查大量输入应始终满足的关系。以求和为例，理想实数中 `sum(xs)` 对排列不变，但浮点求和仅近似满足。我们可比较普通求和与 Kahan 求和，并设置由规模和数据范围解释的界。

```python
from random import Random


def kahan_sum(values):
    total = compensation = 0.0
    for value in values:
        corrected = value - compensation
        updated = total + corrected
        compensation = (updated - total) - corrected
        total = updated
    return total


def reproducible_sum_experiment(seed=2026, trials=200):
    rng = Random(seed)
    worst_gap = 0.0
    witness = None
    for _ in range(trials):
        values = [rng.uniform(-1e8, 1e8) for _ in range(100)]
        ordinary = sum(values)
        stable = kahan_sum(values)
        gap = abs(ordinary - stable)
        if gap > worst_gap:
            worst_gap, witness = gap, values
    return worst_gap, witness


gap, counterexample = reproducible_sum_experiment()
assert gap >= 0.0
assert counterexample is not None
```

固定种子使失败可复现；一旦找到反例，就把它保存为一个小的回归用例。不要只报告“随机测试跑了一千次”：没有种子、输入分布、版本和容差，别人无法复查结论。

## 如何选择生成输入

均匀随机数很少触及数值算法最难的区域。生成策略应主动覆盖：

- 零、符号变化、极大/极小尺度和相近数的相减；
- 接近奇异的矩阵、重根附近的函数、陡峭或平坦的区间；
- 满足前提的典型输入，以及明确违反前提的输入；
- 改变单位或缩放后的等价问题，检查算法是否保持应有的尺度性质。

例如二分法应保持“根仍被区间包住”的不变量；QR 分解应近似保持正交性；对于输入 NaN 或非法容差，接口应以文档规定的方式拒绝，而不是产生静默的可信数字。

## 工程边界与常见误区

- **把默认容差复制到所有地方。** 每个断言应能回答：误差来自哪里、为什么此尺度可接受？
- **用相对误差比较零。** 分母或参考尺度接近零时相对误差失去意义，必须有绝对门槛。
- **吞掉 NaN。** 对科学计算，NaN 可能是合法传播；对优化器输出，它通常表示测试应立刻失败。策略必须显式。
- **随机但不可复现。** 不记录种子会让 CI 中的失败无法定位；固定单一种子又可能过拟合，应同时保存失败样本并轮换种子集。
- **把相关观测当独立样本。** 模拟和统计测试的有效样本量由数据生成过程决定，不能只看数组长度。

## 练习

1. 为温度（摄氏度）、账户余额（分）和单位向量长度分别设计比较策略，说明为什么容差不同。
2. 构造两个接近 \(10^{12}\) 的数，使固定 `1e-6` 容差与相对容差给出不同判断；哪一个符合你的应用语义？
3. 为 `close_enough` 写测试，覆盖负容差、NaN、同号/异号无穷、零附近和大尺度输入；篡改 `comparison_report` 的阈值或结论，确认其证书拒绝。
4. 对一个线性求解器同时编写残差测试与小规模前向误差测试；构造近奇异矩阵说明二者为何不能互相替代。
5. 为 [浮点数错误博物馆](/projects/floating-point-museum) 设计一个可保存、可缩小的随机反例格式，包含种子、输入、容差和运行环境。

## 练习答案提示

1. 温度依传感器分辨率选绝对/相对阈值，余额应用整数分精确比较，单位向量长度可按误差传播选接近 1 的容差；三者的量纲和失败成本不同。
2. 例如 $10^{12}$ 与 $10^{12}+1$：绝对差远大于 $10^{-6}$，相对差却很小；选择取决于应用关心的绝对单位还是比例偏差。
3. 先将容差输入验证与数值比较分开；NaN、无穷和零附近都要定义单独语义，不能让算术表达式偶然决定结果。
4. 残差检验 $\lVert b-A\hat x\rVert$，前向误差比较已知真解；近奇异例可同时残差小、前向误差大，展示问题条件数的作用。
5. 格式至少包含可序列化输入、生成器版本/种子、比较规则、期望失败性质、最小化步骤和运行环境；缩小后仍必须能稳定重现同一失败。

## 下一步

把本课的比较契约接到 [Kahan 求和](/numerical-computing/kahan-summation)、[数值微分](/numerical-computing/numerical-differentiation) 和[浮点数错误博物馆](/projects/floating-point-museum)。下一层将比较随机模拟的抽样误差与浮点误差，并练习报告两者而不是只报告一个结果。
