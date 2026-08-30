<script setup>
import { computed, ref } from 'vue'

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
const scenario = computed(() => scenarios[selected.value])
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
  { key: 'bellman', name: 'Bellman–Ford', complexity: 'O(VE)', result: bellmanFord() },
  { key: 'floyd', name: 'Floyd–Warshall', complexity: 'O(V³)', result: floydWarshall() },
])
</script>

<template>
  <section class="shortest-path-comparison" aria-labelledby="shortest-path-comparison-title">
    <header><div><p class="eyebrow">同图算法对照</p><h2 id="shortest-path-comparison-title">先检查前提，再比较最短路结果</h2><p>切换同一规模的四类图；每张卡先说明能否作出承诺，再给出路径或拒绝原因。</p></div><label>示例图<select v-model="selected"><option v-for="(item, key) in scenarios" :key="key" :value="key">{{ item.label }}</option></select></label></header>
    <div class="comparison-grid"><div class="graph-panel"><svg viewBox="0 0 100 100" role="img" aria-label="当前加权有向图"><defs><marker id="compare-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" /></marker></defs><g v-for="([from, to, weight]) in scenario.edges" :key="`${from}-${to}-${weight}`"><line :x1="nodeById.get(from).x" :y1="nodeById.get(from).y" :x2="nodeById.get(to).x" :y2="nodeById.get(to).y" marker-end="url(#compare-arrow)"/><text :x="(nodeById.get(from).x + nodeById.get(to).x) / 2" :y="(nodeById.get(from).y + nodeById.get(to).y) / 2 - 3">{{ weight }}</text></g><g v-for="node in scenario.nodes" :key="node.id" :transform="`translate(${node.x} ${node.y})`"><circle r="6.4" :class="{ endpoint: node.id === scenario.start || node.id === scenario.target }"/><text text-anchor="middle" dominant-baseline="central">{{ node.id }}</text></g></svg><p><strong>当前判断：</strong>{{ scenario.note }}</p></div><div class="property-panel"><span :class="allUnit ? 'ok' : 'warn'">{{ allUnit ? '全部边权为 1' : '含非单位权边' }}</span><span :class="allNonnegative ? 'ok' : 'warn'">{{ allNonnegative ? '全部边权非负' : '存在负边' }}</span><p>起点 <code>{{ scenario.start }}</code> → 目标 <code>{{ scenario.target }}</code></p><p>读卡顺序：先看状态，再看理由；“拒绝”是正确的前提检查，不是算法失败。</p></div></div>
    <div class="algorithm-cards"><article v-for="card in cards" :key="card.key" :class="card.result.status"><div class="card-top"><h3>{{ card.name }}</h3><code>{{ card.complexity }}</code></div><p class="status">{{ card.result.status === 'applicable' ? '适用' : '拒绝' }}</p><template v-if="card.result.status === 'applicable'"><p>距离：<strong>{{ card.result.distance ?? '不可达' }}</strong></p><p>路径：<code>{{ card.result.path ? card.result.path.join(' → ') : '—' }}</code></p><p class="invariant">{{ card.result.invariant }}</p></template><p v-else class="reason">{{ card.result.reason }}</p></article></div>
    <footer><strong>边界：</strong>BFS 的“拒绝”不表示它不能遍历该图，只表示它的层数结果不能解释为加权最短路；Floyd–Warshall 适合所有源点对，小型交互示例并不意味着它适合大规模稀疏图。</footer>
  </section>
</template>

<style scoped>
.shortest-path-comparison { margin:2rem 0; color:#15334f; }.shortest-path-comparison header { display:flex; justify-content:space-between; align-items:end; gap:1rem; margin-bottom:1rem; }.eyebrow { margin:0 0 .3rem; color:#2563eb; font-size:.75rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }h2 { margin:0; color:#102e4c; font-size:clamp(1.55rem,3vw,2.1rem); letter-spacing:-.025em; }header p:last-child { margin:.38rem 0 0; color:#53677a; }header label { display:grid; gap:.28rem; min-width:min(100%,16rem); color:#53677a; font-size:.82rem; font-weight:700; }select { padding:.52rem .65rem; border:1px solid #b9c9d8; border-radius:.42rem; background:#fff; color:#15334f; font:inherit; }.comparison-grid { display:grid; grid-template-columns:minmax(0,1.08fr) minmax(16rem,.92fr); gap:1rem; }.graph-panel,.property-panel,.algorithm-cards article,footer { border:1px solid #c7d4df; border-radius:.65rem; background:#fff; }.graph-panel { padding:1rem; }.graph-panel svg { width:100%; min-height:15rem; }.graph-panel line { stroke:#355b7e; stroke-width:1.1; vector-effect:non-scaling-stroke; }.graph-panel marker path { fill:#355b7e; }.graph-panel text { fill:#102e4c; font-size:5px; font-weight:800; paint-order:stroke; stroke:#fff; stroke-width:1.2px; }.graph-panel circle { fill:#eaf4fb; stroke:#3f7ea7; stroke-width:1.1; }.graph-panel circle.endpoint { fill:#bfdbfe; stroke:#2563eb; }.graph-panel p { margin:.45rem 0 0; color:#53677a; }.property-panel { padding:1rem; display:flex; flex-direction:column; gap:.7rem; }.property-panel span { padding:.5rem .65rem; border-radius:.45rem; font-weight:800; }.ok { color:#0f766e; background:#effcf9; }.warn { color:#b45309; background:#fff7ed; }.property-panel p { margin:0; color:#53677a; line-height:1.55; }.algorithm-cards { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; margin-top:1rem; }.algorithm-cards article { padding:1rem; }.algorithm-cards article.applicable { border-top:4px solid #0f9d96; }.algorithm-cards article.rejected { border-top:4px solid #f97316; }.card-top { display:flex; justify-content:space-between; gap:.6rem; align-items:baseline; }.card-top h3 { margin:0; color:#102e4c; }.card-top code { color:#53677a; font-size:.78rem; }.status { display:inline-block; margin:.7rem 0; padding:.22rem .5rem; border-radius:999px; font-size:.8rem; font-weight:800; }.applicable .status { color:#0f766e; background:#effcf9; }.rejected .status { color:#b45309; background:#fff7ed; }.algorithm-cards p { margin:.38rem 0; color:#466078; }.algorithm-cards strong,.algorithm-cards code { color:#102e4c; }.invariant { font-size:.88rem; }.reason { color:#9a3412 !important; line-height:1.55; }footer { margin-top:1rem; padding:1rem 1.15rem; border-left:.32rem solid #2563eb; color:#53677a; line-height:1.65; }footer strong { color:#15334f; }select:focus-visible { outline:3px solid rgba(37,99,235,.3); outline-offset:2px; }@media(max-width:760px){ .shortest-path-comparison header { flex-direction:column; align-items:stretch; }.comparison-grid,.algorithm-cards { grid-template-columns:1fr; } }
</style>
