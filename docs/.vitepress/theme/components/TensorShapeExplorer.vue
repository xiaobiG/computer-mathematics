<script setup>
import { computed, ref } from 'vue'

const mode = ref('add')
const examples = [
  { name: '标量', shape: '()', code: '2.5', tone: 'scalar' },
  { name: '向量', shape: '(3,)', code: '[ 2, 5, 7 ]', tone: 'vector' },
  { name: '矩阵', shape: '(2, 3)', code: '[[1, 2, 3], [4, 5, 6]]', tone: 'matrix' },
  { name: '行批次', shape: '(2, 3)', code: '[[1, 2, 3], [4, 5, 6]]', tone: 'batch' },
]
const modes = {
  add: { label: '逐元素加法', title: '相同形状才能逐元素相加', inputs: ['[ 2, 5, 7 ]', '[ 1, 1, 1 ]'], shapes: ['(3,)', '(3,)'], output: '[ 3, 6, 8 ]', outputShape: '(3,)', formula: '(3,) + (3,) → (3,)' },
  multiply: { label: '矩阵乘法', title: '内层维度相同才可复合', inputs: ['X: (2, 3)', 'W: (3, 2)'], shapes: ['2 行 × 3 特征', '3 特征 × 2 输出'], output: 'XW', outputShape: '(2, 2)', formula: '(2, 3) @ (3, 2) → (2, 2)' },
  batch: { label: '批量线性层', title: '首轴保留样本数，末轴变为输出数', inputs: ['X: 2 个样本 × 3 特征', 'W: 3 特征 × 2 输出'], shapes: ['(batch, features)', '(features, outputs)'], output: '2 个样本 × 2 输出', outputShape: '(2, 2)', formula: '(2, 3) @ (3, 2) + (2,) → (2, 2)' },
}
const active = computed(() => modes[mode.value])
</script>

<template>
  <section class="tensor-shape-explorer" aria-labelledby="tensor-shape-title">
    <header><h2 id="tensor-shape-title">形状追踪器</h2><p>把值、轴和操作写在一起；形状是接口的一部分，不是运行后才猜出的注释。</p></header>
    <div class="tensor-shape-explorer__body">
      <div class="shape-library" aria-label="形状示例">
        <article v-for="example in examples" :key="example.name" :class="['shape-example', `shape-example--${example.tone}`]">
          <div><h3>{{ example.name }}</h3><code>{{ example.code }}</code></div><strong>shape: {{ example.shape }}</strong>
        </article>
      </div>
      <div class="shape-workbench">
        <div class="shape-tabs" role="group" aria-label="选择形状操作"><button v-for="(item, key) in modes" :key="key" type="button" :class="{ active: mode === key }" @click="mode = key">{{ item.label }}</button></div>
        <h3>{{ active.title }}</h3>
        <div class="operation-flow"><div v-for="(input, index) in active.inputs" :key="input" class="flow-value"><span>输入 {{ String.fromCharCode(65 + index) }}</span><code>{{ input }}</code><small>shape: {{ active.shapes[index] }}</small></div><span class="flow-arrow" aria-hidden="true">→</span><div class="flow-value flow-value--output"><span>输出</span><code>{{ active.output }}</code><small>shape: {{ active.outputShape }}</small></div></div>
        <p class="shape-conclusion"><span>形状结论</span><strong>{{ active.formula }}</strong></p>
        <aside class="shape-warning"><strong>注意：<code>(3,)</code> 与 <code>(3, 1)</code> 不同</strong><p>前者是一维长度为 3 的向量；后者是 3 行 1 列的二维矩阵。维度数量不同，不能把它们当成同一种接口。</p></aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
.tensor-shape-explorer{container-type:inline-size;margin:2rem 0;border:1px solid #d6e1ed;border-radius:14px;padding:clamp(1rem,3vw,1.75rem);background:#fff;color:#14233e;box-shadow:0 10px 28px rgba(15,35,58,.055)}header h2,.shape-example h3,.shape-workbench h3{margin:0;color:#10213d}header p{margin:.45rem 0 0;color:#526276;line-height:1.58}.tensor-shape-explorer__body{display:grid;grid-template-columns:minmax(16rem,.9fr) minmax(0,1.35fr);gap:1.5rem;margin-top:1.25rem}.shape-library{display:grid;gap:.7rem}.shape-example{display:flex;align-items:center;justify-content:space-between;gap:1rem;border:1px solid #dbe6f0;border-radius:9px;padding:.85rem .95rem;background:#fff}.shape-example h3{font-size:.96rem}.shape-example code{display:block;margin-top:.42rem;color:#31415b;font-size:.82rem;white-space:normal}.shape-example strong{flex:none;border-radius:6px;padding:.35rem .48rem;background:#edf4fb;color:#34517b;font:700 .78rem/1.2 var(--vp-font-family-mono)}.shape-example--vector{border-left:3px solid #0f8b8d}.shape-example--matrix{border-left:3px solid #4f46e5}.shape-example--batch{border-left:3px solid #2563eb}.shape-workbench{padding-left:1.5rem;border-left:1px solid #dbe6f0}.shape-tabs{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem}.shape-tabs button{border:1px solid #cbd9e7;border-radius:7px;padding:.55rem .7rem;background:#fff;color:#17233a;font:700 .84rem/1.2 var(--vp-font-family-base);cursor:pointer}.shape-tabs button.active{border-color:#0f8b8d;background:#0f8b8d;color:#fff}.shape-tabs button:focus-visible{outline:3px solid rgba(20,184,166,.32);outline-offset:2px}.operation-flow{display:grid;grid-template-columns:1fr 1fr auto 1fr;align-items:stretch;gap:.55rem;margin-top:1rem}.flow-value{display:grid;align-content:start;gap:.45rem;border:1px solid #d4e1ee;border-radius:8px;padding:.75rem;background:#f9fbfd}.flow-value span,.shape-conclusion span{color:#607084;font-size:.78rem;font-weight:700}.flow-value code{color:#17233a;overflow-wrap:anywhere;font-size:.83rem}.flow-value small{color:#49688b;font:700 .73rem/1.35 var(--vp-font-family-mono)}.flow-value--output{border-color:#bee7db;background:#f0fbf7}.flow-value--output small{color:#08766a}.flow-arrow{align-self:center;color:#2563a4;font-size:1.55rem}.shape-conclusion{display:grid;gap:.24rem;margin:1rem 0 0;border-radius:8px;padding:.75rem .85rem;background:#edf4fb}.shape-conclusion strong{color:#1d416e;font:700 .98rem/1.35 var(--vp-font-family-mono)}.shape-warning{margin-top:.75rem;border:1px solid #bfccff;border-left:4px solid #4f6df5;border-radius:8px;padding:.8rem .9rem;background:#f5f7ff}.shape-warning strong{color:#283f9a}.shape-warning p{margin:.35rem 0 0;color:#43536f;line-height:1.55}.shape-warning code{color:#394ec2}@container(max-width:780px){.tensor-shape-explorer__body{grid-template-columns:1fr}.shape-workbench{border-left:0;border-top:1px solid #dbe6f0;padding:1.25rem 0 0}.operation-flow{grid-template-columns:1fr 1fr}.flow-arrow{display:none}.flow-value--output{grid-column:1/-1}.shape-example{align-items:flex-start;flex-direction:column}.shape-example strong{align-self:flex-start}}@container(max-width:440px){.operation-flow{grid-template-columns:1fr}.flow-value--output{grid-column:auto}}
</style>
