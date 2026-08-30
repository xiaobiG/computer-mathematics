import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import 'katex/dist/katex.min.css'
import './style.css'
import BfsTraceExplorer from './components/BfsTraceExplorer.vue'
import DijkstraTraceExplorer from './components/DijkstraTraceExplorer.vue'
import FloatingPointExplorer from './components/FloatingPointExplorer.vue'
import ConditioningExplorer from './components/ConditioningExplorer.vue'
import ShortestPathComparisonExplorer from './components/ShortestPathComparisonExplorer.vue'
import LabeledWindowExplorer from './components/LabeledWindowExplorer.vue'
import LessonMeta from './components/LessonMeta.vue'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'doc-before': () => h(LessonMeta),
  }),
  enhanceApp({ app }) {
    app.component('BfsTraceExplorer', BfsTraceExplorer)
    app.component('DijkstraTraceExplorer', DijkstraTraceExplorer)
    app.component('FloatingPointExplorer', FloatingPointExplorer)
    app.component('ConditioningExplorer', ConditioningExplorer)
    app.component('ShortestPathComparisonExplorer', ShortestPathComparisonExplorer)
    app.component('LabeledWindowExplorer', LabeledWindowExplorer)
  },
}
