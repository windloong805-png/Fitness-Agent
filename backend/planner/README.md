# M4 动态规划训练决策模块

模块编号：M4

模块名称：动态规划训练决策模块

对应论文章节：第四章 4.3 动态规划训练决策模型设计

## 模块功能

M4 负责根据用户画像、训练收益评估结果和候选训练动作，生成未来 7 天训练计划。

该模块将 7 天训练安排建模为多阶段决策问题：

- 阶段：未来 7 天中的每一天。
- 状态：用户疲劳状态桶，范围 0~10。
- 动作：力量、有氧、HIIT、核心灵活性、主动恢复等候选训练动作。
- 奖励：来自 M3 的 TotalReward，并加入疲劳路径惩罚。
- 目标：最大化 7 天累计综合收益，同时控制疲劳风险。

## 输入

接口输入：

- `user_id`
- 或 `AgentContext`

模块内部输入：

- M1 用户画像模块输出的 profile、goal、daily_status、constraints、preferences
- M3 训练收益评估模块输出的 recovery、fatigue、training_benefit、total_reward
- 候选训练动作集合

## 输出

输出为 7 天最优训练计划 JSON，包含：

- `total_plan_reward`
- `initial_state`
- `optimal_path`
- 每天的训练类型、强度、时长、收益、疲劳、累计收益和推荐原因

## 数据流

```text
user_id
  -> M1 用户画像模块
  -> M3 build_reward_context
  -> M4 generate_candidate_actions
  -> M4 evaluate_action_reward
  -> M4 plan_weekly_training
  -> 7 天最优训练计划
```

## 与 M1 用户画像模块关系

M4 不直接读取用户画像表。传入 `user_id` 时，M4 通过 M3 的 `build_reward_context()` 获取已经整合好的 AgentContext。

这样设计是为了遵守 Agent 开发规范：跨模块协作通过上下文结构完成，而不是让 M4 直接访问 M1 的数据库细节。

## 与 M3 训练收益评估模块关系

M3 提供单个动作的奖励评价函数，M4 在每个决策阶段调用 M3 的收益计算结果，并结合路径状态进行动态规划搜索。

## FastAPI 接口

### POST /api/planner/plan_weekly

输入：

```json
{
  "user_id": 1
}
```

或：

```json
{
  "agent_context": {}
}
```

输出：

```json
{
  "user_id": 1,
  "horizon_days": 7,
  "total_plan_reward": 0,
  "initial_state": {},
  "optimal_path": [],
  "decision_summary": ""
}
```

## 文件说明

- `actions.py`：候选训练动作库。
- `planner.py`：动态规划核心逻辑。
- `schemas.py`：Pydantic 请求与响应结构。
- `router.py`：FastAPI 接口。
