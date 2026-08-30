import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import 'katex/dist/katex.min.css'
import './style.css'
import BfsTraceExplorer from './components/BfsTraceExplorer.vue'
import LessonMeta from './components/LessonMeta.vue'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'doc-before': () => h(LessonMeta),
  }),
  enhanceApp({ app }) {
    app.component('BfsTraceExplorer', BfsTraceExplorer)
  },
}
