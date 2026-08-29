import { readdir, readFile } from 'node:fs/promises'
import { join, relative } from 'node:path'

const docsRoot = 'docs'
const courseFolders = new Set([
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

const files = (await filesIn(docsRoot)).filter((path) => {
  const [folder, filename] = relative(docsRoot, path).split(/[/\\]/)
  return courseFolders.has(folder) && filename !== 'index.md'
})

const errors = []
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
  if (!/^##\s+/m.test(prose)) {
    errors.push(`${label}: 缺少至少一个二级章节`)
  }
  if (!label.endsWith('rewrite-plan.md')) {
    const requiredMetadata = ['courseLevel', 'prerequisites', 'estimatedMinutes', 'experiment']
    for (const key of requiredMetadata) {
      if (!new RegExp(`^${key}:\\s*.+$`, 'm').test(source)) {
        errors.push(`${label}: 缺少 ${key} 课程元信息`)
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

if (errors.length) {
  console.error('内容校验失败：\n' + errors.map((error) => `- ${error}`).join('\n'))
  process.exit(1)
}

console.log(`内容校验通过：${files.length} 篇课程正文。`)
