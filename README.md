# Fitness-Agent

论文题目：《融合知识增强与动态规划的健身智能体研究——基于 Qwen2.5 大模型的实现》

## 项目简介

Fitness-Agent 是面向个性化健身训练推荐场景的硕士论文项目，目标是构建一个融合知识增强、动态规划和大模型智能交互能力的健身智能体系统。

系统以 Qwen2.5 大模型为交互与解释核心，以 RAG 知识增强提升健身建议的可靠性，以动态规划方法生成可解释的训练计划，并通过用户反馈闭环持续优化推荐策略。

## 核心技术

- Qwen2.5 大模型
- RAG 知识增强
- 动态规划训练决策
- Agent 调度与智能体决策
- FastAPI 后端服务
- MySQL 数据存储
- Vue 3 移动端 H5 前端原型

## 项目结构

```text
Fitness_Agent/
├── backend/             后端服务与 API
├── frontend/            Vue 3 移动端 H5 前端原型
├── knowlege_base/       健身知识库
├── rag/                 检索增强生成模块
├── dynamic_planning/    动态规划算法模块
├── qwen/                Qwen2.5 模型调用模块
├── datasets/            数据集与样例数据
├── experiments/         实验与评估
└── docs/                论文与项目文档
```

## 论文映射体系

本项目采用：

```text
论文章节 ↔ 系统模块 ↔ 代码目录
```

三层映射机制，用于保证后续开发、论文撰写、答辩展示和项目管理的一致性。

核心维护文档包括：

- `docs/thesis_mapping.md`：维护系统模块、代码目录和论文章节的三级映射关系。
- `docs/system_architecture.md`：说明整体系统架构、模块关系和数据流。
- `docs/module_catalog.md`：说明每个模块的职责、输入、输出、依赖和创新点。
- `docs/development_log.md`：记录每次开发内容及其对应论文章节。

后续所有新增模块都必须登记到论文映射体系中，明确其对应论文章节和论文创新点，确保工程实现能够持续支撑毕业论文写作与答辩。

## 前端原型运行

```bash
cd frontend
npm install
npm run dev
```

默认访问地址：

```text
http://localhost:5173
```
