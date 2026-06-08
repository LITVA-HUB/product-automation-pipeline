# Telegram Intake and Mini App Contract

Reviewed on 2026-06-08.

Telegram is the preferred operator interface. It is intentionally safe by
default: webhook intake never creates products in МойСклад. It only stores typed
intake events for review and later processing.

## Supported Inputs

- Plain text: article lists, messy notes, copied supplier messages.
- Supplier URL: detected from message text.
- Table document: `.csv`, `.xls`, `.xlsx`.
- Invoice/product photo: Telegram photo or image document.
- Caption plus file: caption is preserved in the intake payload.

## Backend Flow

```text
Telegram update
  -> POST /telegram/webhook
  -> TelegramIntakeService
  -> IntakeItem(kind, payload)
  -> intake_events(status=pending)
  -> GET /intake/events for Mini App queue
```

## Safety Rules

- No МойСклад writes from webhook handling.
- No publication from webhook handling.
- Telegram tokens stay in `TELEGRAM_BOT_TOKEN` / deployment secret storage.
- The Mini App must require an explicit operator action before creating a product.
- Product creation defaults to `publication_mode=ms_only`.

## Local Smoke Test

```bash
curl -X POST http://localhost:8000/telegram/webhook \
  -H 'Content-Type: application/json' \
  -d '{"message":{"from":{"id":100},"chat":{"id":200},"text":"ART-001 плитка"}}'

curl http://localhost:8000/intake/events
```

Expected: one pending intake event with `kind=text`.
