<script setup>
import { computed, ref } from 'vue'

const contractVersion = 'shortest-path-comparison/v1'
const maxVertices = 8
const maxEdges = 20
const maxAbsoluteWeight = 10_000

const scenarios = {
  unit: {
    label: '无权图：每条边一跳', start: 's', target: 't',
    note: '所有边权为 1：最少边数与最小总权重是同一个目标。',
    nodes: [{ id: 's', x: 12, y: 50 }, { id: 'a', x: 43, y: 22 }, { id: 'b', x: 43, y: 78 }, { id: 't', x: 82, y: 50 }],
    edges: [['s', 'a', 1], ['s', 'b', 1], ['a', 't', 1], ['b', 't', 1]],
  },
  weighted: {
    label: '非负权图：少边不等于便宜', start: 's', target: 't',
    note: '直接两跳路径 s→b→t 的代价是 11；三跳路径 s→b→a→t 的代价只有 3。',
    nodes: [{ id: 's', x: 10, y: 50 }, { id: 'a', x: 43, y: 22 }, { id: 'b', x: 43, y: 78 }, { id: 't', x: 84, y: 50 }],
    edges: [['s', 'a', 5], ['s', 'b', 1], ['b', 'a', 1], ['a', 't', 1], ['b', 't', 10]],
  },
  negative: {
    label: '负边：未来可以改善已知路径', start: 's', target: 't',
    note: '负边 b→a 会把到 a 的代价从 2 改为 -5；Dijkstra 的“定型”前提因此失效。',
    nodes: [{ id: 's', x: 10, y: 50 }, { id: 'a', x: 43, y: 22 }, { id: 'b', x: 43, y: 78 }, { id: 't', x: 84, y: 50 }],
    edges: [['s', 'a', 2], ['s', 'b', 5], ['b', 'a', -10], ['a', 't', 4]],
  },
  cycle: {
    label: '可达负环：最短路无定义', start: 's', target: 't',
    note: '可重复绕行 a→b→a，每多绕一次总代价再减 2，因此不存在有限最短距离。',
    nodes: [{ id: 's', x: 10, y: 50 }, { id: 'a', x: 42, y: 22 }, { id: 'b', x: 45, y: 78 }, { id: 't', x: 85, y: 50 }],
    edges: [['s', 'a', 1], ['a', 'b', -3], ['b', 'a', 1], ['b', 't', 1]],
  },
}

const selected = ref('unit')
const customVertexCount = ref('4')
const customSource = ref('0')
const customTarget = ref('3')
const customEdges = ref('0 1 5\n0 2 1\n2 1 1\n1 3 1\n2 3 10')
const customError = ref('')
const copied = ref(false)
const requestedQueryCount = ref(1)
const customGraph = ref({
  label: '自定义图：可重放输入', start: 0, target: 3,
  note: '这份初始输入可以直接修改；点击“应用并审计”后才会替换当前图。',
  nodes: [{ id: 0, x: 10, y: 50 }, { id: 1, x: 43, y: 22 }, { id: 2, x: 43, y: 78 }, { id: 3, x: 84, y: 50 }],
  edges: [[0, 1, 5], [0, 2, 1], [2, 1, 1], [1, 3, 1], [2, 3, 10]],
})

function numericNodeLayout(vertexCount) {
  return Array.from({ length: vertexCount }, (_, id) => {
    const angle = -Math.PI / 2 + (2 * Math.PI * id) / vertexCount
    return { id, x: 50 + 34 * Math.cos(angle), y: 50 + 34 * Math.sin(angle) }
  })
}
function parseInteger(value, label, minimum, maximum) {
  const number = Number(value)
  if (!Number.isInteger(number) || number < minimum || number > maximum) throw new Error(`${label} 必须是 ${minimum} 到 ${maximum} 的整数。`)
  return number
}
function applyCustomGraph() {
  try {
    const vertexCount = parseInteger(customVertexCount.value, '顶点数', 2, maxVertices)
    const source = parseInteger(customSource.value, '起点', 0, vertexCount - 1)
    const target = parseInteger(customTarget.value, '终点', 0, vertexCount - 1)
    const rows = customEdges.value.split(/\r?\n/).map(row => row.trim()).filter(Boolean)
    if (rows.length > maxEdges) throw new Error(`边数不能超过 ${maxEdges}。`)
    const edges = rows.map((row, index) => {
      const parts = row.split(/[\s,]+/)
      if (parts.length !== 3) throw new Error(`第 ${index + 1} 条边应为“起点 终点 权重”。`)
      const [fromRaw, toRaw, weightRaw] = parts
      const from = parseInteger(fromRaw, `第 ${index + 1} 条边的起点`, 0, vertexCount - 1)
      const to = parseInteger(toRaw, `第 ${index + 1} 条边的终点`, 0, vertexCount - 1)
      const weight = Number(weightRaw)
      if (!Number.isFinite(weight) || Math.abs(weight) > maxAbsoluteWeight) throw new Error(`第 ${index + 1} 条边的权重必须有限，且绝对值不超过 ${maxAbsoluteWeight}。`)
      return [from, to, weight]
    })
    customGraph.value = {
      label: '自定义图：已通过输入契约', start: source, target,
      note: `已接受 ${vertexCount} 个顶点、${edges.length} 条边；下方卡片按同一份边表重新审计。`,
      nodes: numericNodeLayout(vertexCount), edges,
    }
    selected.value = 'custom'
    customError.value = ''
    copied.value = false
  } catch (error) {
    customError.value = error instanceof Error ? error.message : '输入无法解析。'
  }
}
function resetCustomGraph() {
  customVertexCount.value = '4'; customSource.value = '0'; customTarget.value = '3'
  customEdges.value = '0 1 5\n0 2 1\n2 1 1\n1 3 1\n2 3 10'
  customError.value = ''; copied.value = false
}

const scenario = computed(() => selected.value === 'custom' ? customGraph.value : scenarios[selected.value])
const nodeById = computed(() => new Map(scenario.value.nodes.map(node => [node.id, node])))
const allUnit = computed(() => scenario.value.edges.every(([, , weight]) => weight === 1))
const allNonnegative = computed(() => scenario.value.edges.every(([, , weight]) => weight >= 0))

function buildGraph() {
  const graph = Object.fromEntries(scenario.value.nodes.map(node => [node.id, []]))
  for (const [from, to, weight] of scenario.value.edges) graph[from].push({ to, weight })
  return graph
}
function recover(parent) {
  if (!(scenario.value.target in parent)) return null
  const path = []; let node = scenario.value.target
  for (let remaining = scenario.value.nodes.length + 1; remaining > 0; remaining -= 1) {
    path.push(node)
    if (node === scenario.value.start) return path.reverse()
    node = parent[node]
    if (node == null) return null
  }
  return null
}
function bfs() {
  if (!allUnit.value) return { status: 'rejected', reason: '存在非单位权边：最少边数不能承诺最小总权重。' }
  const graph = buildGraph(); const distance = { [scenario.value.start]: 0 }; const parent = { [scenario.value.start]: null }; const queue = [scenario.value.start]
  while (queue.length) { const node = queue.shift(); for (const { to } of graph[node]) if (!(to in distance)) { distance[to] = distance[node] + 1; parent[to] = node; queue.push(to) } }
  return { status: 'applicable', distance: distance[scenario.value.target] ?? null, path: recover(parent), invariant: '首次发现确定最少边数。' }
}
function dijkstra() {
  if (!allNonnegative.value) return { status: 'rejected', reason: '存在负边：已确定节点仍可能被未来路径改善。' }
  const graph = buildGraph(); const distance = Object.fromEntries(scenario.value.nodes.map(node => [node.id, Infinity])); const parent = { [scenario.value.start]: null }; const queue = [{ node: scenario.value.start, distance: 0 }]; distance[scenario.value.start] = 0
  while (queue.length) { queue.sort((left, right) => left.distance - right.distance); const current = queue.shift(); if (current.distance !== distance[current.node]) continue; for (const { to, weight } of graph[current.node]) { const candidate = current.distance + weight; if (candidate < distance[to]) { distance[to] = candidate; parent[to] = current.node; queue.push({ node: to, distance: candidate }) } } }
  return { status: 'applicable', distance: Number.isFinite(distance[scenario.value.target]) ? distance[scenario.value.target] : null, path: recover(parent), invariant: '非负边保证最小暂定距离可定型。' }
}
function bellmanFord() {
  const ids = scenario.value.nodes.map(node => node.id); const distance = Object.fromEntries(ids.map(id => [id, Infinity])); const parent = { [scenario.value.start]: null }; distance[scenario.value.start] = 0
  for (let round = 1; round < ids.length; round += 1) { const prior = { ...distance }; let changed = false; for (const [from, to, weight] of scenario.value.edges) if (Number.isFinite(prior[from]) && prior[from] + weight < distance[to]) { distance[to] = prior[from] + weight; parent[to] = from; changed = true } if (!changed) break }
  const negativeCycle = scenario.value.edges.some(([from, to, weight]) => Number.isFinite(distance[from]) && distance[from] + weight < distance[to])
  if (negativeCycle) return { status: 'rejected', reason: '源点可达负环：可无限降低路径代价。' }
  return { status: 'applicable', distance: Number.isFinite(distance[scenario.value.target]) ? distance[scenario.value.target] : null, path: recover(parent), invariant: '第 k 轮对应至多 k 条边的最短路径。' }
}
function floydWarshall() {
  const ids = scenario.value.nodes.map(node => node.id); const index = Object.fromEntries(ids.map((id, position) => [id, position])); const distance = ids.map((_, row) => ids.map((_, column) => row === column ? 0 : Infinity)); const next = ids.map(() => ids.map(() => null))
  for (const [from, to, weight] of scenario.value.edges) { const left = index[from]; const right = index[to]; if (weight < distance[left][right]) { distance[left][right] = weight; next[left][right] = to } }
  for (let middle = 0; middle < ids.length; middle += 1) for (let from = 0; from < ids.length; from += 1) for (let to = 0; to < ids.length; to += 1) if (distance[from][middle] + distance[middle][to] < distance[from][to]) { distance[from][to] = distance[from][middle] + distance[middle][to]; next[from][to] = next[from][middle] }
  if (distance.some((row, indexValue) => row[indexValue] < 0)) return { status: 'rejected', reason: '图中存在负环：任意源点对的最短距离可能无定义。' }
  const source = index[scenario.value.start]; const target = index[scenario.value.target]; const path = []; let cursor = scenario.value.start
  if (next[source][target] != null) for (let remaining = ids.length + 1; remaining > 0; remaining -= 1) { path.push(cursor); if (cursor === scenario.value.target) break; cursor = next[index[cursor]][target] }
  return { status: 'applicable', distance: Number.isFinite(distance[source][target]) ? distance[source][target] : null, path: path.length ? path : null, invariant: '第 k 层只允许前 k 个顶点作中间点。' }
}
const cards = computed(() => [
  { key: 'bfs', name: 'BFS', complexity: 'O(V + E)', result: bfs() },
  { key: 'dijkstra', name: 'Dijkstra', complexity: 'O((V + E) log V)', result: dijkstra() },
  { key: 'bellman_ford', name: 'Bellman–Ford', complexity: 'O(VE)', result: bellmanFord() },
  { key: 'floyd_warshall', name: 'Floyd–Warshall', complexity: 'O(V³)', result: floydWarshall() },
])
const queryCount = computed(() => Math.min(Math.max(Number(requestedQueryCount.value) || 1, 1), scenario.value.nodes.length))
const workloadCards = computed(() => {
  const vertices = scenario.value.nodes.length
  const edges = scenario.value.edges.length
  const queries = queryCount.value
  const heapFactor = Math.ceil(Math.log2(Math.max(2, vertices)))
  return [
    { key: 'bfs-work', name: 'BFS', status: allUnit.value ? 'applicable' : 'rejected', theory: `Q·O(V + E)`, units: queries * (vertices + edges), note: allUnit.value ? '每个源点都要按层扫描。' : '非单位权下不承诺加权最短路。' },
    { key: 'dijkstra-work', name: 'Dijkstra', status: allNonnegative.value ? 'applicable' : 'rejected', theory: 'Q·O((V + E)·log V)', units: queries * (vertices + edges) * heapFactor, note: allNonnegative.value ? `堆操作按 ⌈log₂V⌉=${heapFactor} 估计。` : '负边使定型前提失效。' },
    { key: 'bellman-work', name: 'Bellman–Ford', status: 'applicable', theory: 'Q·O(VE)', units: queries * Math.max(0, vertices - 1) * edges, note: '这里是最多 V−1 轮的保守上界。' },
    { key: 'floyd-work', name: 'Floyd–Warshall', status: 'applicable', theory: 'O(V³)', units: vertices ** 3, note: '预处理一次；Q 增加不会再增加矩阵候选格。' },
  ]
})
const customInput = computed(() => ({
  contract_version: contractVersion,
  vertex_count: scenario.value.nodes.length,
  edges: scenario.value.edges.map(([from, to, weight]) => [from, to, weight]),
  source: scenario.value.start,
  target: scenario.value.target,
}))
const customInputJson = computed(() => JSON.stringify(customInput.value, null, 2))
const customReportJson = computed(() => JSON.stringify({
  contract_version: contractVersion,
  input: customInput.value,
  comparison: {
    properties: { vertex_count: scenario.value.nodes.length, edge_count: scenario.value.edges.length, all_unit_weights: allUnit.value, all_nonnegative_weights: allNonnegative.value, has_negative_edge: !allNonnegative.value },
    source: scenario.value.start, target: scenario.value.target,
    algorithms: Object.fromEntries(cards.value.map(card => [card.key, card.result])),
  },
}, null, 2))
async function copyInput() {
  try {
    await navigator.clipboard.writeText(customInputJson.value)
    copied.value = true
  } catch {
    copied.value = false
  }
}
</script>

<template>
  <section class="shortest-path-comparison" aria-labelledby="shortest-path-comparison-title">
    <header><div><p class="eyebrow">同图算法对照</p><h2 id="shortest-path-comparison-title">先检查前提，再比较最短路结果</h2><p>切换同一规模的四类图；每张卡先说明能否作出承诺，再给出路径或拒绝原因。</p></div><label>示例图<select v-model="selected"><option v-for="(item, key) in scenarios" :key="key" :value="key">{{ item.label }}</option><option value="custom">自定义小图：输入并重放</option></select></label></header>
    <section v-if="selected === 'custom'" class="custom-editor" aria-labelledby="custom-graph-title">
      <div><p class="eyebrow">受限输入契约</p><h3 id="custom-graph-title">输入一张可重放的小图</h3><p>教学上限为 {{ maxVertices }} 个顶点、{{ maxEdges }} 条有向边；顶点从 0 编号，权重为绝对值不超过 {{ maxAbsoluteWeight }} 的有限数。</p></div>
      <div class="custom-fields"><label>顶点数<input v-model="customVertexCount" inputmode="numeric" aria-label="顶点数"></label><label>起点<input v-model="customSource" inputmode="numeric" aria-label="起点"></label><label>终点<input v-model="customTarget" inputmode="numeric" aria-label="终点"></label></div>
      <label class="edge-input">边表（每行：起点 空格 终点 空格 权重）<textarea v-model="customEdges" rows="5" spellcheck="false" aria-label="边表"></textarea></label>
      <div class="editor-actions"><button type="button" @click="applyCustomGraph">应用并审计</button><button type="button" class="secondary" @click="resetCustomGraph">恢复示例</button><p v-if="customError" class="input-error" role="alert">{{ customError }}</p></div>
      <details class="replay-report"><summary>查看可重放输入与浏览器报告</summary><p>复制的是稳定的输入 JSON；在 Python 中用 <code>shortest_path_replay_report</code> 重放，才能得到可验证的权威报告。</p><button type="button" class="secondary" @click="copyInput">{{ copied ? '已复制输入' : '复制输入 JSON' }}</button><pre aria-label="可重放输入 JSON">{{ customInputJson }}</pre><pre aria-label="浏览器报告 JSON">{{ customReportJson }}</pre></details>
    </section>
    <section class="workload-explorer" aria-labelledby="workload-title">
      <div><p class="eyebrow">查询数量与成本</p><h3 id="workload-title">同一张图，重复单源查询 {{ queryCount }} 次</h3><p>这些是可读的理论工作量上界，不是毫秒排名；Python 的 <code>shortest_path_workload_report</code> 还会重放实际边扫描与松弛计数。</p></div>
      <div class="query-control"><span id="query-count-label">独立源点查询数</span><output aria-live="polite">{{ queryCount }}</output><input v-model.number="requestedQueryCount" type="range" min="1" :max="scenario.nodes.length" step="1" aria-labelledby="query-count-label"></div>
      <div class="workload-cards"><article v-for="card in workloadCards" :key="card.key" :class="card.status"><h4>{{ card.name }}</h4><code>{{ card.theory }}</code><p v-if="card.status === 'applicable'">估计单位：<strong>{{ card.units }}</strong></p><p>{{ card.note }}</p></article></div>
    </section>
    <div class="comparison-grid"><div class="graph-panel"><svg viewBox="0 0 100 100" role="img" aria-label="当前加权有向图"><defs><marker id="compare-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" /></marker></defs><g v-for="([from, to, weight]) in scenario.edges" :key="`${from}-${to}-${weight}`"><line :x1="nodeById.get(from).x" :y1="nodeById.get(from).y" :x2="nodeById.get(to).x" :y2="nodeById.get(to).y" marker-end="url(#compare-arrow)"/><text :x="(nodeById.get(from).x + nodeById.get(to).x) / 2" :y="(nodeById.get(from).y + nodeById.get(to).y) / 2 - 3">{{ weight }}</text></g><g v-for="node in scenario.nodes" :key="node.id" :transform="`translate(${node.x} ${node.y})`"><circle r="6.4" :class="{ endpoint: node.id === scenario.start || node.id === scenario.target }"/><text text-anchor="middle" dominant-baseline="central">{{ node.id }}</text></g></svg><p><strong>当前判断：</strong>{{ scenario.note }}</p></div><div class="property-panel"><span :class="allUnit ? 'ok' : 'warn'">{{ allUnit ? '全部边权为 1' : '含非单位权边' }}</span><span :class="allNonnegative ? 'ok' : 'warn'">{{ allNonnegative ? '全部边权非负' : '存在负边' }}</span><p>起点 <code>{{ scenario.start }}</code> → 目标 <code>{{ scenario.target }}</code></p><p>读卡顺序：先看状态，再看理由；“拒绝”是正确的前提检查，不是算法失败。</p></div></div>
    <div class="algorithm-cards"><article v-for="card in cards" :key="card.key" :class="card.result.status"><div class="card-top"><h3>{{ card.name }}</h3><code>{{ card.complexity }}</code></div><p class="status">{{ card.result.status === 'applicable' ? '适用' : '拒绝' }}</p><template v-if="card.result.status === 'applicable'"><p>距离：<strong>{{ card.result.distance ?? '不可达' }}</strong></p><p>路径：<code>{{ card.result.path ? card.result.path.join(' → ') : '—' }}</code></p><p class="invariant">{{ card.result.invariant }}</p></template><p v-else class="reason">{{ card.result.reason }}</p></article></div>
    <footer><strong>边界：</strong>BFS 的“拒绝”不表示它不能遍历该图，只表示它的层数结果不能解释为加权最短路；Floyd–Warshall 适合所有源点对，小型交互示例并不意味着它适合大规模稀疏图。</footer>
  </section>
</template>

<style scoped>
.shortest-path-comparison { margin:2rem 0; color:#15334f; }.shortest-path-comparison header { display:flex; justify-content:space-between; align-items:end; gap:1rem; margin-bottom:1rem; }.eyebrow { margin:0 0 .3rem; color:#2563eb; font-size:.75rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }h2 { margin:0; color:#102e4c; font-size:clamp(1.55rem,3vw,2.1rem); letter-spacing:-.025em; }h3 { margin:.1rem 0; color:#102e4c; }header p:last-child,.custom-editor p,.workload-explorer p { margin:.38rem 0 0; color:#53677a; }header label,.custom-editor label { display:grid; gap:.28rem; color:#53677a; font-size:.82rem; font-weight:700; }header label { min-width:min(100%,16rem); }select,input,textarea { padding:.52rem .65rem; border:1px solid #b9c9d8; border-radius:.42rem; background:#fff; color:#15334f; font:inherit; }.custom-editor,.workload-explorer { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:1rem; margin:0 0 1rem; padding:1rem; border:1px solid #b9c9d8; border-radius:.65rem; background:#f8fbff; }.custom-fields { display:grid; grid-template-columns:repeat(3,5rem); gap:.65rem; align-content:start; }.custom-fields input { min-width:0; }.edge-input,.editor-actions,.replay-report,.workload-cards { grid-column:1 / -1; }.edge-input textarea { resize:vertical; font-family:var(--vp-font-family-mono); line-height:1.45; }.editor-actions { display:flex; flex-wrap:wrap; align-items:center; gap:.65rem; }.editor-actions button,.replay-report button { border:0; border-radius:.42rem; padding:.52rem .75rem; background:#2563eb; color:#fff; cursor:pointer; font:inherit; font-weight:700; }.editor-actions .secondary,.replay-report .secondary { border:1px solid #b9c9d8; background:#fff; color:#15334f; }.input-error { margin:0 !important; color:#b91c1c !important; font-weight:700; }.replay-report { color:#53677a; }.replay-report summary { cursor:pointer; color:#15334f; font-weight:800; }.replay-report pre { max-height:17rem; overflow:auto; margin:.75rem 0 0; padding:.75rem; border-radius:.45rem; background:#102e4c; color:#e8f1fb; font-size:.76rem; line-height:1.45; }.query-control { display:grid; gap:.28rem; align-content:end; min-width:15rem; color:#53677a; font-size:.82rem; font-weight:700; }.workload-explorer output { color:#102e4c; font-size:1.25rem; }.workload-explorer input[type="range"] { width:100%; padding:0; accent-color:#2563eb; }.workload-cards { display:grid; grid-template-columns:repeat(4,1fr); gap:.7rem; }.workload-cards article { padding:.8rem; border:1px solid #c7d4df; border-radius:.5rem; background:#fff; }.workload-cards article.applicable { border-top:3px solid #0f9d96; }.workload-cards article.rejected { border-top:3px solid #f97316; }.workload-cards h4 { margin:0; color:#102e4c; }.workload-cards code { color:#53677a; font-size:.75rem; }.workload-cards strong { color:#102e4c; }.comparison-grid { display:grid; grid-template-columns:minmax(0,1.08fr) minmax(16rem,.92fr); gap:1rem; }.graph-panel,.property-panel,.algorithm-cards article,footer { border:1px solid #c7d4df; border-radius:.65rem; background:#fff; }.graph-panel { padding:1rem; }.graph-panel svg { width:100%; min-height:15rem; }.graph-panel line { stroke:#355b7e; stroke-width:1.1; vector-effect:non-scaling-stroke; }.graph-panel marker path { fill:#355b7e; }.graph-panel text { fill:#102e4c; font-size:5px; font-weight:800; paint-order:stroke; stroke:#fff; stroke-width:1.2px; }.graph-panel circle { fill:#eaf4fb; stroke:#3f7ea7; stroke-width:1.1; }.graph-panel circle.endpoint { fill:#bfdbfe; stroke:#2563eb; }.graph-panel p { margin:.45rem 0 0; color:#53677a; }.property-panel { padding:1rem; display:flex; flex-direction:column; gap:.7rem; }.property-panel span { padding:.5rem .65rem; border-radius:.45rem; font-weight:800; }.ok { color:#0f766e; background:#effcf9; }.warn { color:#b45309; background:#fff7ed; }.property-panel p { margin:0; color:#53677a; line-height:1.55; }.algorithm-cards { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; margin-top:1rem; }.algorithm-cards article { padding:1rem; }.algorithm-cards article.applicable { border-top:4px solid #0f9d96; }.algorithm-cards article.rejected { border-top:4px solid #f97316; }.card-top { display:flex; justify-content:space-between; gap:.6rem; align-items:baseline; }.card-top h3 { margin:0; color:#102e4c; }.card-top code { color:#53677a; font-size:.78rem; }.status { display:inline-block; margin:.7rem 0; padding:.22rem .5rem; border-radius:999px; font-size:.8rem; font-weight:800; }.applicable .status { color:#0f766e; background:#effcf9; }.rejected .status { color:#b45309; background:#fff7ed; }.algorithm-cards p { margin:.38rem 0; color:#466078; }.algorithm-cards strong,.algorithm-cards code { color:#102e4c; }.invariant { font-size:.88rem; }.reason { color:#9a3412 !important; line-height:1.55; }footer { margin-top:1rem; padding:1rem 1.15rem; border-left:.32rem solid #2563eb; color:#53677a; line-height:1.65; }footer strong { color:#15334f; }select:focus-visible,input:focus-visible,textarea:focus-visible,button:focus-visible { outline:3px solid rgba(37,99,235,.3); outline-offset:2px; }@media(max-width:760px){ .shortest-path-comparison header { flex-direction:column; align-items:stretch; }.custom-editor,.workload-explorer { grid-template-columns:1fr; }.custom-fields { grid-template-columns:repeat(3,1fr); }.workload-cards,.comparison-grid,.algorithm-cards { grid-template-columns:1fr; } }
</style>
