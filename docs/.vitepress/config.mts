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
      { text: '12 周计划', link: '/study-plan' },
      { text: '专题系列', items: series },
      { text: '综合项目', link: '/projects/' },
      { text: '术语表', link: '/glossary' },
      { text: '编辑流程', link: '/editorial-workflow' },
      { text: '项目状态', link: '/about' },
      { text: '写作规范', link: '/contributing' },
    ],
    sidebar: {
      '/linear-algebra/': [{ text: '程序员的线性代数', items: [{ text: '开始学习', link: '/linear-algebra/' }, { text: '向量与点积', link: '/linear-algebra/vectors-dot-product' }, { text: '矩阵乘法与线性变换', link: '/linear-algebra/matrix-multiplication' }, { text: '高斯消元：解线性方程组', link: '/linear-algebra/gaussian-elimination' }, { text: '最小二乘：没有精确解怎么办', link: '/linear-algebra/least-squares' }, { text: '特征值与 PCA', link: '/linear-algebra/eigenvalues-pca' }, { text: 'SVD：矩阵的通用分解', link: '/linear-algebra/svd' }] }],
      '/discrete-math/': [{ text: '算法背后的离散数学', items: [{ text: '开始学习', link: '/discrete-math/' }, { text: '循环不变量与二分查找', link: '/discrete-math/loop-invariants' }, { text: '复杂度：算法规模如何影响时间', link: '/discrete-math/asymptotic-complexity' }, { text: 'BFS：图中的最短步数', link: '/discrete-math/breadth-first-search' }, { text: '递推关系与分治复杂度', link: '/discrete-math/recurrences' }, { text: 'Dijkstra：带权图最短路', link: '/discrete-math/dijkstra' }, { text: '并查集与动态连通性', link: '/discrete-math/union-find' }] }],
      '/probability-ml/': [{ text: '机器学习需要的概率论', items: [{ text: '开始学习', link: '/probability-ml/' }, { text: '条件概率与贝叶斯更新', link: '/probability-ml/bayes' }, { text: '期望、方差与不确定性', link: '/probability-ml/expectation-variance' }, { text: '最大似然：从数据估计参数', link: '/probability-ml/maximum-likelihood' }, { text: '常见分布如何建模现实', link: '/probability-ml/common-distributions' }, { text: '假设检验与 p 值', link: '/probability-ml/hypothesis-testing' }, { text: '协方差、相关性与特征', link: '/probability-ml/covariance-correlation' }] }],
      '/numerical-computing/': [{ text: '数值误差与浮点数', items: [{ text: '开始学习', link: '/numerical-computing/' }, { text: '为什么 0.1 + 0.2 不等于 0.3', link: '/numerical-computing/floating-point' }, { text: '牛顿法与收敛', link: '/numerical-computing/newton-method' }, { text: 'Kahan 求和：减少累计误差', link: '/numerical-computing/kahan-summation' }, { text: '条件数：问题对误差有多敏感', link: '/numerical-computing/condition-number' }, { text: '数值微分与步长选择', link: '/numerical-computing/numerical-differentiation' }, { text: '数值积分：从求和逼近面积', link: '/numerical-computing/numerical-integration' }] }],
      '/number-theory-crypto/': [{ text: '密码学的模运算与数论', items: [{ text: '开始学习', link: '/number-theory-crypto/' }, { text: '模运算与快速幂', link: '/number-theory-crypto/modular-arithmetic' }, { text: '最大公约数与模逆元', link: '/number-theory-crypto/extended-euclid' }, { text: 'RSA：公开加密为何可行', link: '/number-theory-crypto/rsa' }, { text: '中国剩余定理：拆分模运算', link: '/number-theory-crypto/chinese-remainder-theorem' }, { text: '哈希与密码存储', link: '/number-theory-crypto/hashing-passwords' }, { text: 'Diffie–Hellman 密钥交换', link: '/number-theory-crypto/diffie-hellman' }] }],
    },
    socialLinks: [],
    search: { provider: 'local' },
    footer: { message: '持续构建中的计算机数学知识库', copyright: '内容采用 Markdown 优先的工作流维护' },
  },
})
