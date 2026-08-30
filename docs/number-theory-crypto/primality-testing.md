---
title: 素性测试：Miller–Rabin 如何用反例快速排除合数
description: 从费马小定理与平方根结构推导 Miller–Rabin，理解见证者、伪素数、错误概率与大整数工程边界。
courseLevel: "2–3（数论算法与密码工程）"
prerequisites: "模运算、快速幂、因式分解与概率"
estimatedMinutes: 60
experiment: "实现教学版 Miller–Rabin，并用 Carmichael 数验证费马测试的失败"
---

# 素性测试：Miller–Rabin 如何用反例快速排除合数

## 学习目标

读完后，你能解释费马测试为何会被 Carmichael 数欺骗；把 $n-1$ 分解为 $2^sd$ 并推导 Miller–Rabin 的平方链；实现教学版测试；并明确概率性测试的错误方向、轮数与生产级参数边界。

## 从“试除到平方根”太慢开始

判断 $n$ 是否为素数，试除到 $\sqrt n$ 对小整数很好，但密码学候选数有数千比特。我们需要快速排除绝大多数合数，而不是立刻分解它。概率性素性测试的关键不对称性是：发现一个**见证者**可确定合数；多轮未发现见证者只给出“极可能为素数”。

## 直觉与定义：费马小定理与它的漏洞

若 $p$ 为素数且 $a\not\equiv0\pmod p$，则

$$a^{p-1}\equiv1\pmod p.$$

因此若 $a^{n-1}\not\equiv1\pmod n$，$n$ 必为合数。但逆命题错误：Carmichael 数如 $561$ 会对所有与它互素的 $a$ 通过费马测试。只检查最终等于 1 忽略了中间平方链中的异常。

## Miller–Rabin 的平方链

对奇数 $n>2$，写

$$n-1=2^s d,\qquad d\text{ 为奇数}.$$

若 $n$ 是素数，$x=a^d\bmod n$ 要么为 $1$，要么连续平方

$$x,x^2,x^{2^2},\ldots,x^{2^{s-1}}$$

中的某项为 $-1\pmod n$。原因是最后一项平方得到 $a^{n-1}=1$；模素数域中 $y^2=1$ 只有 $y=\pm1$ 两个根。若链在到达 1 前没有经过 -1，就暴露了合数模数中“额外平方根”的结构，$a$ 是合数见证者。

对合数 $n$，随机底数把它误判为“可能素数”的概率每轮至多 $1/4$（标准 Miller–Rabin 结论），独立 $r$ 轮后至多 $4^{-r}$。这是随机选择底数、正确实现和输入范围前提下的界，不是“任何代码都有这个保证”。

## 可运行教学实现

```python
from projects.crypto_toybox.primality import miller_rabin_report, miller_rabin_report_certificate

composite = miller_rabin_report(561, [2, 3, 5])
assert not composite["probably_prime"]
assert composite["witnesses"]
assert composite["certificate"]["all_rounds_replay"]
assert miller_rabin_report_certificate(561, [2, 3, 5], composite)["valid"]

prime = miller_rabin_report(1_000_000_007, [2, 3, 5])
assert prime["probably_prime"]
assert prime["certificate"]["valid"]
```

运行 `python -m unittest projects.crypto_toybox.test_primality`。每一轮保留 $n-1=2^sd$、底数和完整平方链；`miller_rabin_round_certificate` 可逐项重放它。报告只接受调用者明确传入的教学底数，并把发现的见证者单独列出；`miller_rabin_report_certificate` 还会从候选数和底数表重新生成整份报告，拒绝将 `probably_prime`、见证者列表或轮次单独篡改。因此 `probably_prime=False` 带有可复算的合数证据，`True` 始终只是这些轮次下的“可能素数”。每轮由一次 $O(\log n)$ 次模乘的快速幂主导；对大整数，实际成本取决于乘法算法和运行时。真实密钥候选的底数与候选数必须来自密码学安全随机源和经审计库策略。

## 正确性与可验证实验

验证的最强性质是单向的：若函数返回 `False`，可记录底数和平方链，人工复算以确认证据；报告级证书则核对“布尔结论是否与见证者列表一致”。对小 $n$，用试除真值表枚举比较；对 Carmichael 数 $561,1105,1729$，展示费马测试可能通过而 Miller–Rabin 常找到见证者。

函数返回 `True` 不等于形式证明素数；将 API 命名为 `is_probable_prime` 是安全设计的一部分，防止调用者误以为得到了确定性证书。

## 失败案例与工程边界

- **错误随机源**：可预测随机数会危及密钥生成，即使素性测试数学正确。
- **轮数硬编码**：安全级别、候选位数和威胁模型决定轮数；生产库应采用其审计过的策略。
- **只测素性，不生成安全素数参数**：RSA/DH 还涉及因子结构、指数选择、侧信道和协议要求。
- **数据相关时间**：大整数模幂与分支可能泄露秘密；候选素性阶段与私钥运算的侧信道要求不同，仍应使用成熟库。

## 常见误区

1. “通过一轮就证明是素数。”错误：只能降低合数误判概率。
2. “费马小定理反过来也成立。”错误：Carmichael 数是系统反例。
3. “Miller–Rabin 会把素数判成合数。”在正确算法和合法底数下不会；错误方向是合数偶尔通过。
4. “概率性算法不适合密码学。”错误：恰当的概率界和安全随机源正是现代密码工程的一部分。

## 练习

1. **基础题**：将 $560$ 写成 $2^sd$，列出 $n=561$、某个底数的平方链。
2. **推导题**：证明在素数模数下，$y^2\equiv1$ 只有 $y\equiv\pm1$ 两个解。
3. **编码题**：实现朴素费马测试并寻找能通过它的 Carmichael 数，和 Miller–Rabin 对拍。
4. **开放题**：查阅成熟大整数库的素性测试接口，说明其“可能素数”语义与密钥生成流程如何组合。

## 练习答案提示

1. $560=2^4\cdot35$；选一个与 561 互素的底数，依次平方并记录是否出现 $-1\bmod561$，区分分解和见证链。
2. 若 $y^2\equiv1\pmod p$，则 $(y-1)(y+1)\equiv0$；素数模数无零因子，故只能有两类解。
3. 用 Carmichael 数显示费马同余的单向性；对同一底数集合比较两种测试，确保候选底数合法且测试结果命名为“可能素数”。
4. 将库的概率界、底数选择和随机源与密钥生成流程分开描述；实际密钥还需要安全随机候选、参数检查和成熟实现。

## 延伸

素性测试只是一条密码学供应链的开始。继续阅读[RSA](/number-theory-crypto/rsa)了解素数如何进入密钥生成，并把快速模幂的性能与侧信道问题联系到[模运算](/number-theory-crypto/modular-arithmetic)。
