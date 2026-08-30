---
title: 割线法：不用导数也能快速求根
description: 从牛顿法的有限差分近似推导割线迭代，解释超线性收敛、分母消失与无区间保证，并实现可验证求根器。
courseLevel: "2–3（数值算法、收敛与工程边界）"
prerequisites: "函数、导数、牛顿法、绝对与相对误差"
estimatedMinutes: 50
experiment: "用割线法求解平方根，比较无需导数的迭代与分母消失边界"
---

# 割线法：不用导数也能快速求根

## 学习目标

读完后，你能从牛顿法推导割线公式；实现残差、步长和分母保护；解释其超线性但非二次的局部收敛；并判断何时必须回退到二分或受保护的牛顿法。

## 从昂贵导数开始

有些方程能评估 $f(x)$，但解析导数难写、自动微分昂贵或数值差分不稳定。割线法用最近两点的函数值近似导数，通常比二分更快，却不像二分一样始终把根困在一个已知区间内。

## 从割线推导迭代

牛顿法使用 $f'(x_k)$：$x_{k+1}=x_k-f(x_k)/f'(x_k)$。以两点斜率近似导数，

$$f'(x_k)\approx\frac{f(x_k)-f(x_{k-1})}{x_k-x_{k-1}},$$

代入得到

$$x_{k+1}=x_k-f(x_k)\frac{x_k-x_{k-1}}{f(x_k)-f(x_{k-1})}.$$

几何上，这是过 $(x_{k-1},f(x_{k-1}))$ 和 $(x_k,f(x_k))$ 的割线与横轴的交点。若分母接近零，割线近乎水平，步长可能爆炸；这不是可忽略的实现细节，而是算法合同的一部分。

## 可运行实现

```python
from projects.floating_point_museum.root_finding import (
    secant_convergence_certificate,
    secant_convergence_report,
    secant_solution_certificate,
    secant_trace,
    secant_trace_certificate,
)

function = lambda value: value * value - 2.0
root, events = secant_trace(function, 1.0, 2.0)
assert abs(root * root - 2) <= 1e-12
assert secant_trace_certificate(function, events)
assert secant_solution_certificate(function, 1.0, 2.0, root, events)
assert abs(events[-1].candidate_value) <= 1e-12

# 只有在教学中已知 sqrt(2) 时，才能直接观测误差阶。
order_report = secant_convergence_report(events, 2.0 ** 0.5)
assert 1.5 < order_report["order_estimates"][-1][1] < 1.7
assert secant_convergence_certificate(events, 2.0 ** 0.5, order_report)
```

```bash
python -m unittest projects.floating_point_museum.test_root_finding
```

每个 `SecantEvent` 都保存两次插值输入、函数值和新候选点。`secant_trace_certificate` 独立重算割线公式、函数值和相邻事件的连接关系，因此可发现“最终根看起来正确、但某一轮更新公式被改错”的回归。`secant_solution_certificate` 更进一步从给定初值、容差和最大步数重放完整执行，并要求返回根与整段轨迹完全一致；替换根、首轮输入或停止条件都会被拒绝。求根实现每轮只计算一个新函数值，时间为 $O(k)$ 次函数评估、额外空间 $O(k)$ 用于保留轨迹（只调用 `secant_root` 时仍只保留 $O(1)$ 状态）。它检查初值函数值是否有限、分母是否为零、候选值是否有限、步长停滞时残差是否也已满足，以及最大迭代次数。

若教学例已知真根 $r$，可令 $e_k=|x_k-r|$，并由三个连续递减误差估计局部阶：

$$
\widehat p_k=
\frac{\log(e_{k+1}/e_k)}{\log(e_k/e_{k-1})}.
$$

`secant_convergence_report` 记录候选点误差和这些估计，平方根例最后一轮约为 $1.607$，接近 $\varphi$；`secant_convergence_certificate` 会重算该报告，避免图表或结论与轨迹脱节。这个量只是在已知根、进入局部渐近区后对单个运行的观测，不是一般收敛证明，也不应用于未知真根的生产求解。

## 收敛与正确性边界

在简单根附近、函数足够光滑且初值足够好时，割线法收敛阶约为黄金比例 $\varphi\approx1.618$：快于线性二分、慢于二次牛顿。没有导数并非免费午餐：它需要两个历史点，且没有“始终留在含根区间”的保证。

返回时同时满足小残差与合理步长，才有数值证据表明已接近根。小步长但大残差意味着停滞，不应伪装为成功；实现会报告错误。测试覆盖平方根、右端点已为根、常函数造成的零割线斜率以及非法停止参数。

## 失败案例与常见误区

- **分母消失**：若连续两次函数值相同，无法定义下一条割线。
- **跳出可行域**：割线可越过物理边界或函数定义域；无约束问题可改用带区间保护的混合方法。
- **多重根**：像牛顿法一样会失去理想局部速度；不要把一次误差阶观测当作所有初值、所有函数的固定承诺。
- **“不用导数总更好”**：当导数便宜且可靠时，受保护牛顿法可能用更少迭代；比较应基于函数/导数评估成本与失败率。

## 练习

1. **基础题**：对 $x^2-2$ 从 1 和 2 手算一次割线更新。
2. **推导题**：从两点直线方程推导割线公式。
3. **编码题**：用 `secant_solution_certificate` 篡改返回根、首轮输入或一条轨迹，确认拒绝；再篡改 `secant_convergence_report` 的末轮阶估计，确认其证书拒绝，并构造一个分母接近零的失败输入。
4. **开放题**：设计一个“二分保底 + 割线加速”策略，写出何时接受候选步、何时回退。

## 练习答案提示

1. 用两点 $(1,-1),(2,2)$ 的割线与横轴交点公式；保持足够有效位，下一步约为 $4/3$。
2. 将过两点的直线写成斜率式并令 $y=0$，整理为 $x_1-f(x_1)(x_1-x_0)/(f(x_1)-f(x_0))$。
3. 保存每次两点、函数值和候选值；完整证书还应绑定初值、容差与最终根。误差阶实验需要外部真根，报告应只保留严格递减的三元组；常函数或几乎相等的函数值会使分母为零/很小，测试应断言明确失败而非巨大跳步。
4. 只在候选值有限、落在含根区间且带来足够进展时接受割线步；否则二分并更新符号区间，停止同时检查区间、步长和残差。

## 延伸

[牛顿法](/numerical-computing/newton-method)提供导数和区间保护版本；[数值微分](/numerical-computing/numerical-differentiation)解释近似导数为何脆弱；[浮点数错误博物馆](/projects/floating-point-museum)收录实验。继续学习可检索 Brent method、quasi-Newton method 和 root conditioning。
