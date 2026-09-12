import { readdir, readFile } from 'node:fs/promises'
import { join, relative } from 'node:path'
import katex from 'katex'

const docsRoot = 'docs'

async function markdownFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  const nested = await Promise.all(entries.map(async (entry) => {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) return markdownFiles(path)
    return entry.name.endsWith('.md') ? [path] : []
  }))
  return nested.flat()
}

function lineAt(source, index) {
  return source.slice(0, index).split(/\r?\n/).length
}

function proseOnly(source) {
  // Examples may contain unfinished TeX deliberately; only validate formulas
  // a reader expects VitePress to render in the article itself.
  return source
    .replace(/^```[^\n]*\r?\n[\s\S]*?^```\s*$/gm, '')
    .replace(/`[^`\r\n]*`/g, '')
}

function formulasIn(source) {
  const formulas = []
  let remaining = source
  const block = /(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$/g
  for (const match of source.matchAll(block)) {
    formulas.push({ expression: match[1], index: match.index, kind: '块级' })
  }
  remaining = remaining.replace(block, '')

  const unmatchedBlock = /(?<!\\)\$\$/.exec(remaining)
  if (unmatchedBlock) {
    formulas.push({ expression: '', index: unmatchedBlock.index, kind: '未闭合块级' })
    return formulas
  }

  const inline = /(?<!\\)\$([^$\r\n]+?)(?<!\\)\$/g
  for (const match of remaining.matchAll(inline)) {
    formulas.push({ expression: match[1], index: match.index, kind: '行内' })
  }
  const unmatchedInline = /(?<!\\)\$/.exec(remaining.replace(inline, ''))
  if (unmatchedInline) {
    formulas.push({ expression: '', index: unmatchedInline.index, kind: '未闭合行内' })
  }
  return formulas
}

const errors = []
for (const path of await markdownFiles(docsRoot)) {
  const source = proseOnly(await readFile(path, 'utf8'))
  const label = relative(docsRoot, path)
  for (const formula of formulasIn(source)) {
    if (!formula.expression.trim()) {
      errors.push(`${label}:${lineAt(source, formula.index)} ${formula.kind}公式定界符未闭合`)
      continue
    }
    try {
      katex.renderToString(formula.expression, {
        displayMode: formula.kind === '块级',
        throwOnError: true,
        strict: 'error',
      })
    } catch (error) {
      errors.push(`${label}:${lineAt(source, formula.index)} ${formula.kind}公式无法由 KaTeX 解析：${error.message}`)
    }
  }
}

if (errors.length) {
  console.error('数学公式校验失败：\n' + errors.map((error) => `- ${error}`).join('\n'))
  process.exit(1)
}

console.log('数学公式校验通过。')
