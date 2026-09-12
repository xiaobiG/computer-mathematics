<script setup>
import { computed, ref } from 'vue'

const leftInput = ref('1, 2, 3, 4')
const rightInput = ref('3, 4, 5')
const operation = ref('union')
const row = ref(1)
const column = ref(1)
const matrix = [[1, 2, 3], [4, 5, 6]]
const operations = {
  union: { label: '并集 A ∪ B', explain: '至少属于一个集合的元素。' },
  intersection: { label: '交集 A ∩ B', explain: '同时属于两个集合的元素。' },
  left: { label: '差集 A − B', explain: '在 A 中而不在 B 中的元素。' },
  right: { label: '差集 B − A', explain: '在 B 中而不在 A 中的元素。' },
}
function parse(input) {
  return [...new Set(input.split(',').map(item => item.trim()).filter(Boolean))]
}
const left = computed(() => parse(leftInput.value))
const right = computed(() => parse(rightInput.value))
const onlyLeft = computed(() => left.value.filter(item => !right.value.includes(item)))
const both = computed(() => left.value.filter(item => right.value.includes(item)))
const onlyRight = computed(() => right.value.filter(item => !left.value.includes(item)))
const result = computed(() => {
  if (operation.value === 'intersection') return both.value
  if (operation.value === 'left') return onlyLeft.value
  if (operation.value === 'right') return onlyRight.value
  return [...left.value, ...right.value.filter(item => !left.value.includes(item))]
})
const selected = computed(() => matrix[row.value][column.value])
</script>

<template>
  <section class="sets-arrays-explorer" aria-labelledby="sets-arrays-title">
    <header>
      <h2 id="sets-arrays-title">集合运算与数组形状</h2>
      <p>编辑两个有限集合，观察成员关系；再用从 0 开始的坐标读取一个二维数组。</p>
    </header>
    <div class="sets-arrays-explorer__sets">
      <div class="set-inputs">
        <label>集合 A <input v-model="leftInput" aria-label="集合 A，以逗号分隔"></label>
        <label>集合 B <input v-model="rightInput" aria-label="集合 B，以逗号分隔"></label>
        <div class="operation-tabs" role="group" aria-label="选择集合运算">
          <button v-for="(item, key) in operations" :key="key" type="button" :class="{ active: operation === key }" :aria-pressed="operation === key" @click="operation = key">{{ item.label }}</button>
        </div>
        <p class="operation-result" aria-live="polite"><strong>{{ operations[operation].label }}</strong> = { {{ result.join(', ') || '∅' }} }<span>{{ operations[operation].explain }}</span></p>
      </div>
      <div class="membership" aria-label="集合成员关系">
        <div class="membership__circles" aria-hidden="true"><div class="circle circle--a"></div><div class="circle circle--b"></div><div class="membership__items membership__items--a">{{ onlyLeft.join(' · ') || '—' }}</div><div class="membership__items membership__items--both">{{ both.join(' · ') || '—' }}</div><div class="membership__items membership__items--b">{{ onlyRight.join(' · ') || '—' }}</div></div>
        <div class="membership__legend"><span><i class="dot dot--a"></i>只在 A</span><span><i class="dot dot--both"></i>同时在 A 与 B</span><span><i class="dot dot--b"></i>只在 B</span></div>
      </div>
    </div>
    <div class="array-inspector">
      <div><h3>数组形状 <code>(2, 3)</code></h3><p>形状先读行数、再读列数；本页每格的坐标是 <code>(行, 列)</code>。</p><div class="array-grid" role="grid" aria-label="2 行 3 列数组"><button v-for="(value, index) in matrix.flat()" :key="index" type="button" :class="{ selected: Math.floor(index / 3) === row && index % 3 === column }" :aria-label="`元素 ${value}，索引 ${Math.floor(index / 3)}, ${index % 3}`" @click="row = Math.floor(index / 3); column = index % 3">{{ value }}</button></div></div>
      <div class="array-controls"><h3>索引</h3><div><label>行 <select v-model.number="row"><option :value="0">0</option><option :value="1">1</option></select></label><label>列 <select v-model.number="column"><option :value="0">0</option><option :value="1">1</option><option :value="2">2</option></select></label></div><p class="value-card"><span>元素值</span><strong>{{ selected }}</strong></p><p class="coordinate-card"><span>索引位置</span><strong>({{ row }}, {{ column }})</strong></p></div>
    </div>
  </section>
</template>

<style scoped>
.sets-arrays-explorer{margin:2rem 0;border:1px solid #d9e2ea;border-radius:14px;padding:clamp(1rem,3vw,1.75rem);background:#fff;color:#17233a;box-shadow:0 10px 28px rgba(15,35,58,.055)}header h2,h3{margin:0;color:#10213d}header p,.array-inspector p{margin:.45rem 0 0;color:#526276;line-height:1.58}.sets-arrays-explorer__sets{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(20rem,.9fr);gap:1.5rem;margin-top:1.25rem;padding:1.25rem;border:1px solid #e0e7ef;border-radius:10px}.set-inputs{display:grid;gap:.85rem}.set-inputs label,.array-controls label{display:grid;gap:.35rem;color:#0f766e;font-weight:750}input,select{min-width:0;border:1px solid #cbd7e4;border-radius:7px;padding:.65rem .75rem;background:#fff;color:#17233a;font:inherit}input:focus-visible,select:focus-visible,button:focus-visible{outline:3px solid rgba(20,184,166,.32);outline-offset:2px}.operation-tabs{display:flex;flex-wrap:wrap;gap:.5rem}.operation-tabs button{border:1px solid #cbd7e4;border-radius:7px;padding:.55rem .7rem;background:#fff;color:#17233a;font:700 .86rem/1.2 inherit;cursor:pointer}.operation-tabs button.active{border-color:#0f8b8d;background:#0f8b8d;color:#fff}.operation-result{margin:0;padding:1rem;border-radius:8px;background:#f3f7f9;font-family:var(--vp-font-family-mono);line-height:1.6}.operation-result strong{display:block;color:#0f766e;font-family:var(--vp-font-family-base)}.operation-result span{display:block;margin-top:.25rem;color:#607084;font:normal .85rem/1.45 var(--vp-font-family-base)}.membership{border-left:1px solid #e0e7ef;padding-left:1.5rem}.membership__circles{position:relative;min-height:180px;isolation:isolate}.circle{position:absolute;top:21px;width:142px;height:142px;border:2px solid;border-radius:50%;opacity:.9}.circle--a{left:10%;border-color:#0f8b8d;background:rgba(20,184,166,.1)}.circle--b{right:10%;border-color:#4f46e5;background:rgba(79,70,229,.09)}.membership__items{position:absolute;z-index:1;color:#10213d;font-weight:760;text-align:center}.membership__items--a{top:82px;left:18%;width:25%}.membership__items--both{top:82px;left:38%;width:25%}.membership__items--b{top:82px;right:14%;width:25%}.membership__legend{display:flex;flex-wrap:wrap;gap:.65rem;color:#526276;font-size:.78rem}.membership__legend span{display:flex;align-items:center;gap:.3rem}.dot{display:inline-block;width:.75rem;height:.75rem;border-radius:50%}.dot--a{background:#9ce4df}.dot--both{background:#2e8dce}.dot--b{background:#b9c1fa}.array-inspector{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(15rem,.85fr);gap:1.5rem;margin-top:1.25rem;padding:1.25rem;border:1px solid #e0e7ef;border-radius:10px}.array-grid{display:grid;grid-template-columns:repeat(3,1fr);overflow:hidden;margin-top:1rem;border:1px solid #cad7e6}.array-grid button{min-height:58px;border:0;border-right:1px solid #cad7e6;border-bottom:1px solid #cad7e6;background:#fff;color:#17233a;font:700 1.05rem/1 inherit;cursor:pointer}.array-grid button:nth-child(3n){border-right:0}.array-grid button:nth-last-child(-n+3){border-bottom:0}.array-grid button.selected{background:#eef2ff;box-shadow:inset 0 0 0 2px #4f46e5;color:#3730a3}.array-controls{padding-left:1.5rem;border-left:1px solid #e0e7ef}.array-controls>div{display:grid;grid-template-columns:repeat(2,1fr);gap:.65rem;margin-top:.75rem}.array-controls label{color:#4f46e5}.value-card,.coordinate-card{margin:.75rem 0 0;padding:.75rem;border-radius:8px;background:#f4f7fb}.value-card span,.coordinate-card span{display:block;color:#607084;font-size:.8rem}.value-card strong,.coordinate-card strong{display:block;margin-top:.2rem;color:#17233a;font-size:1.15rem}.coordinate-card{background:#f0f1ff}.array-inspector code{color:#4f46e5}@media(max-width:760px){.sets-arrays-explorer__sets,.array-inspector{grid-template-columns:1fr}.membership,.array-controls{border-left:0;border-top:1px solid #e0e7ef;padding:1.25rem 0 0}.circle--a{left:8%}.circle--b{right:8%}.membership__items--a{left:15%}.membership__items--b{right:11%}}
</style>
