<template>
  <section class="page coach-page">
    <header class="page-header">
      <p class="eyebrow">Qwen2.5 AI 教练</p>
      <h1>训练问答与决策解释</h1>
      <p>围绕知识增强检索、动态规划结果和个人反馈提供自然语言说明。</p>
    </header>

    <section class="chat-window">
      <article v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
        <p>{{ message.text }}</p>
      </article>
    </section>

    <div class="quick-questions">
      <button v-for="question in quickQuestions" :key="question" type="button" @click="fillQuestion(question)">
        {{ question }}
      </button>
    </div>

    <form class="chat-input" @submit.prevent="sendQuestion">
      <input v-model="draft" type="text" placeholder="向 AI 教练提问，例如：今天适合练什么？" />
      <button type="submit">发送</button>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { chatMessages } from '../data/mockData'

const messages = ref([...chatMessages])
const draft = ref('')

const quickQuestions = ['今天适合练什么？', '如何减脂？', '疲劳高还要训练吗？']

function fillQuestion(question) {
  draft.value = question
}

function sendQuestion() {
  const text = draft.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', text })
  messages.value.push({
    role: 'assistant',
    text: '我会先调用知识库规则识别训练风险，再结合动态规划推荐路径和你的反馈记录，给出可解释建议。当前原型使用模拟数据，后续可接入 FastAPI 与 Qwen2.5 服务。'
  })
  draft.value = ''
}
</script>
