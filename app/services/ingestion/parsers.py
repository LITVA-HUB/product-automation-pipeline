from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.domain.product_candidate import ProductCandidate
from app.workflow.states import WorkflowStatus


def parse_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def row_to_candidate(
    supplier: str,
    row: dict[str, Any],
    field_map: dict[str, str],
    source_url: str | None = None,
) -> ProductCandidate:
    return ProductCandidate(
        supplier=supplier,
        source_type="csv",
        source_url=source_url,
        raw_name=_get(row, field_map.get("raw_name")),
        raw_article=_get(row, field_map.get("raw_article")),
        raw_price=_get(row, field_map.get("raw_price")),
        raw_description=_get(row, field_map.get("raw_description")),
        raw_fields=dict(row),
        status=WorkflowStatus.PARSED,
    )


def _get(row: dict[str, Any], key: str | None) -> str | None:
    if not key:
        return None
    value = row.get(key)
    if value is None:
        return None
    return str(value)
