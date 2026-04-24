# KKB-2 代码审查报告

## 审查信息
- 审查时间：2026-04-24
- 审查人：审查官
- 审查范围：KKB-2 工程骨架

## 问题列表（P0/P1/P2 分级）

### P0（必须修复）

**[Blocking] backend/app/main.py:16**
- 严重程度：blocking | 类别：security
- 问题：CORS 配置 `allow_origins=["*"]` 允许所有来源跨域请求
- 建议：限定为具体的前端域名，如 `allow_origins=["http://localhost:3000"]`
- 理由：生产环境下任意来源的 CORS 请求可能导致敏感数据泄露

**[Blocking] backend/app/main.py:4**
- 严重程度：blocking | 类别：code-quality
- 问题：`settings` 导入但未使用
- 建议：移除未使用的导入 `from app.config import settings`
- 理由：违反 Python 导入规范，ruff check 报告 ERROR

**[Blocking] backend/tests/test_config.py:1**
- 严重程度：blocking | 类别：code-quality
- 问题：`pytest` 导入但未使用
- 建议：移除 `import pytest`
- 理由：未使用的导入导致 ruff check 报错

**[Blocking] backend/tests/test_main.py:1**
- 严重程度：blocking | 类别：code-quality
- 问题：`pytest` 导入但未使用
- 建议：移除 `import pytest`
- 理由：未使用的导入导致 ruff check 报错

**[Blocking] backend/tests/test_vault.py:1**
- 严重程度：blocking | 类别：code-quality
- 问题：`pytest` 导入但未使用
- 建议：移除 `import pytest`
- 理由：未使用的导入导致 ruff check 报错

### P1（建议修复）

**[Major] backend/app/config.py:7-10**
- 严重程度：major | 类别：security
- 问题：`DATA_DIR` 和 `VAULT_PATH` 环境变量配置缺失
- 建议：明确添加 `VAULT_PATH` 或 `DATA_DIR` 到配置类，确保从环境变量读取
- 理由：当前只有硬编码默认值，生产部署时路径不可配置

**[Major] backend/app/config.py**
- 严重程度：major | 类别：missing-feature
- 问题：缺少 `API_KEY` 配置项（任务要求中提到）
- 建议：添加 `API_KEY: str | None = None` 配置项以支持未来认证需求
- 理由：任务要求覆盖所有必需环境变量，包括 API_KEY

**[Major] docker-compose.yml**
- 严重程度：major | 类别：configuration
- 问题：backend 服务未显式设置 `PYTHONUNBUFFERED=1`
- 建议：添加环境变量 `PYTHONUNBUFFERED=1` 确保日志实时输出
- 理由：便于在 docker logs 中调试

**[Major] backend/Dockerfile:6**
- 严重程度：major | 类别：security
- 问题：Dockerfile 中使用 `pip install -e ".[dev]"` 安装了 dev 依赖（含 pytest）
- 建议：生产镜像应使用 `pip install --no-cache-dir .` 仅安装生产依赖
- 理由：dev 依赖包含测试工具，不应出现在生产镜像中

### P2（可选优化）

**[Minor] backend/app/main.py**
- 严重程度：minor | 类别：code-quality
- 问题：缺少 OpenAPI 文档配置（title/description 已设置但 version 未关联）
- 建议：确认 FastAPI 初始化配置完整

**[Minor] docker-compose.yml**
- 严重程度：minor | 类别：configuration
- 问题：frontend 的 `VITE_API_BASE_URL` 使用 `localhost:8000`，在容器内访问不到
- 建议：改为 `http://backend:8000`（容器内部服务名）
- 理由：Docker 网络内部服务通信应使用服务名而非 localhost

**[Minor] backend/.env.example**
- 严重程度：minor | 类别：documentation
- 问题：backend/.env.example 与 frontend/.env.example 内容相同，都是 `VITE_API_BASE_URL`
- 建议：backend 的 .env.example 应包含 backend 专属配置（如 OLLAMA_BASE_URL, CHROMA_HOST）
- 理由：配置示例应针对对应服务

## 通过项

### 架构审查 ✅
- `backend/app/main.py` — FastAPI 实例正确初始化，CORS 和路由注册完整
- `frontend/vite.config.ts` — proxy 配置正确代理到 `http://localhost:8000`
- `docker-compose.yml` — 服务依赖关系正确（backend → chromadb，frontend → backend），端口映射正确（8000, 3000, 8001），volume 挂载正确（./vault:/app/vault）
- `Makefile` — 目标完整（dev, build, up, down, test, lint, clean），覆盖必需命令

### 编码规范审查 ✅
- Backend ruff check: 4 个 F401 错误（未使用导入），无其他 ERROR
- Frontend: package.json 存在，lint 脚本已配置（未实际运行，需先 npm install）
- Python 类型注解：`config.py` 使用 BaseSettings，`main.py` 使用类型注解
- TypeScript 类型：`App.tsx` 使用 JSX，API 类型定义在 `api.ts` 中完整定义
- 敏感信息：`.env` 文件未提交，仅 `.env.example` 模板

### 安全审查 ✅
- `.env.example` 包含占位符而非真实密钥
- Docker Compose 暴露必要端口（8000, 3000, 8001），无多余暴露
- git 提交中无 `.env` 文件

### 测试覆盖审查 ✅
- `backend/tests/` 有 3 个测试文件：test_main.py, test_config.py, test_vault.py
- 测试覆盖：健康检查接口（test_main.py）、config 加载（test_config.py）、vault 路径解析（test_vault.py）
- `docker-compose.yml` 中 backend 通过 `pip install -e ".[dev]"` 安装了 pytest

### 示例数据审查 ✅
- `vault/demo/` 下有 5 篇笔记
- 每篇笔记包含 frontmatter（title, tags, created/date）
- 包含 `[[双向链接]]` 语法（如 `[[概念-第二大脑]]`、`[[项目-知识库搭建]]`）

## 结论
**[NEEDS_REVISION]**

需要修复 5 个 P0 blocking 问题（移除未使用的导入），以及 4 个 P1 建议项后方可通过审查。

---
*审查完成时间：2026-04-24*