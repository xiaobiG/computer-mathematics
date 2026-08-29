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
  const label = relative(docsRoot, path)
  if (!/^---\r?\ntitle:\s*.+\r?\ndescription:\s*.+\r?\n---/m.test(source)) {
    errors.push(`${label}: 缺少 title 与 description frontmatter`)
  }
  if ((source.match(/^#\s+/gm) ?? []).length !== 1) {
    errors.push(`${label}: 应当且只能包含一个一级标题`)
  }
  if (!/^##\s+练习\s*$/m.test(source)) {
    errors.push(`${label}: 缺少“练习”章节`)
  }
  if (!/^##\s+/m.test(source)) {
    errors.push(`${label}: 缺少至少一个二级章节`)
  }
}

if (errors.length) {
  console.error('内容校验失败：\n' + errors.map((error) => `- ${error}`).join('\n'))
  process.exit(1)
}

console.log(`内容校验通过：${files.length} 篇课程正文。`)
