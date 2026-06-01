<template>
  <section class="page home-page">
    <header class="hero-panel">
      <p class="eyebrow">Fitness-Agent 智能体驾驶舱</p>
      <h1>{{ dashboard.greeting }}</h1>
      <p class="hero-copy">基于 Qwen2.5 的知识增强推理与动态规划，为今日训练生成可解释决策。</p>
    </header>

    <div class="metric-grid two">
      <article class="metric-card">
        <span>今日恢复指数</span>
        <strong>{{ dashboard.recoveryIndex }}</strong>
        <small>适合中等强度训练</small>
      </article>
      <article class="metric-card warning">
        <span>今日疲劳指数</span>
        <strong>{{ dashboard.fatigueIndex }}</strong>
        <small>处于可控区间</small>
      </article>
    </div>

    <article class="training-card">
      <div>
        <p class="eyebrow">今日推荐训练</p>
        <h2>{{ dashboard.todayTraining.title }}</h2>
      </div>
      <div class="training-meta">
        <span>{{ dashboard.todayTraining.duration }}</span>
        <span>{{ dashboard.todayTraining.intensity }}</span>
      </div>
      <p>{{ dashboard.todayTraining.focus }}</p>
    </article>

    <section class="score-panel">
      <div>
        <p class="eyebrow">综合训练收益评分</p>
        <h2>{{ dashboard.benefitScore }} / 100</h2>
      </div>
      <div class="score-ring">{{ dashboard.benefitScore }}</div>
    </section>

    <section class="content-panel">
      <p class="eyebrow">AI推荐理由</p>
      <p>{{ dashboard.aiReason }}</p>
    </section>

    <div class="action-row">
      <button class="primary-button">开始训练</button>
      <RouterLink to="/coach" class="secondary-button">咨询AI</RouterLink>
      <RouterLink to="/plan" class="ghost-button">重新规划</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { dashboard } from '../data/mockData'
</script>
