# Telegram Intake and Mini App Contract

Reviewed on 2026-06-08.

Telegram is the preferred operator interface. It is intentionally safe by
default: webhook intake never creates products in МойСклад. It stores typed
intake events in Postgres for review and later processing.

## Supported Inputs

- Plain text: article lists, messy notes, copied supplier messages.
- Supplier URL: detected from message text.
- Table document: `.csv`, `.xls`, `.xlsx`.
- Invoice/product photo: Telegram photo or image document.
- Caption plus file: caption is preserved in the intake payload.

When `TELEGRAM_BOT_TOKEN` is configured, file inputs are downloaded through
Telegram `getFile` into `LOCAL_STORAGE_PATH/telegram/<event_id>/source.*`.
Without the token, the event is still stored with `telegram://<file_id>` so it
can be downloaded later.

## Backend Flow

```text
Telegram update
  -> POST /telegram/webhook
  -> TelegramIntakeService
  -> optional Telegram getFile download
  -> IntakeItem(kind, payload)
  -> intake_events(status=pending)
  -> GET /miniapp/api/intake/events for Mini App queue
```

The operator UI is served at `/miniapp`. In `APP_ENV=prod`, Mini App API calls
must include `X-Telegram-Init-Data` from `window.Telegram.WebApp.initData`; the
backend verifies the Telegram HMAC before returning queue data.

## Safety Rules

- No МойСклад writes from webhook handling.
- No publication from webhook handling.
- Telegram tokens stay in `TELEGRAM_BOT_TOKEN` / deployment secret storage.
- Webhook secret validation uses `X-Telegram-Bot-Api-Secret-Token` when
  `TELEGRAM_WEBHOOK_SECRET` is configured.
- Mini App authentication uses validated Telegram `initData`; never trust
  `initDataUnsafe` directly.
- The Mini App must require an explicit operator action before creating a product.
- Product creation defaults to `publication_mode=ms_only`.

## Local Smoke Test

```bash
curl -X POST http://localhost:8000/telegram/webhook \
  -H 'Content-Type: application/json' \
  -d '{"message":{"from":{"id":100},"chat":{"id":200},"text":"ART-001 плитка"}}'

curl http://localhost:8000/intake/events
curl http://localhost:8000/miniapp/api/intake/events
```

Expected: one pending intake event with `kind=text`.

## Production Webhook Setup

Set the webhook with a secret token:

```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d "url=https://<domain>/telegram/webhook" \
  -d "secret_token=$TELEGRAM_WEBHOOK_SECRET" \
  -d 'allowed_updates=["message","edited_message"]'
```

Telegram sends the same secret in `X-Telegram-Bot-Api-Secret-Token`; requests
with the wrong secret are rejected before any event is stored.
