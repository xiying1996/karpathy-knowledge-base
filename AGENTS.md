# Karpathy Knowledge Base - Agent 指南

> 本文件供 AI 编码助手使用，包含项目架构、开发规范和关键约定。

---

## 1. 项目概述

Karpathy Knowledge Base 是一个受 Andrej Karpathy 启发的**个人知识库系统**，融合了 PKM（个人知识管理）最佳实践和现代 AI 技术。

### 核心特性

- **笔记存储**：基于 Obsidian Vault，本地 Markdown 文件
- **语义搜索**：基于 ChromaDB 向量数据库的语义搜索
- **RAG 问答**：基于本地 LLM 的智能问答（开发中）
- **双向链接**：Obsidian 风格的双向链接 `[[笔记名]]`
- **文件监控**：Vault 文件变更自动同步到向量数据库

### 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 笔记存储 | Obsidian Vault | - |
| 后端框架 | FastAPI + Python | 3.12+ |
| 前端框架 | React + Vite | TypeScript |
| 向量数据库 | ChromaDB | latest |
| 本地 LLM | Ollama | - |
| 容器化 | Docker Compose | - |
| UI 样式 | Tailwind CSS | 3.4+ |

---

## 2. 项目结构

```
karpathy-knowledge-base/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # FastAPI 入口，包含 lifespan 管理
│   │   ├── config.py        # 配置管理（Pydantic Settings）
│   │   ├── routers/         # API 路由
│   │   │   ├── health.py    # 健康检查 /api/health
│   │   │   ├── notes.py     # 笔记管理 /api/notes
│   │   │   ├── search.py    # 语义搜索 /api/search
│   │   │   └── rag.py       # RAG 问答 /api/rag/ask（开发中）
│   │   ├── services/       # 业务逻辑
│   │   │   ├── vault_reader.py    # 解析 Obsidian Vault
│   │   │   ├── vector_store.py    # ChromaDB 向量存储
│   │   │   ├── indexer.py         # 笔记索引器
│   │   │   └── file_watcher.py   # 文件监控
│   │   └── models/         # Pydantic 数据模型
│   ├── tests/              # pytest 单元测试
│   ├── pyproject.toml     # Python 依赖管理
│   ├── Dockerfile         # 生产镜像
│   └── Dockerfile.dev     # 开发镜像（包含 dev 依赖）
├── frontend/               # React + Vite 前端
│   ├── src/
│   │   ├── main.tsx       # React 入口
│   │   ├── App.tsx        # 路由配置
│   │   ├── pages/         # 页面组件
│   │   │   ├── Home.tsx   # 笔记列表页
│   │   │   ├── Search.tsx # 语义搜索页
│   │   │   └── Chat.tsx   # AI 问答页
│   │   └── services/      # API 调用
│   │       └── api.ts     # axios API 封装
│   ├── package.json
│   ├── vite.config.ts     # Vite 配置，包含 API 代理
│   └── Dockerfile
├── vault/                  # Obsidian Vault
│   └── demo/               # 示例笔记（*.md 文件）
├── docs/                  # 设计文档
│   └── design/            # 架构、需求、技术选型文档
├── docker-compose.yml      # Docker Compose 配置
├── Makefile               # 常用命令
└── README.md
```

---

## 3. 环境变量

### Backend (`backend/.env`)

```bash
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_HOST=localhost:8000
CHROMA_PORT=8000
DATA_DIR=./vault
VAULT_PATH=./vault
LOG_LEVEL=INFO
API_KEY=
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
FILE_WATCHER_ENABLED=true
FILE_WATCHER_MODE=watch
FILE_WATCHER_POLL_INTERVAL=2
FILE_WATCHER_DEBOUNCE=2
```

### Frontend (`frontend/.env`)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

> 注意：在 Docker 环境中，前端的 `VITE_API_BASE_URL` 应设为 `http://backend:8000`

---

## 4. 常用命令

### Docker Compose（推荐）

```bash
make dev     # 开发模式启动（重新构建）
make up      # 后台启动
make down    # 停止服务
make logs    # 查看日志
```

### 后端开发

```bash
# 安装依赖
make install-backend-deps
# 或
cd backend && pip install -e ".[dev]"

# 运行测试
make test

# 代码检查
make lint

# 启动开发服务器
cd backend && uvicorn app.main:app --reload
```

### 前端开发

```bash
# 安装依赖
make install-frontend-deps
# 或
cd frontend && npm install

# 开发服务器（端口 3000）
cd frontend && npm run dev

# 构建生产版本
cd frontend && npm run build

# 代码检查
cd frontend && npm run lint
```

### 调试命令

```bash
make logs-backend    # 查看后端日志
make logs-frontend  # 查看前端日志
make backend-shell   # 进入后端容器 shell
make frontend-shell  # 进入前端容器 shell
```

---

## 5. API 设计

### 已实现的端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 根路径，返回 API 版本信息 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/notes` | 笔记列表（支持 `?search=` 过滤） |
| GET | `/api/notes/{note_id}` | 获取指定笔记详情 |
| POST | `/api/search` | 语义搜索（需要 ChromaDB） |
| POST | `/api/rag/ask` | RAG 问答（开发中，返回 501） |

### 请求/响应示例

**笔记列表**：
```json
GET /api/notes
Response: {
  "notes": [
    {
      "id": "概念-第二大脑",
      "title": "第二大脑",
      "content": "...",
      "path": "demo/概念-第二大脑.md",
      "tags": ["concept", "pkm"],
      "links": ["MOC-知识管理"],
      "created": "2026-04-20"
    }
  ],
  "total": 5
}
```

**语义搜索**：
```json
POST /api/search
Request: { "query": "第二大脑是什么", "limit": 10 }
Response: {
  "results": [
    {
      "id": "概念-第二大脑",
      "title": "第二大脑",
      "snippet": "...第二大脑是一种利用...",
      "score": 0.92
    }
  ],
  "query": "第二大脑是什么"
}
```

---

## 6. 代码风格

### Python（后端）

- 使用 **Ruff** 进行代码检查和格式化
- 目标 Python 版本：3.12+
- 行长度限制：100 字符
- Pydantic 用于数据验证和序列化
- 异步优先（使用 `async/await`）

配置位于 `backend/pyproject.toml`：
```toml
[tool.ruff]
line-length = 100
target-version = "py312"
```

### TypeScript（前端）

- 使用 ESLint + TypeScript 插件
- 严格模式开启（`strict: true`）
- React 函数组件，使用 Hooks
- 使用 `axios` 进行 API 调用

配置位于 `frontend/tsconfig.json`：
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

---

## 7. 测试

### 后端测试（pytest）

测试文件位于 `backend/tests/`：

| 文件 | 描述 |
|------|------|
| `test_config.py` | 配置测试 |
| `test_vault.py` | Vault 路径测试 |
| `test_notes.py` | 笔记 API 测试 |
| `test_search.py` | 搜索功能测试（使用 mock） |
| `test_indexer.py` | 索引器测试 |
| `test_file_watcher.py` | 文件监控测试 |
| `conftest.py` | pytest fixture 配置 |

运行测试：
```bash
make test          # 基础测试
make test-backend  # 详细测试（-v 参数）
```

### 前端测试

> 当前无前端测试配置。

---

## 8. 核心模块说明

### VaultReader（`backend/app/services/vault_reader.py`）

负责解析 Obsidian Vault 中的 Markdown 文件：

- 读取 YAML frontmatter 元数据
- 提取笔记标题（支持 `# 标题` 语法）
- 解析双向链接 `[[笔记名]]`
- 按 `id`（文件名）查找笔记

关键方法：
- `read_note(path)` - 读取单个笔记
- `list_notes(search)` - 列出所有笔记（支持搜索过滤）
- `get_note_by_id(note_id)` - 按 ID 获取笔记

### VectorStore（`backend/app/services/vector_store.py`）

ChromaDB REST API 客户端：

- 连接远程 ChromaDB 服务
- 查询 `notes` collection
- 返回相关性得分和片段

### Indexer（`backend/app/services/indexer.py`）

笔记索引器：

- 将笔记内容分块（按行分块，chunk_size=500）
- 同步到 ChromaDB 向量数据库
- 支持增量 upsert/delete

### FileWatcher（`backend/app/services/file_watcher.py`）

基于 `watchdog` 的文件监控：

- 支持 `watch`（inotify/FSEvents）和 `poll` 两种模式
- 防抖处理（debounce=2秒）
- 监听 `.md` 文件的 CREATE/MODIFY/DELETE 事件

---

## 9. 笔记格式规范

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
- **标签**：支持字符串或对象 `{status: "..."}` 格式
- **双向链接**：使用 `[[笔记名]]` 语法

---

## 10. 架构要点

### 应用生命周期

`backend/app/main.py` 使用 FastAPI `lifespan` 管理：

1. 启动时：如果 `FILE_WATCHER_ENABLED=true`，启动 FileWatcher 和 Indexer
2. 运行时：处理 API 请求
3. 关闭时：停止 FileWatcher

### 依赖注入模式

后端使用**全局单例模式**管理服务实例：

```python
_vault_reader: VaultReader | None = None

def get_vault_reader() -> VaultReader:
    global _vault_reader
    if _vault_reader is None:
        _vault_reader = VaultReader(settings.VAULT_PATH)
    return _vault_reader
```

### 前端路由

使用 `react-router-dom`：

- `/` → `Home.tsx` - 笔记列表
- `/search` → `Search.tsx` - 语义搜索
- `/chat` → `Chat.tsx` - AI 问答

### API 代理

开发环境下，Vite 将 `/api` 请求代理到 `http://localhost:8000`（详见 `frontend/vite.config.ts`）。

---

## 11. Docker 部署

### 服务架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   frontend  │────▶│   backend   │────▶│   chromadb   │
│  (port 3000)│     │  (port 8000)│     │  (port 8001) │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   ollama    │
                   │ (port 11434)│
                   │  (可选/本地) │
                   └─────────────┘
```

### 镜像说明

| 镜像 | Dockerfile | 描述 |
|------|------------|------|
| backend | `Dockerfile.dev` | 开发镜像，包含 pytest、ruff |
| frontend | `Dockerfile` | 生产镜像，npm run dev |
| chromadb | 官方镜像 | chromadb/chroma:latest |

---

## 12. 开发注意事项

1. **Vault 路径**：默认 `./vault`，可通过 `VAULT_PATH` 环境变量修改
2. **ChromaDB 依赖**：搜索功能依赖 ChromaDB 服务，需先启动 `chromadb` 容器
3. **RAG 功能**：当前 `rag.py` 路由为空，返回 501 状态码
4. **文件监控**：在 Docker 中运行时会挂载 `./vault:/app/vault`
5. **中文支持**：系统专为中文笔记优化，Embedding 模型使用 BGE-large-zh

---

## 13. 相关文档

- [需求文档](docs/design/requirements.md) - 功能需求和用户旅程
- [架构设计](docs/design/architecture.md) - 详细技术架构
- [技术选型](docs/design/tech-stack.md) - 技术对比和选型理由
- [用户流程](docs/design/user-flow.md) - 用户交互流程
