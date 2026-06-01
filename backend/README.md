# Fitness-Agent Backend

后端服务用于承载 FastAPI 接口、SQLAlchemy 数据模型、Agent 调度层和各业务模块。

## 当前已实现模块

- M1 用户画像模块：`backend/profile/`
- M8 数据存储基础配置：`backend/database.py`

## 数据库配置

当前后端要求连接本地 MySQL 数据库 `fitness_agent`，不再默认使用 SQLite。
M1 用户画像模块以 `backend/profile/models.py` 中的 ORM 模型为数据库结构标准。

1. 安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

2. 创建本地 MySQL 数据库：

```sql
CREATE DATABASE fitness_agent
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

3. 在项目根目录创建 `.env`：

```bash
copy .env.example .env
```

4. 修改 `.env` 中的 MySQL 账号和密码：

```text
DATABASE_URL=mysql+pymysql://root:your_password@127.0.0.1:3306/fitness_agent?charset=utf8mb4
```

`.env` 已在 `.gitignore` 中忽略，不应提交到仓库。

## 启动 FastAPI

请在项目根目录运行：

```bash
uvicorn backend.main:app --reload
```

启动时后端会执行数据库连通性检查，并在开发阶段自动创建用户画像相关数据表。

## 重建 M1 用户画像表

如果本地 MySQL 中已经存在旧版或手工创建的用户画像表，请使用以下命令按项目 ORM 模型重建：

```bash
python -m backend.profile.reset_schema
```

注意：该命令会删除并重建 M1 用户画像相关表，包括 `users`、`user_profiles`、`user_goals`、`daily_statuses`、`user_constraints`、`user_preferences`，执行后旧数据会被清空。

## 已提供接口

- `GET /api/profile/{user_id}`
- `POST /api/profile`
- `PUT /api/profile/{user_id}`
