# Staging Runbook

Reviewed on 2026-06-08.

This project must be verified against staging systems before any production
write is enabled. Production credentials are not allowed in local development,
CI, or first integration tests.

## Required Staging Credentials

- `MOYSKLAD_TOKEN`: token for a test МойСклад account.
- `BITRIX_WEBHOOK_URL`: incoming webhook for a test Bitrix/1С-Битрикс site with
  `catalog` permissions and access to the target product iblock.
- `OPENROUTER_API_KEY`: OpenRouter key with a spending limit suitable for test
  extraction runs.
- `DATABASE_URL`: staging Postgres database.
- `REDIS_URL`: staging Redis instance for Celery.

## No-Production Safety Rules

- `AUTO_PUBLISH_ENABLED=false` until validators have been tested on real sample
  products.
- Do not set the МойСклад `Выгружено на сайте` flag in staging rehearsals unless
  the linked Bitrix site is also staging.
- Never commit `.env`, generated maps with secrets, raw supplier exports that are
  not approved for publication, or API responses containing tokens.
- Use a dedicated supplier prefix or test collection marker for integration
  products so they are easy to clean up.

## Metadata Discovery

Run these commands only after the staging credentials are loaded into the shell:

```bash
export MOYSKLAD_TOKEN=...
./scripts/dump_ms_attributes.py --out local_storage/staging/ms_attributes.json

export BITRIX_WEBHOOK_URL=...
./scripts/dump_bitrix_properties.py \
  --iblock-id <STAGING_PRODUCT_IBLOCK_ID> \
  --out local_storage/staging/bitrix_properties.json
```

The `local_storage/` directory is ignored by git. Review generated maps manually
before using them in write mappers.

## First Integration Smoke Test

1. Start services with `docker compose up --build`.
2. Run Alembic migrations against staging DB.
3. Create one product candidate from a known test supplier row.
4. Run extraction with OpenRouter model `google/gemini-3.1-flash-lite`.
5. Apply normalization, naming, rules, duplicate detection, and validation.
6. Create the product in test МойСклад only.
7. Verify the product fields and image manually.
8. Configure the test Bitrix card.
9. Verify site price, coefficient, quantity accounting, card type, supplier, and images.
10. Approve manually; keep publication disabled until repeated tests pass.

## Evidence to Capture

- Candidate id and workflow audit log.
- МойСклад product id/code.
- Bitrix product id.
- Validation results before МойСклад and after site.
- Any human corrections saved in `human_reviews`.
