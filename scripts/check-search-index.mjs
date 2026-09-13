import { readdir, readFile, stat } from "node:fs/promises";
import { join } from "node:path";

const chunksDirectory = "docs/.vitepress/dist/assets/chunks";
const maximumBytes = 1.35 * 1024 * 1024;
const excludedTitles = [
  "版本迭代看板",
  "课程深度升级路线图",
  "编辑与发布流程",
  "十二周计算机数学学习计划",
];
const requiredCoursePhrases = [
  "最大流最小割：残量网络为何能证明最优",
  "残量网络",
  "lambda",
];
const codeOnlyPhrase = "encoded_red";

const candidates = (await readdir(chunksDirectory)).filter((name) =>
  /^@localSearchIndexroot\..+\.js$/.test(name),
);
if (candidates.length !== 1) {
  throw new Error("expected exactly one local-search index, found " + candidates.length);
}

const indexPath = join(chunksDirectory, candidates[0]);
const bytes = (await stat(indexPath)).size;
if (bytes > maximumBytes) {
  throw new Error(
    "local-search index is " + (bytes / 1024).toFixed(1) + " KiB; budget is " + (maximumBytes / 1024).toFixed(0) + " KiB",
  );
}

const source = await readFile(indexPath, "utf8");
const leakedTitle = excludedTitles.find((title) => source.includes(title));
if (leakedTitle) {
  throw new Error("excluded operational page remains in local search: " + leakedTitle);
}
const absentPhrase = requiredCoursePhrases.find((phrase) => !source.includes(phrase));
if (absentPhrase) {
  throw new Error("course content is unexpectedly absent from local search: " + absentPhrase);
}
if (source.includes(codeOnlyPhrase)) {
  throw new Error("fenced code unexpectedly remains in local search: " + codeOnlyPhrase);
}

console.log("本地搜索索引校验通过：" + (bytes / 1024).toFixed(1) + " KiB，课程正文与公式可搜索，围栏代码与辅助页面已排除。");
