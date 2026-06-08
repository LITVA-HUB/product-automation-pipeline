import json
import subprocess
import sys
from pathlib import Path


def test_dry_run_cli_processes_sample_csv(tmp_path):
    output = tmp_path / "result.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/dry_run_pipeline.py",
            "--input",
            "examples/sample_supplier_products.csv",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))

    assert "validated_before_ms" in result.stdout
    assert payload["processed"] == 1
    assert payload["products"][0]["status"] == "validated_before_ms"
    assert payload["products"][0]["purchase_price"] == "800.00"
    assert payload["products"][0]["site_price"] == "1150.00"
    assert payload["products"][0]["main_image"] == "examples/images/main.jpg"
