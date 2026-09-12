<script setup>
import { computed, ref } from 'vue'

const scenarios = {
  stable: {
    label: '稳定窗口：指标近似不变',
    note: '当前窗口的分数略有波动，但分类、概率误差和损失没有触发给定政策。',
    reference: { probabilities: [.9, .1, .8, .2, .7, .3], labels: [1, 0, 1, 0, 1, 0] },
    current: { probabilities: [.8, .2, .7, .3, .8, .2], labels: [1, 0, 1, 0, 1, 0] },
  },
  accuracy: {
    label: '准确率下降：阈值分类整体翻转',
    note: '标签已到达；0.5 阈值下的错误数上升，准确率和对数损失共同给出复核信号。',
    reference: { probabilities: [.9, .1, .8, .2, .7, .3], labels: [1, 0, 1, 0, 1, 0] },
    current: { probabilities: [.1, .9, .2, .8, .3, .7], labels: [1, 0, 1, 0, 1, 0] },
  },
  confident: {
    label: '过度自信错误：准确率掩盖损失',
    note: '只有一个阈值错误，但它以接近 1 的概率押错；对数损失会放大这类概率承诺破裂。',
    reference: { probabilities: [.9, .1, .8, .2, .7, .3], labels: [1, 0, 1, 0, 1, 0] },
    current: { probabilities: [.99, .05, .98, .02, .99, .05], labels: [1, 0, 1, 0, 0, 0] },
  },
}

const selected = ref('stable')
const accuracyThreshold = ref(.2)
const lossThreshold = ref(.3)
const scenario = computed(() => scenarios[selected.value])

function metrics(window) {
  const clipped = probability => Math.min(Math.max(probability, 1e-12), 1 - 1e-12)
  const prediction = probability => Number(probability >= .5)
  const confusion = { tp: 0, fp: 0, tn: 0, fn: 0 }
  for (const [probability, label] of window.probabilities.map((probability, index) => [probability, window.labels[index]])) {
    const name = prediction(probability) ? (label ? 'tp' : 'fp') : (label ? 'fn' : 'tn')
    confusion[name] += 1
  }
  const count = window.labels.length
  return {
    count, confusion,
    accuracy: (confusion.tp + confusion.tn) / count,
    brier: window.probabilities.reduce((total, probability, index) => total + (probability - window.labels[index]) ** 2, 0) / count,
    logLoss: -window.probabilities.reduce((total, probability, index) => { const p = clipped(probability); const label = window.labels[index]; return total + label * Math.log(p) + (1 - label) * Math.log(1 - p) }, 0) / count,
  }
}
const reference = computed(() => metrics(scenario.value.reference))
const current = computed(() => metrics(scenario.value.current))
const accuracyDrop = computed(() => reference.value.accuracy - current.value.accuracy)
const lossIncrease = computed(() => current.value.logLoss - reference.value.logLoss)
const signals = computed(() => ({ accuracy: accuracyDrop.value >= accuracyThreshold.value, loss: lossIncrease.value >= lossThreshold.value }))
const needsReview = computed(() => signals.value.accuracy || signals.value.loss)
const windowCards = computed(() => [
  { key: 'reference', label: '参考带标签窗口', value: reference.value, tone: 'reference' },
  { key: 'current', label: '当前带标签窗口', value: current.value, tone: needsReview.value ? 'review' : 'current' },
])
</script>

<template>
  <section class="labeled-window-explorer" aria-labelledby="labeled-window-title">
    <header><div><p class="eyebrow">延迟标签到达后</p><h2 id="labeled-window-title">用同一口径审计性能与概率承诺</h2><p>先固定参考窗口和当前窗口，再把信号限定为人工复核；页面不会生成自动重训或部署指令。</p></div><label>窗口情形<select v-model="selected"><option v-for="(item, key) in scenarios" :key="key" :value="key">{{ item.label }}</option></select></label></header>
    <p class="scenario-note"><strong>当前情形：</strong>{{ scenario.note }}</p>
    <div class="policy-controls"><label>准确率下降阈值 <output>{{ accuracyThreshold.toFixed(2) }}</output><input v-model.number="accuracyThreshold" type="range" min="0" max="0.6" step="0.05" aria-label="准确率下降阈值"></label><label>对数损失上升阈值 <output>{{ lossThreshold.toFixed(2) }}</output><input v-model.number="lossThreshold" type="range" min="0" max="1.5" step="0.05" aria-label="对数损失上升阈值"></label></div>
    <div class="window-cards"><article v-for="card in windowCards" :key="card.key" :class="card.tone"><h3>{{ card.label }}</h3><p>样本数：<strong>{{ card.value.count }}</strong></p><dl><div><dt>准确率</dt><dd>{{ card.value.accuracy.toFixed(3) }}</dd></div><div><dt>Brier</dt><dd>{{ card.value.brier.toFixed(3) }}</dd></div><div><dt>对数损失</dt><dd>{{ card.value.logLoss.toFixed(3) }}</dd></div></dl><p class="matrix">TP {{ card.value.confusion.tp }} · FP {{ card.value.confusion.fp }} · TN {{ card.value.confusion.tn }} · FN {{ card.value.confusion.fn }}</p></article></div>
    <div class="signal-panel" :class="{ review: needsReview }"><div><p class="eyebrow">政策信号</p><h3>{{ needsReview ? '需要复核带标签窗口' : '当前没有政策信号' }}</h3><p>准确率下降 {{ accuracyDrop.toFixed(3) }}（{{ signals.accuracy ? '达到' : '未达到' }}阈值）；对数损失上升 {{ lossIncrease.toFixed(3) }}（{{ signals.loss ? '达到' : '未达到' }}阈值）。</p></div><p><strong>行动边界：</strong>记录窗口、标签延迟、数据来源和阈值后交由人工复核；这不是自动重训、改变阈值或上线新模型的命令。</p></div>
    <footer><strong>读法：</strong>准确率评价阈值分类；Brier 与对数损失评价概率。小窗口的变化也可能来自抽样波动，Python 报告会同时给出准确率 Wilson 区间和完整输入合同。</footer>
  </section>
</template>

<style scoped>
.labeled-window-explorer { margin:2rem 0; color:#15334f; }.labeled-window-explorer header { display:flex; justify-content:space-between; align-items:end; gap:1rem; }.eyebrow { margin:0 0 .3rem; color:#7c3aed; font-size:.75rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }h2 { margin:0; color:#2e1065; font-size:clamp(1.55rem,3vw,2.1rem); letter-spacing:-.025em; }h3 { margin:0; color:#2e1065; }.labeled-window-explorer header p:last-child,.scenario-note,.signal-panel p,footer { color:#5b5670; line-height:1.6; }.labeled-window-explorer label { display:grid; gap:.28rem; color:#5b5670; font-size:.82rem; font-weight:700; }.labeled-window-explorer header label { min-width:min(100%,17rem); }select,input { padding:.52rem .65rem; border:1px solid #d3c8e5; border-radius:.42rem; background:#fff; color:#2e1065; font:inherit; }.scenario-note { margin:1rem 0; padding:.8rem 1rem; border-left:.3rem solid #8b5cf6; border-radius:.4rem; background:#f7f3ff; }.scenario-note strong { color:#4c1d95; }.policy-controls { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; padding:1rem; border:1px solid #ded6ec; border-radius:.65rem; background:#fcfbff; }.policy-controls output { color:#4c1d95; font-size:1.2rem; }.policy-controls input[type="range"] { width:100%; padding:0; accent-color:#7c3aed; }.window-cards { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; margin-top:1rem; }.window-cards article,.signal-panel,footer { padding:1rem; border:1px solid #ded6ec; border-radius:.65rem; background:#fff; }.window-cards article.reference { border-top:4px solid #64748b; }.window-cards article.current { border-top:4px solid #0f9d96; }.window-cards article.review { border-top:4px solid #ea580c; }.window-cards p { margin:.48rem 0; color:#5b5670; }.window-cards strong,.window-cards dd { color:#2e1065; }.window-cards dl { display:grid; grid-template-columns:repeat(3,1fr); gap:.45rem; margin:.8rem 0; }.window-cards dl div { padding:.55rem; border-radius:.4rem; background:#f8f6fc; }.window-cards dt { color:#756f85; font-size:.76rem; }.window-cards dd { margin:.2rem 0 0; font-weight:800; }.matrix { font-family:var(--vp-font-family-mono); font-size:.82rem; }.signal-panel { display:grid; grid-template-columns:minmax(0,1fr) minmax(15rem,.75fr); gap:1rem; margin-top:1rem; border-left:.32rem solid #0f9d96; }.signal-panel.review { border-left-color:#ea580c; background:#fffaf5; }.signal-panel p { margin:.38rem 0 0; }.signal-panel strong { color:#2e1065; }footer { margin-top:1rem; border-left:.32rem solid #7c3aed; }select:focus-visible,input:focus-visible { outline:3px solid rgba(124,58,237,.26); outline-offset:2px; }@media(max-width:760px){ .labeled-window-explorer header { flex-direction:column; align-items:stretch; }.policy-controls,.window-cards,.signal-panel,.window-cards dl { grid-template-columns:1fr; } }
</style>
