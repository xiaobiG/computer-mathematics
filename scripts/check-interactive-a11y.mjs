import { readFile } from "node:fs/promises";

const requiredStateBindings = [
  ["docs/.vitepress/theme/components/TensorShapeExplorer.vue", ':aria-pressed="mode === key"'],
  ["docs/.vitepress/theme/components/SetsArraysExplorer.vue", ':aria-pressed="operation === key"'],
  ["docs/.vitepress/theme/components/FloatingPointExplorer.vue", ':aria-pressed="selected === key"'],
];
const requiredLiveResults = [
  ["docs/.vitepress/theme/components/TensorShapeExplorer.vue", 'class="shape-conclusion" aria-live="polite"'],
  ["docs/.vitepress/theme/components/SetsArraysExplorer.vue", 'class="operation-result" aria-live="polite"'],
];

for (const [path, requiredBinding] of requiredStateBindings) {
  const source = await readFile(path, "utf8");
  if (!source.includes(requiredBinding)) {
    throw new Error(path + " must expose its selected button state with " + requiredBinding);
  }
}
for (const [path, requiredBinding] of requiredLiveResults) {
  const source = await readFile(path, "utf8");
  if (!source.includes(requiredBinding)) {
    throw new Error(path + " must announce its changed result with " + requiredBinding);
  }
}

console.log("交互组件无障碍校验通过：状态切换组公开 aria-pressed，动态结果使用礼貌播报。");
