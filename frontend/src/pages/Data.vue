<template>
  <section class="page">
    <header class="page-header">
      <p class="eyebrow">训练数据分析</p>
      <h1>收益、恢复与疲劳状态</h1>
      <p>数据面板用于展示智能体决策的输入特征与用户反馈闭环结果。</p>
    </header>

    <section class="metric-grid three">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
        <small>{{ metric.hint }}</small>
      </article>
    </section>

    <section class="chart-panel">
      <div>
        <p class="eyebrow">训练收益曲线</p>
        <h2>Benefit Score</h2>
      </div>
      <div class="fake-chart benefit"></div>
    </section>

    <section class="chart-panel">
      <div>
        <p class="eyebrow">恢复状态曲线</p>
        <h2>Recovery Trend</h2>
      </div>
      <div class="fake-chart recovery"></div>
    </section>

    <section class="chart-panel">
      <div>
        <p class="eyebrow">疲劳指数曲线</p>
        <h2>Fatigue Trend</h2>
      </div>
      <div class="fake-chart fatigue"></div>
    </section>
  </section>
</template>

<script setup>
import { metrics } from '../data/mockData'
</script>
