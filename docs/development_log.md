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
