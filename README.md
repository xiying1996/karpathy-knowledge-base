# Karpathy Knowledge Base

Karpathy 式个人知识库 — 基于 Obsidian + AI 驱动的第二大脑

## 项目简介

这是一个受 Andrej Karpathy 启发的个人知识库系统，融合了 PKM（个人知识管理）最佳实践和现代 AI 技术。系统支持笔记管理、语义搜索和 RAG 问答，所有数据存储在本地 Obsidian Vault 中，确保隐私安全。

## 快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/xiying1996/karpathy-knowledge-base.git
cd karpathy-knowledge-base

# 2. 启动服务
docker compose up --build

# 3. 访问应用
open http://localhost:3000
```

API 服务：http://localhost:8000

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 笔记存储 | Obsidian Vault | - |
| 后端框架 | FastAPI + Python | 3.12+ |
| 前端框架 | React + Vite | TypeScript |
| 向量数据库 | ChromaDB | latest |
| 本地 LLM | Ollama | - |
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
│   │   ├── main.py         # FastAPI 入口
│   │   ├── config.py       # 配置管理
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── models/         # 数据模型
│   ├── tests/              # 单元测试
│   └── pyproject.toml
├── frontend/               # React + Vite 前端
│   ├── src/
│   │   ├── components/     # UI 组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API 调用
│   │   └── App.tsx
│   └── package.json
├── vault/                  # Obsidian Vault
│   └── demo/               # 示例笔记
├── docker-compose.yml       # Docker Compose 配置
├── Makefile                # 常用命令
└── README.md
```

## 主要功能

- [x] **笔记管理** - 笔记列表、详情查看
- [x] **语义搜索** - 基于向量数据库的语义搜索
- [ ] **RAG 问答** - 基于本地 LLM 的智能问答（开发中）
- [ ] **双向链接** - Obsidian 风格的双向链接（规划中）
- [ ] **知识图谱** - 可视化知识网络（规划中）

## 常用命令

```bash
make dev          # 开发模式启动
make up           # 后台启动
make down         # 停止服务
make test         # 运行测试
make lint         # 代码检查
make logs         # 查看日志
```

## 开发指南

### 后端开发

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## 环境变量

### Backend (.env)

```
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_HOST=localhost:8000
DATA_DIR=./vault
VAULT_PATH=./vault
```

### Frontend (.env)

```
VITE_API_BASE_URL=http://localhost:8000
```

## 相关文档

- [需求文档](docs/design/requirements.md)
- [架构设计](docs/design/architecture.md)
- [技术选型](docs/design/tech-stack.md)
- [用户流程](docs/design/user-flow.md)

## License

MIT
