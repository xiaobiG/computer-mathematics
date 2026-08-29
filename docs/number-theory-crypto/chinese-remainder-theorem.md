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

## 严格陈述

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

它有解当且仅当 $g=\gcd(m,n)$ 整除 $b-a$。先除以 $g$，再在互素的 $m/g$ 与 $n/g$ 上求逆元，即可得到模 $\operatorname{lcm}(m,n)$ 的合并解。这比只实现“完全互素版”更能显式表达边界。

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
4. **开放题**：调研并解释 RSA-CRT 故障攻击的“一个分支错误”前提；列出库设计中不暴露错误结果的两种策略。

## 延伸

先掌握[扩展欧几里得与模逆元](/number-theory-crypto/extended-euclid)，再阅读[RSA](/number-theory-crypto/rsa)中的 CRT 私钥优化。后续可进入素数测试和有限域：它们同样依赖“哪些操作可以安全地在模空间中进行”的精确条件。
