# Karpathy Knowledge Base

Karpathy 式个人知识库 — 基于 Obsidian + AI 驱动的第二大脑

## 项目简介

这是一个受 Andrej Karpathy 启发的个人知识库系统，融合了 PKM（个人知识管理）最佳实践和现代 AI 技术。系统支持笔记管理、语义搜索和 RAG 问答，所有笔记数据存储在本地 Obsidian Vault 中，确保隐私安全。

## 快速启动

### Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/xiying1996/karpathy-knowledge-base.git
cd karpathy-knowledge-base

# 2. 配置环境变量（可选）
cp backend/.env.example backend/.env
# 编辑 backend/.env，配置 LLM API Key

# 3. 启动服务
docker compose up --build

# 4. 访问应用
open http://localhost:3000
```

### 本地开发

```bash
# 启动 ChromaDB（向量数据库）
docker run -d --name chromadb -p 8001:8000 chromadb/chroma

# 启动后端
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8002

# 启动前端（新终端）
cd frontend
npm install
npm run dev
```

访问地址：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8002

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 笔记存储 | Obsidian Vault | - |
| 后端框架 | FastAPI + Python | 3.12+ |
| 前端框架 | React + Vite | TypeScript |
| 向量数据库 | ChromaDB | latest |
| LLM 服务 | MiniMax / DeepSeek | 云端 API |
| 容器化 | Docker Compose | - |
| UI 样式 | Tailwind CSS | 3.4+ |

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层 (UI Layer)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Web AI      │  │ Obsidian    │  │ Command Line    │  │
│  │ Chat UI     │  │ Client      │  │ Interface       │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    AI 服务层 (AI Layer)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Embedding   │  │ LLM         │  │ RAG             │  │
│  │ Service     │  │ Service     │  │ Orchestrator    │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    数据层 (Data Layer)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Obsidian    │  │ Vector DB   │  │ Graph DB        │  │
│  │ Vault       │  │ (ChromaDB)  │  │ (NetworkX)      │  │
│  │ (Markdown)  │  │             │  │                 │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

详细架构设计请参阅 [docs/design/architecture.md](docs/design/architecture.md)

## 项目结构

```
karpathy-knowledge-base/
├── docs/
│   └── design/              # 设计文档
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # FastAPI 入口（含 lifespan 管理）
│   │   ├── config.py       # 配置管理（Pydantic Settings）
│   │   ├── middleware/     # 中间件
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── models/         # 数据模型
│   ├── tests/              # 单元测试（32 个全部通过）
│   └── pyproject.toml
├── frontend/               # React + Vite 前端
│   ├── src/
│   │   ├── pages/          # 页面（Home/Search/Chat/NoteDetail）
│   │   ├── services/       # API 调用（axios 封装）
│   │   └── App.tsx         # 路由配置
│   └── package.json
├── vault/                  # Obsidian Vault
│   └── demo/               # 示例笔记（5 篇）
├── docker-compose.yml       # Docker Compose 配置
├── Makefile                # 常用命令
└── README.md
```

## 主要功能

### 已实现 ✅

- [x] **笔记管理** - 笔记列表、详情查看、双向链接渲染
- [x] **语义搜索** - 基于 ChromaDB 向量数据库的语义搜索，支持关键词高亮
- [x] **RAG 问答** - 基于 MiniMax/DeepSeek 的智能问答，带来源追溯
- [x] **双向链接** - Obsidian 风格 `[[笔记名]]` 双向链接解析
- [x] **文件监控** - 自动检测 Vault 文件变更并同步到向量数据库
- [x] **API Key 认证** - 可选的 `X-API-Key` 请求头认证

### 开发中 🚧

- [ ] **笔记编辑** - 创建/编辑/删除笔记（当前只读）
- [ ] **知识图谱** - 可视化知识网络
- [ ] **搜索历史** - 保存搜索记录

### 规划中 📋

- [ ] **间隔复习** - 基于 SRS 的笔记复习
- [ ] **标签管理** - 标签云、标签筛选
- [ ] **流式响应** - SSE/WebSocket 实时回答

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/notes` | 笔记列表（支持 `?search=` 过滤） |
| GET | `/api/notes/{note_id}` | 获取指定笔记详情 |
| POST | `/api/search` | 语义搜索 |
| POST | `/api/rag/ask` | RAG 问答 |

## 常用命令

```bash
make dev          # 开发模式启动（重新构建）
make up           # 后台启动
make down         # 停止服务
make test         # 运行测试
make lint         # 代码检查（Ruff + ESLint）
make logs         # 查看日志
```

## 开发指南

### 后端开发

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8002
```

运行测试：
```bash
cd backend
pytest tests/ -v
```

代码检查：
```bash
cd backend
ruff check .
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

代码检查：
```bash
cd frontend
npm run lint
```

## 环境变量

### Backend (.env)

```bash
# LLM Provider (minimax | deepseek)
LLM_PROVIDER=minimax

# MiniMax 配置
MINIMAX_API_KEY=sk-xxx
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-M2.7

# DeepSeek 配置
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# ChromaDB 配置
CHROMA_HOST=localhost:8001
CHROMA_PORT=8001

# Vault 路径（建议使用绝对路径）
VAULT_PATH=/path/to/vault

# 可选：API Key 认证
API_KEY=your-secret-key

# CORS 配置
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8002
```

## 笔记格式

笔记使用 Markdown + YAML frontmatter：

```markdown
---
title: 笔记标题
tags:
  - concept
  - pkm
created: 2026-04-20
---

# 笔记标题

笔记内容...

相关链接：[[其他笔记]]
```

- **ID**：等于文件名（不含 `.md`）
- **标题**：优先使用 frontmatter 中的 `title`，否则从 `#` 提取
- **标签**：支持字符串或对象格式
- **双向链接**：使用 `[[笔记名]]` 语法

## 相关文档

- [需求文档](docs/design/requirements.md)
- [架构设计](docs/design/architecture.md)
- [技术选型](docs/design/tech-stack.md)
- [用户流程](docs/design/user-flow.md)

## License

MIT
