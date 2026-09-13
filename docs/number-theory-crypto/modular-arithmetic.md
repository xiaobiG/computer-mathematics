---
courseLevel: "1–2（核心概念与算法）"
prerequisites: "整除、余数与二进制"
estimatedMinutes: 65
experiment: "重放逐位快速幂轨迹，验证不变量并统计控制流成本"
title: 模运算与快速幂：为什么大指数不必先算出来
description: 从同余封闭性推导重复平方，以逐位轨迹证明循环不变量，并理解复杂度与侧信道边界。
---

# 模运算与快速幂：为什么大指数不必先算出来

## 文章元信息

- **建议阅读层级**：1–3 · 同余模型、算法证明与安全边界
- **前置知识**：整数除法、二进制表示、循环不变量
- **预计学习时间**：65 分钟
- **配套实验**：[密码学玩具箱](/projects/crypto-toybox)

## 学习目标

- 使用同余将大数运算约化为有限模数内运算；
- 用重复平方计算 $a^e\bmod n$ 并证明其不变量；
- 区分教学算法的复杂度正确性与生产密码实现的侧信道要求。

## 从一个计算问题开始

RSA 解密需要计算 $m^d\bmod n$，其中 $d$ 有数千位。若先计算 $m^d$，内存和时间都会耗尽；为何每一步先取模仍能保证最终余数完全相同？

## 定义与推导

若 $n$ 整除 $a-b$，记 $a\equiv b\pmod n$。同余在加法和乘法下封闭：

$$a\equiv b\pmod n\Rightarrow ac\equiv bc\pmod n.$$

因此 $((a\bmod n)(b\bmod n))\bmod n=(ab)\bmod n$。将指数写为二进制，$e=\sum_i e_i2^i$；依次平方得到 $a^{2^i}$，只有 $e_i=1$ 时乘入结果。指数每轮右移一位，循环次数为位数而非指数值。

## 手算轨迹：每一位到底保存了什么

以 $3^{13}\bmod7$ 为例，$13=(1101)_2$。算法从最低位开始读取，因此位序是 $1,0,1,1$。令原指数为 $E$，每一轮开始时维护

$$
\mathrm{result}\cdot\mathrm{base}^{\mathrm{exponent}}
\equiv a^E\pmod n.
$$

下表的 `result`、`base` 和 `exponent` 都是本轮处理**后**的值；最后一列不是额外计算，而是把状态代回不变量的检查。

| 轮次 | 处理前指数与最低位 | 处理后 `result` | 处理后 `base` | 右移后指数 | 不变量左侧（模 7） |
| --- | --- | --- | --- | --- | --- |
| 开始 | $13$, $-$ | $1$ | $3$ | $13$ | $1\cdot3^{13}\equiv3$ |
| 1 | $13$, $1$ | $3$ | $3^2\equiv2$ | $6$ | $3\cdot2^6\equiv3$ |
| 2 | $6$, $0$ | $3$ | $2^2\equiv4$ | $3$ | $3\cdot4^3\equiv3$ |
| 3 | $3$, $1$ | $3\cdot4\equiv5$ | $4^2\equiv2$ | $1$ | $5\cdot2\equiv3$ |
| 4 | $1$, $1$ | $5\cdot2\equiv3$ | $2^2\equiv4$ | $0$ | $3\cdot4^0\equiv3$ |

指数归零时，不变量左侧只剩 `result`，所以答案是 $3$。这也解释了为何不能只看最终值：每一行都要同时更新“已收集的 1 位贡献”、下一次的平方底数和未处理的高位。

## 不变量为何在两种位上都成立

设某轮开始时剩余指数为 $q=2q'+b$，其中 $b\in\{0,1\}$ 是最低位；并假设当前状态满足

$$
rB^q\equiv a^E\pmod n.
$$

若 $b=0$，算法保留 $r$，再令 $B'=B^2,q'=q/2$。于是

$$
r(B')^{q'}=r(B^2)^{q'}=rB^{2q'}=rB^q\equiv a^E\pmod n.
$$

若 $b=1$，算法先把当前 $B$ 乘入结果：$r'=rB$，然后仍令 $B'=B^2,q'=(q-1)/2$。于是

$$
r'(B')^{q'}=rB(B^2)^{q'}=rB^{2q'+1}=rB^q\equiv a^E\pmod n.
$$

两种分支都保持同一不变量；右移使 $q$ 严格减小，故非负指数必会结束。终止时 $q=0$，$B^0=1$，得到 $r\equiv a^E\pmod n$。这就是循环正确性的完整理由，而不只是“二进制很快”。

## 算法实现与正确性

```python
from projects.crypto_toybox.main import mod_pow_trace, mod_pow_trace_certificate

result, events = mod_pow_trace(3, 13, 7)
assert result == pow(3, 13, 7)
assert [event.bit for event in events] == [1, 0, 1, 1]
assert mod_pow_trace_certificate(3, 13, 7, result, events)
```

`ModPowEvent` 记录每轮处理前的剩余指数、当前位、更新后的 `result`/`base` 和右移结果；它正是上表的可重放版本。`mod_pow_trace_certificate` 从原始输入独立重放每次模乘，因此能发现“最终答案偶然正确、某一位的更新却写错”的问题。把第二轮的 `result_after` 从 $3$ 篡改成 $4$，即使你保留最终答案，证书也会拒绝这条不满足不变量的轨迹。时间为 $O(\log e)$ 次模乘，保留教学轨迹为 $O(\log e)$ 额外空间；普通 `mod_pow` 不保留轨迹，仍为 $O(1)$（忽略大整数位数）。

### 控制流为何泄露信息

对非零指数，循环总会做 `bit_length(e)` 次平方，却只在位为 1 时做额外乘法。因此总模乘数为

$$\mathrm{bit\_length}(e)+\mathrm{popcount}(e).$$

```python
from projects.crypto_toybox.main import mod_pow_operation_profile

assert mod_pow_operation_profile(8).total_modular_multiplications == 5   # 1000
assert mod_pow_operation_profile(15).total_modular_multiplications == 8  # 1111
```

这个函数只把**公开教学输入**的控制流依赖变成可检查数值；它不是计时器、攻击工具或常量时间实现。真实设备的可观察性还受编译器、缓存、分支预测和大整数算法影响，但只要秘密位决定分支，设计就不应把“平均运行快”误当作安全。

## 失败案例与工程边界

普通实现的 `if exponent & 1` 和运行时间可能泄漏指数位；本课的 `mod_pow_trace` 更是有意将每一位公开，绝不能用于私钥。生产密码只能使用经审计库中的常量时间实现，还需要安全随机数、填充、协议验证和密钥管理。负指数意味着模逆元，只有底数与模数互素时才有定义。

## 常见误区

- 模运算不能把除法随意分配：除法需要模逆元。
- $O(\log e)$ 不代表所有成本很小，大整数乘法随位数增长。
- `pow` 输出正确不证明自写密码系统安全。

## 练习

1. **基础**：手算 $3^{13}\bmod7$ 的完整五行轨迹，并逐行核对不变量左侧。
2. **推导**：从 $q=2q'+b$ 出发，分别完成 $b=0$ 与 $b=1$ 的不变量保持证明；指出终止性使用了哪个整数性质。
3. **编码**：篡改 `mod_pow_trace(3, 13, 7)` 的第二个 `result_after`，确认 `mod_pow_trace_certificate` 拒绝；再测试模数 1、负指数、底数为负和指数为 0 的合同。
4. **开放**：比较“平方—乘”与 Montgomery ladder 的控制流，说明后者为何更适合秘密指数，并说明固定操作形态仍不等于完整的生产安全证明。

## 练习答案提示

1. 位处理顺序是最低位优先的 $1,0,1,1$；每行同时列出乘入后的 `result`、平方后的 `base` 和右移指数，不能只写若干幂值。
2. 写成 $q=2q'+b$ 后，$b=0$ 用 $r(B^2)^{q'}$，$b=1$ 用 $(rB)(B^2)^{q'}$；终止性来自每轮把正整数指数整除 2。
3. 证书应拒绝中间事件，即使最后 `result` 仍写成正确余数。模数 1 是退化环，负指数需要先求逆元，负底数应按模规范化，零指数在合法模数下返回乘法单位元；分别定义/测试异常契约。
4. 平方—乘的分支随指数位变化，可能形成可观测模式；ladder 每位执行固定形态的操作，更适合秘密标量，但真实实现仍需审计库、恒定时间大整数和完整协议防护。

## 延伸与下一步

[模逆元](/number-theory-crypto/extended-euclid)给出负指数/除法的合法条件；[RSA](/number-theory-crypto/rsa)将快速幂嵌入公钥协议，但必须额外处理填充与攻击面。
