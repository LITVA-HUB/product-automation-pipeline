# Architecture

The system is a deterministic product pipeline with LLM-assisted extraction.
External systems are isolated behind ports so the domain model and business
rules remain independent from МойСклад, OpenRouter, optional Bitrix diagnostics,
and storage.

## Pipeline

```text
supplier source
  -> ingestion
  -> parser
  -> LLM extraction
  -> normalization
  -> name construction
  -> business rules
  -> duplicate detection
  -> validation before МойСклад
  -> create or update in МойСклад
  -> verify МойСклад
  -> human approval
  -> optionally set МойСклад "Выгружено на сайте"
```

## Core Entity

`ProductCandidate` is the single object passed through the pipeline. LLM-derived
fields use `FieldWithConfidence`; deterministic fields such as prices,
coefficients, package type, publication flags, and external ids are written only
by service code.

## Workflow

The workflow is explicit. Code outside `workflow/` must not mutate status
directly. Invalid transitions raise an error and must be logged by the caller
when persistence is added.

## Deterministic Business Rules

- package type: `УПК`;
- purchase price: `retail_price * 0.8`;
- site price: `retail_price * 1.15`;
- site unit coefficient: `units_per_package`;
- site card type: `Ламинат`;
- publication mode defaults to `ms_only`;
- МойСклад field `Выгружено на сайте` defaults to `false`;
- МойСклад group: value of "Производитель для сайта".

These rules are covered by unit tests before any external write integration is
implemented.
