<script setup>
import { computed, ref } from 'vue'

const graph = {
  start: 's',
  nodes: [
    { id: 's', x: 12, y: 50 }, { id: 'a', x: 39, y: 24 },
    { id: 'b', x: 43, y: 76 }, { id: 't', x: 82, y: 50 },
  ],
  edges: [
    ['s', 'a', 2], ['s', 'b', 5], ['a', 'b', 1], ['a', 't', 5], ['b', 't', 2],
  ],
}

const step = ref(0)

function snapshot(current, message, distances, parent, settled, heap) {
  return {
    current, message, distances: { ...distances }, parent: { ...parent },
    settled: [...settled], heap: heap.map((entry) => ({ ...entry })),
  }
}

function buildTrace() {
  const distances = Object.fromEntries(graph.nodes.map(({ id }) => [id, Infinity]))
  const parent = {}
  const settled = new Set()
  const heap = [{ node: graph.start, distance: 0 }]
  const outgoing = Object.fromEntries(graph.nodes.map(({ id }) => [id, []]))
  for (const [from, to, weight] of graph.edges) outgoing[from].push({ to, weight })
  distances[graph.start] = 0
  const events = [snapshot(null, '初始化：起点 s 的暂定距离为 0，放入最小堆。', distances, parent, settled, heap)]

  while (heap.length) {
    heap.sort((left, right) => left.distance - right.distance || left.node.localeCompare(right.node))
    const candidate = heap.shift()
    if (settled.has(candidate.node)) {
      events.push(snapshot(candidate.node, `${candidate.node} 的堆条目已过期，跳过它。`, distances, parent, settled, heap))
      continue
    }
    settled.add(candidate.node)
    events.push(snapshot(candidate.node, `弹出暂定距离最小的 ${candidate.node}=${candidate.distance}；非负边保证它现在可确定。`, distances, parent, settled, heap))
    for (const { to, weight } of outgoing[candidate.node]) {
      if (settled.has(to)) continue
      const proposal = distances[candidate.node] + weight
      if (proposal < distances[to]) {
        const previous = distances[to]
        distances[to] = proposal
        parent[to] = candidate.node
        heap.push({ node: to, distance: proposal })
        events.push(snapshot(candidate.node, `松弛 ${candidate.node} → ${to}：${Number.isFinite(previous) ? previous : '∞'} 改为 ${proposal}。`, distances, parent, settled, heap))
      } else {
        events.push(snapshot(candidate.node, `检查 ${candidate.node} → ${to}：候选 ${proposal} 不优于现有 ${distances[to]}，保持不变。`, distances, parent, settled, heap))
      }
    }
  }
  events.push(snapshot(null, '最小堆为空：所有可达节点都已按最终最短距离确定。', distances, parent, settled, heap))
  return events
}

const trace = computed(buildTrace)
const state = computed(() => trace.value[step.value])
const nodeById = new Map(graph.nodes.map((node) => [node.id, node]))

function previous() { step.value = Math.max(0, step.value - 1) }
function next() { step.value = Math.min(trace.value.length - 1, step.value + 1) }
function reset() { step.value = 0 }
function nodeState(id) {
  if (id === state.value.current) return 'current'
  if (state.value.settled.includes(id)) return 'settled'
  if (state.value.heap.some((entry) => entry.node === id)) return 'frontier'
  return 'unseen'
}
function distance(id) { return Number.isFinite(state.value.distances[id]) ? state.value.distances[id] : '∞' }
</script>

<template>
  <section class="dijkstra-explorer" aria-labelledby="dijkstra-explorer-title">
    <header>
      <div>
        <h2 id="dijkstra-explorer-title">Dijkstra 轨迹实验</h2>
        <p>逐步观察“最小暂定距离 → 松弛邻边 → 最终确定”的不变量。</p>
      </div>
      <div class="result-chip">最终：s → a → b → t，总代价 5</div>
    </header>

    <div class="dijkstra-grid">
      <div class="graph-panel">
        <svg viewBox="0 0 100 100" role="img" aria-label="Dijkstra 加权有向图的当前状态">
          <defs><marker id="dijkstra-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" /></marker></defs>
          <g v-for="([from, to, weight]) in graph.edges" :key="`${from}-${to}`">
            <line :x1="nodeById.get(from).x" :y1="nodeById.get(from).y" :x2="nodeById.get(to).x" :y2="nodeById.get(to).y" marker-end="url(#dijkstra-arrow)" class="edge" />
            <text :x="(nodeById.get(from).x + nodeById.get(to).x) / 2" :y="(nodeById.get(from).y + nodeById.get(to).y) / 2 - 3" class="weight">{{ weight }}</text>
          </g>
          <g v-for="node in graph.nodes" :key="node.id" :transform="`translate(${node.x} ${node.y})`">
            <circle r="8" class="node-ring" :class="nodeState(node.id)" />
            <circle r="5.8" class="node" :class="nodeState(node.id)" />
            <text text-anchor="middle" dominant-baseline="central" class="node-name">{{ node.id }}</text>
          </g>
        </svg>
        <div class="legend"><span><i class="current"></i>当前弹出</span><span><i class="frontier"></i>堆中候选</span><span><i class="settled"></i>已确定</span></div>
      </div>

      <div class="state-panel">
        <dl><div><dt>当前节点</dt><dd>{{ state.current ?? '—' }}</dd></div><div><dt>最小堆</dt><dd>{{ state.heap.length ? state.heap.map((entry) => `${entry.node}:${entry.distance}`).join(', ') : '[]' }}</dd></div></dl>
        <table><thead><tr><th>节点</th><th>暂定距离</th><th>前驱</th><th>状态</th></tr></thead><tbody>
          <tr v-for="node in graph.nodes" :key="node.id"><td>{{ node.id }}</td><td>{{ distance(node.id) }}</td><td>{{ state.parent[node.id] ?? '—' }}</td><td>{{ nodeState(node.id) === 'settled' ? '已确定' : nodeState(node.id) === 'frontier' ? '候选' : nodeState(node.id) === 'current' ? '当前' : '未发现' }}</td></tr>
        </tbody></table>
        <div class="controls"><button type="button" class="secondary" :disabled="step === 0" @click="previous">上一步</button><span aria-live="polite">步骤 {{ step + 1 }} / {{ trace.length }}</span><button type="button" :disabled="step === trace.length - 1" @click="next">下一步</button></div>
      </div>
    </div>
    <footer><p aria-live="polite"><strong>本步解释：</strong>{{ state.message }}</p><button type="button" class="secondary reset" @click="reset">重置</button></footer>
  </section>
</template>

<style scoped>
.dijkstra-explorer { margin: 2rem 0; color: #15334f; }
header { display: flex; justify-content: space-between; gap: 1rem; align-items: end; margin-bottom: 1rem; }
h2 { margin: 0; color: #102e4c; font-size: clamp(1.55rem, 3vw, 2.1rem); letter-spacing: -.025em; }
header p { margin: .38rem 0 0; color: #53677a; }
.result-chip { padding: .5rem .7rem; border: 1px solid #9bcfc9; border-radius: 999px; color: #0f766e; background: #effcf9; font-size: .82rem; font-weight: 700; white-space: nowrap; }
.dijkstra-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(19rem, .9fr); gap: 1rem; }
.graph-panel, .state-panel, footer { border: 1px solid #c7d4df; border-radius: .6rem; background: #fff; }
.graph-panel { min-height: 25rem; padding: 1rem; display: flex; flex-direction: column; }
svg { width: 100%; min-height: 20rem; flex: 1; overflow: visible; }
.edge { stroke: #355b7e; stroke-width: 1.05; vector-effect: non-scaling-stroke; }
marker path { fill: #355b7e; }.weight { fill: #294b6e; font-size: 5px; font-weight: 750; paint-order: stroke; stroke: white; stroke-width: 1.4px; }
.node-ring { fill: transparent; stroke: transparent; stroke-width: 1.2; }.node { fill: #fff; stroke: #143f68; stroke-width: 1.1; }.node-name { fill: #102e4c; font-size: 5.5px; font-weight: 800; }
.node.current { fill: #79e0d5; stroke: #087b78; }.node-ring.current { fill: rgba(20,184,166,.18); stroke: #0f9d96; }.node.frontier { fill: #e3fbf7; stroke: #0f9d96; }.node-ring.frontier { stroke: #0f9d96; stroke-dasharray: 2 1.5; }.node.settled { fill: #eaf4fb; stroke: #3f7ea7; }
.legend { display: flex; flex-wrap: wrap; gap: .65rem 1rem; color: #466078; font-size: .8rem; }.legend span { display: inline-flex; align-items: center; gap: .35rem; }.legend i { width: .8rem; height: .8rem; display: inline-block; border: 2px solid #143f68; border-radius: 50%; }.legend i.current { background: #79e0d5; border-color: #087b78; }.legend i.frontier { background: #e3fbf7; border-color: #0f9d96; border-style: dashed; }.legend i.settled { background: #eaf4fb; border-color: #3f7ea7; }
.state-panel { overflow: hidden; display: flex; flex-direction: column; }.state-panel dl { margin: 0; border-bottom: 1px solid #c7d4df; }.state-panel dl div { display: grid; grid-template-columns: 6.5rem 1fr; border-bottom: 1px solid #d7e0e8; }.state-panel dl div:last-child { border: 0; }.state-panel dt, .state-panel dd { margin: 0; padding: .75rem .85rem; }.state-panel dt { border-right: 1px solid #d7e0e8; color: #294b6e; font-weight: 700; }.state-panel dd { color: #087b78; font-family: var(--vp-font-family-mono); overflow-wrap: anywhere; }
table { width: 100%; border-collapse: collapse; font-size: .82rem; } th, td { padding: .55rem .35rem; border-bottom: 1px solid #dce5ec; border-right: 1px solid #dce5ec; text-align: center; white-space: nowrap; } th:last-child, td:last-child { border-right: 0; } th { color: #294b6e; background: #f8fbfd; }
.controls { display: grid; grid-template-columns: 1fr auto 1fr; gap: .55rem; align-items: center; padding: .85rem; margin-top: auto; }.controls span { color: #294b6e; font-size: .82rem; font-weight: 650; white-space: nowrap; text-align: center; }
button { min-height: 2.4rem; border: 1px solid #0f766e; border-radius: .42rem; background: #0f8f88; color: #fff; font: inherit; font-weight: 700; cursor: pointer; } button:hover:not(:disabled) { background: #0b756f; } button:focus-visible { outline: 3px solid rgba(20,184,166,.35); outline-offset: 2px; } button:disabled { cursor: not-allowed; opacity: .45; }.secondary { color: #0f766e; background: #fff; }
footer { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-top: 1rem; padding: 1rem 1.15rem; border-left: .32rem solid #0f9d96; } footer p { margin: 0; color: #53677a; }.reset { padding: .4rem .95rem; flex: 0 0 auto; }
@media (max-width: 760px) { header, footer { flex-direction: column; align-items: stretch; }.result-chip { white-space: normal; }.dijkstra-grid { grid-template-columns: 1fr; }.graph-panel { min-height: 21rem; }.reset { width: 100%; } }
</style>
