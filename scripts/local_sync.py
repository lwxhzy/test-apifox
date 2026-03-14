"""
本地同步 OpenAPI spec 到 Apifox（带变更分析 + 飞书通知）

用法:
  python scripts/local_sync.py              # 正常同步
  python scripts/local_sync.py --dry-run    # 仅分析变更，不实际同步
  python scripts/local_sync.py --force      # 跳过缓存检查，强制同步

环境变量（支持 .env 文件）:
  APIFOX_ACCESS_TOKEN  — Apifox API 访问令牌（必填）
  APIFOX_PROJECT_ID    — Apifox 项目 ID（必填）
  FEISHU_WEBHOOK       — 飞书机器人 Webhook URL（可选）
"""
import hashlib
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import httpx

CACHE_DIR = PROJECT_ROOT / ".apifox-cache"
CACHE_FILE = CACHE_DIR / "openapi-previous.json"

APIFOX_API = "https://api.apifox.com/v1/projects/{project_id}/import-openapi"


# ── 工具函数 ──


def load_env():
    """从 .env 文件加载环境变量（如果存在）"""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ── 导出 ──


def export_openapi() -> dict:
    from main import app
    return app.openapi()


# ── 变更分析 ──


def analyze_changes(new_spec: dict, old_spec: dict | None) -> dict:
    """对比新旧 spec，返回变更摘要"""
    title = new_spec["info"]["title"]
    version = new_spec["info"]["version"]
    new_paths = set(new_spec.get("paths", {}).keys())
    total_endpoints = sum(
        len([m for m in methods if m != "parameters"])
        for methods in new_spec.get("paths", {}).values()
    )

    if old_spec is None:
        path_details = []
        for p in sorted(new_paths):
            methods = [m.upper() for m in new_spec["paths"][p] if m != "parameters"]
            path_details.append(f"  + {p} [{' '.join(methods)}]")
        return {
            "status": "initial",
            "title": f"{title} v{version}",
            "summary": f"首次同步：共 {total_endpoints} 个接口，{len(new_paths)} 个路径",
            "details": "接口列表：\n" + "\n".join(path_details),
        }

    old_version = old_spec["info"]["version"]
    old_paths = set(old_spec.get("paths", {}).keys())
    old_endpoints = sum(
        len([m for m in methods if m != "parameters"])
        for methods in old_spec.get("paths", {}).values()
    )

    new_spec_json = json.dumps(new_spec, sort_keys=True)
    old_spec_json = json.dumps(old_spec, sort_keys=True)
    if sha256(new_spec_json) == sha256(old_spec_json):
        return {
            "status": "unchanged",
            "title": f"{title} v{version}",
            "summary": f"接口无变化，已跳过同步",
            "details": f"接口数：{total_endpoints} | 路径数：{len(new_paths)}",
        }

    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)
    common = sorted(new_paths & old_paths)

    modified = []
    for p in common:
        old_methods = set(m for m in old_spec["paths"][p] if m != "parameters")
        new_methods = set(m for m in new_spec["paths"][p] if m != "parameters")
        if old_methods != new_methods:
            methods_str = " ".join(m.upper() for m in sorted(new_methods))
            modified.append(f"  ~ {p} [{methods_str}]")

    details_parts = []
    details_parts.append(
        f"接口数：{old_endpoints} → {total_endpoints} | "
        f"路径数：{len(old_paths)} → {len(new_paths)}"
    )

    if added:
        lines = []
        for p in added:
            methods = [m.upper() for m in new_spec["paths"][p] if m != "parameters"]
            lines.append(f"  + {p} [{' '.join(methods)}]")
        details_parts.append(f"\n新增路径（+{len(added)}）：\n" + "\n".join(lines))

    if removed:
        lines = [f"  - {p}" for p in removed]
        details_parts.append(f"\n删除路径（-{len(removed)}）：\n" + "\n".join(lines))

    if modified:
        details_parts.append(f"\n变更路径：\n" + "\n".join(modified))

    if not added and not removed and not modified:
        details_parts.append("\n变更内容：字段描述、示例值或 Schema 结构更新")

    return {
        "status": "changed",
        "title": f"{title} v{old_version} → v{version}",
        "summary": f"接口有变更",
        "details": "\n".join(details_parts),
    }


# ── 同步 ──


def sync_to_apifox(spec: dict, access_token: str, project_id: str) -> dict:
    url = APIFOX_API.format(project_id=project_id)
    resp = httpx.post(
        url,
        headers={
            "X-Apifox-Api-Version": "2024-03-28",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={
            "input": json.dumps(spec, ensure_ascii=False),
            "options": {
                "targetEndpointFolderId": 0,
                "targetSchemaFolderId": 0,
                "endpointOverwriteBehavior": "OVERWRITE_EXISTING",
                "schemaOverwriteBehavior": "OVERWRITE_EXISTING",
                "updateFolderOfChangedEndpoint": True,
                "prependBasePath": False,
            },
        },
        timeout=30,
    )
    if not resp.is_success:
        raise Exception(f"Apifox API 错误 [{resp.status_code}]: {resp.text}")
    return resp.json()


# ── 飞书通知 ──


def notify_feishu(webhook: str, title: str, template: str, content: str):
    body = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content},
                }
            ],
        },
    }
    try:
        resp = httpx.post(webhook, json=body, timeout=10)
        if resp.is_success:
            print("飞书通知已发送")
        else:
            print(f"飞书通知发送失败: {resp.text}")
    except Exception as e:
        print(f"飞书通知发送异常: {e}")


# ── 缓存 ──


def load_cached_spec() -> dict | None:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return None


def save_cached_spec(spec: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── 输出格式化 ──


def print_header(text: str):
    width = 50
    print(f"\n{'─' * width}")
    print(f"  {text}")
    print(f"{'─' * width}")


def print_result(changes: dict, synced: bool):
    status_icon = {"initial": "🆕", "changed": "📝", "unchanged": "⏭️"}
    icon = status_icon.get(changes["status"], "")

    print_header(f"{icon} {changes['title']}")
    print(f"\n{changes['summary']}")
    print(f"\n{changes['details']}")

    if synced:
        print(f"\n✅ 已同步到 Apifox")
    elif changes["status"] == "unchanged":
        print(f"\n⏭️  接口无变化，跳过同步")
    else:
        print(f"\n🔍 仅预览，未同步（使用 --dry-run）")


# ── 主流程 ──


def main():
    load_env()

    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    access_token = os.getenv("APIFOX_ACCESS_TOKEN")
    project_id = os.getenv("APIFOX_PROJECT_ID")
    feishu_webhook = os.getenv("FEISHU_WEBHOOK")

    if not dry_run and (not access_token or not project_id):
        print("错误: 请设置 APIFOX_ACCESS_TOKEN 和 APIFOX_PROJECT_ID")
        print("可以通过环境变量或项目根目录的 .env 文件配置")
        sys.exit(1)

    # 导出
    print("导出 OpenAPI spec...")
    spec = export_openapi()

    # 加载缓存并分析变更
    old_spec = None if force else load_cached_spec()
    changes = analyze_changes(spec, old_spec)

    # 输出变更摘要
    print_result(changes, synced=False)

    # 同步
    synced = False
    if not dry_run and changes["status"] != "unchanged":
        print("\n同步到 Apifox...")
        try:
            sync_to_apifox(spec, access_token, project_id)
            save_cached_spec(spec)
            synced = True
            print("✅ 同步成功")
        except Exception as e:
            print(f"❌ 同步失败: {e}")
            if feishu_webhook:
                notify_feishu(
                    feishu_webhook,
                    "Apifox 同步失败",
                    "red",
                    f"**本地同步失败**\n\n{changes['title']}\n\n错误: {e}",
                )
            sys.exit(1)

    # 飞书通知
    if feishu_webhook:
        if synced:
            notify_feishu(
                feishu_webhook,
                "Apifox 同步成功",
                "green",
                f"**本地同步**\n\n"
                f"```\n{changes['title']}\n\n{changes['details']}\n```",
            )
        elif changes["status"] == "unchanged":
            notify_feishu(
                feishu_webhook,
                "Apifox 同步跳过",
                "wathet",
                f"{changes['title']}\n\n{changes['summary']}",
            )


if __name__ == "__main__":
    main()
