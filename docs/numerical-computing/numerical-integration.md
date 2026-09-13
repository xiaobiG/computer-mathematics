---
title: 数值积分：从求和逼近面积
description: 从插值推导复合梯形法与 Simpson 法，比较误差阶、函数调用成本和间断/尖峰的失败边界。
courseLevel: "2–3（算法与误差）"
prerequisites: "积分、泰勒展开、函数与求和"
estimatedMinutes: 70
experiment: "比较求积误差阶、自适应预算、端点奇性与无界尾部"
---

# 数值积分：从求和逼近面积

## 学习目标

你将推导梯形/Simpson 公式与误差阶，重放自适应预算，区分端点奇性和无界尾部，并识别固定网格的失效边界。

## 从“函数只能运行，不能积分”开始

物理模拟、概率密度和黑盒模型常只有 `f(x)`；分段过少会漏曲率，过多浪费调用并累积舍入。数值积分以可控局部近似替代函数，再检查误差是否按预期收敛。

## 直觉、定义与推导：从插值到复合公式

设 $x_i=a+ih,h=(b-a)/n$。在每个小区间以端点连线近似 $f$，积分线性插值得到梯形法：

$$T_n=h\left[\frac{f(a)+f(b)}2+\sum_{i=1}^{n-1}f(x_i)\right].$$

若 $f''$ 连续，整体误差满足 $E_T=O(h^2)$。这意味着将 $n$ 翻倍，误差约缩小四倍。

Simpson 法在两个相邻区间上用过三个点的二次插值，要求 $n$ 为偶数：

$$S_n=\frac h3\left[f(x_0)+f(x_n)+4\sum_{i\text{ odd}}f(x_i)+2\sum_{i\text{ even},0<i<n}f(x_i)\right].$$

若四阶导数有界，误差为 $O(h^4)$；相同光滑前提下 $n$ 翻倍可约缩小十六倍。高阶并非魔法：不光滑函数没有这些导数时，理论阶会消失。

## 可运行实现与验证

```python
from math import pi, sin

from projects.floating_point_museum.integration import (
    composite_simpson,
    composite_trapezoid,
    refinement_report,
)

assert abs(composite_trapezoid(sin, 0.0, pi, 64) - 2.0) < 1e-3
assert abs(composite_simpson(sin, 0.0, pi, 64) - 2.0) < 1e-6

report = refinement_report(sin, 0.0, pi, exact=2.0, segments=8)
assert 3.9 < report.trapezoid_error_ratio < 4.1
assert 15.5 < report.simpson_error_ratio < 16.5
```

以 $\int_0^\pi\sin x\,dx=2$ 为测试预言：计算 $n,2n$ 的误差比。平滑函数上，梯形法应趋近 $4$，Simpson 应趋近 $16$。`refinement_report` 在某条规则恰好精确时拒绝比值——分母为零不是“无限收敛阶”。这比只打印“看起来接近 2”的结果更能验证实现和推导。

时间复杂度为 $O(n)$ 次函数调用，空间为 $O(1)$。当 `f` 是昂贵模拟器时，减少调用通常比循环优化重要；当 `f` 很便宜、$n$ 极大时，求和顺序和补偿求和开始影响最后几位。

## 算法选择：固定网格还是自适应

固定网格适合曲率分布相对均匀且预算清楚的函数。自适应算法比较一个区间的粗估计与二分后的细估计，将更多点放在高曲率或疑似奇异区域；它不是“自动更正确”，仍需最大深度、误差预算和函数异常处理。

### 自适应 Simpson：把误差预算传给子区间

对一个区间，记粗 Simpson 估计为 $S$、二分后的两个估计之和为 $S_2$。在函数足够光滑时，第四阶主误差的比例给出 Richardson 估计：

$$\widehat E=\frac{|S_2-S|}{15},\qquad S_{\mathrm{corrected}}=S_2+\frac{S_2-S}{15}.$$

当 $\widehat E\leq\tau$ 时接受该叶区间；否则把区间和预算都平分，两个子问题各用 $\tau/2$。因此已接受叶子的误差估计之和不超过最初预算。下面的实现将估计值、采样次数、最大调用预算、终止叶区间和是否耗尽深度都放进报告：

```python
from math import pi, sin

from projects.floating_point_museum.integration import (
    adaptive_simpson,
    adaptive_simpson_certificate,
)

report = adaptive_simpson(
    sin, 0.0, pi, absolute_tolerance=1e-10,
    max_depth=20, max_evaluations=500,
)
assert report.converged
assert report.certificate["valid"]
assert abs(report.estimate - 2.0) < 1e-10
assert adaptive_simpson_certificate(sin, 0.0, pi, report)

# 不允许把深度或函数调用预算耗尽伪装成成功。
limited = adaptive_simpson(sin, 0.0, pi, absolute_tolerance=1e-14, max_depth=0)
assert not limited.converged
assert not limited.certificate["valid"]

budget_limited = adaptive_simpson(sin, 0.0, pi, max_evaluations=3)
assert budget_limited.evaluation_budget_exhausted
assert budget_limited.evaluations == 3
assert budget_limited.leaves[0].status == "evaluation_budget_exhausted"
```

每次细分需两个新四分点；预算不足不会留下隐藏的半步。叶状态为 `accepted`、深度或预算耗尽，证书重放整条轨迹。`estimated_error` 只适于光滑模型；跳变/尖峰/噪声应分段，`converged=False` 是诊断信号。

蒙特卡洛积分在高维中常比张量网格更可行，但收敛通常是 $O(N^{-1/2})$，与维度和方差强相关。不要把一维 Simpson 的高阶收敛外推到高维问题。

## 端点奇性：函数值无穷，不等于积分一定发散

`f(0)` 不存在时，前面的求积器正确地拒绝非有限采样值；但这还不足以回答积分是否存在。考虑一族可精确分析的反例：

$$I_p=\int_0^1x^{-p}\,dx.$$

先从一个正截断 $\varepsilon$ 开始，而不是把 $0$ 传给程序。若 $p\ne1$，

$$I_p(\varepsilon)=\int_\varepsilon^1x^{-p}\,dx
=\frac{1-\varepsilon^{1-p}}{1-p}.$$

若 $p<1$，当 $\varepsilon\to0^+$ 时，$\varepsilon^{1-p}\to0$，故积分收敛到 $1/(1-p)$，而被截掉的尾部恰为

$$\int_0^\varepsilon x^{-p}\,dx=\frac{\varepsilon^{1-p}}{1-p}.$$

反之，$p=1$ 时 $I_1(\varepsilon)=\log(1/\varepsilon)$，而 $p>1$ 时上式也随截断趋零而无界增长；两种情形都发散。这里的结论来自解析极限，**不是**因为若干次网格计算“看起来变大”。

```python
from projects.floating_point_museum.integration import (
    endpoint_power_integral_certificate,
    endpoint_power_integral_report,
)

finite = endpoint_power_integral_report(.5, [.1, .01, .001])
assert finite["converges"]
assert finite["limit"] == 2.0
assert finite["tail_bounds"][1] == .2  # 从 0 到 0.01 的精确遗漏量
assert endpoint_power_integral_certificate(.5, [.1, .01, .001], finite)

divergent = endpoint_power_integral_report(1.0, [.1, .01, .001])
assert not divergent["converges"]
assert divergent["limit"] is None
```

`endpoint_power_integral_report` 要求截断向零减小，保存积分、分类和精确尾项；证书重算它们。它只诊断该解析族，不能从黑盒采样判断奇点或未知尾部。

## 无界域：大截断不是尾部证明

对 $J_p=\int_0^\infty(1+x)^{-p}\,dx$，只算到 $L$ 仍遗漏尾部。解析式表明仅 $p>1$ 收敛，极限为 $1/(p-1)$，遗漏量为 $(1+L)^{1-p}/(p-1)$；$p\le1$ 即使有限截断数值稳定也发散：

```python
from projects.floating_point_museum.integration import (
    unbounded_power_tail_certificate,
    unbounded_power_tail_report,
)

finite = unbounded_power_tail_report(2.0, [1.0, 9.0, 99.0])
assert finite["limit"] == 1.0 and finite["tail_bounds"][-1] == .01
assert unbounded_power_tail_certificate(2.0, [1.0, 9.0, 99.0], finite)
assert not unbounded_power_tail_report(1.0, [1.0, 9.0, 99.0])["converges"]
```

这不是一般无界积分器；它只说明有限区间求积还必须有独立尾界、变量变换或专门理论，不能由“大到够用”的截断自行证明。

## 失败案例与工程边界

- **间断**：阶跃函数的导数不存在，网格是否撞上跳点会主导误差；按已知断点分段积分。
- **窄尖峰**：等距点可能完全错过峰；使用领域知识、自适应采样或变量变换。
- **高频振荡**：采样不足会混叠，结果可能稳定地错误；网格须解析振荡尺度。
- **端点奇性或无界区间**：采样器拒绝 `inf`/`nan` 是正确的输入契约，但不自动代表积分发散；必须用解析尾界、变量变换或专门算法区分可积奇性。
- **极大 n**：普通浮点累计可能吞掉小项；考虑 Kahan/pairwise 求和并报告容差。
- **昂贵或有副作用的函数**：调用预算是资源契约，不是数值误差上界。预算耗尽时报告叶区间和未估计误差，不能把最后的父区间估计标成达标结果。

## 常见误区

1. “Simpson 总比梯形好。”错误：它依赖更强光滑性，且函数值噪声会破坏高阶优势。
2. “误差小就说明积分正确。”错误：可能两个网格都漏掉同一个尖峰。
3. “分段数翻倍必然误差减半。”错误：误差阶取决于公式和函数正则性。
4. “数值积分只适合一维。”错误：高维可用随机方法、稀疏网格或问题结构，但策略不同。

## 练习

1. **基础题**：由端点线性插值推导单个小区间的梯形面积公式。
2. **推导题**：若梯形误差为 $Ch^2$，证明分段数翻倍时误差比趋于 $4$。
3. **编码题**：对 `sin` 比较 $n=8,16,32,64$ 的两种方法，输出误差比；再对 $|x|$ 在 $[-1,1]$ 上重复并解释结果。
4. **工程题**：为一个昂贵且带尖峰或端点奇性的仿真函数设计自适应积分的停止规则、最大预算和异常值策略；说明为何 `estimated_error` 不能替代对尖峰是否被采样到或奇性是否可积的审计。

## 练习答案提示

1. 在区间两端取函数值，用底乘平均高近似线性插值下的面积，得到 $h(f(a)+f(b))/2$。
2. $h$ 减半后 $Ch^2$ 变为 $C(h/2)^2$，所以旧误差与新误差之比趋于 4；前提是渐近区间且函数足够光滑。
3. 对每个 $n$ 记录绝对误差与相邻比；$|x|$ 在 0 不光滑，理论高阶比可能不出现，不能将此当实现失败。
4. 用粗细估计差分配局部误差预算，设函数调用/递归深度上限；`|S_2-S|/15` 只在光滑假设下可解释为误差估计。遇到 NaN、尖峰或不连续信号时记录区间并按契约分段、回退或失败；端点奇性还应给出解析尾界或变量变换。若预算不足两个新点，显式返回未收敛叶。

## 延伸

积分中的“缩小步长会先变好后受浮点限制”与[数值微分](/numerical-computing/numerical-differentiation)相呼应。继续学习 Richardson 外推、自适应 Gauss–Kronrod 和蒙特卡洛/重要性采样；对工程实现，优先选择经验证的科学计算库。
