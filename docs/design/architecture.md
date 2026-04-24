# 技术架构设计

> 版本: v1.0 | 日期: 2026-04-24 | 状态: 初稿

---

## 1. 整体架构

### 1.1 系统分层

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层 (UI Layer)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Obsidian    │  │ Web AI      │  │ Command Line    │  │
│  │ Client      │  │ Chat UI     │  │ Interface       │  │
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
│  │ Vault       │  │ (Milvus/    │  │ (Neo4j or       │  │
│  │ (Markdown)  │  │ ChromaDB)   │  │ NetworkX)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    基础设施层 (Infra)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ 本地部署    │  │ Docker      │  │ Cloud APIs      │  │
│  │ ( Ollama ) │  │ Compose     │  │ (可选)          │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 技术选型总览

| 层次 | 组件 | 选型 | 理由 |
|------|------|------|------|
| 笔记存储 | Obsidian Vault | **必须** | Karpathy 方法论核心 |
| 本地 LLM | Ollama | 默认推荐 | 完全离线，数据不外泄 |
| 向量数据库 | ChromaDB | MVP 首选 | 轻量、易部署、支持本地 |
| 图数据库 | NetworkX + D3.js | MVP 首选 | 简单够用，浏览器可视化 |
| Embedding | BGE-large-zh | 中文默认 | 中文效果好，开源 |
| LLM | Llama3 / Qwen2 | 按需选择 | 本地运行，支持中文 |
| 后端框架 | FastAPI | **必须** | Python 生态，高性能 |
| 前端 | React + Vite | Web 界面 | 现代化，性能好 |
| 同步方案 | Obsidian Sync / Syncthing | 可选 | 按需选择 |

---

## 2. 核心模块设计

### 2.1 笔记索引模块（Note Indexer）

**职责**：监听 Vault 变化，维护笔记索引。

```python
# 模块：note_indexer.py
class NoteIndexer:
    """
    负责：
    1. 扫描 Obsidian Vault
    2. 解析 Markdown 内容（提取双链、元信息）
    3. 更新向量数据库
    4. 更新图谱数据
    """

    def __init__(self, vault_path: Path, vector_store, graph_store):
        self.vault_path = vault_path
        self.vector_store = vector_store
        self.graph_store = graph_store

    def scan_vault(self):
        """增量扫描 Vault，返回新增/修改/删除的笔记"""
        pass

    def parse_note(self, note_path: Path) -> Note:
        """解析单个笔记"""
        pass

    def extract_links(self, content: str) -> list[Link]:
        """提取双向链接"""
        pass

    def index_note(self, note: Note):
        """索引单篇笔记到向量库 + 图库"""
        pass

    def watch_changes(self):
        """文件监控，持续增量更新"""
        pass
```

**数据流**：
```
Vault File Change → File Watcher → Note Indexer
                                    ├── Parse Markdown
                                    ├── Extract Links & Tags
                                    ├── Chunk Content
                                    ├── Generate Embeddings
                                    ├── Upsert to VectorDB
                                    └── Update GraphDB
```

### 2.2 RAG 编排模块（RAG Orchestrator）

**职责**：协调检索和生成流程。

```python
# 模块：rag_engine.py
class RAGEngine:
    """
    RAG 流程编排：
    1. Query Processing（意图识别）
    2. Retrieval（多路召回）
    3. Reranking（重排序）
    4. Generation（生成回答）
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        vector_store: VectorStore,
        graph_store: GraphStore
    ):
        self.embedding = embedding_service
        self.llm = llm_service
        self.vector = vector_store
        self.graph = graph_store

    async def query(self, question: str, top_k: int = 5) -> RAGResponse:
        # Step 1: Query Understanding
        intent = self.classify_intent(question)

        # Step 2: Multi-retrieval
        if intent == "concept":
            # 优先语义搜索
            semantic_results = await self.vector.search(question, top_k)
            # 结合图谱邻居扩展
            graph_neighbors = await self.expand_via_graph(semantic_results)
            results = self.merge_results(semantic_results, graph_neighbors)
        else:
            results = await self.vector.search(question, top_k)

        # Step 3: Rerank（可选）
        if len(results) > top_k:
            results = self.rerank(question, results, top_k)

        # Step 4: Generate
        context = self.build_context(results)
        answer = await self.llm.generate(
            prompt=self.prompt_template,
            context=context,
            question=question
        )

        return RAGResponse(
            answer=answer,
            sources=[r.note for r in results],
            suggested_questions=self.generate_suggestions(results)
        )
```

### 2.3 Embedding 服务（Embedding Service）

**支持多模型切换**：

```python
# 模块：embedding_service.py
class EmbeddingService:
    """
    支持多种 Embedding 模型：
    - BGE-large-zh（中文首选）
    - text-embedding-3-small（OpenAI）
    - Ollama 本地模型
    """

    PROVIDERS = {
        "bge": BGEModel,
        "openai": OpenAIEmbedding,
        "ollama": OllamaEmbedding,
    }

    def __init__(self, provider: str = "bge", model: str = "BAAI/bge-large-zh-v1.5"):
        self.provider = self.PROVIDERS[provider](model)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """批量生成 embedding"""
        return self.provider.encode(texts)

    def embed_query(self, query: str) -> list[float]:
        """单次查询 embedding"""
        return self.provider.encode([query])[0]
```

### 2.4 LLM 服务（LLM Service）

```python
# 模块：llm_service.py
class LLMService:
    """
    支持多 LLM 后端：
    - Ollama（本地，默认）
    - OpenAI API
    - Anthropic API
    - MiniMax API
    """

    PROVIDERS = {
        "ollama": OllamaLLM,
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "minimax": MiniMaxLLM,
    }

    def __init__(self, provider: str = "ollama", model: str = "llama3"):
        self.provider = self.PROVIDERS[provider](model)

    async def generate(self, prompt: str, system: str = "", **kwargs) -> str:
        """流式生成"""
        async for chunk in self.provider.stream(prompt, system, **kwargs):
            yield chunk

    async def chat(self, messages: list[ChatMessage], **kwargs) -> str:
        """对话模式"""
        return await self.provider.chat(messages, **kwargs)
```

### 2.5 图谱服务（Graph Service）

```python
# 模块：graph_service.py
class GraphService:
    """
    知识图谱管理：
    - 构建：解析双链 → 节点 + 边
    - 查询：邻居节点、路径发现、聚类
    - 可视化：导出 D3.js 兼容格式
    """

    def __init__(self, storage_path: Path):
        self.graph = nx.DiGraph()  # NetworkX
        self.storage_path = storage_path

    def build_from_vault(self, notes: list[Note]):
        """从笔记集合构建图谱"""
        for note in notes:
            self.graph.add_node(note.id, **note.graph_metadata)

        for link in note.links:
            self.graph.add_edge(
                link.source_id,
                link.target_id,
                link_type=link.type
            )

    def get_neighbors(self, note_id: str, depth: int = 1) -> list[str]:
        """获取邻居节点"""
        return list(nx.descendants(self.graph, note_id))[:depth]

    def find_paths(self, source_id: str, target_id: str) -> list[list[str]]:
        """找两节点间所有路径（用于发现隐藏关联）"""
        try:
            return list(nx.all_simple_paths(self.graph, source_id, target_id, cutoff=3))
        except nx.NetworkXNoPath:
            return []

    def get_centrality(self) -> dict[str, float]:
        """计算节点中心性（识别核心概念）"""
        return nx.degree_centrality(self.graph)

    def get_isolated_nodes(self) -> list[str]:
        """获取孤立节点（需要补充链接）"""
        return [n for n in self.graph.nodes() if self.graph.degree(n) == 0]

    def export_d3(self) -> dict:
        """导出 D3.js 力导向图格式"""
        return {
            "nodes": [
                {"id": n, **self.graph.nodes[n]}
                for n in self.graph.nodes()
            ],
            "links": [
                {"source": u, "target": v, **d}
                for u, v, d in self.graph.edges(data=True)
            ]
        }
```

---

## 3. API 设计

### 3.1 REST API

```
POST /api/v1/notes/search       # 语义搜索
POST /api/v1/notes/query        # RAG 问答
GET  /api/v1/notes/{id}         # 获取笔记详情
GET  /api/v1/notes/{id}/backlinks  # 获取反向链接
GET  /api/v1/graph/export       # 导出图谱数据
GET  /api/v1/graph/stats        # 图谱统计
POST /api/v1/index/rebuild      # 重建索引（管理员）
GET  /api/v1/health             # 健康检查
```

### 3.2 请求/响应示例

**语义搜索**：
```json
// POST /api/v1/notes/search
// Request
{
    "query": "注意力机制的工作原理",
    "top_k": 5,
    "filters": {
        "tags": ["深度学习"],
        "date_range": ["2024-01-01", "2024-12-31"]
    }
}

// Response
{
    "results": [
        {
            "note_id": "uuid-001",
            "title": "注意力机制",
            "snippet": "...Self-Attention 通过计算 Query、Key、Value...",
            "score": 0.92,
            "tags": ["深度学习", "NLP"],
            "links": ["transformer", "multi-head"]
        }
    ],
    "total": 1,
    "took_ms": 120
}
```

**RAG 问答**：
```json
// POST /api/v1/notes/query
// Request
{
    "question": "Transformer 的注意力机制是怎么计算的？",
    "mode": "detailed",  // "concise" | "detailed"
    "include_sources": true
}

// Response
{
    "answer": "根据你的笔记，Transformer 的注意力机制计算如下...\n\n1. 计算 Q、K、V 矩阵\n2. ...\n\n来源：[[注意力机制]], [[Transformer架构]]",
    "sources": [
        {"note_id": "uuid-001", "title": "注意力机制"},
        {"note_id": "uuid-002", "title": "Transformer架构"}
    ],
    "suggestions": [
        "Multi-head attention 和 single-head 有什么区别？",
        "如何用 PyTorch 实现注意力？"
    ]
}
```

---

## 4. 数据存储

### 4.1 Vault 结构（Obsidian 标准）

```
vault-root/
├── .obsidian/           # Obsidian 配置
│   ├── plugins/         # 启用的插件
│   ├── workspace.json
│   └── app.json
├── 00-Daily/           # 每日笔记
│   ├── 2024-01-01.md
│   └── 2024-01-02.md
├── 10-Projects/        # 项目笔记
│   ├── nanoGPT/
│   │   ├── README.md
│   │   ├── experiments/
│   │   └── notes/
│   └── llm.c/
├── 20-Concepts/        # 概念卡
│   ├── 注意力机制.md
│   └── Transformer.md
├── 30-Papers/          # 论文笔记
│   └── Attention-Is-All-You-Need.md
├── 40-Resources/       # 资源收藏
│   └── 博客推荐.md
├── MOC/                # Map of Content 索引
│   ├── Deep-Learning-MOC.md
│   └── NLP-MOC.md
└── templates/          # 笔记模板
    ├── Daily-Template.md
    └── Paper-Template.md
```

### 4.2 向量数据库（ChromaDB）

```python
# ChromaDB Collection Schema
collection = client.create_collection(
    name="notes",
    metadata={
        "description": "Karpathy-style knowledge base notes",
        "embedding_model": "BAAI/bge-large-zh-v1.5"
    }
)

# 每条记录
{
    "id": "note_001_chunk_0",
    "embedding": [0.123, ...],  # 1024-dim
    "document": "## 注意力机制\n\nSelf-Attention 是...",  # chunk text
    "metadata": {
        "note_id": "note_001",
        "title": "注意力机制",
        "tags": ["深度学习", "NLP"],
        "created_at": "2024-01-01T10:00:00Z",
        "source_url": null,
        "chunk_index": 0
    }
}
```

### 4.3 图谱存储（NetworkX + JSON）

```json
// graph.json
{
    "version": "1.0",
    "generated_at": "2024-01-01T12:00:00Z",
    "nodes": [
        {
            "id": "note_001",
            "title": "注意力机制",
            "type": "concept",
            "tags": ["深度学习", "NLP"],
            "created_at": "2024-01-01",
            "link_count": 5
        }
    ],
    "edges": [
        {
            "source": "note_001",
            "target": "note_002",
            "type": "relates_to",
            "context": "注意力机制是 Transformer 的核心组件"
        }
    ]
}
```

---

## 5. 部署架构

### 5.1 本地开发环境

```yaml
# docker-compose.yml
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ~/Obsidian/Vault:/app/vault
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - EMBEDDING_PROVIDER=ollama
      - LLM_PROVIDER=ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  ollama_data:
  chroma_data:
```

### 5.2 索引同步机制

```
┌──────────────┐    File Watcher    ┌──────────────┐
│ Obsidian     │ ─────────────────▶ │ Note Indexer │
│ Vault         │                     │              │
└──────────────┘                     └──────┬───────┘
                                             │
                         ┌───────────────────┼───────────────────┐
                         ▼                   ▼                   ▼
                  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                  │  ChromaDB   │     │  NetworkX   │     │   Search    │
                  │ (Vectors)   │     │  (Graph)   │     │   Index     │
                  └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 6. 安全和隐私

### 6.1 数据安全策略

| 措施 | 说明 |
|------|------|
| 本地优先 | 所有笔记数据存储在本地 Vault，不自动上传云端 |
| API 隔离 | LLM API 调用可选本地 Ollama，完全离线 |
| 加密存储 | Vault 可使用 VeraCrypt 加密（可选） |
| 访问控制 | API 支持 JWT 认证 |
| 日志脱敏 | 日志中不记录笔记敏感内容 |

### 6.2 API 安全

```python
# 速率限制
@app.middleware("http:ratelimit")
async def rate_limit(request: Request, call_next):
    # 每个 IP 每分钟 60 次请求
    pass

# JWT 认证
@app.get("/api/v1/notes/search", dependencies=[Security(verify_jwt)])
async def search_notes(...):
    pass
```

---

## 7. 性能优化

### 7.1 索引优化

- **增量索引**：文件监控，只重新索引变更文件
- **批量写入**：ChromaDB 批量 upsert，减少 IO
- **缓存 Embedding**：已计算的不重复计算

### 7.2 查询优化

- **查询缓存**：相同 query 返回缓存结果（TTL=1小时）
- **预热机制**：启动时预加载高频访问笔记
- **异步处理**：RAG 生成异步返回，减少阻塞

### 7.3 图谱优化

- **分层加载**：大图谱按需加载，只渲染可视区域
- **WebGL 渲染**：D3.js + Canvas/WebGL 处理 1000+ 节点
