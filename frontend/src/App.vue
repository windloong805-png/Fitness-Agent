<template>
  <div class="app-shell">
    <main class="app-main">
      <RouterView />
    </main>
    <AppTabBar />
  </div>
</template>

<script setup>
import AppTabBar from './components/AppTabBar.vue'
</script>
