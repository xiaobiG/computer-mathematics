<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { frontmatter } = useData()

const fields = computed(() => [
  { label: '建议层级', value: frontmatter.value.courseLevel },
  { label: '前置知识', value: frontmatter.value.prerequisites },
  { label: '预计学习', value: frontmatter.value.estimatedMinutes ? `${frontmatter.value.estimatedMinutes} 分钟` : undefined },
  { label: '配套实验', value: frontmatter.value.experiment },
].filter((field) => typeof field.value === 'string' || typeof field.value === 'number'))
</script>

<template>
  <aside v-if="fields.length" class="lesson-meta" aria-label="课程信息">
    <div v-for="field in fields" :key="field.label" class="lesson-meta__item">
      <span class="lesson-meta__label">{{ field.label }}</span>
      <span class="lesson-meta__value">{{ field.value }}</span>
    </div>
  </aside>
</template>
