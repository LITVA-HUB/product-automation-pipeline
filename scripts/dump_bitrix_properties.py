#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen


def call_bitrix(webhook_url: str, method: str, payload: dict) -> dict:
    base = webhook_url.rstrip("/")
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        f"{base}/{method}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Dump Bitrix iblock property metadata.")
    parser.add_argument("--iblock-id", required=True)
    parser.add_argument("--out", default="docs/bitrix_properties.sample.json")
    args = parser.parse_args()

    webhook_url = os.environ.get("BITRIX_WEBHOOK_URL")
    if not webhook_url:
        print("BITRIX_WEBHOOK_URL is required", file=sys.stderr)
        return 2

    response = call_bitrix(
        webhook_url,
        "catalog.productProperty.list",
        {
            "select": ["id", "name", "code", "iblockId", "propertyType", "multiple", "isRequired"],
            "filter": {"iblockId": int(args.iblock_id)},
            "order": {"id": "ASC"},
        },
    )
    if "error" in response:
        print(json.dumps(response, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    result_root = response.get("result", {})
    properties = result_root.get(
        "productProperties", result_root if isinstance(result_root, list) else []
    )
    result = {
        item.get("code") or item.get("id"): {
            "id": item.get("id"),
            "name": item.get("name"),
            "code": item.get("code"),
            "iblock_id": item.get("iblockId"),
            "property_type": item.get("propertyType"),
            "multiple": item.get("multiple"),
            "required": item.get("isRequired"),
        }
        for item in properties
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} properties to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
