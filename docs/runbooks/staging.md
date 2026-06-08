# Staging Runbook

Reviewed on 2026-06-08.

This project must be verified against staging systems before any production
write is enabled. Production credentials are not allowed in local development,
CI, or first integration tests.

## Required Staging Credentials

- `MOYSKLAD_TOKEN`: token for a test МойСклад account.
- `OPENROUTER_API_KEY`: OpenRouter key with a spending limit suitable for test
  extraction runs.
- `DATABASE_URL`: staging Postgres database.
- `REDIS_URL`: staging Redis instance for Celery.
- `TELEGRAM_BOT_TOKEN`: staging bot token, not the production bot.
- `TELEGRAM_WEBHOOK_SECRET`: random webhook secret for staging.

## No-Production Safety Rules

- `AUTO_PUBLISH_ENABLED=false` until validators have been tested on real sample
  products.
- Do not set the МойСклад `Выгружено на сайте` flag in staging rehearsals unless
  the linked site is also staging.
- Never commit `.env`, generated maps with secrets, raw supplier exports that are
  not approved for publication, or API responses containing tokens.
- Use a dedicated supplier prefix or test collection marker for integration
  products so they are easy to clean up.

## Metadata Discovery

Run these commands only after the staging credentials are loaded into the shell:

```bash
export MOYSKLAD_TOKEN=...
./scripts/dump_ms_attributes.py --out local_storage/staging/ms_attributes.json

```

The `local_storage/` directory is ignored by git. Review generated maps manually
before using them in write mappers. Bitrix property discovery is optional and
only needed for diagnostics/fallbacks.

## First Integration Smoke Test

1. Start services with `docker compose up --build` or
   `docker-compose -p product_pipeline up --build` on legacy Docker Compose.
2. Confirm the `migrate` service completed `alembic upgrade head`.
3. Create one product candidate from a known test supplier row.
4. Run extraction with OpenRouter model `google/gemini-3.1-flash-lite`.
5. Apply normalization, naming, rules, duplicate detection, and validation.
6. Create the product in test МойСклад only.
7. Verify the product fields and image manually.
8. Confirm `Выгружено на сайте=false` by default.
9. Approve manually; keep site activation disabled until repeated tests pass.
10. In a staging-only site sync, set `Выгружено на сайте=true` and verify activation timing.

## Telegram Intake Smoke Test

1. Set the staging webhook to `https://<staging-domain>/telegram/webhook` with
   `secret_token=$TELEGRAM_WEBHOOK_SECRET`.
2. Send a text article list, a supplier URL, a spreadsheet, and a photo invoice
   to the staging bot.
3. Open `/miniapp` from Telegram and confirm all events appear as pending.
4. For file/photo inputs, verify `payload.storage_path` points to
   `LOCAL_STORAGE_PATH/telegram/<event_id>/source.*`.
5. Confirm no products were created in МойСклад from webhook handling.

## Evidence to Capture

- Candidate id and workflow audit log.
- МойСклад product id/code.
- Validation results before МойСклад and, when site activation is explicitly tested, after sync.
- Any human corrections saved in `human_reviews`.
