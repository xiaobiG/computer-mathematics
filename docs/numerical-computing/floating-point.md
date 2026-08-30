---
courseLevel: "1–2（核心概念与工程）"
prerequisites: "二进制、小数与 Python 基础"
estimatedMinutes: 50
experiment: "观察舍入、NaN、无穷与容差比较"
title: 浮点数表示：为什么 0.1 + 0.2 不等于 0.3
description: 从 IEEE 754 的有限二进制表示、舍入到尺度相关的稳健比较。
---

# 浮点数表示：为什么 0.1 + 0.2 不等于 0.3

## 文章元信息

- **建议阅读层级**：1–3 · 核心表示、误差模型与工程模式
- **前置知识**：二进制、分数、科学计数法
- **预计学习时间**：55 分钟
- **配套实验**：[浮点数错误博物馆](/projects/floating-point-museum)

## 学习目标

读完后，你能从 binary64 的符号、尾数和指数解释舍入；用 ULP 审计一次十进制转换；为不同尺度选择比较契约；并能区分普通有限值、NaN、无穷、零与次正规数的工程语义。

## 从一个计算问题开始

支付、传感器和机器学习程序都要比较计算结果。为什么 JavaScript/Python 中 `0.1 + 0.2 == 0.3` 常为假？若把它简单修成“保留两位小数”，又会在哪些极大或极小的数上重新出错？

## 直觉模型：有限格点不是实数轴

二进制有限小数只能精确表示约分后分母为 $2^k$ 的有理数。$0.1=1/10$ 的分母含因子 5，因此二进制展开无限循环，存储时必须选择附近的有限值。

把 binary64 想成一条不均匀的格点轴：数越大，格点越稀；靠近零时还有次正规数区域。程序看到的 `0.1` 是某个格点，而源文件中的字符 `"0.1"` 表示精确分数 $1/10$。区分这两者，才能精确谈“误差”。

## 严格定义：从字段到一次舍入

IEEE 754 二进制浮点数可抽象为

$$(-1)^s\times(1.f)_2\times2^{e-\text{bias}},$$

其中符号位 $s$、有限位数的尾数 $f$ 与有限指数 $e$ 决定可表示集合。一次运算的真实结果通常不在集合中，硬件按舍入规则映射到附近值；加法再舍入一次，所以两个“最接近”的近似相加不必等于第三个近似。

对一个有限十进制字面量 $x$，设 $\operatorname{fl}(x)$ 是转换后的 binary64 值，局部格距为 $\operatorname{ulp}(\operatorname{fl}(x))$。在默认的“最近值、偶数舍入”模式下（非恰好平分的情形），转换误差满足

$$
|\operatorname{fl}(x)-x|\leq \frac12\operatorname{ulp}(\operatorname{fl}(x)).
$$

这不是“所有计算的总误差界”：后续每个运算仍会继续舍入；它只是验证**一次文本到 binary64 转换**的局部证据。

## 分步实验：把字面量、存储值与 ULP 对齐

$1/2=0.1_2$ 可以有限表示，$1/10=0.000110011\ldots_2$ 则不断重复。以下比较使用绝对容差与相对容差的较大者，而不是固定的小数位：

```python
from projects.floating_point_museum.examples import nearly_equal
from projects.floating_point_museum.representation import (
    adjacent_values,
    decimal_rounding_certificate,
    decimal_rounding_report,
    float64_parts,
    spacing_at,
)

parts = float64_parts(0.1)
assert parts.classification == "normal"
report = decimal_rounding_report("0.1")
assert report.exact_value.numerator == 1 and report.exact_value.denominator == 10
assert report.rounding_direction == "up"
assert report.certificate["rounding_error_is_within_half_ulp"]
assert decimal_rounding_certificate(report)["valid"]
assert 0.1 + 0.2 != 0.3
assert nearly_equal(0.1 + 0.2, 0.3)

lower, upper = adjacent_values(1.0)
assert lower < 1.0 < upper
assert upper - 1.0 == 2.0 ** -52
assert spacing_at(1e16) == 2.0
assert 1e16 + 1.0 == 1e16
```

`decimal_rounding_report` 用精确分数解析源字符串，再与 `Fraction.from_float` 得到的存储分数相减；因此不会用一个已被舍入的 Python 浮点数“验证”它自己。它报告误差的方向和以 ULP 为单位的大小，并证实其不超过半个 ULP。`decimal_rounding_certificate` 则重新解析文字、重建全部字段，并把存储值与两个有限相邻格点的精确距离比较；篡改误差或舍入方向会被拒绝。`float64_parts` 让符号、11 位有偏指数和 52 位尾数字段可见；`adjacent_values` 与 `spacing_at` 则显示浮点数不是均匀网格。`1e16` 附近两个相邻可表示数相差 2，所以加 1 会在舍入后回到原数。所有这些检查为 $O(1)$。相对项适合大尺度，绝对项保证接近零时仍有合理阈值；两者参数必须源自量纲、测量精度和业务容忍度。

## 正确性与工程边界

若差值不超过 `tolerance * max(1, |x|, |y|)`，函数明确实现“在允许绝对或相对误差内相等”的业务定义；它并不恢复数学上的相等。NaN 与任何数（包括自身）都不相等，应显式检测；无穷值、正负零、次正规数、上溢和下溢也有独立语义。表示实验专门拒绝非有限字面量、相邻值请求，避免把特殊值混进普通数的网格直觉。金额宜用最小货币单位整数或十进制定点类型，不能依赖 epsilon。

## 常见误区

- 认为所有十进制小数都不精确：0.5、0.25 可以精确表示。
- 认为固定 `1e-12` 是万能容差：尺度与单位改变时它会失效。
- 用 `round` 掩盖算法不稳定；消去和累计误差仍会存在。

## 练习

1. **基础**：判断 $0.125$、$0.2$、$0.375$ 中哪些能有限二进制表示。
2. **推导**：说明为什么约分后分母只含 2 是二进制有限表示的充要条件。
3. **编码**：篡改 `decimal_rounding_report("0.1")` 的误差或方向，确认 `decimal_rounding_certificate` 拒绝；再为 `nearly_equal` 添加接近零、巨大数、NaN 和无穷的测试策略。
4. **开放**：为温度传感器和货币金额分别设计比较/存储方案，并说明参数依据。

## 练习答案提示

1. 将小数约分后观察分母：$0.125=1/8$、$0.375=3/8$ 能有限表示，而 $0.2=1/5$ 不能。
2. 有限二进制小数可写作整数除以 $2^k$；反向证明时先把分母约分，任何奇质因子都不能被 $2^k$ 消去。
3. 十进制舍入证书须从源文字重新计算字段，并与相邻浮点格点比较；接近零应覆盖绝对容差，巨大数应覆盖相对容差；NaN 要单独断言为不相等，无穷值则分别测试同号与异号。
4. 温度先明确传感器分辨率和安全阈值，再选绝对/相对容差；货币以最小货币单位整数或十进制定点存储，不能把二进制 epsilon 当业务规则。

## 延伸与下一步

表示误差是输入扰动的来源；[条件数](/numerical-computing/condition-number)说明同样大小的扰动为何会在不同问题中产生截然不同的输出误差。
