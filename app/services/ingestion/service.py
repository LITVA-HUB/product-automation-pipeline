from __future__ import annotations

from pathlib import Path

from app.domain.product_candidate import ProductCandidate
from app.services.ingestion.parsers import parse_csv_rows, row_to_candidate


class IngestionService:
    def from_csv(
        self,
        supplier: str,
        path: str | Path,
        field_map: dict[str, str],
    ) -> list[ProductCandidate]:
        rows = parse_csv_rows(path)
        return [row_to_candidate(supplier=supplier, row=row, field_map=field_map) for row in rows]
