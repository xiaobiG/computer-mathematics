# 浮点数错误博物馆

运行方式与数值错误案例说明见站点中的《项目：浮点数错误博物馆》；`representation.py` 可查看 binary64 字段、相邻可表示数和 ULP 间距，`integration.py` 用复合梯形/Simpson 法报告网格加密误差比，`simulation.py` 另提供固定种子、多次重复的蒙特卡洛抽样误差报告，`linear_iterations.py` 提供带残差/步长轨迹的 Jacobi 与 Gauss–Seidel 教学实现，`root_finding.py` 用受保护牛顿法记录符号变化区间与二分回退，`interpolation.py` 用差商和嵌套求值展示多项式插值，`conditioning.py` 则用可复核的 $2\\times2$ 病态线性系统对照条件数、输入扰动、解变化与残差。
