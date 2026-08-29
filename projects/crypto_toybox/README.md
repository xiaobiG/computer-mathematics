# 密码学玩具箱

仅用于理解数论、有限域乘法群、教学 Diffie–Hellman、RSA、教学签名验签与椭圆曲线群运算的数学结构；不应用于真实安全场景。RSA 构造会检查小质数因子与公开指数前提，`rsa_round_trip_report` 用含非互素代表元的小样例审计 CRT 正确性；`chinese_remainder.py` 合并互素或相容的非互素同余条件，`finite_group.py` 限制在小素数域中枚举元素阶、生成元和离散对数，`diffie_hellman.py` 展示诚实与中间人交换的不同转录，`elliptic_curve.py` 演示小素域上的点加和 double-and-add。完整说明见站点中的《项目：密码学玩具箱》。
