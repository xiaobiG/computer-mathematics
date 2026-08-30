<script setup>
import { computed, ref } from 'vue'

const exponent = ref(-6)
const epsilon = computed(() => 10 ** exponent.value)
const conditionNumber = computed(() => ((2 + epsilon.value) ** 2) / epsilon.value)
const rhsRelativeChange = computed(() => epsilon.value / (2 + 2 * epsilon.value))
const solutionRelativeChange = computed(() => 1)
const conditionBound = computed(() => conditionNumber.value * rhsRelativeChange.value)
const digits = computed(() => Math.max(2, Math.min(10, -exponent.value + 2)))
const scientific = value => Number(value).toExponential(3)
const fixed = value => Number(value).toFixed(digits.value)
</script>

<template>
  <section class="conditioning-explorer" aria-labelledby="conditioning-explorer-title">
    <header>
      <div>
        <p class="eyebrow">交互式病态系统实验</p>
        <h2 id="conditioning-explorer-title">一丁点右端扰动，为什么解会移动一大步？</h2>
        <p>滑动 <code>ε</code>：矩阵保持不变，只有第二个方程的右端多出 <code>ε</code>。</p>
      </div>
      <output class="epsilon-chip" aria-live="polite">ε = {{ scientific(epsilon) }}</output>
    </header>

    <label class="slider-label" for="conditioning-epsilon">
      <span>扰动尺度：10<sup>{{ exponent }}</sup></span>
      <input id="conditioning-epsilon" v-model.number="exponent" type="range" min="-12" max="-3" step="1">
      <span>10<sup>-3</sup></span>
    </label>

    <div class="equation-grid">
      <article>
        <p class="card-label">参考问题</p>
        <code class="matrix">[ 1  1 ] [x₁] = [ 2 ]<br>[ 1  1 + ε ] [x₂]   [ 2 + ε ]</code>
        <p>解：<strong>(1, 1)</strong></p>
      </article>
      <article class="perturbed">
        <p class="card-label">右端被扰动后</p>
        <code class="matrix">[ 1  1 ] [x₁] = [ 2 ]<br>[ 1  1 + ε ] [x₂]   [ 2 + 2ε ]</code>
        <p>解：<strong>(0, 2)</strong></p>
      </article>
    </div>

    <div class="amplification" aria-label="扰动放大对比">
      <div class="bar-row"><span>右端相对变化</span><div class="track"><i class="input-bar" :style="{ width: `${Math.max(1, Math.min(100, rhsRelativeChange * 1000000))}%` }" /></div><b>{{ scientific(rhsRelativeChange) }}</b></div>
      <div class="bar-row"><span>解的相对变化</span><div class="track"><i class="output-bar" :style="{ width: `${solutionRelativeChange * 100}%` }" /></div><b>{{ fixed(solutionRelativeChange) }}</b></div>
    </div>

    <dl class="metrics">
      <div><dt>κ∞(A)</dt><dd>{{ scientific(conditionNumber) }}</dd></div>
      <div><dt>κ∞(A) · ||δb||∞ / ||b||∞</dt><dd>{{ fixed(conditionBound) }}</dd></div>
      <div><dt>扰动问题的残差</dt><dd class="ok">0</dd></div>
      <div><dt>这说明什么</dt><dd>小残差只说明解满足被扰动后的方程</dd></div>
    </dl>

    <footer><strong>读法：</strong>无论 ε 多小，扰动后的精确解都从 $(1,1)$ 变为 $(0,2)$，相对变化为 1；而右端相对变化随 ε 线性缩小。κ∞ 同时增大，使条件数界仍容许这次放大。它不是在说“程序算错”，而是在显示问题本身接近奇异。 </footer>
  </section>
</template>

<style scoped>
.conditioning-explorer { margin: 2rem 0; color: #15334f; }.conditioning-explorer header { display:flex; gap:1rem; align-items:end; justify-content:space-between; margin-bottom:1rem; }.eyebrow { margin:0 0 .3rem; color:#7c3aed; font-size:.75rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }.conditioning-explorer h2 { margin:0; color:#102e4c; font-size:clamp(1.5rem,3vw,2.05rem); letter-spacing:-.025em; }.conditioning-explorer header p:last-child { margin:.38rem 0 0; color:#53677a; }.epsilon-chip { padding:.5rem .75rem; border:1px solid #c4b5fd; border-radius:999px; background:#f5f3ff; color:#6d28d9; font-family:var(--vp-font-family-mono); font-weight:800; white-space:nowrap; }.slider-label { display:grid; grid-template-columns:max-content 1fr max-content; gap:.75rem; align-items:center; padding:.85rem 1rem; border:1px solid #d8d4fe; border-radius:.65rem; background:#faf9ff; color:#4c3a78; font-weight:700; }.slider-label input { width:100%; accent-color:#7c3aed; }.equation-grid { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1rem; }.equation-grid article { padding:1rem 1.1rem; border:1px solid #c7d4df; border-radius:.65rem; background:#fff; }.equation-grid article.perturbed { border-color:#fdba74; background:#fffaf4; }.card-label { margin:0 0 .6rem; color:#53677a; font-size:.8rem; font-weight:800; }.matrix { display:block; overflow:auto; color:#102e4c; font-family:var(--vp-font-family-mono); line-height:1.65; white-space:pre; }.equation-grid article p:last-child { margin:.8rem 0 0; color:#34516d; }.perturbed strong { color:#c2410c; }.amplification { margin-top:1rem; padding:1rem; border:1px solid #c7d4df; border-radius:.65rem; background:#fff; }.bar-row { display:grid; grid-template-columns:8.5rem minmax(5rem,1fr) 7rem; gap:.7rem; align-items:center; margin:.55rem 0; color:#294b6e; font-size:.87rem; font-weight:700; }.track { height:.75rem; overflow:hidden; border-radius:999px; background:#e9eef3; }.track i { display:block; min-width:.2rem; height:100%; border-radius:inherit; }.input-bar { background:#0f9d96; }.output-bar { background:#f97316; }.bar-row b { color:#102e4c; font-family:var(--vp-font-family-mono); font-size:.8rem; text-align:right; }.metrics { display:grid; grid-template-columns:repeat(2,1fr); margin:1rem 0 0; overflow:hidden; border:1px solid #c7d4df; border-radius:.65rem; background:#fff; }.metrics div { display:grid; grid-template-columns:minmax(0,1fr) minmax(8rem,1fr); border-right:1px solid #d7e0e8; border-bottom:1px solid #d7e0e8; }.metrics div:nth-child(2n) { border-right:0; }.metrics div:nth-last-child(-n+2) { border-bottom:0; }.metrics dt,.metrics dd { margin:0; padding:.78rem .9rem; }.metrics dt { background:#f8fbfd; color:#294b6e; font-weight:700; }.metrics dd { overflow-wrap:anywhere; color:#102e4c; font-family:var(--vp-font-family-mono); }.metrics dd.ok { color:#0f766e; font-weight:800; } footer { margin-top:1rem; padding:1rem 1.15rem; border:1px solid #ddd6fe; border-left:.32rem solid #7c3aed; border-radius:.65rem; background:#faf9ff; color:#53677a; line-height:1.65; } footer strong { color:#3b2b68; } @media(max-width:760px){ .conditioning-explorer header { flex-direction:column; align-items:stretch; }.epsilon-chip { white-space:normal; }.slider-label { grid-template-columns:1fr; gap:.35rem; }.equation-grid,.metrics { grid-template-columns:1fr; }.metrics div,.metrics div:nth-child(2n) { border-right:0; border-bottom:1px solid #d7e0e8; }.metrics div:last-child { border-bottom:0; }.bar-row { grid-template-columns:1fr; gap:.3rem; }.bar-row b { text-align:left; } }
</style>
