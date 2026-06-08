# Full Product Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-oriented automation pipeline for creating, validating, reviewing, and publishing product cards in МойСклад and 1С-Битрикс.

**Architecture:** The system uses a hexagonal architecture: domain models and deterministic business rules are pure Python, services depend on ports, and adapters handle OpenRouter, МойСклад, Bitrix, storage, and persistence. The workflow engine is the only status transition authority. External writes are idempotent and gated by validation.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, Celery, Redis, PostgreSQL, httpx, OpenRouter `google/gemini-3.1-flash-lite`, pytest, respx.

---

## File Map

- `app/domain/`: ProductCandidate, enums, value objects, validation error shape.
- `app/workflow/`: explicit status/event transition table and workflow engine.
- `app/services/ingestion/`: CSV/Excel/manual parsers and raw candidate creation.
- `app/services/naming/`: deterministic product name and original-name construction.
- `app/services/rules/`: fixed business rules for prices, package type, coefficient, and Bitrix card type.
- `app/services/duplicates/`: local and МойСклад duplicate detection.
- `app/services/validation/`: pre-МойСклад, МойСклад, and site validation checklists.
- `app/adapters/repositories/`: SQLAlchemy repositories.
- `app/adapters/moysklad/`: REST client and Candidate -> МойСклад payload mapper.
- `app/adapters/bitrix/`: REST client and Candidate -> Bitrix property mapper.
- `app/adapters/llm/`: OpenRouter adapter locked to `google/gemini-3.1-flash-lite`.
- `app/tasks/`: Celery task wrappers for pipeline steps.
- `app/api/`: FastAPI routes for products, review queue, health, and metadata.
- `tests/`: unit and integration tests for every deterministic module and mocked external HTTP adapters.

## Task 1: Persistence Foundation

**Files:**
- Create: `app/db.py`
- Create: `app/adapters/repositories/models.py`
- Create: `app/adapters/repositories/product_repository.py`
- Create: `tests/unit/test_product_repository.py`

- [x] Write failing repository tests for create/get/update and indexed field sync.
- [x] Implement SQLAlchemy models for `products`, `audit_logs`, `validation_results`, and `api_requests`.
- [x] Implement `ProductRepository` with JSON candidate serialization.
- [x] Run `pytest tests/unit/test_product_repository.py -q`.

## Task 2: Ingestion and Parser Foundation

**Files:**
- Create: `app/services/ingestion/service.py`
- Create: `app/services/ingestion/parsers.py`
- Create: `tests/unit/test_ingestion.py`

- [x] Write failing tests for manual, CSV, and row-to-candidate parsing.
- [x] Implement parser functions that do not interpret values with LLM.
- [x] Implement ingestion service that returns candidates in `imported` or `parsed`.
- [x] Run `pytest tests/unit/test_ingestion.py -q`.

## Task 3: Naming and Validation

**Files:**
- Create: `app/services/naming/service.py`
- Create: `app/services/validation/service.py`
- Create: `tests/unit/test_naming_and_validation.py`

- [x] Write failing tests for deterministic name construction and validation checklists.
- [x] Implement name constructor from product type, manufacturer, collection, color, size, and article.
- [x] Implement before-МойСклад and after-site validation rules from the Word process.
- [x] Run `pytest tests/unit/test_naming_and_validation.py -q`.

## Task 4: External Adapter Contracts

**Files:**
- Create: `app/adapters/moysklad/client.py`
- Create: `app/adapters/moysklad/mappers.py`
- Create: `app/adapters/bitrix/rest_client.py`
- Create: `app/adapters/bitrix/mappers.py`
- Create: `tests/unit/test_external_mappers.py`
- Create: `tests/unit/test_http_clients.py`

- [x] Write failing mapper tests for МойСклад price minor units, attributes, and Bitrix fixed fields.
- [x] Implement mappers without making network calls.
- [x] Implement thin async HTTP clients with authentication headers and base methods.
- [x] Run mapper and client tests.

## Task 5: Duplicate Detection

**Files:**
- Create: `app/services/duplicates/service.py`
- Create: `tests/unit/test_duplicates.py`

- [x] Write tests for hard matches by article/supplier code and soft candidate matches.
- [x] Implement deterministic duplicate decisions: `unique`, `duplicate`, `possible_duplicate`.
- [x] Ensure possible duplicates set review reasons, never auto-create.

## Task 6: LLM Extraction Contracts

**Files:**
- Create: `app/domain/extraction.py`
- Modify: `app/adapters/llm/openrouter.py`
- Create: `tests/unit/test_extraction_contract.py`

- [x] Write tests for strict JSON payload construction and invalid JSON retry classification.
- [x] Implement `ExtractionResult`, `ImageClassification`, and schema helpers.
- [x] Add parsing method that validates JSON into Pydantic models.

## Task 7: API and Human Review

**Files:**
- Create: `app/api/routes_products.py`
- Create: `app/api/routes_review.py`
- Modify: `app/main.py`
- Create: `tests/unit/test_api.py`

- [x] Write FastAPI tests for health, product creation, candidate retrieval, review decisions.
- [x] Implement initial routes for health, manual product creation, candidate retrieval, and review decisions.
- [ ] Persist human corrections as audit-ready data.

## Task 8: Workflow Orchestration and Tasks

**Files:**
- Create: `app/tasks/celery_app.py`
- Create: `app/tasks/pipeline_tasks.py`
- Create: `app/services/pipeline/orchestrator.py`
- Create: `tests/unit/test_pipeline_orchestrator.py`

- [ ] Write tests proving each task is idempotent and calls the next workflow transition.
- [ ] Implement Celery wrappers as thin calls into services.
- [ ] Keep external write retries isolated to transient errors.

## Task 9: Docker, Alembic, and CI

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `.github/workflows/tests.yml`

- [x] Add containerized Postgres, Redis, API, and worker services.
- [x] Add Alembic migration for initial tables.
- [x] Add GitHub Actions running `pip install -e ".[dev]"` and `pytest -q`.

## Task 10: Staging Integration Gate

**Files:**
- Modify: `docs/integrations.md`
- Modify: `scripts/dump_ms_attributes.py`
- Modify: `scripts/dump_bitrix_properties.py`
- Create: `docs/runbooks/staging.md`

- [ ] Document required staging credentials and no-prod safety rules.
- [ ] Run discovery scripts against staging when credentials are available.
- [ ] Store generated attribute/property maps outside tracked secrets.
