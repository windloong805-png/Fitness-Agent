<template>
  <nav class="tab-bar">
    <RouterLink v-for="item in tabs" :key="item.path" :to="item.path" class="tab-item">
      <span class="tab-icon">{{ item.icon }}</span>
      <span>{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup>
const tabs = [
  { path: '/home', label: '首页', icon: '⌂' },
  { path: '/plan', label: '计划', icon: '◎' },
  { path: '/coach', label: 'AI教练', icon: '✦' },
  { path: '/data', label: '数据', icon: '▥' },
  { path: '/mine', label: '我的', icon: '◌' }
]
</script>
