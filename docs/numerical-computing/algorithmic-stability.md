---
courseLevel: "2–3（误差分析与工程）"
prerequisites: "浮点数表示、相对误差、二次方程"
estimatedMinutes: 60
experiment: "比较二次公式的消去误差与稳定改写"
title: 算法稳定性：同一个公式为什么会算出不同精度
description: 通过二次方程的小根比较前向误差、后向关系与避免消去的稳定改写。
---

# 算法稳定性：同一个公式为什么会算出不同精度

## 文章元信息

- **建议阅读层级**：2–3 · 误差模型、稳定改写与工程选择
- **前置知识**：[浮点数表示](/numerical-computing/floating-point)、[条件数](/numerical-computing/condition-number)、二次方程
- **预计学习时间**：60 分钟
- **配套实验**：[浮点数错误博物馆](/projects/floating-point-museum)

## 问题场景：一个正常的问题，两个精度完全不同的答案

考虑 $x^2+10^8x+1=0$。两根中一根约为 $-10^8$，另一根约为 $-10^{-8}$。若把教科书公式直接翻成浮点代码，小根的相对误差会很大；改写后却能恢复它。这不是改变数学问题，而是避免在有限精度中相减两个几乎相同的大数。

## 学习目标

读完后，你能够：

1. 区分问题的条件数与算法稳定性；
2. 找出二次公式中产生消去的分支；
3. 从 Vieta 关系推导稳定的小根计算；
4. 用高精度参考值和相对误差验证改写的效果。

## 直觉模型：先算准一个根，再用乘积得到另一个

对 $ax^2+bx+c=0$，直接公式为

$$r_{1,2}=\frac{-b\pm\sqrt{b^2-4ac}}{2a}.$$ 

当 $b>0$ 且 $b^2\gg4ac$ 时，$-b+\sqrt{b^2-4ac}$ 是两个接近 $-b$ 的数相加；在实现上等价于相近大数相减，低位会被抹去。另一支 $-b-\sqrt{\cdot}$ 没有这个问题，先可靠地得到大根 $r_1$，再用 $r_1r_2=c/a$ 得到小根即可。

## 严格定义与分步推导

令 $D=b^2-4ac\ge0$，并定义

$$q=-\frac12\left(b+\mathrm{sign}(b)\sqrt D\right).$$

这样 $q$ 总选择绝对值较大的、没有消去的一支。因此一个根是 $r_1=q/a$。由系数比较（或 Vieta 定理）

$$r_1r_2=\frac ca,$$

所以在 $q\ne0$ 时

$$r_2=\frac{c}{q}.$$ 

该步骤没有宣称数学结果不同；它只改变有限精度下的求值路径。若 $D=0$，两个根相同，直接返回 $-b/(2a)$，避免不必要的除以 $q$。

## 算法实现：与高精度参考值并排审计

```python
from projects.floating_point_museum.stability import (
    quadratic_scaling_report,
    quadratic_scaling_report_certificate,
    quadratic_stability_report,
    quadratic_stability_report_certificate,
)

report = quadratic_stability_report(1.0, 1e8, 1.0)
assert report["certificate"]["direct_formula_exposes_cancellation"]
assert report["certificate"]["stable_small_root_has_high_accuracy"]
assert quadratic_stability_report_certificate(1.0, 1e8, 1.0, report)
print(report["direct_small_root_relative_error"])
print(report["stable_small_root_relative_error"])

scaled = quadratic_scaling_report(1.0, 1e308, 1.0)
assert not scaled["certificate"]["unscaled_binary64_discriminant_is_finite"]
assert scaled["certificate"]["scaling_preserved_nonzero_coefficients"]
assert quadratic_scaling_report_certificate(1.0, 1e308, 1.0, scaled)
```

运行 `python -m unittest projects.floating_point_museum.test_stability`。实验以高精度十进制计算作为课堂参考，不把同一段 binary64 代码的输出当作真值。它分别报告两种公式的小根相对误差；重放器绑定系数、两条路径、参考根与结论，篡改误差或“存在消去”都会失败。稳定公式在此例达到 $10^{-12}$ 量级；两式都只做常数次算术。

## 系数缩放：先让有限路径存在，再谈稳定改写

系数同乘非零 $s$ 不改变根，因此可令 $m=\max(|a|,|b|,|c|)$，改用

$$\tilde a=\frac{a}{m},\qquad \tilde b=\frac{b}{m},\qquad \tilde c=\frac{c}{m}.$$

这样每个缩放后系数的绝对值至多为 1，故 $\tilde b^2-4\tilde a\tilde c$ 不会仅因乘法上溢。`quadratic_scaling_report(1,10^{308},1)` 会公开原始判别式在 binary64 中不有限、缩放系数 $(10^{-308},1,10^{-308})$、稳定根和十进制参考根；它并不伪称已经成为生产求根器。

缩放也有严格的失败边界：如果一个原本非零的系数在除以 $m$ 后下溢为零，缩放后的多项式已经不同，教学实现会拒绝。例如 $(1,10^{308},5\times10^{-324})$ 中最后一项不能被悄悄丢弃。该例说明“缩放能避免中间上溢”不等于“任何尺度差异都能由 binary64 无损处理”。

## 正确性、稳定性与适用边界

Vieta 推导保证实数算术中两种公式等价。实验中的精度差说明**算法稳定性**：一个稳定算法对舍入扰动不额外放大太多。它与[条件数](/numerical-computing/condition-number)不同，后者描述原问题本身的敏感性；良态问题也可能被不稳定求值路径算坏，病态问题则不能仅靠改写完全挽救。

此教学实现只处理有限系数、实根和二次式。未缩放的 `stable_quadratic_roots` 仍要求 **binary64 中已经算出的判别式有限**：例如 $b=10^{308}$ 会令 $b^2$ 上溢，合同会在开方和根计算前拒绝，而不是把 `inf` 当作大根或“稳定公式”的证据。受限的 `quadratic_scaling_report` 则将“如何缩放”公开为可重放证据，并在非零项会下溢时拒绝。缩放系数可保留相同根：对任意非零 $s$，

$$
ax^2+bx+c=0
\quad\Longleftrightarrow\quad
(sa)x^2+(sb)x+sc=0.
$$

但怎样选 $s$、避免下溢、处理复根及评估缩放后的误差都超出本页的小实验；生产求根器还需异常处理和经过审计的库。

## 工程陷阱与反例

- 只把 `float` 换成更多小数位：若继续相减近似相等的量，仍会浪费有效数字。
- 用残差替代小根误差：大根主导的残差可以很小，却掩盖小根的相对误差。
- 在 $D=0$ 时无条件使用 $c/q$：会把重根边界变成除零。
- **把 `inf` 当作根。** 系数有限不保证中间的 $b^2-4ac$ 有限；先用受限缩放报告检查非零项未丢失，或交给具备溢出控制的求根库。
- **缩放后把下溢项当作零。** 这已改变原方程；本实验拒绝该路径，而不是把“少一项”的结果称作原方程的根。

## 练习

1. **基础**：说明 $b<0$ 时为什么 $q$ 要选择相反符号的分支。
2. **推导**：从 $(x-r_1)(x-r_2)$ 展开推导 $r_1r_2=c/a$。
3. **编码**：为 $x^2-10^8x+1=0$ 写测试，比较两种公式得到的小根。
4. **边界题**：解释为何 $(a,b,c)=(1,10^{308},1)$ 的未缩放路径会失败、受限缩放为何能通过；再说明 $(1,10^{308},5\times10^{-324})$ 为什么仍须拒绝。
5. **开放**：调查一个科学计算库的二次方程或多项式求根 API，说明它如何处理缩放、复根或上溢。

## 练习答案提示

1. 令 $q=-\tfrac12(b+\mathrm{sign}(b)\sqrt D)$，这样 $q$ 总是两个同号大数相加，避免相近数相减；另一根用 $c/q$ 得到。
2. 展开 $a(x-r_1)(x-r_2)$ 后比较常数项，得到 $ar_1r_2=c$；这也解释为何已求得稳定的一根可恢复另一根。
3. 用高精度或稳定公式作参考，分别断言小根的相对误差；另测重根和无实根，避免只验证一个有利案例。
4. 前一例归一化后仍保留三个非零项且判别式有限；后一例的极小常数项会下溢成零，已经不再是同一多项式。
5. API 调研需查看输入缩放、复数返回/异常、溢出和退化系数的文档与行为；教学公式不能直接当生产实现的替代品。

## 延伸

[Kahan 与 pairwise 求和](/numerical-computing/kahan-summation)展示另一类稳定改写；[数值插值](/numerical-computing/interpolation)则说明即使求值稳定，高阶模型本身也可能对数据扰动敏感。
