# OpenRouter Provider

Reviewed on 2026-06-08.

The project uses OpenRouter as the only LLM gateway. The model is locked to:

```text
google/gemini-3.1-flash-lite
```

The model id was verified against OpenRouter's live `/api/v1/models` endpoint on
2026-06-08.

## API Shape

- Authentication: `Authorization: Bearer <OPENROUTER_API_KEY>`.
- Base chat endpoint: `POST https://openrouter.ai/api/v1/chat/completions`.
- JSON mode: requests include `response_format: {"type": "json_object"}`.

## Implementation Rule

`OpenRouterLLMProvider` rejects any model other than
`google/gemini-3.1-flash-lite`. This is intentional. Model switching must be a
conscious code review decision, not an environment variable accident.

## Runtime Behavior

`OpenRouterLLMProvider.extract_fields(...)` performs one chat-completions POST,
extracts `choices[0].message.content`, and validates that content as
`ExtractionResult`. Invalid JSON or schema drift raises `ValueError`, which keeps
bad LLM output out of the deterministic pipeline.

The default prompt explicitly forbids price calculation, publication, and writes
to external systems. Those actions remain deterministic service responsibilities.

## Sources

- https://openrouter.ai/docs/api/api-reference/models/get-models
- https://openrouter.ai/docs/api-reference/chat-completion
- https://openrouter.ai/docs/api/reference/authentication
- https://openrouter.ai/docs/requests
