# 密码学的模运算与数论

现代密码系统依靠严格的数学性质、清晰的安全假设和经审计的实现，而不是算法保密或“自己写出来能运行”。

## 课程地图

1. 整除、质数与最大公约数
2. 同余、模逆元与快速幂
3. 欧拉函数、费马小定理与中国剩余定理
4. RSA 的数学结构
5. 密钥交换与椭圆曲线的直觉
6. 哈希、KDF、随机数与安全工程边界

## 当前深度版

- [模运算与快速幂](/number-theory-crypto/modular-arithmetic)：重复平方的不变量、复杂度与侧信道边界；
- [扩展欧几里得与模逆元](/number-theory-crypto/extended-euclid)：贝祖等式、逆元存在条件与算法证明；
- [中国剩余定理](/number-theory-crypto/chinese-remainder-theorem)：构造、唯一性、通用合并和 RSA-CRT 故障边界；
- [RSA](/number-theory-crypto/rsa)：模逆元、欧拉/CRT 正确性、快速幂与裸 RSA 的失败模式；
- [密码学与数论深度版路线](/number-theory-crypto/rewrite-plan)：原语、协议和攻击面之间的学习路径；
- [密码学玩具箱](/projects/crypto-toybox)：仅教学用途的可测试数论实验。

> 教学实现只用于理解原理。真实系统应使用经过审计的成熟密码库。
