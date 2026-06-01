<template>
  <section class="page">
    <header class="page-header">
      <p class="eyebrow">用户画像与系统设置</p>
      <h1>{{ profile.name }}</h1>
      <p>个人状态、训练目标和健康限制将作为智能体决策的长期约束。</p>
    </header>

    <section class="profile-card">
      <div>
        <span>年龄</span>
        <strong>{{ profile.age }}</strong>
      </div>
      <div>
        <span>身高</span>
        <strong>{{ profile.height }}</strong>
      </div>
      <div>
        <span>体重</span>
        <strong>{{ profile.weight }}</strong>
      </div>
    </section>

    <section class="settings-list">
      <article class="setting-item">
        <span>训练目标</span>
        <strong>{{ profile.goal }}</strong>
      </article>
      <article class="setting-item">
        <span>训练水平</span>
        <strong>{{ profile.level }}</strong>
      </article>
      <article class="setting-item">
        <span>健康限制</span>
        <strong>{{ profile.limits.join('；') }}</strong>
      </article>
      <article class="setting-item">
        <span>模型设置</span>
        <strong>{{ profile.model.base }} · {{ profile.model.agentMode }}</strong>
        <p>{{ profile.model.feedback }}</p>
      </article>
      <article class="setting-item">
        <span>知识库设置</span>
        <div class="tag-list">
          <em v-for="item in profile.knowledgeBase" :key="item">{{ item }}</em>
        </div>
      </article>
    </section>
  </section>
</template>

<script setup>
import { profile } from '../data/mockData'
</script>
