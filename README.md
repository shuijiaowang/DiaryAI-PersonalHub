# DiaryAI · Personal Hub

> 以「每日日记」为唯一输入，由 AI 把自然语言切片成结构化数据，沉淀成一份持续生长的「个人数字档案」，并在档案之上提供统计、提醒、陪伴和自动化能力。

需求与设计文档见 [`docs/`](./docs)：
- [项目文档（需求 / 想法）](./docs/项目文档_ai.md)
- [设计文档（技术栈 / 架构）](./docs/设计文档_ai.md)

---

## 目录

```
.
├── server/      # FastAPI + SQLAlchemy + Postgres + Celery 后端
├── web/         # Vue 3 + TS + Vite + Naive UI 前端
├── docs/        # 需求 / 设计 / 历史文档
└── docker-compose.yml
```

## 技术栈一览

- **后端**：Python 3.11 + FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2
- **数据库**：PostgreSQL 16/17（JSONB + GIN 索引），Redis 7（缓存 / 任务队列，可选）
- **后台任务**：FastAPI BackgroundTasks（MVP）→ Celery（横向扩展）
- **LLM**：DeepSeek（默认）/ OpenAI / Ollama（可热切换的 Provider 抽象）
- **前端**：Vue 3 + TypeScript + Vite + Pinia + Naive UI + ECharts

## 快速开始（Docker，推荐）

```bash
# 1. 准备后端环境变量
cp server/.env.example server/.env
# 编辑 server/.env，至少填入 DEEPSEEK_API_KEY

# 2. 拉起 Postgres + Redis + API + Web
docker compose up -d postgres redis api web

# 3. 第一次运行需要建表
docker compose exec api alembic revision --autogenerate -m "init"
docker compose exec api alembic upgrade head

# 4. 打开
# 前端:  http://localhost:5173
# API:  http://localhost:8000/docs   (Swagger UI)

# 5. 可选：启动 Celery worker
docker compose --profile worker up -d worker
```

## 本地开发（不用 Docker）

后端：

```bash
cd server
python -m venv .venv && .venv/Scripts/Activate.ps1   # Windows
pip install -e ".[dev]"
cp .env.example .env                                  # 编辑 .env
alembic upgrade head
uvicorn app.main:app --reload
```

前端：

```bash
cd web
pnpm install
pnpm dev
```

## 项目原则（写给 AI 也写给我自己）

1. 任何 LLM 调用必须走 `app/ai/providers/base.py`，禁止业务代码直接 import `openai`。
2. 任何 AI 输出必须经过 Pydantic 校验后才能入库。
3. API Key、密码、密钥只能从环境变量读，禁止硬编码。
4. 数据库写操作必须在 Service 层，路由层只负责入参校验与调用。
5. 加新模块 = 在 `server/app/modules/` 下新增一个目录，**不要**改主流程。
6. 时间字段统一 `timestamptz`，业务里全程 UTC，前端再转本地时区。

详细开发顺序与硬约束见 [`docs/设计文档_ai.md`](./docs/设计文档_ai.md)。
