import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'

const outputRoot = process.argv[2]
if (!outputRoot) {
  console.error('用法：node scripts/check-rendered-math.mjs <VitePress 输出目录>')
  process.exit(1)
}

async function htmlFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  const nested = await Promise.all(entries.map(async (entry) => {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) return htmlFiles(path)
    return entry.name.endsWith('.html') ? [path] : []
  }))
  return nested.flat()
}

function readerVisibleHtml(html) {
  // Code examples and script payloads intentionally preserve source syntax.
  // The check concerns text VitePress sends to readers as rendered prose.
  return html
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<pre\b[^>]*>[\s\S]*?<\/pre>/gi, '')
    .replace(/<code\b[^>]*>[\s\S]*?<\/code>/gi, '')
}

const errors = []
let mathPages = 0
for (const path of await htmlFiles(outputRoot)) {
  const html = await readFile(path, 'utf8')
  if (html.includes('katex-display') || html.includes('class="katex"')) mathPages += 1
  // A documentation page can legitimately mention the text `katex-error` in
  // a code span.  Match the rendered CSS class instead of any text occurrence.
  if (/class="[^"]*\bkatex-error\b[^"]*"/.test(html)) {
    errors.push(`${path}: 出现 KaTeX 错误节点`)
  }
  const visible = readerVisibleHtml(html)
  if (visible.includes('\\(') || visible.includes('\\[')) {
    errors.push(`${path}: 正文仍包含未渲染的 LaTeX 定界符`)
  }
  // The site's Markdown math plugin leaves \operatorname{...} as plain
  // reader-visible text instead of handing it to KaTeX.  Use \mathrm{...}
  // for named teaching operators and reject a regression in rendered prose.
  if (visible.includes('\\operatorname{')) {
    errors.push(`${path}: 正文仍包含未渲染的 \\operatorname 命令`)
  }
}

if (errors.length) {
  console.error('渲染后数学公式校验失败：\n' + errors.map((error) => `- ${error}`).join('\n'))
  process.exit(1)
}

console.log(`渲染后数学公式校验通过：${mathPages} 个页面包含 KaTeX。`)
