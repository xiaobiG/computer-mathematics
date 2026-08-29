# 数值误差与浮点数

计算机操作的是有限精度的近似值。深度版将表示误差、问题条件、算法稳定性和工程容差分开讨论，避免把数值问题误化为“多保留几位小数”。

## 课程地图

1. 二进制小数与 IEEE 754
2. 舍入、溢出与 NaN
3. 绝对误差、相对误差与消去误差
4. 条件数与算法稳定性
5. 求根、积分与线性方程的数值解
6. 浮点比较、Kahan 求和与工程实践

## 当前深度版

- [浮点数表示](/numerical-computing/floating-point)：IEEE 754、舍入、NaN 与尺度相关比较；
- [绝对误差、相对误差与消去](/numerical-computing/error-propagation)：误差传播、相减条件数与零参考值边界；
- [条件数](/numerical-computing/condition-number)：用可运行的 $2\\times2$ 扰动报告对照病态问题、前向/后向误差与稳定算法；
- [算法稳定性：二次公式](/numerical-computing/algorithmic-stability)：从 Vieta 关系推导避免消去的小根公式，并以高精度参考值审计前向误差；
- [浮点比较、容差与属性测试](/numerical-computing/tolerances-property-testing)：尺度相关契约、残差与可复现实验；
- [牛顿法](/numerical-computing/newton-method)：二次收敛、停止准则与区间保护；
- [割线法](/numerical-computing/secant-method)：用两点函数值替代导数的快速求根；
- [迭代解线性方程组](/numerical-computing/iterative-linear-systems)：Jacobi、Gauss–Seidel、残差与收敛/发散证据；
- [数值微分](/numerical-computing/numerical-differentiation)：截断误差、舍入误差与步长选择；
- [数值插值](/numerical-computing/interpolation)：差商、牛顿形式、Runge 现象与外推边界；
- [数值积分](/numerical-computing/numerical-integration)：梯形法、Simpson 法与自适应切分边界；
- [随机模拟的误差与可复现性](/numerical-computing/stochastic-simulation-reproducibility)：抽样波动、固定种子与可复核报告；
- [数值计算深度版路线](/numerical-computing/rewrite-plan)：稳定求和、数值线性代数与工程实验。

第一个实验：复现并解释 `0.1 + 0.2 !== 0.3`。
