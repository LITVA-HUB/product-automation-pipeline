# Product Automation Pipeline

Automation system for creating and validating product cards in **МойСклад** and
**1С-Битрикс**. The pipeline converts supplier data into a normalized
`ProductCandidate`, creates the product in МойСклад, configures the Bitrix card,
validates every critical field, and publishes only after approval.

## Current Status

This repository starts with the core foundation:

- domain model for product candidates;
- deterministic workflow state machine;
- business rules for prices, packaging, coefficients, and site card type;
- OpenRouter LLM adapter locked to `google/gemini-3.1-flash-lite`;
- interface ports for МойСклад and Bitrix integrations;
- unit tests for the highest-risk business rules.

## Non-Negotiable Rules

- LLM output is advisory only. It never writes to МойСклад, Bitrix, prices, or
  publication flags directly.
- The only allowed LLM provider is OpenRouter.
- The only allowed model is `google/gemini-3.1-flash-lite`.
- МойСклад retail price is always per unit of measure, not per package.
- Purchase price is `retail_price * 0.8`.
- Site price is `retail_price * 1.15`.
- Package type is always `УПК`.
- Site card type is always `Ламинат`.
- Publication happens only after validation and approval.

## Quick Start

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Copy `.env.example` to `.env` and fill real secrets only in local or deployment
environments. Never commit tokens.

## Project Layout

```text
app/
  adapters/      # OpenRouter, МойСклад, Bitrix, storage implementations
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
- [MoySklad and Bitrix Integration Notes](docs/integrations.md)

## Validation

```bash
pytest -q
```

Current baseline: `8 passed`.
