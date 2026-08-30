<script setup>
import { computed, ref } from 'vue'

const cases = {
  decimal: {
    name: '十进制小数',
    left: 0.1,
    right: 0.2,
    source: '0.1 + 0.2',
    expected: '数学十进制：0.3',
    explanation: '0.1、0.2 与 0.3 都要先舍入到 binary64。两次加法的结果恰好比 JavaScript 中的 0.3 大一个 ULP。',
  },
  spacing: {
    name: '大数附近的间距',
    left: 1e16,
    right: 1,
    source: '1e16 + 1',
    expected: '实数算术：10000000000000001',
    explanation: '此处相邻 binary64 数的间距是 2；1 正好落在中点，round-to-nearest-even 舍入回偶数 10000000000000000。',
  },
}

const selected = ref('decimal')
const current = computed(() => cases[selected.value])
const result = computed(() => current.value.left + current.value.right)
const reference = computed(() => selected.value === 'decimal' ? 0.3 : current.value.left)
const differsFromReference = computed(() => result.value !== reference.value)
const leftOperandChanged = computed(() => result.value !== current.value.left)

function nextUp(value) {
  if (!Number.isFinite(value)) return value
  if (Object.is(value, -0)) return Number.MIN_VALUE
  const bytes = new ArrayBuffer(8)
  const view = new DataView(bytes)
  view.setFloat64(0, value)
  let bits = view.getBigUint64(0)
  bits += value >= 0 ? 1n : -1n
  view.setBigUint64(0, bits)
  return view.getFloat64(0)
}

const ulp = computed(() => Math.abs(nextUp(current.value.left) - current.value.left))
const delta = computed(() => result.value - reference.value)
function choose(key) { selected.value = key }
</script>

<template>
  <section class="float-explorer" aria-labelledby="float-explorer-title">
    <header>
      <div>
        <p class="eyebrow">交互式数值错误博物馆</p>
        <h2 id="float-explorer-title">一次加法，两个舍入边界</h2>
        <p>切换案例，比较人类书写的实数算术与 binary64 实际保存的结果。</p>
      </div>
      <div class="binary-chip">IEEE 754 · binary64</div>
    </header>

    <div class="case-switcher" role="group" aria-label="选择浮点案例">
      <button v-for="(item, key) in cases" :key="key" type="button" :class="{ active: selected === key }" @click="choose(key)">{{ item.name }}</button>
    </div>

    <div class="float-grid">
      <div class="calculation-panel">
        <p class="expression"><code>{{ current.source }}</code></p>
        <div class="operands"><span>{{ current.left }}</span><b>+</b><span>{{ current.right }}</span></div>
        <p class="equals">=</p>
        <output class="result" aria-live="polite">{{ result }}</output>
        <p class="expected">{{ current.expected }}</p>
      </div>
      <dl class="measurement-panel">
        <div><dt>左操作数附近 ULP</dt><dd>{{ ulp }}</dd></div>
        <div><dt>与参考值的差</dt><dd>{{ delta }}</dd></div>
        <div v-if="selected === 'decimal'"><dt>与 JavaScript 的 0.3 相等</dt><dd :class="differsFromReference ? 'warn' : 'ok'">{{ differsFromReference ? '不相等' : '相等' }}</dd></div>
        <div v-else><dt>加法改变左操作数</dt><dd :class="leftOperandChanged ? 'warn' : 'ok'">{{ leftOperandChanged ? '是' : '否' }}</dd></div>
      </dl>
    </div>

    <footer><strong>解释：</strong>{{ current.explanation }}<br><span>ULP 是该数附近两个相邻可表示浮点数之差；它随数值尺度变化，不是固定 epsilon。</span></footer>
  </section>
</template>

<style scoped>
.float-explorer { margin: 2rem 0; color: #15334f; }.float-explorer header { display: flex; justify-content: space-between; gap: 1rem; align-items: end; margin-bottom: 1rem; }.eyebrow { margin: 0 0 .3rem; color: #0f766e; font-size: .75rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }.float-explorer h2 { margin: 0; color: #102e4c; font-size: clamp(1.55rem, 3vw, 2.1rem); letter-spacing: -.025em; }.float-explorer header p:last-child { margin: .38rem 0 0; color: #53677a; }.binary-chip { padding: .48rem .72rem; border: 1px solid #9bcfc9; border-radius: 999px; color: #0f766e; background: #effcf9; font-size: .8rem; font-weight: 750; white-space: nowrap; }.case-switcher { display: flex; gap: .65rem; margin-bottom: 1rem; }.case-switcher button { min-height: 2.35rem; padding: .45rem .85rem; border: 1px solid #7fa5bb; border-radius: .45rem; background: #fff; color: #294b6e; font: inherit; font-weight: 700; cursor: pointer; }.case-switcher button.active { border-color: #0f766e; background: #0f8f88; color: #fff; }.case-switcher button:focus-visible { outline: 3px solid rgba(20,184,166,.35); outline-offset: 2px; }.float-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(18rem, .85fr); gap: 1rem; }.calculation-panel, .measurement-panel, footer { border: 1px solid #c7d4df; border-radius: .65rem; background: #fff; }.calculation-panel { padding: 1.2rem; text-align: center; }.expression { margin: 0 0 .85rem; color: #53677a; }.expression code { padding: .25rem .45rem; border-radius: .3rem; background: #f2f7fa; }.operands { display: flex; justify-content: center; align-items: center; gap: .75rem; color: #102e4c; font-family: var(--vp-font-family-mono); font-size: clamp(1.25rem, 3vw, 1.8rem); font-weight: 750; }.operands b, .equals { color: #0f9d96; }.equals { margin: .55rem 0; font-size: 1.45rem; }.result { display: block; overflow-wrap: anywhere; color: #0f766e; font-family: var(--vp-font-family-mono); font-size: clamp(1.35rem, 3.5vw, 2.1rem); font-weight: 800; }.expected { margin: .85rem 0 0; color: #667f93; font-size: .86rem; }.measurement-panel { margin: 0; overflow: hidden; }.measurement-panel div { display: grid; grid-template-columns: minmax(0, 1fr) minmax(8rem, 1fr); border-bottom: 1px solid #d7e0e8; }.measurement-panel div:last-child { border-bottom: 0; }.measurement-panel dt, .measurement-panel dd { margin: 0; padding: .85rem .95rem; }.measurement-panel dt { color: #294b6e; background: #f8fbfd; font-weight: 700; }.measurement-panel dd { overflow-wrap: anywhere; color: #102e4c; font-family: var(--vp-font-family-mono); }.measurement-panel dd.warn { color: #b45309; font-weight: 800; }.measurement-panel dd.ok { color: #0f766e; font-weight: 800; }footer { margin-top: 1rem; padding: 1rem 1.15rem; border-left: .32rem solid #0f9d96; color: #53677a; line-height: 1.65; } footer strong { color: #15334f; } footer span { font-size: .88rem; } @media (max-width: 760px) { .float-explorer header { flex-direction: column; align-items: stretch; }.binary-chip { white-space: normal; }.float-grid { grid-template-columns: 1fr; }.case-switcher { display: grid; grid-template-columns: 1fr 1fr; }.measurement-panel div { grid-template-columns: 1fr; }.measurement-panel dt { padding-bottom: .3rem; }.measurement-panel dd { padding-top: .3rem; } }
</style>
