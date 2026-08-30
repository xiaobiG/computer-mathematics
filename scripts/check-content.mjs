import { readdir, readFile } from 'node:fs/promises'
import { join, relative } from 'node:path'

const docsRoot = 'docs'
const courseFolders = new Set([
  'foundations',
  'discrete-math',
  'linear-algebra',
  'probability-ml',
  'numerical-computing',
  'number-theory-crypto',
])

async function filesIn(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  const files = await Promise.all(entries.map(async (entry) => {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) return filesIn(path)
    return entry.name.endsWith('.md') ? [path] : []
  }))
  return files.flat()
}

const allMarkdownFiles = await filesIn(docsRoot)
const files = allMarkdownFiles.filter((path) => {
  const [folder, filename] = relative(docsRoot, path).split(/[/\\]/)
  return courseFolders.has(folder) && filename !== 'index.md'
})

// VitePress serves `index.md` as a directory URL and every other Markdown
// file without its extension.  Keep this map in the content checker so a
// course link cannot silently become a reader-facing 404 after a rename.
const pageUrls = new Set(allMarkdownFiles.map((path) => {
  const normalized = relative(docsRoot, path).replace(/\\/g, '/')
  if (normalized === 'index.md') return '/'
  if (normalized.endsWith('/index.md')) return `/${normalized.slice(0, -'index.md'.length)}`
  return `/${normalized.slice(0, -'.md'.length)}`
}))

// These anchors are the public contract for the five topic roadmaps.  They
// correspond to the named concepts in the curriculum blueprint, not merely
// to a topic's article count.  Keeping them explicit catches a broken route
// or an accidental deletion before a reader discovers a gap halfway through
// a learning path.
const roadmapAnchors = {
  '程序员的线性代数': [
    '/linear-algebra/vectors-dot-product',
    '/linear-algebra/linear-combinations-basis',
    '/linear-algebra/four-fundamental-subspaces',
    '/linear-algebra/orthogonal-projection-qr',
    '/linear-algebra/gaussian-elimination',
    '/linear-algebra/lu-factorization-pivoting',
    '/linear-algebra/least-squares',
    '/linear-algebra/eigenvalues-pca',
    '/linear-algebra/svd',
    '/linear-algebra/jacobian-hessian-autodiff',
    '/projects/linear-algebra-lab',
  ],
  '算法背后的离散数学': [
    '/discrete-math/logic-induction-proofs',
    '/discrete-math/sets-relations-orders',
    '/discrete-math/recurrences',
    '/discrete-math/loop-invariants',
    '/discrete-math/graph-foundations-topological-sort',
    '/discrete-math/breadth-first-search',
    '/discrete-math/depth-first-search',
    '/discrete-math/union-find',
    '/discrete-math/dijkstra',
    '/discrete-math/bellman-ford',
    '/discrete-math/floyd-warshall',
    '/discrete-math/greedy-exchange-arguments',
    '/discrete-math/dynamic-programming-dag',
    '/discrete-math/p-np-reductions',
    '/projects/algorithm-lab',
  ],
  '机器学习需要的概率论': [
    '/probability-ml/probability-space-events',
    '/probability-ml/joint-marginal-conditional',
    '/probability-ml/expectation-variance',
    '/probability-ml/common-distributions',
    '/probability-ml/laws-of-large-numbers-clt',
    '/probability-ml/bayes',
    '/probability-ml/conjugate-priors-predictive',
    '/probability-ml/maximum-likelihood',
    '/probability-ml/cross-entropy-kl',
    '/probability-ml/hypothesis-testing',
    '/probability-ml/monte-carlo-importance-sampling',
    '/probability-ml/metropolis-hastings',
    '/probability-ml/generative-discriminative-logistic',
    '/projects/naive-bayes-spam',
  ],
  '数值误差与浮点数': [
    '/numerical-computing/floating-point',
    '/numerical-computing/error-propagation',
    '/numerical-computing/condition-number',
    '/numerical-computing/algorithmic-stability',
    '/numerical-computing/kahan-summation',
    '/numerical-computing/iterative-linear-systems',
    '/numerical-computing/preconditioned-conjugate-gradient',
    '/numerical-computing/newton-method',
    '/numerical-computing/secant-method',
    '/numerical-computing/numerical-differentiation',
    '/numerical-computing/interpolation',
    '/numerical-computing/numerical-integration',
    '/numerical-computing/stochastic-simulation-reproducibility',
    '/numerical-computing/tolerances-property-testing',
    '/projects/floating-point-museum',
  ],
  '密码学的模运算与数论': [
    '/number-theory-crypto/extended-euclid',
    '/number-theory-crypto/modular-arithmetic',
    '/number-theory-crypto/chinese-remainder-theorem',
    '/number-theory-crypto/primality-testing',
    '/number-theory-crypto/finite-fields-groups',
    '/number-theory-crypto/rsa',
    '/number-theory-crypto/diffie-hellman',
    '/number-theory-crypto/hashing-passwords',
    '/number-theory-crypto/message-authentication-codes',
    '/number-theory-crypto/elliptic-curve-prelude',
    '/projects/crypto-toybox',
  ],
}

const errors = []
for (const [topic, anchors] of Object.entries(roadmapAnchors)) {
  for (const anchor of anchors) {
    if (!pageUrls.has(anchor)) {
      errors.push(`${topic}: 课程路线锚点 ${anchor} 找不到对应 Markdown 页面`)
    }
  }
}
// The initial deep-rewrite cohort is the site-wide reference implementation
// for the lesson contract.  Keep its reader-facing stages from silently
// regressing during later edits, while other lessons continue to use the
// broader structural checks below as they are upgraded.
const priorityDeepLessons = new Set([
  'linear-algebra/vectors-dot-product.md',
  'linear-algebra/gaussian-elimination.md',
  'linear-algebra/least-squares.md',
  'discrete-math/loop-invariants.md',
  'discrete-math/dijkstra.md',
  'probability-ml/bayes.md',
  'probability-ml/maximum-likelihood.md',
  'numerical-computing/floating-point.md',
  'numerical-computing/condition-number.md',
  'number-theory-crypto/rsa.md',
])
const priorityStagePatterns = [
  ['问题场景', /^##\s+.*(?:问题|开始|场景|案例).*$/m],
  ['直觉或严格定义', /^##\s+.*(?:定义|直觉|符号).*$/m],
  ['分步推导或算法证明', /^##\s+.*(?:推导|证明|算法).*$/m],
  ['正确性、复杂度或工程边界', /^##\s+.*(?:正确性|边界|复杂度).*$/m],
  ['算法实现或实验', /^##\s+.*(?:实现|实验|算法).*$/m],
]
// Headings evolve as an article is revised, so the all-course gate checks the
// explanatory prose rather than prescribing identical heading text.  Together
// with the existing executable-code, failure-boundary and exercise gates this
// keeps the reader-facing chain visible: problem -> model -> derivation.
const narrativeStagePatterns = [
  ['问题场景', /(?:问题|开始|反例|失败|需求)/],
  ['直觉或定义', /(?:直觉|定义|符号|模型|设\s*[A-Za-z$])/],
  ['推导、证明或算法', /(?:推导|证明|算法|不变量|公式|等价)/],
]
for (const path of files) {
  const source = await readFile(path, 'utf8')
  // Structural Markdown headings must be read outside fenced code examples.
  // Otherwise a Python/shell comment such as `# example output` is mistaken
  // for a second H1 and blocks a valid lesson from publishing.
  const prose = source.replace(/^```[^\n]*\r?\n[\s\S]*?^```\s*$/gm, '')
  const label = relative(docsRoot, path)
  const [folder] = label.split(/[/\\]/)
  if (!/^---\r?\n(?=[\s\S]*?^title:\s*.+$)(?=[\s\S]*?^description:\s*.+$)[\s\S]*?^---\s*$/m.test(source)) {
    errors.push(`${label}: 缺少 title 与 description frontmatter`)
  }
  if ((prose.match(/^#\s+/gm) ?? []).length !== 1) {
    errors.push(`${label}: 应当且只能包含一个一级标题`)
  }
  if (!/^##\s+练习\s*$/m.test(prose)) {
    errors.push(`${label}: 缺少“练习”章节`)
  }
  if (!label.endsWith('rewrite-plan.md') && !/^##\s+练习答案提示\s*$/m.test(prose)) {
    errors.push(`${label}: 缺少“练习答案提示”章节`)
  }
  if (!label.endsWith('rewrite-plan.md') && !/^##\s+学习目标\s*$/m.test(prose)) {
    errors.push(`${label}: 缺少“学习目标”章节`)
  }
  if (!label.endsWith('rewrite-plan.md')) {
    const exerciseHeading = /^##\s+练习\s*$/m.exec(prose)
    if (exerciseHeading) {
      const afterHeading = prose.slice(exerciseHeading.index + exerciseHeading[0].length)
      const nextHeading = afterHeading.search(/^##\s+/m)
      const exerciseBody = nextHeading === -1 ? afterHeading : afterHeading.slice(0, nextHeading)
      const exerciseCount = (exerciseBody.match(/^\d+\.\s+/gm) ?? []).length
      if (exerciseCount < 4) {
        errors.push(`${label}: “练习”章节至少需要 4 道分层题目（当前 ${exerciseCount} 道）`)
      }
    }
    const answerHeading = /^##\s+练习答案提示\s*$/m.exec(prose)
    if (answerHeading) {
      const afterHeading = prose.slice(answerHeading.index + answerHeading[0].length)
      const nextHeading = afterHeading.search(/^##\s+/m)
      const answerBody = nextHeading === -1 ? afterHeading : afterHeading.slice(0, nextHeading)
      const answerCount = (answerBody.match(/^\d+\.\s+/gm) ?? []).length
      if (answerCount < 4) {
        errors.push(`${label}: “练习答案提示”章节至少需要 4 条对应提示（当前 ${answerCount} 条）`)
      }
    }
    if (!/```(?:python|bash)\r?\n[\s\S]*?```/.test(source)) {
      errors.push(`${label}: 缺少可运行的 Python 或 Bash 代码块`)
    }
    if (!/^##\s+.*(?:失败|边界|误区).*$/m.test(prose)) {
      errors.push(`${label}: 缺少失败案例、工程边界或常见误区章节`)
    }
    if (!/^##\s+(?:延伸|延伸与下一步|下一步)\s*$/m.test(prose)) {
      errors.push(`${label}: 缺少“延伸”或“下一步”章节`)
    }
  }
  if (!/^##\s+/m.test(prose)) {
    errors.push(`${label}: 缺少至少一个二级章节`)
  }
  if (!label.endsWith('rewrite-plan.md')) {
    for (const [stage, pattern] of narrativeStagePatterns) {
      if (!pattern.test(prose)) {
        errors.push(`${label}: 缺少深度课程叙事“${stage}”`)
      }
    }
    const requiredMetadata = ['courseLevel', 'prerequisites', 'estimatedMinutes', 'experiment']
    for (const key of requiredMetadata) {
      if (!new RegExp(`^${key}:\\s*.+$`, 'm').test(source)) {
        errors.push(`${label}: 缺少 ${key} 课程元信息`)
      }
    }
  }
  if (priorityDeepLessons.has(label)) {
    for (const [stage, pattern] of priorityStagePatterns) {
      if (!pattern.test(prose)) {
        errors.push(`${label}: 优先深度文章缺少“${stage}”正文锚点`)
      }
    }
  }
  if (folder === 'linear-algebra' && !label.endsWith('rewrite-plan.md')) {
    const requiredSections = [
      '学习目标',
      '从一个计算问题开始',
      '常见误区',
      '练习',
    ]
    for (const section of requiredSections) {
      if (!new RegExp(`^##\\s+${section}\\s*$`, 'm').test(prose)) {
        errors.push(`${label}: v0.2 深度文章缺少“${section}”章节`)
      }
    }
    if (!/^##\s+.*(?:失败案例|工程边界).*$/m.test(prose)) {
      errors.push(`${label}: v0.2 深度文章缺少失败案例或工程边界`)
    }
    if (!/```(?:python)?\r?\n[\s\S]*?```/.test(source)) {
      errors.push(`${label}: v0.2 深度文章缺少可运行代码块`)
    }
  }
}

for (const path of allMarkdownFiles) {
  const source = await readFile(path, 'utf8')
  const prose = source.replace(/^```[^\n]*\r?\n[\s\S]*?^```\s*$/gm, '')
  const label = relative(docsRoot, path)
  // Links are intentionally checked only after stripping fenced examples:
  // snippets may demonstrate arbitrary URLs or unfinished exercise paths.
  const links = prose.matchAll(/\[[^\]]*\]\((\/[^\s)#]+)(?:#[^\s)]*)?\)/g)
  for (const match of links) {
    const target = decodeURIComponent(match[1])
    if (!pageUrls.has(target)) {
      errors.push(`${label}: 内部链接 ${match[1]} 找不到对应 Markdown 页面`)
    }
  }
}

// These public progress numbers are intentionally checked against the source
// tree.  Otherwise adding a lesson can silently leave the dashboard claiming
// an older course count, which makes a learning roadmap look more complete or
// less complete than the material readers can actually open.
const actualCourses = files.filter((path) => !path.endsWith('rewrite-plan.md')).length
const about = await readFile(join(docsRoot, 'about.md'), 'utf8')
const maturity = await readFile(join(docsRoot, 'course-maturity.md'), 'utf8')
if (!about.includes(`课程正文 | ${files.length} 篇`) || !about.includes(`${actualCourses} 篇实际课程`)) {
  errors.push(`about.md: 课程规模应为 ${files.length} 篇正文、${actualCourses} 篇实际课程`)
}
if (!maturity.includes(`所有 ${actualCourses} 篇实际课程文章`)) {
  errors.push(`course-maturity.md: 实际课程数应为 ${actualCourses}`)
}

// The public maturity table also reports each topic's actual course count.
// Verify the source-derived values so the roadmap remains an honest planning
// surface as new lessons are added.
const maturityTopicLabels = {
  foundations: '预备知识',
  'linear-algebra': '线性代数',
  'discrete-math': '离散数学',
  'probability-ml': '概率论',
  'numerical-computing': '数值计算',
  'number-theory-crypto': '数论与密码学',
}
for (const [folder, topic] of Object.entries(maturityTopicLabels)) {
  const count = files.filter((path) => {
    const label = relative(docsRoot, path).replace(/\\/g, '/')
    return label.startsWith(`${folder}/`) && !label.endsWith('rewrite-plan.md')
  }).length
  if (!maturity.includes(`| ${topic} | ${count} 篇 |`)) {
    errors.push(`course-maturity.md: ${topic} 的实际课程数应为 ${count} 篇`)
  }
}

if (errors.length) {
  console.error('内容校验失败：\n' + errors.map((error) => `- ${error}`).join('\n'))
  process.exit(1)
}

console.log(`内容校验通过：${files.length} 篇课程正文。`)
