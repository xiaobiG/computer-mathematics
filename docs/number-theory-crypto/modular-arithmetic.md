---
courseLevel: "1–2（核心概念与算法）"
prerequisites: "整除、余数与二进制"
estimatedMinutes: 50
experiment: "实现快速幂并统计乘法次数"
title: 模运算与快速幂：为什么大指数不必先算出来
description: 从同余封闭性推导重复平方，证明循环不变量并理解复杂度与侧信道边界。
---

# 模运算与快速幂：为什么大指数不必先算出来

## 文章元信息

- **建议阅读层级**：1–3 · 同余模型、算法证明与安全边界
- **前置知识**：整数除法、二进制表示、循环不变量
- **预计学习时间**：50 分钟
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

## 算法实现与正确性

```python
from projects.crypto_toybox.main import mod_pow_trace, mod_pow_trace_certificate

result, events = mod_pow_trace(3, 13, 7)
assert result == pow(3, 13, 7)
assert [event.bit for event in events] == [1, 0, 1, 1]
assert mod_pow_trace_certificate(3, 13, 7, result, events)
```

`ModPowEvent` 记录每轮处理前的剩余指数、当前位、更新后的 `result`/`base` 和右移结果。`mod_pow_trace_certificate` 从原始输入独立重放每次模乘，因此能发现“最终答案偶然正确、某一位的更新却写错”的问题。不变量是：初始指数为 $E$ 时，$result\cdot base^{exponent}\equiv a^E\pmod n$。若最低位为 1，将一个 `base` 移到 `result`；平方 `base` 且指数右移保持等价。指数归零时不变量给出结果正确。时间为 $O(\log e)$ 次模乘，保留教学轨迹为 $O(\log e)$ 额外空间；普通 `mod_pow` 不保留轨迹，仍为 $O(1)$（忽略大整数位数）。

### 控制流为何泄露信息

对非零指数，循环总会做 `bit_length(e)` 次平方，却只在位为 1 时做额外乘法。因此总模乘数为

$$\operatorname{bit\_length}(e)+\operatorname{popcount}(e).$$

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

1. **基础**：手算 $3^{13}\bmod7$ 的平方链。
2. **推导**：用不变量证明最低位为 0 时循环仍保持等价。
3. **编码**：测试模数 1、负指数、底数为负和指数为 0。
4. **开放**：比较“平方—乘”与 Montgomery ladder 的控制流，说明后者为何更适合秘密指数。

## 练习答案提示

1. 将 $13$ 写成二进制 $1101$，逐次平方得到幂，再只乘对应的 1 位项并随时取模；不要先计算完整整数幂。
2. 循环不变量可写为 `result * base^remaining ≡ original_base^original_exponent (mod m)`；最低位为 0 时只平方 `base` 并右移指数，等价式仍保持。
3. 模数 1 是退化环，负指数需要先求逆元，负底数应按模规范化，零指数在合法模数下返回乘法单位元；分别定义/测试异常契约。
4. 平方—乘的分支随指数位变化，可能形成可观测模式；ladder 每位执行固定形态的操作，更适合秘密标量，但真实实现仍需审计库、恒定时间大整数和完整协议防护。

## 延伸与下一步

[模逆元](/number-theory-crypto/extended-euclid)给出负指数/除法的合法条件；[RSA](/number-theory-crypto/rsa)将快速幂嵌入公钥协议，但必须额外处理填充与攻击面。
