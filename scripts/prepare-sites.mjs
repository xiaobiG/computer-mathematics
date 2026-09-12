import { cp, mkdir, rm, writeFile } from 'node:fs/promises'

await rm('dist', { recursive: true, force: true })
await mkdir('dist/server', { recursive: true })
await cp('docs/.vitepress/dist', 'dist/client', { recursive: true })
await mkdir('dist/.openai', { recursive: true })
await cp('.openai/hosting.json', 'dist/.openai/hosting.json')

// Sites serves VitePress's pre-rendered HTML and assets through Cloudflare's
// static asset binding; this worker keeps the documentation deployment static.
await writeFile(
  'dist/server/index.js',
  `export default { fetch(request, env) { return env.ASSETS.fetch(request) } }\n`,
)
