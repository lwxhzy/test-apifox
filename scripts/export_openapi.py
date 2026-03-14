"""
离线导出 OpenAPI spec 到 JSON 文件（供 CI 使用）
用法: python scripts/export_openapi.py [output_path]
"""
import json
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中，CI 环境下 import main 需要
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"
    spec = app.openapi()
    Path(output_path).write_text(
        json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OpenAPI spec exported to {output_path}")
    print(f"  title:     {spec['info']['title']}")
    print(f"  version:   {spec['info']['version']}")
    print(f"  endpoints: {sum(len(m) for m in spec['paths'].values())}")


if __name__ == "__main__":
    main()
