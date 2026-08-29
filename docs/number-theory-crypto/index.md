# 密码学的模运算与数论

现代密码系统依靠严格的数学性质、清晰的安全假设和经审计的实现，而不是算法保密或“自己写出来能运行”。

## 课程地图

1. 整除、质数与最大公约数
2. 同余、模逆元与快速幂
3. 欧拉函数、费马小定理与中国剩余定理
4. RSA 的数学结构
5. 数字签名与公开验证
6. 密钥交换与椭圆曲线的直觉
7. 哈希、KDF、随机数与安全工程边界

## 当前深度版

- [模运算与快速幂](/number-theory-crypto/modular-arithmetic)：重复平方的不变量、复杂度与侧信道边界；
- [扩展欧几里得与模逆元](/number-theory-crypto/extended-euclid)：贝祖等式、逆元存在条件与算法证明；
- [中国剩余定理](/number-theory-crypto/chinese-remainder-theorem)：构造、唯一性、通用合并和 RSA-CRT 故障边界；
- [有限域、群与离散对数直觉](/number-theory-crypto/finite-fields-groups)：乘法群、元素阶、生成元与小子群边界；
- [RSA](/number-theory-crypto/rsa)：模逆元、欧拉/CRT 正确性、快速幂与裸 RSA 的失败模式；
- [数字签名](/number-theory-crypto/digital-signatures)：RSA 验签等式、公开验证、HMAC/加密的边界与裸签名风险；
- [Diffie–Hellman](/number-theory-crypto/diffie-hellman)：共享秘密的推导、离散对数假设与中间人攻击；
- [哈希与密码存储](/number-theory-crypto/hashing-passwords)：KDF、盐、成本参数与在线/离线猜测边界；
- [消息认证码：HMAC](/number-theory-crypto/message-authentication-codes)：带密钥完整性、篡改检测与重放边界；
- [素性测试](/number-theory-crypto/primality-testing)：Miller–Rabin、Carmichael 数与概率性证书；
- [椭圆曲线密码学预备](/number-theory-crypto/elliptic-curve-prelude)：有限域点群、标量乘法与安全实现边界；
- [密码学与数论深度版路线](/number-theory-crypto/rewrite-plan)：原语、协议和攻击面之间的学习路径；
- [密码学玩具箱](/projects/crypto-toybox)：仅教学用途的可测试数论实验。

> 教学实现只用于理解原理。真实系统应使用经过审计的成熟密码库。
