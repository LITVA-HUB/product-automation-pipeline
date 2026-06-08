#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "https://api.moysklad.ru/api/remap/1.2"


def request_json(url: str, token: str) -> dict:
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"МойСклад metadata request failed: {exc.code} {body}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Dump МойСклад product attributes metadata.")
    parser.add_argument("--out", default="docs/ms_attributes.sample.json")
    args = parser.parse_args()

    token = os.environ.get("MOYSKLAD_TOKEN")
    if not token:
        print("MOYSKLAD_TOKEN is required", file=sys.stderr)
        return 2

    metadata = request_json(f"{BASE_URL}/entity/product/metadata", token)
    attributes = metadata.get("attributes", [])
    result = {
        item["name"]: {
            "id": item.get("id"),
            "type": item.get("type"),
            "meta": item.get("meta"),
            "required": item.get("required", False),
        }
        for item in attributes
        if item.get("name")
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} attributes to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
