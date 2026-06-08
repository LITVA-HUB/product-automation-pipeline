# Product Automation Pipeline

Automation system for creating and validating product cards in **МойСклад**.
The website is controlled through МойСклад synchronization: by default products
are created only in МойСклад, and site activation is enabled only by explicitly
setting the МойСклад field `Выгружено на сайте`.

## Current Status

The repository contains a tested application pipeline:

- domain model for product candidates;
- deterministic workflow state machine and audit-ready repositories;
- arbitrary intake classification for text, supplier URLs, tables, and invoice images;
- Telegram webhook intake, Telegram file download, and full Mini App operator workflow;
- CSV/manual ingestion;
- LLM extraction contracts and OpenRouter adapter locked to `google/gemini-3.1-flash-lite`;
- deterministic naming, pricing, duplicate detection, image grouping, validation, and publication services;
- МойСклад REST adapter methods behind ports;
- FastAPI routes for products and human review decisions;
- database-backed product, review, and intake APIs;
- production auth guard for operator APIs through Telegram Mini App `initData`;
- Celery task wrappers for workflow progression;
- Docker Compose, Alembic migrations, and GitHub Actions test workflow;
- reproducible dry-run CLI with a sample supplier export.

## Non-Negotiable Rules

- LLM output is advisory only. It never writes to МойСклад, prices, or
  publication flags directly.
- The only allowed LLM provider is OpenRouter.
- The only allowed model is `google/gemini-3.1-flash-lite`.
- МойСклад retail price is always per unit of measure, not per package.
- Purchase price is `retail_price * 0.8`.
- Site price is `retail_price * 1.15`.
- Package type is always `УПК`.
- Site card type is always `Ламинат`.
- Products default to `ms_only`.
- `Выгружено на сайте` defaults to `false`.
- Site activation happens only after validation and approval.

## Quick Start

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Copy `.env.example` to `.env` and fill real secrets only in local or deployment
environments. Never commit tokens.

## Production Start

```bash
cp .env.example .env
docker compose up --build
```

The compose stack waits for Postgres and Redis, runs `alembic upgrade head`, and
then starts the API and worker. The operator Mini App is served at `/miniapp`;
Telegram webhooks must point to `/telegram/webhook`.

If your Docker installation uses the legacy `docker-compose` command, run
`docker-compose -p product_pipeline up --build` so the project name is ASCII.

## Live Staging

- Mini App: `https://api-staging.lumatestdomen.online/product-automation/miniapp`
- Webhook: `https://api-staging.lumatestdomen.online/product-automation/telegram/webhook`
- Service: `product-automation-api.service` on `luma-vps`
- Public path: nginx proxies `/product-automation/` to `127.0.0.1:8020`
- Real МойСклад writes are disabled with `MOYSKLAD_WRITES_ENABLED=false`.

## Dry Run

Run the pipeline locally without OpenRouter or МойСклад writes:

```bash
python scripts/dry_run_pipeline.py \
  --input examples/sample_supplier_products.csv \
  --output local_storage/dry_run/result.json
```

Expected result: one product reaches `validated_before_ms`; prices, coefficient,
name, image grouping, and validation are computed by deterministic services.

## Project Layout

```text
app/
  adapters/      # OpenRouter, МойСклад, optional Bitrix/storage implementations
  domain/        # pure Pydantic domain models
  ports/         # Protocol interfaces for external systems
  services/      # deterministic business services
  workflow/      # explicit state machine
docs/
  architecture.md
  integrations.md
  openrouter.md
tests/
  unit/
```

## Documentation

- [Architecture](docs/architecture.md)
- [OpenRouter Provider](docs/openrouter.md)
- [MoySklad Integration Notes](docs/integrations.md)
- [Staging Runbook](docs/runbooks/staging.md)
- [Telegram Intake](docs/telegram.md)
- [Implementation Plan](docs/superpowers/plans/2026-06-08-full-product-pipeline.md)

## Validation

```bash
pytest -q
```

Current baseline: `75 passed`.

## Staging Gate

Real МойСклад discovery requires staging credentials:

- `MOYSKLAD_TOKEN`

Generated metadata maps must be written under `local_storage/`, which is ignored
by git. API keys must stay in `.env` or deployment secret storage; never commit
real tokens.
