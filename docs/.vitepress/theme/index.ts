import DefaultTheme from 'vitepress/theme'
import 'katex/dist/katex.min.css'
import './style.css'
import BfsTraceExplorer from './components/BfsTraceExplorer.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('BfsTraceExplorer', BfsTraceExplorer)
  },
}
