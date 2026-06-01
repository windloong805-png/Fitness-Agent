export const dashboard = {
  userName: '赵同学',
  greeting: '下午好，赵同学',
  recoveryIndex: 82,
  fatigueIndex: 31,
  benefitScore: 88,
  todayTraining: {
    title: '上肢力量 + 低强度有氧',
    duration: '48 分钟',
    intensity: '中等',
    focus: '胸背激活、心肺维持、疲劳可控',
    reason:
      'Qwen2.5 结合知识库规则判断当前恢复良好，动态规划模块在收益、疲劳与目标约束之间选择了综合收益最高的训练路径。'
  },
  aiReason:
    '知识增强检索到“睡眠充足且疲劳低于 40 时可安排中等强度训练”的运动建议，智能体决策层结合用户反馈闭环，将今日计划调整为力量训练优先、心肺训练辅助。'
}

export const sevenDayPlan = [
  {
    day: '今天',
    type: '上肢力量',
    duration: '48 分钟',
    intensity: '中等',
    reason: '恢复指数较高，适合提升训练收益。'
  },
  {
    day: '周二',
    type: '核心稳定',
    duration: '35 分钟',
    intensity: '中低',
    reason: '降低局部肌群疲劳，保持动作质量。'
  },
  {
    day: '周三',
    type: '下肢力量',
    duration: '45 分钟',
    intensity: '中等',
    reason: '动态规划建议在恢复窗口期安排大肌群刺激。'
  },
  {
    day: '周四',
    type: '主动恢复',
    duration: '28 分钟',
    intensity: '低',
    reason: '控制疲劳积累，为后续训练保留状态。'
  },
  {
    day: '周五',
    type: 'HIIT 燃脂',
    duration: '22 分钟',
    intensity: '较高',
    reason: '在疲劳阈值允许范围内提高能量消耗。'
  },
  {
    day: '周六',
    type: '全身循环',
    duration: '42 分钟',
    intensity: '中等',
    reason: '综合力量、心肺和动作控制收益。'
  },
  {
    day: '周日',
    type: '拉伸与评估',
    duration: '25 分钟',
    intensity: '低',
    reason: '采集反馈，更新下一周期智能体策略。'
  }
]

export const chatMessages = [
  {
    role: 'assistant',
    text: '我是 Fitness-Agent AI 教练。当前基于 Qwen2.5、知识增强规则和动态规划结果，为你解释训练建议。'
  },
  {
    role: 'user',
    text: '今天适合练什么？'
  },
  {
    role: 'assistant',
    text: '今天推荐上肢力量加低强度有氧。你的恢复指数为 82，疲劳指数为 31，预计训练收益较高且风险可控。'
  }
]

export const metrics = [
  { label: '计划完成率', value: '86%', hint: '近 14 天' },
  { label: '目标达成率', value: '72%', hint: '减脂阶段' },
  { label: 'AI推荐采纳率', value: '91%', hint: '反馈闭环' }
]

export const profile = {
  name: '赵同学',
  age: 24,
  height: '176 cm',
  weight: '72 kg',
  goal: '减脂增肌，提升心肺耐力',
  level: '中级训练者',
  limits: ['膝关节避免高冲击跳跃', '睡眠不足时降低 HIIT 强度'],
  model: {
    base: 'Qwen2.5',
    agentMode: '知识增强 + 动态规划',
    feedback: '训练后 RPE、完成度、疲劳感自动进入下一轮决策'
  },
  knowledgeBase: ['运动处方知识库', '动作安全规则库', '营养与恢复建议库']
}
