---
title: 中国剩余定理：拆分模运算
description: 从互素模数的逆元构造推导中国剩余定理，理解唯一性、算法实现与 RSA-CRT 故障边界。
courseLevel: "2–3（推导、算法与安全工程）"
prerequisites: "同余、最大公约数、扩展欧几里得与模逆元"
estimatedMinutes: 50
experiment: "实现通用 CRT 合并器，并验证互素与非互素输入"
---

# 中国剩余定理：拆分模运算

## 学习目标

读完后，你能构造并证明互素模数同余方程组的唯一解；实现会拒绝不合法输入的 CRT 合并器；并能说明 RSA-CRT 为什么快、为何一次故障输出会泄露私钥。

## 从一只“不同刻度的钟”开始

某事件距现在的分钟数 $x$ 除以 $3$ 余 $2$、除以 $5$ 余 $3$。单独看两个条件都给出无限多个候选；合在一起却在模 $15$ 意义下锁定一个答案。中国剩余定理（CRT）说明何时这种“分而治之”既完整又不会冲突。

## 直觉与严格定义

令正整数 $m_1,\ldots,m_k$ 两两互素，给定余数 $a_1,\ldots,a_k$。方程组

$$x\equiv a_i\pmod {m_i}\quad(i=1,\ldots,k)$$

在模 $M=\prod_i m_i$ 下恰有一个解。这里“两两互素”是 $\gcd(m_i,m_j)=1$（$i\ne j$）；它保证稍后出现的逆元一定存在。

## 构造：每个积木只影响自己的余数

令 $M_i=M/m_i$。因为 $m_i$ 与 $M_i$ 互素，存在逆元 $y_i$ 满足

$$M_i y_i\equiv1\pmod {m_i}.$$

构造

$$x=\sum_{i=1}^{k} a_iM_i y_i\pmod M.$$

检查第 $j$ 个模数：第 $j$ 项余 $a_j$；所有 $i\ne j$ 的项都含因子 $m_j$，余 $0$。因此 $x$ 同时满足全部同余。

唯一性也只需一行：若 $x,z$ 都满足，$m_i\mid(x-z)$ 对所有 $i$ 成立；模数两两互素，所以 $M\mid(x-z)$，即 $x\equiv z\pmod M$。

对 $x\equiv2\pmod3,x\equiv3\pmod5$，$M=15$。$M_1=5$ 的模 $3$ 逆元是 $2$，$M_2=3$ 的模 $5$ 逆元是 $2$，故

$$x\equiv2\cdot5\cdot2+3\cdot3\cdot2=38\equiv8\pmod{15}.$$

## 算法：逐个合并而不是假设所有模数互素

两个同余 $x\equiv a\pmod m$、$x\equiv b\pmod n$ 可以写成 $x=a+mt$。代入后需解

$$mt\equiv b-a\pmod n.$$

它有解当且仅当 $g=\gcd(m,n)$ 整除 $b-a$。先除以 $g$，再在互素的 $m/g$ 与 $n/g$ 上求逆元，即可得到模 $\mathrm{lcm}(m,n)$ 的合并解。这比只实现“完全互素版”更能显式表达边界。

```python
from projects.crypto_toybox.chinese_remainder import chinese_remainder, combine_congruences

assert chinese_remainder([(2, 3), (3, 5), (2, 7)]) == (23, 105)
assert combine_congruences((1, 4), (3, 6)) == (9, 12)
```

运行 `python -m unittest projects.crypto_toybox.test_chinese_remainder`。实现以 `(residue, modulus)` 表示每条同余，不只适用于两两互素模数；测试用三条互素条件恢复一个隐藏整数的模类，也验证 $x\equiv1\pmod4,x\equiv3\pmod6$ 合并为 $x\equiv9\pmod{12}$。每次合并由一次扩展欧几里得主导，时间约为 $O(\log\min(m,n))$ 个大整数算术步骤；但实际密码库中，大整数乘法和常数时间实现才是主要工程成本。

## 正确性与可验证实验

每次 `combine_congruences` 返回后，断言 `result % m == a % m` 和 `result % n == b % n`；再生成小模数和一个秘密 $x$，由 $x\bmod m_i$ 还原并比对 $x\bmod M$。另测两类负例：

- $x\equiv0\pmod2,x\equiv1\pmod2$ 不相容，必须报错；
- $x\equiv1\pmod4,x\equiv3\pmod6$ 相容，合并后为 $x\equiv9\pmod{12}$，说明非互素不等于无解。

## RSA-CRT：更快，也更需要防护

若 RSA 模数为 $N=pq$，私钥指数为 $d$，可计算 $m_p=c^{d\bmod(p-1)}\bmod p$ 与 $m_q=c^{d\bmod(q-1)}\bmod q$，再用 CRT 合并。两个约半长度的模幂通常显著快于一次模 $N$ 的模幂。

但若硬件故障让其中一个分支错误，攻击者得到正确结果 $s$ 与错误结果 $s'$ 时，常可由 $\gcd(s-s',N)$ 恢复 $p$ 或 $q$。生产实现因此需要消息盲化、结果校验和抗故障设计；绝不能把上面的教学代码当作 RSA 私钥运算器。

## 一个分支错了，为什么差值会泄露因子

设 CRT 私钥运算的 $p$ 分支被故障改写，而 $q$ 分支仍正确。正确输出 $s$ 与错误输出 $s'$ 满足

$$
s\equiv s'\pmod q,\qquad s\not\equiv s'\pmod p.
$$

所以 $q$ 整除 $s-s'$，但 $p$ 不整除它；对 $N=pq$ 求最大公约数便得到

$$
\gcd(s-s',N)=q.
$$

下面的受限教学实验要求显式传入不超过 1000 的小质因子，并且只把一个分支残余加一。它不是可用于真实设备的私钥运算或故障注入接口：价值在于把“一个分支错误”的前提和差值为何携带另一因子的原因放在同一份可重放算术记录里。

```python
from projects.crypto_toybox.chinese_remainder import (
    toy_rsa_crt_fault_certificate,
    toy_rsa_crt_fault_report,
)

report = toy_rsa_crt_fault_report(5, 11, 3, 7, faulted_branch="p")
assert report["correct_matches_direct_private_power"]
assert report["difference_gcd"] == 11  # q 分支仍正确，因此 q 整除差值
assert report["cofactor"] == 5
assert toy_rsa_crt_fault_certificate(5, 11, 3, 7, "p", report)
```

对 $p=5,q=11,N=55$，正确 CRT 结果为 $28$、故障结果为 $39$，故 $\gcd(28-39,55)=11$。这并不表示任何一次计算错误都会立即泄露因子：需要攻击者能够得到相关的正确/故障输出，且故障模式恰好保留一个分支。现实库还必须防止错误结果外泄、使用盲化并验证私钥运算；不要将这个小整数演示外推成攻击成熟实现的方法。

## 失败案例与工程边界

- **逆元不存在**：模数不互素时不能直接把 $M_i$ “除掉”；必须先检查 gcd。
- **整数溢出**：固定宽度语言的 $m\cdot n$ 可能溢出，破坏结果甚至安全性；使用经审计的大整数库。
- **泄露分支与时间**：根据秘密选择不同路径或使用普通大整数 `%`，可能暴露 RSA 私钥信息。
- **错误的安全推断**：CRT 只保证算术正确，不能替代 OAEP/PSS 填充、随机数和协议认证。

## 常见误区

1. “模数不互素就一定无解。”错误：相容条件是余数之差可被 gcd 整除。
2. “解就是一个普通整数。”错误：解是模最小公倍数的等价类。
3. “CRT 能让任何密码算法安全。”错误：它是加速和结构工具，不提供语义安全。
4. “合并后不必复核。”错误：在故障敏感场景，验证结果是安全边界的一部分。

## 练习

1. **基础题**：手算 $x\equiv1\pmod4,x\equiv3\pmod5$ 的最小非负解。
2. **推导题**：证明若两个解都满足两两互素模数的同余组，它们之差可被乘积 $M$ 整除。
3. **编码题**：为 `crt` 编写随机化测试，覆盖互素、相容非互素和不相容三种输入；验证每个返回余数。
4. **开放题**：运行 `toy_rsa_crt_fault_report`，说明错误 $p$ 分支时为何恢复 $q$；再列出库设计中不暴露错误结果的两种策略。

## 练习答案提示

1. 令 $x=1+4t$，代入模 5 条件得 $4t\equiv2$，解出 $t$ 后取最小非负代表元。
2. 两个解之差同时被每个互素模数整除；由互素性可被乘积整除，因此解在模 $M$ 下唯一。
3. 生成后逐一验证返回值对每个模数的余数；非互素相容性要检查余数差是否被 gcd 整除，不相容输入必须明确失败。
4. 保留正确的 $q$ 分支使 $q\mid(s-s')$，再检查差值的 gcd；此例仍依赖攻击者能得到或比较错误私钥运算结果。库可重算/验证结果、使用盲化并且不把故障细节暴露给请求方。

## 延伸

先掌握[扩展欧几里得与模逆元](/number-theory-crypto/extended-euclid)，再阅读[RSA](/number-theory-crypto/rsa)中的 CRT 私钥优化。后续可进入素数测试和有限域：它们同样依赖“哪些操作可以安全地在模空间中进行”的精确条件。
