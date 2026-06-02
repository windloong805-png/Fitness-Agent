# M3 训练收益评估模块

模块名称：M3 训练收益评估模块

对应论文章节：第四章 4.2 训练收益评估模型设计

## 模块职责

M3 负责将用户状态和候选训练动作转化为可计算、可解释的训练评价信号，核心指标包括：

- Recovery：恢复指数，0~10，越高代表越适合训练。
- Fatigue：疲劳指数，0~10，越高代表越需要恢复。
- TrainingBenefit：训练收益，0~10，用于评估本次训练价值。
- TotalReward：综合收益，0~10，为 M4 动态规划模块提供评价函数。

## 输入

来自 M1 用户画像模块：

- profile：用户长期画像。
- goal：训练目标。
- daily_status：每日状态。
- constraints：健康限制。
- preferences：训练偏好。

来自候选训练动作：

- training_type：训练类型。
- intensity：训练强度。
- duration：预计训练时长。
- goal_match_score：目标匹配分。

## 输出

- `RewardOutput`
- `AgentContextSchema`

`AgentContextSchema.computed_state` 包含：

- bmi
- recovery
- fatigue
- training_benefit
- total_reward

## 数据流

```text
M1 用户画像模块
  -> AgentContext
  -> M3 训练收益评估模块
  -> Recovery / Fatigue / TrainingBenefit / TotalReward
  -> M4 动态规划模块
  -> M5 Qwen 交互模块解释训练依据
```

## 与 M1 用户画像模块关系

M3 不直接构建用户画像，而是调用 M1 的 `get_profile()` 获取标准 AgentContext。

这样设计的原因是保持模块边界清晰：M1 负责用户状态建模，M3 负责训练收益评价，后续 M4 和 M5 通过统一 AgentContext 使用结果。

## 与 M4 动态规划模块关系

M4 需要在多个候选训练动作之间搜索最优路径。M3 提供 `calculate_total_reward()` 作为评价函数，使动态规划能够比较不同训练动作在收益、恢复和疲劳之间的权衡。

## 与 Qwen2.5 的关系

M3 的输出不仅是数值，也包含解释依据。Qwen2.5 可以基于 Recovery、Fatigue、TrainingBenefit 和 TotalReward 生成自然语言说明，例如“为什么今天适合中等强度力量训练”。

## 文件说明

- `formulas.py`：纯公式层，不读取数据库。
- `calculator.py`：计算器层，负责连接 M1 AgentContext 与 M3 评价结果。
- `schemas.py`：Pydantic 数据结构。
- `router.py`：FastAPI 接口层，提供训练收益计算和 M3 AgentContext 查询接口。
- `__init__.py`：模块导出入口。

## FastAPI 接口

### POST /api/reward/calculate

输入：

- `RewardInput`

输出：

- `RewardOutput`

用途：

- 直接计算 Recovery、Fatigue、TrainingBenefit 和 TotalReward。
- 用于前端调试、论文演示和 M3 公式验证。

### GET /api/reward/context/{user_id}

输入：

- `user_id`
- 可选 query 参数：`training_type`、`intensity`、`duration`、`goal_match_score`、`training_load`、`soreness_count`、`stress_score`、`sleep_quality_score`

输出：

- `AgentContextSchema`

用途：

- 从 M1 用户画像模块读取用户上下文。
- 计算并返回包含 M3 computed_state 的扩展 AgentContext。
