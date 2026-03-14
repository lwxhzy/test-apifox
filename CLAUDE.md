# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供项目指引。

## 常用命令

```bash
# 安装依赖
pip install fastapi uvicorn httpx pydantic

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python main.py

# 同步 OpenAPI spec 到 Apifox（需要环境变量）
APIFOX_ACCESS_TOKEN=<token> APIFOX_PROJECT_ID=<id> python scripts/sync_apifox.py
```

启动服务后，交互式 API 文档地址：`http://localhost:8000/docs`

## 架构说明

这是一个最小化的 FastAPI 应用，主要用于演示 **Apifox API 同步** —— 离线导出应用的 OpenAPI spec（无需启动 HTTP 服务），然后通过 Apifox 导入 API 推送上去。

### 核心流程

```
main.py  →  app/__init__.py (create_app)  →  app/views.py (路由)
                                          →  app/schemas.py (Pydantic 模型)

scripts/sync_apifox.py:
  import main.app  →  app.openapi()  →  POST https://api.apifox.com/v1/projects/{id}/import-openapi
```

- **`app/views.py`** — 所有路由挂在 `/api/v1` 前缀下，当前返回桩数据，可在此添加真实持久化逻辑。
- **`app/schemas.py`** — 请求校验和响应序列化共用的 Pydantic 模型。字段级别的 `description` 和 `examples` 是有意为之，同步后会填充到 Apifox 文档中。
- **`scripts/sync_apifox.py`** — 直接导入 `main.app` 调用 `app.openapi()` 获取 spec，无需启动服务。推送时使用 `endpointOverwriteBehavior: OVERWRITE_EXISTING`，重复执行会覆盖已有接口。

### Apifox 同步配置

同步脚本依赖两个环境变量：
- `APIFOX_ACCESS_TOKEN` — Apifox 个人访问令牌
- `APIFOX_PROJECT_ID` — 目标 Apifox 项目 ID
