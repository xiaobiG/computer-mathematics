import { defineConfig } from 'vitepress'
import markdownItKatex from 'markdown-it-katex'

const series = [
  { text: '程序员的线性代数', link: '/linear-algebra/' },
  { text: '算法背后的离散数学', link: '/discrete-math/' },
  { text: '机器学习需要的概率论', link: '/probability-ml/' },
  { text: '数值误差与浮点数', link: '/numerical-computing/' },
  { text: '密码学的模运算与数论', link: '/number-theory-crypto/' },
]

export default defineConfig({
  lang: 'zh-CN',
  title: '计算机数学',
  description: '从原理到代码，建立可计算的数学直觉。',
  base: '/computer-mathematics/',
  cleanUrls: true,
  markdown: {
    config: (md) => md.use(markdownItKatex),
  },
  themeConfig: {
    nav: [
      { text: '学习路线', link: '/roadmap' },
      { text: '课程架构', link: '/curriculum-architecture' },
      { text: '成熟度看板', link: '/course-maturity' },
      { text: '12 周计划', link: '/study-plan' },
      { text: '专题系列', items: series },
      { text: '综合项目', link: '/projects/' },
      { text: '术语表', link: '/glossary' },
      { text: '编辑流程', link: '/editorial-workflow' },
      { text: '项目状态', link: '/about' },
      { text: '写作规范', link: '/contributing' },
    ],
    sidebar: {
      '/linear-algebra/': [{ text: '程序员的线性代数', items: [{ text: '开始学习', link: '/linear-algebra/' }, { text: 'v0.2 重写清单', link: '/linear-algebra/rewrite-plan' }, { text: '向量与点积', link: '/linear-algebra/vectors-dot-product' }, { text: '线性组合、基与维度', link: '/linear-algebra/linear-combinations-basis' }, { text: '矩阵的四个基本子空间', link: '/linear-algebra/four-fundamental-subspaces' }, { text: '矩阵乘法与线性变换', link: '/linear-algebra/matrix-multiplication' }, { text: '高斯消元：解线性方程组', link: '/linear-algebra/gaussian-elimination' }, { text: 'LU 分解与主元选择', link: '/linear-algebra/lu-factorization-pivoting' }, { text: '正交投影、Gram–Schmidt 与 QR', link: '/linear-algebra/orthogonal-projection-qr' }, { text: '最小二乘：没有精确解怎么办', link: '/linear-algebra/least-squares' }, { text: '特征值与 PCA', link: '/linear-algebra/eigenvalues-pca' }, { text: '幂迭代：主特征方向', link: '/linear-algebra/power-iteration' }, { text: 'SVD：矩阵的通用分解', link: '/linear-algebra/svd' }, { text: '低秩图像压缩', link: '/linear-algebra/low-rank-image-compression' }, { text: 'Jacobian、Hessian 与自动微分', link: '/linear-algebra/jacobian-hessian-autodiff' }] }],
      '/discrete-math/': [{ text: '算法背后的离散数学', items: [{ text: '开始学习', link: '/discrete-math/' }, { text: '深度版路线', link: '/discrete-math/rewrite-plan' }, { text: '命题逻辑、量词与归纳法', link: '/discrete-math/logic-induction-proofs' }, { text: '集合、关系、等价类与偏序', link: '/discrete-math/sets-relations-orders' }, { text: '循环不变量与二分查找', link: '/discrete-math/loop-invariants' }, { text: '复杂度：算法规模如何影响时间', link: '/discrete-math/asymptotic-complexity' }, { text: '图、树、二分图与拓扑排序', link: '/discrete-math/graph-foundations-topological-sort' }, { text: 'BFS：图中的最短步数', link: '/discrete-math/breadth-first-search' }, { text: 'DFS：发现时间与显式栈', link: '/discrete-math/depth-first-search' }, { text: '强连通分量：互相可达与凝聚图', link: '/discrete-math/strongly-connected-components' }, { text: '递推关系与分治复杂度', link: '/discrete-math/recurrences' }, { text: 'Dijkstra：带权图最短路', link: '/discrete-math/dijkstra' }, { text: 'Bellman–Ford：负边最短路', link: '/discrete-math/bellman-ford' }, { text: 'Floyd–Warshall：全源最短路', link: '/discrete-math/floyd-warshall' }, { text: '最大流最小割：残量网络', link: '/discrete-math/max-flow-min-cut' }, { text: '并查集与动态连通性', link: '/discrete-math/union-find' }, { text: '贪心算法：交换论证', link: '/discrete-math/greedy-exchange-arguments' }, { text: '动态规划：状态与 DAG', link: '/discrete-math/dynamic-programming-dag' }, { text: 'P、NP 与多项式归约', link: '/discrete-math/p-np-reductions' }] }],
      '/probability-ml/': [{ text: '机器学习需要的概率论', items: [{ text: '开始学习', link: '/probability-ml/' }, { text: '深度版路线', link: '/probability-ml/rewrite-plan' }, { text: '条件概率与贝叶斯更新', link: '/probability-ml/bayes' }, { text: '联合、边缘与条件分布', link: '/probability-ml/joint-marginal-conditional' }, { text: '期望、方差与不确定性', link: '/probability-ml/expectation-variance' }, { text: '协方差、相关性与特征', link: '/probability-ml/covariance-correlation' }, { text: '抽样误差与置信区间', link: '/probability-ml/confidence-intervals-sampling' }, { text: '最大似然：从数据估计参数', link: '/probability-ml/maximum-likelihood' }, { text: '交叉熵与 KL 散度', link: '/probability-ml/cross-entropy-kl' }, { text: '生成模型、朴素贝叶斯与逻辑回归', link: '/probability-ml/generative-discriminative-logistic' }, { text: '共轭先验与后验预测', link: '/probability-ml/conjugate-priors-predictive' }, { text: '常见分布如何建模现实', link: '/probability-ml/common-distributions' }, { text: '假设检验与 p 值', link: '/probability-ml/hypothesis-testing' }, { text: '蒙特卡洛与重要性采样', link: '/probability-ml/monte-carlo-importance-sampling' }, { text: 'Metropolis–Hastings：MCMC 采样', link: '/probability-ml/metropolis-hastings' }, { text: '概率校准与可靠性曲线', link: '/probability-ml/calibration-reliability' }] }],
      '/numerical-computing/': [{ text: '数值误差与浮点数', items: [{ text: '开始学习', link: '/numerical-computing/' }, { text: '深度版路线', link: '/numerical-computing/rewrite-plan' }, { text: '浮点数表示', link: '/numerical-computing/floating-point' }, { text: '绝对/相对误差与消去', link: '/numerical-computing/error-propagation' }, { text: '牛顿法与收敛', link: '/numerical-computing/newton-method' }, { text: '割线法：不用导数求根', link: '/numerical-computing/secant-method' }, { text: '迭代解线性方程组', link: '/numerical-computing/iterative-linear-systems' }, { text: 'Kahan 求和：减少累计误差', link: '/numerical-computing/kahan-summation' }, { text: '条件数：问题对误差有多敏感', link: '/numerical-computing/condition-number' }, { text: '浮点比较、容差与属性测试', link: '/numerical-computing/tolerances-property-testing' }, { text: '数值微分与步长选择', link: '/numerical-computing/numerical-differentiation' }, { text: '数值插值：差商与外推', link: '/numerical-computing/interpolation' }, { text: '数值积分：从求和逼近面积', link: '/numerical-computing/numerical-integration' }, { text: '随机模拟的误差与可复现性', link: '/numerical-computing/stochastic-simulation-reproducibility' }] }],
      '/number-theory-crypto/': [{ text: '密码学的模运算与数论', items: [{ text: '开始学习', link: '/number-theory-crypto/' }, { text: '深度版路线', link: '/number-theory-crypto/rewrite-plan' }, { text: '模运算与快速幂', link: '/number-theory-crypto/modular-arithmetic' }, { text: '最大公约数与模逆元', link: '/number-theory-crypto/extended-euclid' }, { text: '有限域、群与离散对数直觉', link: '/number-theory-crypto/finite-fields-groups' }, { text: 'RSA：公开加密为何可行', link: '/number-theory-crypto/rsa' }, { text: '数字签名与公开验证', link: '/number-theory-crypto/digital-signatures' }, { text: '中国剩余定理：拆分模运算', link: '/number-theory-crypto/chinese-remainder-theorem' }, { text: '素性测试：Miller–Rabin', link: '/number-theory-crypto/primality-testing' }, { text: '哈希与密码存储', link: '/number-theory-crypto/hashing-passwords' }, { text: '消息认证码：HMAC', link: '/number-theory-crypto/message-authentication-codes' }, { text: 'Diffie–Hellman 密钥交换', link: '/number-theory-crypto/diffie-hellman' }, { text: '椭圆曲线密码学预备', link: '/number-theory-crypto/elliptic-curve-prelude' }] }],
    },
    socialLinks: [],
    search: { provider: 'local' },
    footer: { message: '持续构建中的计算机数学知识库', copyright: '内容采用 Markdown 优先的工作流维护' },
  },
})
