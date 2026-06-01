<template>
  <section class="page">
    <header class="page-header">
      <p class="eyebrow">动态规划训练计划</p>
      <h1>今日与未来 7 天安排</h1>
      <p>智能体在收益最大化、疲劳约束和用户反馈之间搜索当前最优路径。</p>
    </header>

    <article class="content-panel featured-plan">
      <p class="eyebrow">今日计划</p>
      <h2>{{ sevenDayPlan[0].type }}</h2>
      <div class="training-meta">
        <span>{{ sevenDayPlan[0].duration }}</span>
        <span>{{ sevenDayPlan[0].intensity }}</span>
      </div>
      <p>{{ sevenDayPlan[0].reason }}</p>
    </article>

    <section class="plan-list">
      <article v-for="item in sevenDayPlan" :key="item.day" class="plan-item">
        <div class="day-badge">{{ item.day }}</div>
        <div>
          <h3>{{ item.type }}</h3>
          <p>{{ item.reason }}</p>
          <div class="training-meta compact">
            <span>{{ item.duration }}</span>
            <span>{{ item.intensity }}</span>
          </div>
        </div>
      </article>
    </section>

    <section class="path-panel">
      <p class="eyebrow">动态规划最优路径</p>
      <h2>状态转移：恢复状态 → 训练动作 → 收益反馈</h2>
      <div class="path-steps">
        <span>知识库约束</span>
        <span>Qwen2.5 解释</span>
        <span>DP 评分</span>
        <span>用户反馈闭环</span>
      </div>
      <p>系统将每天视为一个决策阶段，综合训练收益、疲劳代价、健康限制和目标进度，生成一条可调整的 7 天训练路径。</p>
    </section>
  </section>
</template>

<script setup>
import { sevenDayPlan } from '../data/mockData'
</script>
