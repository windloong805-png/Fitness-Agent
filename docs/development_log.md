# Fitness-Agent 开发日志

本文档用于记录项目开发过程，并将每次开发活动映射到论文结构、代码文件和设计原因。

## 日志模板

```text
# YYYY-MM-DD

完成内容：

对应论文章节：

新增文件：

修改文件：

设计原因：

后续计划：
```

## 2026-06-01

完成内容：

- GitHub 仓库初始化
- 项目目录结构创建
- MySQL 数据库建立
- 用户画像数据表设计
- Vue 3 移动端 H5 前端原型创建
- 论文-系统-代码映射体系创建

对应论文章节：

- 第 3 章 系统需求分析与总体设计
- 第 3 章 数据库设计
- 第 4 章 用户画像建模
- 第 6 章 系统实现与界面展示

新增文件：

- `frontend/index.html`
- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/main.js`
- `frontend/src/App.vue`
- `frontend/src/router/index.js`
- `frontend/src/data/mockData.js`
- `frontend/src/components/AppTabBar.vue`
- `frontend/src/pages/Home.vue`
- `frontend/src/pages/Plan.vue`
- `frontend/src/pages/Coach.vue`
- `frontend/src/pages/Data.vue`
- `frontend/src/pages/Mine.vue`
- `frontend/src/assets/styles.css`
- `docs/thesis_mapping.md`
- `docs/system_architecture.md`
- `docs/development_log.md`
- `docs/module_catalog.md`

修改文件：

- `README.md`
- `frontend/README.md`
- `.gitignore`

设计原因：

- 建立“论文章节 ↔ 系统模块 ↔ 代码目录”的三层映射机制，保证后续开发能够直接支撑硕士论文撰写和答辩说明。
- 将用户画像、知识增强、动态规划、Qwen2.5 交互和反馈闭环拆分为可维护模块，降低后续接入 FastAPI、MySQL 和模型服务的复杂度。
- 先完成移动端 H5 原型，使系统功能结构、交互流程和论文展示材料能够提前验证。

后续计划：

- 完善 FastAPI 后端接口目录。
- 实现用户画像 CRUD 与 MySQL 数据读写。
- 建立 RAG 知识库导入与检索流程。
- 实现动态规划训练推荐算法原型。
- 接入 Qwen2.5 模型调用与问答解释接口。

## 2026-06-01 M1 用户画像模块开发

完成内容：

- 创建 `backend/profile/` 用户画像模块目录。
- 创建 SQLAlchemy 模型：`User`、`UserProfile`、`UserGoal`、`DailyStatus`、`UserConstraint`、`UserPreference`。
- 创建 Pydantic Schema，支持画像创建、更新、读取和 AgentContext 输出。
- 创建 `profile_service.py`，实现 `create_profile()`、`update_profile()`、`get_profile()`、`build_agent_context()`。
- 创建 FastAPI 接口：`GET /api/profile/{user_id}`、`POST /api/profile`、`PUT /api/profile/{user_id}`。
- 创建后端数据库基础配置和 FastAPI 应用入口。

对应论文章节：

- 第四章 系统设计
- 第四章 用户画像模型设计
- 第六章 系统实现

新增文件：

- `backend/__init__.py`
- `backend/database.py`
- `backend/main.py`
- `backend/requirements.txt`
- `backend/profile/__init__.py`
- `backend/profile/models.py`
- `backend/profile/schemas.py`
- `backend/profile/context.py`
- `backend/profile/service.py`
- `backend/profile/router.py`

修改文件：

- `backend/README.md`
- `docs/development_log.md`

设计原因：

- M1 用户画像模块是智能体决策的基础输入，需要先形成结构化用户画像、动态状态画像和可复用的 AgentContext。
- AgentContext 将长期画像、训练目标、当日状态、健康限制、偏好和计算状态统一封装，便于后续 RAG、动态规划和 Qwen2.5 模块复用。
- 采用 SQLAlchemy + Pydantic 分层设计，便于后续从本地 SQLite 切换到 MySQL，并接入 FastAPI 服务。

后续计划：

- 增加用户画像模块单元测试。
- 增加数据库迁移工具 Alembic。
- 将前端“我的页”和“数据页”从模拟数据切换为 `/api/profile` 接口数据。
- 在 M4 动态规划模块中接入 `build_agent_context()` 输出。

## 2026-06-01 后端 MySQL 数据库连接配置

完成内容：

- 检查 `backend/database.py`，确认原配置仍存在 SQLite 默认回退。
- 修改数据库配置为必须通过环境变量 `DATABASE_URL` 连接 MySQL。
- 新增 `.env.example`，提供本地 MySQL 数据库 `fitness_agent` 的连接示例。
- 增加 `pymysql` 依赖。
- 在 FastAPI 启动阶段增加数据库连通性检查。
- 更新 `backend/README.md` 的 MySQL 建库、环境变量和启动说明。

对应论文章节：

- 第三章 数据库设计
- 第六章 后端实现

新增文件：

- `.env.example`

修改文件：

- `backend/database.py`
- `backend/main.py`
- `backend/requirements.txt`
- `backend/README.md`
- `docs/development_log.md`

设计原因：

- 数据存储模块需要明确连接论文项目指定的 MySQL 数据库 `fitness_agent`，避免开发阶段误用 SQLite 导致数据库设计与系统实现不一致。
- 使用 `.env` 管理数据库连接信息，避免账号密码进入代码仓库。

后续计划：

- 根据 MySQL 表结构引入 Alembic 迁移管理。
- 增加数据库连接失败时的部署排查文档。

## 2026-06-01 MySQL 外键类型兼容修复

完成内容：

- 定位后端启动时报错：`daily_statuses.user_id` 与 `users.id` 外键字段类型不兼容。
- 检查本地 MySQL `fitness_agent` 已有表结构，确认主键和外键使用 `bigint`。
- 将 M1 用户画像 ORM 模型中的主键、外键从 `Integer` 调整为 `BigInteger`。
- 将 `DailyStatus` ORM 表名从 `daily_statuses` 对齐为已有 MySQL 表 `daily_status`。
- 调整 `User`、`UserProfile`、`UserGoal`、`UserConstraint`、`UserPreference` 模型字段，使其兼容当前 MySQL 表结构。
- 调整 `profile_service.py`，将前端原型字段映射到当前 MySQL 实际字段，避免写入不存在的列。
- 扩展 Pydantic Schema，兼容已有 MySQL 字段和原型字段。

对应论文章节：

- 第三章 数据库设计
- 第四章 用户画像模型设计
- 第六章 后端实现

修改文件：

- `backend/profile/models.py`
- `backend/profile/schemas.py`
- `backend/profile/service.py`
- `docs/development_log.md`

设计原因：

- 当前 MySQL 数据库已经存在用户画像相关数据表，代码模型必须与实际表结构保持一致，否则 FastAPI 启动时自动建表会触发外键类型不兼容。
- 通过对齐 ORM 模型与服务层字段映射，保证后端既能连接本地 MySQL，又能继续向前端和 Agent 调度层输出统一的 AgentContext。

验证结果：

- Python 语法检查通过。
- MySQL `SELECT 1` 连通性检查通过。
- `Base.metadata.create_all(bind=engine)` 启动建表流程通过。
- FastAPI `TestClient` 启动生命周期通过，`GET /` 返回 200。

## 2026-06-01 以项目模型为标准重建 M1 数据库表

完成内容：

- 根据开发规范调整方向：不再以 MySQL 中旧有手工表为标准，而以项目文件中的 ORM 模型和 Schema 字段为标准。
- 恢复 M1 用户画像模块标准字段：`nickname`、`occupation`、`target_date`、`progress`、`daily_statuses`、`soreness_level`、`rpe`、`note`、`preference_type`、`value`、`weight` 等。
- 新增 `backend/profile/reset_schema.py`，用于删除旧表并按 ORM 模型重建 MySQL 表结构。
- 执行数据库重建，将 MySQL `fitness_agent` 中的用户画像相关表调整为项目代码标准字段。
- 更新 `backend/README.md`，增加 M1 用户画像表重建说明。

对应论文章节：

- 第三章 数据库设计
- 第四章 用户画像模型设计
- 第六章 系统实现

新增文件：

- `backend/profile/reset_schema.py`

修改文件：

- `backend/profile/models.py`
- `backend/profile/schemas.py`
- `backend/profile/service.py`
- `backend/README.md`
- `docs/development_log.md`

设计原因：

- 论文项目应保持“系统设计 -> 代码模型 -> 数据库结构”的正向一致性，数据库不应反向约束领域模型。
- 以 ORM 模型作为 M1 用户画像模块的数据结构标准，便于后续 FastAPI、动态规划、RAG 和 Qwen2.5 AgentContext 统一使用。

验证结果：

- Python 语法检查通过。
- MySQL 表结构已重建为项目标准字段。
- `Base.metadata.create_all(bind=engine)` 验证通过。
- FastAPI `TestClient` 启动生命周期通过，`GET /` 返回 200。
- 真实 MySQL 接口测试通过：`POST /api/profile` 返回 201，`GET /api/profile/{user_id}` 返回 200。

## 2026-06-01 创建统一开发规范文档

完成内容：

- 新增 `docs/development_rules.md`，作为 Fitness-Agent 项目的统一开发规范文件。
- 明确项目开发原则、开发前必读文档、模块开发规范、文档更新规范、代码规范、数据库规范、FastAPI 规范、前端规范和 Agent 开发规范。
- 在根 `README.md` 中新增“开发规范”章节，加入统一规范文档入口。

对应论文章节：

- 第三章 系统需求分析与总体设计
- 第六章 系统实现

新增文件：

- `docs/development_rules.md`

修改文件：

- `README.md`
- `docs/development_log.md`

设计原因：

- 项目进入多模块持续开发阶段，需要统一规范约束后续代码、文档、数据库、接口、前端和 Agent 能力开发。
- 通过开发规范文件保证“论文章节 ↔ 系统模块 ↔ 代码目录”三层映射机制长期有效。

后续计划：

- 后续新增模块时，先阅读 `docs/development_rules.md` 并同步更新论文映射文档。

## 2026-06-02 M3 训练收益评估模块开发

完成内容：

- 按 `docs/development_rules.md` 要求阅读开发规范、论文映射、模块目录和系统架构文档。
- 创建 `backend/reward/` 目录。
- 实现 `calculate_recovery()`，计算 0~10 的恢复指数。
- 实现 `calculate_fatigue()`，计算 0~10 的疲劳指数。
- 实现 `calculate_training_benefit()`，计算 0~10 的训练收益。
- 实现 `calculate_total_reward()`，使用可配置权重计算综合收益。
- 实现 `calculate_reward()`，统一输出 Recovery、Fatigue、TrainingBenefit 和 TotalReward。
- 实现 `build_reward_context(user_id)`，从 M1 用户画像模块读取 AgentContext 并扩展 M3 computed_state。
- 创建 M3 Pydantic Schema：`RewardInput`、`RewardOutput`、`AgentContextSchema`、`RewardWeights`。
- 创建 `backend/reward/README.md`，说明模块职责、输入、输出、数据流、对应论文章节以及与 M1/M4 的关系。
- 更新 `docs/thesis_mapping.md` 和 `docs/module_catalog.md`，补充 M3 实际实现目录与职责。

对应论文章节：

- 第四章 4.2 训练收益评估模型设计

新增文件：

- `backend/reward/__init__.py`
- `backend/reward/formulas.py`
- `backend/reward/calculator.py`
- `backend/reward/schemas.py`
- `backend/reward/README.md`

修改文件：

- `docs/thesis_mapping.md`
- `docs/module_catalog.md`
- `docs/development_log.md`

设计原因：

- M3 是 M4 动态规划模块的评价函数来源，需要把用户状态和候选训练动作统一转换为可计算奖励。
- 恢复指数和疲劳指数用于控制训练风险，训练收益用于表达目标贡献，综合收益用于在收益与疲劳代价之间做权衡。
- 将公式层与计算器层分离，可以让 M4 在不依赖数据库的情况下批量调用评价函数，也能让 Qwen2.5 使用结构化解释依据。

后续计划：

- 为 M3 增加 FastAPI 查询接口，便于前端数据页和计划页调用。
- 在 M4 动态规划模块中接入 `calculate_total_reward()`。
- 在实验模块中对不同权重组合进行对比实验。

## 2026-06-02 M3 训练收益评估模块接口开发

完成内容：

- 新增 `backend/reward/router.py`。
- 新增 `POST /api/reward/calculate` 接口，用于直接计算 Recovery、Fatigue、TrainingBenefit 和 TotalReward。
- 新增 `GET /api/reward/context/{user_id}` 接口，用于读取 M1 用户画像并返回包含 M3 computed_state 的扩展 AgentContext。
- 在 `backend/main.py` 注册 M3 路由。
- 更新 `backend/reward/README.md`，补充 FastAPI 接口说明。

对应论文章节：

- 第四章 4.2 训练收益评估模型设计
- 第六章 系统实现

新增文件：

- `backend/reward/router.py`

修改文件：

- `backend/main.py`
- `backend/reward/README.md`
- `docs/development_log.md`

设计原因：

- M3 内部函数适合 M4 动态规划模块直接调用，但接口层有助于前端展示、接口调试和论文答辩演示。
- `POST /api/reward/calculate` 展示奖励函数的纯计算能力。
- `GET /api/reward/context/{user_id}` 展示 M1 用户画像到 M3 训练收益评估的完整数据流。

后续计划：

- 在前端数据页展示 M3 指标。
- 在 M4 动态规划模块中复用 M3 的内部评价函数。

## 2026-06-02 M4 动态规划训练决策模块开发

完成内容：

- 创建 `backend/planner/` 目录。
- 创建 `actions.py`，实现候选训练动作集合生成函数 `generate_candidate_actions()`。
- 创建 `planner.py`，实现核心函数 `evaluate_action_reward()` 和 `plan_weekly_training()`。
- 创建 `schemas.py`，定义 `TrainingAction`、`ActionEvaluation`、`DailyPlan`、`PlannerRequest`、`WeeklyPlanResponse`。
- 创建 `router.py`，新增 `POST /api/planner/plan_weekly` 接口。
- 创建 `README.md`，说明模块功能、输入、输出、数据流和论文对应章节。
- 在 `backend/main.py` 注册 M4 路由。
- 更新 `docs/thesis_mapping.md` 和 `docs/module_catalog.md`，登记 M4 实现补充。

对应论文章节：

- 第四章 4.3 动态规划训练决策模型设计
- 第六章 系统实现

新增文件：

- `backend/planner/__init__.py`
- `backend/planner/actions.py`
- `backend/planner/planner.py`
- `backend/planner/schemas.py`
- `backend/planner/router.py`
- `backend/planner/README.md`

修改文件：

- `backend/main.py`
- `docs/thesis_mapping.md`
- `docs/module_catalog.md`
- `docs/development_log.md`

设计原因：

- M4 是 Fitness-Agent 从“单次训练建议”走向“多日训练计划生成”的关键模块。
- 使用未来 7 天作为决策阶段，使用疲劳桶作为状态变量，可以清晰表达动态规划中的状态转移。
- M4 复用 M3 的奖励函数，而不是重复实现收益公式，保证训练收益评估与计划生成的一致性。
- 接口 `POST /api/planner/plan_weekly` 便于前端计划页展示，也便于论文答辩演示“用户画像 -> 训练收益 -> 动态规划路径”的完整流程。

后续计划：

- 将 M4 输出接入前端计划页。
- 为 M4 增加单元测试和实验对比脚本。
- 后续接入 M2 知识增强模块，对候选动作增加知识库安全约束。
