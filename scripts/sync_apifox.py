"""
离线导出 OpenAPI spec 并同步到 Apifox
用法: python scripts/sync_apifox.py
需要环境变量: APIFOX_ACCESS_TOKEN, APIFOX_PROJECT_ID
"""
import json
import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中，CI 环境下 import main 需要
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

APIFOX_API = "https://api.apifox.com/v1/projects/{project_id}/import-openapi"


def export_openapi():
    """离线导出 FastAPI 的 OpenAPI spec（不启动服务）"""
    from main import app
    return app.openapi()


def sync_to_apifox(spec: dict, access_token: str, project_id: str):
    """推送到 Apifox"""
    url = APIFOX_API.format(project_id=project_id)
    resp = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={
            "input": json.dumps(spec, ensure_ascii=False),
            "options": {
                "endpointOverwriteBehavior": "OVERWRITE_EXISTING",
                "updateFolderOfChangedEndpoint": True,
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    access_token = os.getenv("APIFOX_ACCESS_TOKEN")
    project_id = os.getenv("APIFOX_PROJECT_ID")

    if not access_token or not project_id:
        print("错误: 请设置 APIFOX_ACCESS_TOKEN 和 APIFOX_PROJECT_ID 环境变量")
        sys.exit(1)

    print("导出 OpenAPI spec...")
    spec = export_openapi()
    print(f"导出成功: {spec['info']['title']} v{spec['info']['version']}")
    print(f"接口数量: {sum(len(methods) for methods in spec['paths'].values())}")

    print("同步到 Apifox...")
    result = sync_to_apifox(spec, access_token, project_id)
    print(f"同步完成: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
