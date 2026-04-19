# DiaryAI-PersonalHub · 设计文档（技术栈与大框架）

> 本文档对应 `项目文档_ai.md` 的需求落地。本项目将由 AI（Cursor / Vibe Coding）完全接管开发，因此技术选型的第一原则是：**AI 友好、生态成熟、文档丰富、能跑就别折腾**。

---

## 0. 推荐技术栈（一张表）

| 层 | 选型 | 备选 | 理由 |
|---|---|---|---|
| **后端语言** | **Python 3.11+** | Go / Node.js (TS) | LLM / Prompt / 数据处理生态最成熟，老代码就是 Python，AI 写起来最顺手 |
| **后端框架** | **FastAPI** | Flask / Django | 异步原生、自动 OpenAPI 文档、Pydantic 校验，和 LLM 工作流天然契合 |
| **数据库** | **PostgreSQL 16+** | MySQL 8 / MongoDB | 同时拥有关系型 + JSONB，事件 `data` 字段可以原生 JSON 存储与索引，鱼和熊掌都要 |
| **ORM** | **SQLAlchemy 2.0 + Alembic** | SQLModel / Tortoise | 标准、稳定、AI 训练数据多 |
| **缓存 / 队列** | **Redis** | — | LLM 调用结果缓存、限流、后台任务（解析日记是耗时操作）|
| **后台任务** | **Celery** 或 **ARQ** | RQ / Dramatiq | 解析日记走异步队列，前端轮询 / WebSocket 拿结果 |
| **LLM 抽象层** | **LangChain** 或 **自封装 Provider 层** | LlamaIndex / 直接 OpenAI SDK | 让 DeepSeek / OpenAI / Claude / 本地 Ollama 可热切换 |
| **向量检索（远期）** | **pgvector**（Postgres 扩展） | Qdrant / Milvus | 不用单独再起一套服务，直接复用 Postgres |
| **认证** | **JWT (fastapi-jwt-auth / fastapi-users)** | Session | 前后端分离友好 |
| **前端框架** | **Vue 3 + Vite + TypeScript** | React / SvelteKit | 老代码倾向、社区中文资料多、AI 写 Vue SFC 很稳 |
| **UI 组件库** | **Naive UI** 或 **Element Plus** | Ant Design Vue | 组件全、暗色模式好看、TS 支持好 |
| **状态管理** | **Pinia** | Vuex | Vue 3 官方推荐 |
| **图表** | **ECharts** + `vue-echarts` | Chart.js / AntV | 中国友好、文档丰富、统计页够用 |
| **HTTP 客户端** | **Axios** + 自动生成的 OpenAPI 客户端 | Fetch | 直接从 FastAPI 的 OpenAPI 生成 TS 类型 |
| **包管理** | 后端 **uv** / **Poetry**；前端 **pnpm** | pip / npm | 速度与依赖锁 |
| **代码质量** | **Ruff + Black + mypy**，前端 **ESLint + Prettier** | — | 让 AI 写完直接 lint，自动修 |
| **部署** | **Docker Compose**（dev & 单机生产） | k8s（远期） | 一条命令拉起全套，开发到上线零摩擦 |
| **可观测** | **Loguru**（日志）+ **Prometheus + Grafana**（远期） | — | LLM 调用必须有完整调用链日志 |

> 一句话：**Python + FastAPI + PostgreSQL + Vue 3**，老代码的 Python + DeepSeek + PG 思路全部保留，只是把"脚本"重写成"服务"。

---

## 1. 选型权衡说明（给 AI 看，避免它中途劝你换）

### 为什么不是 Go？
- Go 性能好、部署简单，但 LLM 生态、Prompt 工程库、数据处理库远不如 Python。
- 这个项目的瓶颈永远是 LLM，不是后端 QPS。
- AI 写 Python 的训练数据多得多，出错率更低。

### 为什么不是 Node.js？
- 也可以，但 Python 生态在数据 / AI 这块仍是绝对优势。
- 如果未来想做 BFF + SSR，可以再加一层 Node，但主后端不必。

### 为什么不是 MongoDB？
- 项目里 80% 的数据是结构化的（用户、日记、事件、模块），20% 是半结构化（事件 `data`）。
- Postgres 的 JSONB 兼顾两者，还能在 JSON 字段上建索引、做 SQL 查询，远比 Mongo 灵活。
- 未来加向量检索直接 `pgvector`，不用再起一套。

### 为什么不是 MySQL？
- MySQL 的 JSON 支持比 PG 弱，索引、查询、生成列都不如 PG 顺。
- 这个项目"半结构化"的味道太重，PG 是最佳搭档。

### 关于 LLM
- 默认 **DeepSeek**（老代码已接通，便宜、中文好）。
- 必须封装一层 `LLMProvider` 接口，方便随时切到 OpenAI / Claude / 本地 Ollama。
- 调用必须可重试、可缓存（同 prompt 命中缓存直接返回）、可审计（每次调用落日志表）。

---

## 2. 系统大框架

### 2.1 总体架构图（文字版）

```
┌──────────────────────────────────────────────────────────────────┐
│                         浏览器 (Vue 3 SPA)                       │
│   写日记 / 看统计 / 维护画像 / 与 AI 对话 / 模块管理              │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTPS / JSON (REST + WebSocket)
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI 网关层 (api/)                        │
│  鉴权中间件 · 请求校验(Pydantic) · 自动 OpenAPI · 限流            │
└──────────────────────────┬───────────────────────────────────────┘
                           │
        ┌──────────────────┼─────────────────────────────┐
        ▼                  ▼                             ▼
┌───────────────┐  ┌──────────────────┐         ┌──────────────────┐
│  Service 层    │  │ AI Pipeline 层    │         │ Task Queue       │
│  业务编排      │──▶ Prompt 构造        │────────▶ Celery / ARQ     │
│  事务/校验     │  │ LLM 调用 + 缓存   │         │ 异步解析日记      │
└──────┬────────┘  │ 结构化校验         │         └────────┬─────────┘
       │           │ Action 执行 + 回滚 │                  │
       │           └──────────┬─────────┘                  │
       │                      │                            │
       ▼                      ▼                            ▼
┌──────────────┐    ┌──────────────────┐         ┌──────────────────┐
│ Repo / DAO   │    │ LLM Provider     │         │     Redis        │
│ SQLAlchemy   │    │ DeepSeek/OpenAI  │         │ 缓存 / Broker    │
│              │    │ Ollama (远期)    │         └──────────────────┘
└──────┬───────┘    └──────────────────┘
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PostgreSQL 16 / 17                            │
│  关系表 + JSONB 字段 + (远期 pgvector 做语义检索)                 │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 后端目录骨架（建议）

```
server/
├── app/
│   ├── main.py                # FastAPI entry
│   ├── core/                  # 配置、日志、安全、依赖注入
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── api/                   # 路由层（按业务拆分）
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── diaries.py
│   │       ├── events.py
│   │       ├── modules.py
│   │       ├── profile.py
│   │       └── stats.py
│   ├── schemas/               # Pydantic 模型（请求/响应 DTO）
│   ├── models/                # SQLAlchemy ORM 模型
│   ├── repositories/          # DAO，纯数据访问，不含业务
│   ├── services/              # 业务编排层
│   │   ├── diary_service.py
│   │   ├── event_service.py
│   │   ├── module_service.py
│   │   └── profile_service.py
│   ├── ai/                    # ⭐ AI Pipeline，本项目灵魂
│   │   ├── providers/         # LLM 提供商抽象
│   │   │   ├── base.py
│   │   │   ├── deepseek.py
│   │   │   ├── openai.py
│   │   │   └── ollama.py
│   │   ├── prompts/           # Prompt 模板（jinja2 / 字符串）
│   │   ├── pipelines/
│   │   │   ├── diary_parser.py     # 日记 → 事件 + actions
│   │   │   └── action_executor.py  # 执行 actions（带回滚/重试）
│   │   ├── cache.py           # prompt 哈希缓存
│   │   └── audit.py           # 调用审计落库
│   ├── tasks/                 # Celery / ARQ 后台任务
│   │   └── parse_diary.py
│   ├── modules/               # ⭐ 内置业务模块（每个模块一个目录）
│   │   ├── _base.py           # 模块基类：schema + prompt + action
│   │   ├── weather/
│   │   ├── meal/
│   │   ├── expense/
│   │   ├── memo/
│   │   └── reading/
│   └── db/
│       ├── session.py
│       └── migrations/        # alembic
├── tests/
├── pyproject.toml             # uv / Poetry
├── alembic.ini
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

### 2.3 前端目录骨架（建议）

```
web/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   ├── stores/                # Pinia
│   │   ├── user.ts
│   │   ├── diary.ts
│   │   └── profile.ts
│   ├── api/                   # 由 OpenAPI 自动生成 + 业务封装
│   ├── views/
│   │   ├── LoginView.vue
│   │   ├── DiaryView.vue       # 写/看日记
│   │   ├── DashboardView.vue   # 统计总览
│   │   ├── ProfileView.vue     # 个人画像（模块化表单）
│   │   ├── ModuleView.vue      # 各业务模块的明细页（消费/饮食/备忘…）
│   │   └── ChatView.vue        # 与 AI 对话
│   ├── components/
│   ├── composables/
│   └── styles/
├── vite.config.ts
├── package.json
└── .env.development
```

---

## 3. 核心数据模型（数据库 schema 蓝图）

> 字段名仅作示意，AI 实现时按 Python/PEP8 命名。

### 3.1 user
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint pk | |
| username | varchar uniq | |
| email | varchar uniq | |
| password_hash | varchar | bcrypt |
| created_at / updated_at | timestamptz | |

### 3.2 diary（日记）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint pk | |
| user_id | fk → user | |
| date | date | 一天一篇，`(user_id, date)` 唯一 |
| raw_text | text | 原始日记 |
| ai_processed_text | text | AI 规范化版本 |
| status | enum | `draft / parsing / parsed / failed` |
| parse_error | text | 失败原因 |
| created_at / updated_at | | |

### 3.3 event（事件 / 解析结果）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint pk | |
| diary_id | fk → diary | |
| user_id | fk → user | 冗余，加速查询 |
| module_code | varchar | 例如 `expense / meal / weather` |
| raw_text | text | 原文片段 |
| ai_processed_text | text | AI 规范化片段 |
| data | jsonb | 模块专属结构化字段 |
| locked | bool | 用户人工修改过 → AI 不能再覆盖 |
| created_at / updated_at | | |

> 索引：`(user_id, module_code, created_at)`、`data` 上根据热门字段建 GIN 索引（如 `data->'price'`）。

### 3.4 module（模块定义，可扩展 / 可启用禁用）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint pk | |
| code | varchar uniq | `expense / meal / memo …` |
| name | varchar | 中文名 |
| description | text | |
| schema | jsonb | 数据 schema（用于 AI prompt + 校验） |
| prompt_fragment | text | AI 解析时插入到主 prompt 的片段 |
| actions | jsonb | 允许的 action 列表（insert/update/delete…） |
| is_builtin | bool | 内置 or 插件 |
| enabled | bool | |
| created_at / updated_at | | |

### 3.5 profile_section（全局画像，模块化）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint pk | |
| user_id | fk → user | |
| module_code | varchar | 复用 `module.code`（如 `basic / work / hobby / relation / memo`）|
| content | jsonb | 实际数据 |
| privacy | enum | `public / ai_only / private`（控制是否参与 AI 上下文） |
| updated_by_event_id | fk → event | 最近一次由哪个事件触发更新（溯源） |
| created_at / updated_at | | |

### 3.6 ai_call_log（LLM 调用审计）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint pk | |
| user_id | fk | |
| diary_id | fk nullable | |
| provider / model | varchar | |
| prompt_hash | varchar | 用于缓存命中 |
| prompt | text | |
| response | text | |
| tokens_in / tokens_out / latency_ms / cost | | |
| status | enum | `success / parse_failed / api_error` |
| created_at | | |

### 3.7 action_log（AI 动作执行日志）
记录每个 `insert/update` action 的执行结果，用于回滚和"AI 纠错系统"。

---

## 4. 关键流程设计

### 4.1 日记解析流程（核心闭环）

```
用户提交日记
   │
   ▼
DiaryService.create()  ── 落 draft 行
   │
   ▼
触发 Celery 任务 parse_diary(diary_id)
   │
   ▼
DiaryParserPipeline.run():
   1. 拉取 user 的 profile_section（过滤 privacy）
   2. 拉取所有 enabled module 的 schema + prompt_fragment
   3. 用 jinja2 拼出完整 prompt
   4. 查 prompt_hash 缓存（Redis）→ 命中直接返回
   5. 调 LLMProvider.chat() → 写 ai_call_log
   6. 清洗 ```json``` 包裹 → json.loads
   7. Pydantic 按 module schema 校验
        - 单条事件失败 → 仅对该条事件二次调用 AI 重做（最多 N 次）
        - 整体失败 → diary.status = failed，结束
   8. 调 ActionExecutor.run(actions)
        - 在一个 DB 事务里执行
        - 每个 action 落 action_log
        - 失败 → 整篇回滚 → status = failed
   9. 成功 → status = parsed，前端通过 WebSocket / 轮询拿到通知
```

### 4.2 模块插件机制
- 每个模块 = `_base.Module` 的子类，提供：
  - `schema()`：返回 Pydantic 模型
  - `prompt_fragment()`：返回这个模块在大 prompt 里的描述片段
  - `validate(data)`：额外校验
  - `apply_action(action, db)`：如何把 AI 的 action 落到自己的存储（默认就是写 event 表，但备忘录这种带状态的可以重写）
- 启动时扫描 `app/modules/*` 自动注册。
- 远期：支持把模块定义热加载自数据库的 `module.schema / prompt_fragment` 字段，让用户/AI 自己加模块。

### 4.3 AI 纠错与回滚
- 三层防线：
  1. **Schema 校验**：返回不符合 schema → 自动重试（最多 3 次，每次把上次错误塞回 prompt）
  2. **Action 执行失败**：DB 事务回滚 + 标记失败
  3. **用户人工修正**：event 上打 `locked = true`，未来即使重解析也不覆盖

### 4.4 鉴权
- 注册/登录 → 颁发 JWT（access + refresh）
- FastAPI dependency 注入当前用户
- 所有 API 都按 `user_id` 隔离

---

## 5. 与老代码的迁移映射

| 老文件 | 在新架构里的归宿 |
|---|---|
| `server/utils/ai_utils.py` | `app/ai/providers/deepseek.py` |
| `server/utils/json_utils.py` (build_ai_prompt) | `app/ai/pipelines/diary_parser.py` + `app/ai/prompts/` |
| `server/utils/json_utils.py` (clean_ai_json_wrapper / save) | `app/ai/pipelines/diary_parser.py` 内部工具 |
| `server/utils/executorDemo.py` | 暂不迁移（Python 沙盒执行属于远期"AI 自主代码"能力，MVP 不需要） |
| `server/config/templates.jsonc` | 拆分到 `app/modules/{weather,meal,expense}/schema.py` 与 `prompt.py` |
| `server/config/global_info.json` | 数据库 `profile_section` 表的初始种子 |
| `server/config/global_model_memo.jsonc` | `app/modules/memo/`（备忘录模块的 action 设计） |
| `server/diaries/2026-3-5.txt` + `result/output.json` | `tests/fixtures/`，作为端到端测试样本 |
| `server/db/config.py` | `app/db/session.py`（SQLAlchemy 引擎 + Session 工厂） |
| `server/model/models.py` | `app/models/*.py`（按 3.1~3.7 重新设计） |
| `server/dao/dao.py` | `app/repositories/*.py` |
| `server/initialize/initialize.py` | 拆为：API 路由 + Celery 任务 + Pipeline |

---

## 6. 开发与上线

### 6.1 一键拉起（开发）
`docker-compose.yml` 至少包含：
- `postgres:16`（带 `pgvector` 扩展，方便远期升级）
- `redis:7`
- `api`（FastAPI + uvicorn --reload）
- `worker`（Celery / ARQ）
- `web`（Vite dev server）

### 6.2 配置管理
- 用 **Pydantic Settings** 统一从环境变量读：`DATABASE_URL / REDIS_URL / LLM_PROVIDER / DEEPSEEK_API_KEY / JWT_SECRET …`
- **绝对不要**像老代码那样把 API Key 硬编码在源码里。

### 6.3 测试
- `pytest` + `httpx` 跑接口；
- LLM 调用在测试里用 fixture mock，避免真花钱；
- 留一个独立的 `tests/e2e_with_real_llm/` 目录用真 key 跑端到端验收（用 `2026-3-5.txt` 那篇）。

### 6.4 上线建议（个人单机）
- 一台 2C4G 的 VPS：Docker Compose 起全套；
- Caddy / Nginx 反代 + 自动 HTTPS；
- 数据库每日 `pg_dump` 备份到对象存储；
- 日志用 Loguru 写文件 + 滚动。

---

## 7. 给 AI 的开发顺序建议（Roadmap）

第一周（地基）：
1. 用 Docker Compose 搭起 Postgres + Redis + 空的 FastAPI；
2. 建 `user / diary / event / module / profile_section / ai_call_log` 表 + Alembic 迁移；
3. 实现注册 / 登录 / JWT；
4. 把老 `templates.jsonc` 转成 `app/modules/weather|meal|expense` 三个模块。

第二周（主流程）：
5. 实现 `LLMProvider` 抽象 + DeepSeek 实现 + Redis 缓存；
6. 实现 `DiaryParserPipeline`（同步版本，先不上 Celery）；
7. 实现 `ActionExecutor` + 回滚；
8. 用 `2026-3-5.txt` 端到端测试通过。

第三周（前端）：
9. Vite + Vue 3 + Pinia + Naive UI 起项目；
10. 登录页 / 日记页 / 个人资料页；
11. 接通日记提交 → 解析 → 显示事件列表。

第四周（统计与备忘）：
12. ECharts 做消费 / 饮食统计页；
13. 备忘录模块（带 insert/update action）；
14. 把同步解析改成 Celery 异步 + WebSocket 推送结果。

到这里 MVP 完成。再往后的所有"远期想法"都是在这个骨架上加模块，而不是改框架。

---

## 8. 给 AI 的硬约束（写代码时必须遵守）

1. **任何 LLM 调用必须经过 `app/ai/providers/base.py` 抽象**，不允许在业务代码里直接 import `openai` / `requests`。
2. **任何 AI 输出必须经过 Pydantic 校验后才能进库**，不允许 `json.loads` 后直接用。
3. **API Key、密码、密钥**只能从环境变量读，禁止出现在代码里。
4. **数据库写操作必须在 Service 层**，路由层只做参数校验和调用。
5. **每个模块**都遵循 `schema + prompt_fragment + actions` 三件套，不许在主流程里写 `if module_code == "expense"` 这种硬编码分支。
6. **所有时间字段**用 `timestamptz`，业务里全程 UTC，前端再转本地时区。
7. **写测试**：每加一个模块至少配一个最小端到端用例（输入一段日记 → 断言生成对应事件）。

---

至此，需求（`项目文档_ai.md`）和设计（本文档）形成完整闭环。AI 可以直接拿这两份文档作为 Cursor 的 Project Rules / 上下文，开始重写。
