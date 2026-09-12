import { readFile } from "node:fs/promises";

const requiredStateBindings = [
  ["docs/.vitepress/theme/components/TensorShapeExplorer.vue", ':aria-pressed="mode === key"'],
  ["docs/.vitepress/theme/components/SetsArraysExplorer.vue", ':aria-pressed="operation === key"'],
  ["docs/.vitepress/theme/components/FloatingPointExplorer.vue", ':aria-pressed="selected === key"'],
];

for (const [path, requiredBinding] of requiredStateBindings) {
  const source = await readFile(path, "utf8");
  if (!source.includes(requiredBinding)) {
    throw new Error(path + " must expose its selected button state with " + requiredBinding);
  }
}

console.log("交互组件无障碍校验通过：三个状态切换组均公开 aria-pressed。");
