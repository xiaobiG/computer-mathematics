<script setup>
import { computed, ref } from 'vue'

const examples = {
  layers: {
    label: '分层图：首个发现即为最短路',
    start: 'A',
    nodes: [
      { id: 'A', x: 14, y: 50 }, { id: 'B', x: 38, y: 24 },
      { id: 'C', x: 38, y: 76 }, { id: 'D', x: 67, y: 18 },
      { id: 'E', x: 67, y: 50 }, { id: 'F', x: 67, y: 82 },
    ],
    graph: {
      A: ['B', 'C'], B: ['A', 'D', 'E'], C: ['A', 'E', 'F'],
      D: ['B'], E: ['B', 'C'], F: ['C'],
    },
  },
  diamond: {
    label: '菱形图：多个路径的同层相遇',
    start: 'A',
    nodes: [
      { id: 'A', x: 14, y: 50 }, { id: 'B', x: 42, y: 22 },
      { id: 'C', x: 42, y: 78 }, { id: 'D', x: 72, y: 50 },
      { id: 'E', x: 88, y: 24 }, { id: 'F', x: 88, y: 76 },
    ],
    graph: {
      A: ['B', 'C'], B: ['A', 'D'], C: ['A', 'D'],
      D: ['B', 'C', 'E', 'F'], E: ['D'], F: ['D'],
    },
  },
}

const selected = ref('layers')
const step = ref(0)
const example = computed(() => examples[selected.value])

function buildTrace({ graph, start }) {
  const queue = [start]
  const distance = { [start]: 0 }
  const parent = { [start]: '—' }
  const discovered = [start]
  const snapshot = (current, message) => ({
    current, message, queue: [...queue], discovered: [...discovered],
    distance: { ...distance }, parent: { ...parent },
  })
  const events = [snapshot(null, `初始化：起点 ${start} 入队，距离为 0。`)]

  while (queue.length) {
    const current = queue.shift()
    events.push(snapshot(current, `取出 ${current}，检查它所有尚未发现的邻居。`))
    for (const neighbor of graph[current]) {
      if (neighbor in distance) continue
      distance[neighbor] = distance[current] + 1
      parent[neighbor] = current
      discovered.push(neighbor)
      queue.push(neighbor)
      events.push(snapshot(current, `首次从 ${current} 发现 ${neighbor}，距离确定为 ${distance[neighbor]}。`))
    }
  }
  events.push(snapshot(null, '队列为空：所有可达节点都已按非递减距离处理。'))
  return events
}

const trace = computed(() => buildTrace(example.value))
const state = computed(() => trace.value[step.value])
const nodeById = computed(() => new Map(example.value.nodes.map((node) => [node.id, node])))
const edges = computed(() => {
  const pairs = []
  const seen = new Set()
  for (const [from, neighbors] of Object.entries(example.value.graph)) {
    for (const to of neighbors) {
      const key = [from, to].sort().join(':')
      if (!seen.has(key)) {
        seen.add(key)
        pairs.push({ from: nodeById.value.get(from), to: nodeById.value.get(to) })
      }
    }
  }
  return pairs
})

function changeExample() {
  step.value = 0
}

function previous() {
  step.value = Math.max(0, step.value - 1)
}

function next() {
  step.value = Math.min(trace.value.length - 1, step.value + 1)
}

function reset() {
  step.value = 0
}

function nodeState(id) {
  if (id === state.value.current) return 'is-current'
  if (state.value.queue.includes(id)) return 'is-frontier'
  if (state.value.discovered.includes(id)) return 'is-discovered'
  return 'is-unseen'
}
</script>

<template>
  <section class="bfs-explorer" aria-labelledby="bfs-explorer-title">
    <div class="explorer-heading">
      <div>
        <h2 id="bfs-explorer-title">BFS 轨迹实验</h2>
        <p>逐步检查队列与首次发现规则如何共同保证无权最短路。</p>
      </div>
      <div class="example-picker">
        <label for="bfs-example">示例图</label>
        <select id="bfs-example" v-model="selected" @change="changeExample">
          <option v-for="(item, key) in examples" :key="key" :value="key">{{ item.label }}</option>
        </select>
      </div>
    </div>

    <div class="explorer-grid">
      <div class="graph-panel" aria-label="当前 BFS 图状态">
        <svg class="graph-canvas" viewBox="0 0 100 100" role="img" aria-label="节点和边的 BFS 状态图">
          <line
            v-for="edge in edges"
            :key="`${edge.from.id}-${edge.to.id}`"
            :x1="edge.from.x" :y1="edge.from.y" :x2="edge.to.x" :y2="edge.to.y"
            class="graph-edge"
          />
          <g v-for="node in example.nodes" :key="node.id" :transform="`translate(${node.x} ${node.y})`">
            <circle r="7.2" class="node-halo" :class="nodeState(node.id)" />
            <circle r="5.4" class="node-core" :class="nodeState(node.id)" />
            <text text-anchor="middle" dominant-baseline="central" class="node-label">{{ node.id }}</text>
          </g>
        </svg>
        <div class="legend" aria-label="图例">
          <span><i class="legend-dot current"></i>当前节点</span>
          <span><i class="legend-dot frontier"></i>队列前沿</span>
          <span><i class="legend-dot discovered"></i>已发现</span>
          <span><i class="legend-dot unseen"></i>未发现</span>
        </div>
      </div>

      <div class="trace-panel">
        <dl class="state-list">
          <div><dt>当前节点</dt><dd>{{ state.current ?? '—' }}</dd></div>
          <div><dt>队列</dt><dd>{{ state.queue.length ? `[${state.queue.join(', ')}]` : '[]' }}</dd></div>
          <div><dt>已发现</dt><dd>{ {{ state.discovered.join(', ') }} }</dd></div>
        </dl>
        <div class="trace-table-wrap">
          <table>
            <thead><tr><th>发现顺序</th><th>节点</th><th>距离（从 A）</th><th>前驱</th></tr></thead>
            <tbody>
              <tr v-for="(node, index) in example.nodes" :key="node.id" :class="{ pending: !(node.id in state.distance) }">
                <td>{{ node.id in state.distance ? state.discovered.indexOf(node.id) + 1 : '—' }}</td>
                <td>{{ node.id }}</td>
                <td>{{ state.distance[node.id] ?? '—' }}</td>
                <td>{{ state.parent[node.id] ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="controls">
          <button type="button" class="secondary" :disabled="step === 0" @click="previous">上一步</button>
          <span aria-live="polite">步骤 {{ step + 1 }} / {{ trace.length }}</span>
          <button type="button" :disabled="step === trace.length - 1" @click="next">下一步</button>
        </div>
      </div>
    </div>

    <div class="invariant-panel" aria-live="polite">
      <div class="invariant-copy">
        <strong>不变量：已发现节点的距离不会倒退</strong>
        <p>{{ state.message }}</p>
      </div>
      <button type="button" class="reset-button" @click="reset">重置</button>
    </div>
  </section>
</template>

<style scoped>
.bfs-explorer { margin: 2rem 0; color: #15334f; }
.explorer-heading { display: flex; justify-content: space-between; gap: 1rem; align-items: end; margin-bottom: 1rem; }
.explorer-heading h2 { margin: 0; color: #102e4c; font-size: clamp(1.55rem, 3vw, 2.1rem); letter-spacing: -0.025em; }
.explorer-heading p { margin: .38rem 0 0; color: #53677a; }
.example-picker { display: grid; gap: .28rem; min-width: min(100%, 15rem); color: #53677a; font-size: .82rem; font-weight: 650; }
.example-picker select { appearance: auto; width: 100%; padding: .52rem .65rem; border: 1px solid #b9c9d8; border-radius: .42rem; background: #fff; color: #15334f; font: inherit; }
.explorer-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(20rem, .85fr); gap: 1rem; }
.graph-panel, .trace-panel, .invariant-panel { border: 1px solid #c7d4df; border-radius: .6rem; background: #fff; }
.graph-panel { padding: 1rem; min-height: 27rem; display: flex; flex-direction: column; }
.graph-canvas { display: block; width: 100%; flex: 1; min-height: 20rem; overflow: visible; }
.graph-edge { stroke: #294b6e; stroke-width: 1.05; vector-effect: non-scaling-stroke; }
.node-halo { fill: transparent; stroke: transparent; stroke-width: 1.1; transition: all .2s ease; }
.node-core { fill: #fff; stroke: #143f68; stroke-width: 1; transition: all .2s ease; }
.node-halo.is-current { fill: rgba(20, 184, 166, .18); stroke: #0f9d96; }
.node-core.is-current { fill: #79e0d5; stroke: #087b78; }
.node-halo.is-frontier { stroke: #0f9d96; stroke-dasharray: 2.1 1.5; }
.node-core.is-frontier { fill: #e3fbf7; stroke: #0f9d96; }
.node-core.is-discovered { fill: #eaf4fb; stroke: #3f7ea7; }
.node-label { fill: #102e4c; font-size: 5.25px; font-weight: 750; pointer-events: none; }
.legend { display: flex; flex-wrap: wrap; gap: .65rem 1rem; color: #466078; font-size: .8rem; }
.legend span { display: inline-flex; gap: .35rem; align-items: center; }
.legend-dot { width: .8rem; height: .8rem; border-radius: 50%; border: 2px solid #143f68; display: inline-block; }
.legend-dot.current { background: #79e0d5; border-color: #087b78; box-shadow: 0 0 0 2px rgba(20, 184, 166, .18); }
.legend-dot.frontier { border-color: #0f9d96; border-style: dashed; background: #e3fbf7; }
.legend-dot.discovered { background: #eaf4fb; border-color: #3f7ea7; }
.trace-panel { overflow: hidden; display: flex; flex-direction: column; }
.state-list { margin: 0; border-bottom: 1px solid #c7d4df; }
.state-list div { display: grid; grid-template-columns: 7rem 1fr; min-height: 3.2rem; border-bottom: 1px solid #d7e0e8; }
.state-list div:last-child { border-bottom: 0; }
.state-list dt, .state-list dd { margin: 0; padding: .8rem .9rem; display: flex; align-items: center; }
.state-list dt { border-right: 1px solid #d7e0e8; color: #294b6e; font-weight: 700; }
.state-list dd { color: #087b78; font-family: var(--vp-font-family-mono); font-weight: 650; overflow-wrap: anywhere; }
.trace-table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .82rem; }
th, td { padding: .55rem .5rem; border-bottom: 1px solid #dce5ec; border-right: 1px solid #dce5ec; text-align: center; white-space: nowrap; }
th:last-child, td:last-child { border-right: 0; }
th { color: #294b6e; background: #f8fbfd; font-weight: 720; }
.pending { color: #93a3b1; }
.controls { display: grid; grid-template-columns: 1fr auto 1fr; gap: .6rem; align-items: center; padding: .85rem; margin-top: auto; }
button { min-height: 2.45rem; border: 1px solid #0f766e; border-radius: .42rem; background: #0f8f88; color: #fff; font: inherit; font-weight: 700; cursor: pointer; transition: background .15s ease, opacity .15s ease; }
button:hover:not(:disabled) { background: #0b756f; }
button:focus-visible, select:focus-visible { outline: 3px solid rgba(20, 184, 166, .35); outline-offset: 2px; }
button:disabled { cursor: not-allowed; opacity: .45; }
button.secondary, .reset-button { background: #fff; color: #0f766e; }
.controls span { color: #294b6e; font-size: .82rem; font-weight: 650; white-space: nowrap; text-align: center; }
.invariant-panel { display: flex; justify-content: space-between; gap: 1.25rem; align-items: center; margin-top: 1rem; padding: 1.1rem 1.15rem; border-left: .32rem solid #0f9d96; }
.invariant-copy strong { color: #102e4c; }
.invariant-copy p { margin: .28rem 0 0; color: #53677a; }
.reset-button { padding: .55rem 1rem; flex: 0 0 auto; }
@media (max-width: 760px) {
  .explorer-heading, .invariant-panel { align-items: stretch; flex-direction: column; }
  .explorer-grid { grid-template-columns: 1fr; }
  .graph-panel { min-height: 22rem; }
  .example-picker { min-width: 0; }
  .reset-button { width: 100%; }
}
@media (prefers-reduced-motion: reduce) { .node-halo, .node-core, button { transition: none; } }
</style>
