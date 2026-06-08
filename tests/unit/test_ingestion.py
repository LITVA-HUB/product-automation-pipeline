from app.services.ingestion.parsers import parse_csv_rows, row_to_candidate
from app.services.ingestion.service import IngestionService
from app.workflow.states import WorkflowStatus


def test_row_to_candidate_preserves_raw_fields_without_interpretation():
    candidate = row_to_candidate(
        supplier="Kerama",
        row={"Название": "Tile 60x120", "Артикул": "A-1", "Цена": "1234.50", "Код": "K-1"},
        field_map={"raw_name": "Название", "raw_article": "Артикул", "raw_price": "Цена"},
    )

    assert candidate.status == WorkflowStatus.PARSED
    assert candidate.raw_name == "Tile 60x120"
    assert candidate.raw_article == "A-1"
    assert candidate.raw_price == "1234.50"
    assert candidate.raw_fields["Код"] == "K-1"
    assert candidate.article.value is None


def test_parse_csv_rows_reads_supplier_export(tmp_path):
    path = tmp_path / "products.csv"
    path.write_text("Название,Артикул,Цена\nTile,A-1,100\n", encoding="utf-8")

    rows = parse_csv_rows(path)

    assert rows == [{"Название": "Tile", "Артикул": "A-1", "Цена": "100"}]


def test_ingestion_service_creates_parsed_candidates_from_csv(tmp_path):
    path = tmp_path / "products.csv"
    path.write_text("name,article,price\nTile,A-1,100\n", encoding="utf-8")
    service = IngestionService()

    candidates = service.from_csv(
        supplier="Kerama",
        path=path,
        field_map={"raw_name": "name", "raw_article": "article", "raw_price": "price"},
    )

    assert len(candidates) == 1
    assert candidates[0].supplier == "Kerama"
    assert candidates[0].status == WorkflowStatus.PARSED
